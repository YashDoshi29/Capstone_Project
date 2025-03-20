"""
SynPro Model: Enhanced version with optional spectral norm,
multiple GAN losses (wgan-gp, r1, hinge), and mixed-precision training.
"""

import warnings
import numpy as np
import pandas as pd
import torch
from torch import nn, optim
from torch.nn import functional as F
from torch.nn.utils import spectral_norm
from tqdm import tqdm
from torch.cuda.amp import autocast, GradScaler

from synpro.base import BaseSynthesizer, random_state
from synpro.data_sampler import DataSampler
from synpro.data_transformer import DataTransformer
from synpro.errors import InvalidDataError


def apply_spectral_norm_if_enabled(module, enable_spectral_norm):
    """Utility to apply spectral norm to all linear layers in `module` if enabled_spectral_norm=True."""
    if not enable_spectral_norm:
        return module

    for name, layer in module.named_children():
        if isinstance(layer, nn.Linear):
            sn_layer = spectral_norm(layer)
            setattr(module, name, sn_layer)
        else:
            apply_spectral_norm_if_enabled(layer, enable_spectral_norm)
    return module


class Discriminator(nn.Module):
    """
    Discriminator for the SynPro model with optional spectral normalization.
    """

    def __init__(self, input_dim, discriminator_dim, pac=10, enable_spectral_norm=False):
        super().__init__()
        self.pac = pac
        dim = input_dim * pac

        layers = []
        in_features = dim
        for layer_size in discriminator_dim:
            linear = nn.Linear(in_features, layer_size)
            layers.append(linear)
            layers.append(nn.LeakyReLU(0.2))
            layers.append(nn.Dropout(0.5))
            in_features = layer_size

        layers.append(nn.Linear(in_features, 1))
        self.seq = nn.Sequential(*layers)
        # Optionally apply spectral normalization
        if enable_spectral_norm:
            apply_spectral_norm_if_enabled(self.seq, True)

    def calc_gradient_penalty_wgan_gp(self, real_data, fake_data, device='cpu', lambda_=10):
        """WGAN-GP gradient penalty."""
        alpha = torch.rand(real_data.size(0), 1, device=device)
        alpha = alpha.expand(real_data.size())
        interpolates = alpha * real_data + ((1 - alpha) * fake_data)
        interpolates.requires_grad_(True)

        disc_interpolates = self(interpolates)
        grad_outputs = torch.ones(disc_interpolates.size(), device=device)
        gradients = torch.autograd.grad(
            outputs=disc_interpolates,
            inputs=interpolates,
            grad_outputs=grad_outputs,
            create_graph=True,
            retain_graph=True,
            only_inputs=True
        )[0]

        gradient_norm = gradients.view(gradients.size(0), -1).norm(2, dim=1)
        gradient_penalty = ((gradient_norm - 1) ** 2).mean() * lambda_
        return gradient_penalty

    def calc_gradient_penalty_r1(self, real_data, d_real):
        """
        R1 regularization (https://arxiv.org/abs/1801.04406).
        Typically you do gamma/2 * E[|| grad D(real_data)||^2].
        We'll incorporate gamma factor externally if needed.
        """
        grad_real = torch.autograd.grad(
            outputs=d_real.sum(),
            inputs=real_data,
            create_graph=True
        )[0]
        grad_penalty = grad_real.view(grad_real.size(0), -1).pow(2).sum(dim=1).mean()
        return grad_penalty

    def forward(self, x):
        assert x.size(0) % self.pac == 0, "Batch size must be divisible by pac"
        # flatten if pac > 1
        return self.seq(x.view(x.size(0), -1))


class Residual(nn.Module):
    """
    Simple Residual block for the SynPro Generator.
    """
    def __init__(self, i, o):
        super().__init__()
        self.fc = nn.Linear(i, o)
        self.bn = nn.BatchNorm1d(o)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.fc(x)
        out = self.bn(out)
        out = self.relu(out)
        # Concatenate skip connection
        return torch.cat([x, out], dim=1)


class Generator(nn.Module):
    """
    Generator for the SynPro model (with residual connections).
    """

    def __init__(self, embedding_dim, generator_dim, data_dim, enable_spectral_norm=False):
        super().__init__()
        dim = embedding_dim
        layers = []
        for gdim in generator_dim:
            layers.append(Residual(dim, gdim))
            dim += gdim
        layers.append(nn.Linear(dim, data_dim))
        self.seq = nn.Sequential(*layers)

        # Usually spectral norm is used in discriminator, but you can do so here if you prefer
        if enable_spectral_norm:
            apply_spectral_norm_if_enabled(self.seq, True)

    def forward(self, x):
        return self.seq(x)


class SynPro(BaseSynthesizer):
    """
    SynPro: A next-level synthesizer with advanced features:

    - Choice of adversarial loss: wgan-gp, r1, or hinge.
    - Optional spectral normalization in the discriminator (and generator if desired).
    - Mixed-precision training for faster GPU training.
    """

    def __init__(
        self,
        embedding_dim=128,
        generator_dim=(256, 256),
        discriminator_dim=(256, 256),
        generator_lr=2e-4,
        generator_decay=1e-6,
        discriminator_lr=2e-4,
        discriminator_decay=1e-6,
        batch_size=500,
        discriminator_steps=1,
        log_frequency=True,
        verbose=False,
        epochs=300,
        pac=10,
        cuda=True,
        adv_loss='wgan-gp',          # 'wgan-gp', 'r1', 'hinge'
        gp_lambda=10.0,              # gradient penalty lambda for wgan-gp
        r1_gamma=10.0,               # r1 penalty gamma
        enable_spectral_norm=False,
        mixed_precision=False        # enable AMP for faster GPU training
    ):
        super().__init__()

        assert batch_size % 2 == 0, "Batch size must be even (default) for these settings."
        self._embedding_dim = embedding_dim
        self._generator_dim = generator_dim
        self._discriminator_dim = discriminator_dim

        self._generator_lr = generator_lr
        self._generator_decay = generator_decay
        self._discriminator_lr = discriminator_lr
        self._discriminator_decay = discriminator_decay

        self._batch_size = batch_size
        self._discriminator_steps = discriminator_steps
        self._log_frequency = log_frequency
        self._verbose = verbose
        self._epochs = epochs
        self._pac = pac

        # Adversarial loss settings
        self._adv_loss = adv_loss
        self._gp_lambda = gp_lambda
        self._r1_gamma = r1_gamma
        self._enable_spectral_norm = enable_spectral_norm
        self._mixed_precision = mixed_precision

        if not cuda or not torch.cuda.is_available():
            device = 'cpu'
        elif isinstance(cuda, str):
            device = cuda
        else:
            device = 'cuda'
        self._device = torch.device(device)

        self._transformer = None
        self._data_sampler = None
        self._generator = None
        self.loss_values = None

        # We'll use a GradScaler if mixed_precision is True
        self._scaler = GradScaler() if self._mixed_precision else None

    @staticmethod
    def _gumbel_softmax(logits, tau=1, hard=False, eps=1e-10, dim=-1):
        # Retry a few times to avoid NaNs
        for _ in range(10):
            out = F.gumbel_softmax(logits, tau=tau, hard=hard, eps=eps, dim=dim)
            if not torch.isnan(out).any():
                return out
        raise ValueError("gumbel_softmax returning NaN repeatedly.")

    def _apply_activate(self, data):
        """Map generator output to final space (tanh or softmax)."""
        out = []
        st = 0
        for col_info in self._transformer.output_info_list:
            for span_info in col_info:
                if span_info.activation_fn == 'tanh':
                    ed = st + span_info.dim
                    out.append(torch.tanh(data[:, st:ed]))
                    st = ed
                elif span_info.activation_fn == 'softmax':
                    ed = st + span_info.dim
                    chunk = self._gumbel_softmax(data[:, st:ed], tau=0.2)
                    out.append(chunk)
                    st = ed
                else:
                    raise ValueError(f"Unknown activation {span_info.activation_fn}.")
        return torch.cat(out, dim=1)

    def _cond_loss(self, data, c, m):
        """
        Cross entropy loss on the discrete columns for which we conditioned.
        """
        losses = []
        st_data = 0
        st_cond = 0
        for col_info in self._transformer.output_info_list:
            # If discrete
            if len(col_info) == 1 and col_info[0].activation_fn == 'softmax':
                span = col_info[0].dim
                ed_data = st_data + span
                ed_cond = st_cond + span

                cross_ent = F.cross_entropy(
                    data[:, st_data:ed_data],
                    torch.argmax(c[:, st_cond:ed_cond], dim=1),
                    reduction='none'
                )
                losses.append(cross_ent)
                st_data = ed_data
                st_cond = ed_cond
            else:
                # If continuous or multi-chunk column
                span = sum(sp.dim for sp in col_info)
                st_data += span
        if not losses:
            return 0

        # (batch, #discrete columns)
        losses = torch.stack(losses, dim=1)
        return (losses * m).sum() / data.size(0)

    def _validate_discrete_columns(self, train_data, discrete_columns):
        if isinstance(train_data, pd.DataFrame):
            invalid_cols = set(discrete_columns) - set(train_data.columns)
        elif isinstance(train_data, np.ndarray):
            invalid_cols = []
            for c in discrete_columns:
                if c < 0 or c >= train_data.shape[1]:
                    invalid_cols.append(c)
        else:
            raise TypeError("train_data must be DataFrame or NumPy array.")

        if invalid_cols:
            raise ValueError(f"Invalid columns found: {invalid_cols}")

    def _validate_null_data(self, train_data, discrete_columns):
        if isinstance(train_data, pd.DataFrame):
            cont_cols = set(train_data.columns) - set(discrete_columns)
            has_nulls = train_data[list(cont_cols)].isna().any().any()
        else:
            cont_cols = [i for i in range(train_data.shape[1]) if i not in discrete_columns]
            has_nulls = pd.DataFrame(train_data)[cont_cols].isna().any().any()

        if has_nulls:
            raise InvalidDataError(
                "SynPro does not support null values in continuous data. Remove or impute them."
            )

    @random_state
    def fit(self, train_data, discrete_columns=(), epochs=None):
        """Train the SynPro model on data with advanced features."""
        self._validate_discrete_columns(train_data, discrete_columns)
        self._validate_null_data(train_data, discrete_columns)

        if epochs is None:
            epochs = self._epochs
        else:
            warnings.warn(
                "`epochs` argument in `fit` is deprecated; use the constructor param instead.",
                DeprecationWarning
            )

        # Transform data
        self._transformer = DataTransformer()
        self._transformer.fit(train_data, discrete_columns)
        train_data = self._transformer.transform(train_data)
        self._data_sampler = DataSampler(train_data, self._transformer.output_info_list, self._log_frequency)

        data_dim = self._transformer.output_dimensions
        gen_input_dim = self._embedding_dim + self._data_sampler.dim_cond_vec()

        self._generator = Generator(
            gen_input_dim,
            self._generator_dim,
            data_dim,
            enable_spectral_norm=False  # Typically spectral norm is more crucial in D
        ).to(self._device)

        discriminator = Discriminator(
            data_dim + self._data_sampler.dim_cond_vec(),
            self._discriminator_dim,
            pac=self._pac,
            enable_spectral_norm=self._enable_spectral_norm
        ).to(self._device)

        optimizerG = optim.Adam(
            self._generator.parameters(),
            lr=self._generator_lr,
            betas=(0.5, 0.9),
            weight_decay=self._generator_decay
        )
        optimizerD = optim.Adam(
            discriminator.parameters(),
            lr=self._discriminator_lr,
            betas=(0.5, 0.9),
            weight_decay=self._discriminator_decay
        )

        mean = torch.zeros(self._batch_size, self._embedding_dim, device=self._device)
        std = mean + 1
        self.loss_values = pd.DataFrame(columns=['Epoch', 'Generator Loss', 'Discriminator Loss'])

        steps_per_epoch = max(len(train_data) // self._batch_size, 1)
        epoch_iterator = tqdm(range(epochs), disable=(not self._verbose))
        if self._verbose:
            desc = "Gen. ({gen:.2f}) | Discrim. ({dis:.2f})"
            epoch_iterator.set_description(desc.format(gen=0, dis=0))

        for epoch in epoch_iterator:
            for _ in range(steps_per_epoch):
                # ==========================
                # Train Discriminator
                # ==========================
                for _dstep in range(self._discriminator_steps):
                    # Sample noise
                    fakez = torch.normal(mean=mean, std=std)
                    condvec = self._data_sampler.sample_condvec(self._batch_size)
                    if condvec is None:
                        c1, m1, col, opt = None, None, None, None
                        real = self._data_sampler.sample_data(train_data, self._batch_size, col, opt)
                    else:
                        c1, m1, col, opt = condvec
                        c1 = torch.from_numpy(c1).to(self._device)
                        m1 = torch.from_numpy(m1).to(self._device)
                        fakez = torch.cat([fakez, c1], dim=1)

                        perm = np.arange(self._batch_size)
                        np.random.shuffle(perm)
                        real = self._data_sampler.sample_data(train_data, self._batch_size, col[perm], opt[perm])
                        c2 = c1[perm]

                    real = torch.from_numpy(real.astype('float32')).to(self._device)

                    # Forward pass in mixed precision if enabled
                    if self._scaler:
                        with autocast():
                            fake = self._generator(fakez)
                            fakeact = self._apply_activate(fake)

                            if c1 is not None:
                                fake_cat = torch.cat([fakeact, c1], dim=1)
                                real_cat = torch.cat([real, c2], dim=1)
                            else:
                                fake_cat = fakeact
                                real_cat = real

                            d_fake = discriminator(fake_cat)
                            d_real = discriminator(real_cat)

                            if self._adv_loss == 'wgan-gp':
                                gp = discriminator.calc_gradient_penalty_wgan_gp(
                                    real_cat, fake_cat, device=self._device, lambda_=self._gp_lambda
                                )
                                loss_d = -(torch.mean(d_real) - torch.mean(d_fake)) + gp

                            elif self._adv_loss == 'r1':
                                # R1 penalty uses gradient wrt real data
                                r1_penalty = discriminator.calc_gradient_penalty_r1(real_cat, d_real)
                                loss_d = -(torch.mean(d_real) - torch.mean(d_fake)) + 0.5 * self._r1_gamma * r1_penalty

                            elif self._adv_loss == 'hinge':
                                # Hinge-based loss
                                loss_d_real = torch.mean(F.relu(1.0 - d_real))
                                loss_d_fake = torch.mean(F.relu(1.0 + d_fake))
                                loss_d = loss_d_real + loss_d_fake

                            else:
                                raise ValueError(f"Unsupported adv_loss: {self._adv_loss}")

                        optimizerD.zero_grad()
                        # scale and backward
                        self._scaler.scale(loss_d).backward(retain_graph=True)
                        self._scaler.step(optimizerD)
                        self._scaler.update()

                    else:
                        # Normal precision
                        fake = self._generator(fakez)
                        fakeact = self._apply_activate(fake)

                        if c1 is not None:
                            fake_cat = torch.cat([fakeact, c1], dim=1)
                            real_cat = torch.cat([real, c2], dim=1)
                        else:
                            fake_cat = fakeact
                            real_cat = real

                        d_fake = discriminator(fake_cat)
                        d_real = discriminator(real_cat)

                        if self._adv_loss == 'wgan-gp':
                            gp = discriminator.calc_gradient_penalty_wgan_gp(
                                real_cat, fake_cat, device=self._device, lambda_=self._gp_lambda
                            )
                            loss_d = -(torch.mean(d_real) - torch.mean(d_fake)) + gp

                        elif self._adv_loss == 'r1':
                            r1_penalty = discriminator.calc_gradient_penalty_r1(real_cat, d_real)
                            loss_d = -(torch.mean(d_real) - torch.mean(d_fake)) + 0.5 * self._r1_gamma * r1_penalty

                        elif self._adv_loss == 'hinge':
                            loss_d_real = torch.mean(F.relu(1.0 - d_real))
                            loss_d_fake = torch.mean(F.relu(1.0 + d_fake))
                            loss_d = loss_d_real + loss_d_fake

                        else:
                            raise ValueError(f"Unsupported adv_loss: {self._adv_loss}")

                        optimizerD.zero_grad()
                        loss_d.backward(retain_graph=True)
                        optimizerD.step()

                # ==========================
                # Train Generator
                # ==========================
                fakez = torch.normal(mean=mean, std=std)
                condvec = self._data_sampler.sample_condvec(self._batch_size)
                if condvec is None:
                    c1, m1, col, opt = None, None, None, None
                else:
                    c1, m1, col, opt = condvec
                    c1 = torch.from_numpy(c1).to(self._device)
                    m1 = torch.from_numpy(m1).to(self._device)
                    fakez = torch.cat([fakez, c1], dim=1)

                if self._scaler:
                    with autocast():
                        fake = self._generator(fakez)
                        fakeact = self._apply_activate(fake)
                        if c1 is not None:
                            y_fake = discriminator(torch.cat([fakeact, c1], dim=1))
                        else:
                            y_fake = discriminator(fakeact)

                        cross_entropy = 0
                        if condvec is not None:
                            cross_entropy = self._cond_loss(fake, c1, m1)

                        if self._adv_loss in ['wgan-gp', 'r1']:
                            loss_g = -torch.mean(y_fake) + cross_entropy
                        elif self._adv_loss == 'hinge':
                            # Hinge generator tries to push d_fake >= -1
                            loss_g = -torch.mean(y_fake) + cross_entropy
                        else:
                            raise ValueError(f"Unsupported adv_loss: {self._adv_loss}")

                    optimizerG.zero_grad()
                    self._scaler.scale(loss_g).backward()
                    self._scaler.step(optimizerG)
                    self._scaler.update()

                else:
                    # normal precision
                    fake = self._generator(fakez)
                    fakeact = self._apply_activate(fake)
                    if c1 is not None:
                        y_fake = discriminator(torch.cat([fakeact, c1], dim=1))
                    else:
                        y_fake = discriminator(fakeact)

                    cross_entropy = 0
                    if condvec is not None:
                        cross_entropy = self._cond_loss(fake, c1, m1)

                    if self._adv_loss in ['wgan-gp', 'r1']:
                        loss_g = -torch.mean(y_fake) + cross_entropy
                    elif self._adv_loss == 'hinge':
                        loss_g = -torch.mean(y_fake) + cross_entropy
                    else:
                        raise ValueError(f"Unsupported adv_loss: {self._adv_loss}")

                    optimizerG.zero_grad()
                    loss_g.backward()
                    optimizerG.step()

            g_loss_val = loss_g.detach().cpu().item()
            d_loss_val = loss_d.detach().cpu().item()
            row = pd.DataFrame({
                "Epoch": [epoch],
                "Generator Loss": [g_loss_val],
                "Discriminator Loss": [d_loss_val],
            })
            self.loss_values = pd.concat([self.loss_values, row], ignore_index=True)

            if self._verbose:
                epoch_iterator.set_description(desc.format(gen=g_loss_val, dis=d_loss_val))

    @random_state
    def sample(self, n, condition_column=None, condition_value=None):
        """Sample data from the trained SynPro model."""
        if condition_column is not None and condition_value is not None:
            col_info = self._transformer.convert_column_name_value_to_id(condition_column, condition_value)
            global_cond_vec = self._data_sampler.generate_cond_from_condition_column_info(col_info, self._batch_size)
        else:
            global_cond_vec = None

        steps = n // self._batch_size + 1
        data = []
        for _ in range(steps):
            mean = torch.zeros(self._batch_size, self._embedding_dim, device=self._device)
            std = mean + 1
            fakez = torch.normal(mean=mean, std=std)

            if global_cond_vec is not None:
                c1 = torch.from_numpy(global_cond_vec).to(self._device)
                fakez = torch.cat([fakez, c1], dim=1)
            else:
                condvec = self._data_sampler.sample_original_condvec(self._batch_size)
                if condvec is not None:
                    c1 = torch.from_numpy(condvec).to(self._device)
                    fakez = torch.cat([fakez, c1], dim=1)

            # Inference can also do autocast if desired, but typically optional
            fake = self._generator(fakez)
            fakeact = self._apply_activate(fake)
            data.append(fakeact.detach().cpu().numpy())

        data = np.concatenate(data, axis=0)
        data = data[:n]
        return self._transformer.inverse_transform(data)

    def set_device(self, device):
        """Move the model to a specified device: CPU or GPU."""
        self._device = torch.device(device)
        if self._generator is not None:
            self._generator.to(self._device)
