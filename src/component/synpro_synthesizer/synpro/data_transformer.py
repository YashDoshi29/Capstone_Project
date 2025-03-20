"""
DataTransformer module for SynPro.
"""

from collections import namedtuple

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from rdt.transformers import ClusterBasedNormalizer, OneHotEncoder

from synpro.errors import InvalidDataError

SpanInfo = namedtuple('SpanInfo', ['dim', 'activation_fn'])
ColumnTransformInfo = namedtuple(
    'ColumnTransformInfo',
    ['column_name', 'column_type', 'transform', 'output_info', 'output_dimensions'],
)


class DataTransformer:
    """
    Data Transformer for the SynPro model.

    - Continuous columns: modeled by a ClusterBasedNormalizer (Bayesian GMM),
      resulting in a normalized scalar + one-hot-encoded cluster membership.
    - Discrete columns: one-hot-encoded via RDT's OneHotEncoder.
    """

    def __init__(self, max_clusters=10, weight_threshold=0.005):
        self._max_clusters = max_clusters
        self._weight_threshold = weight_threshold

    def _fit_continuous(self, data):
        column_name = data.columns[0]
        gm = ClusterBasedNormalizer(
            missing_value_generation='from_column',
            max_clusters=min(len(data), self._max_clusters),
            weight_threshold=self._weight_threshold,
        )
        gm.fit(data, column_name)
        num_components = sum(gm.valid_component_indicator)

        return ColumnTransformInfo(
            column_name=column_name,
            column_type='continuous',
            transform=gm,
            output_info=[SpanInfo(1, 'tanh'), SpanInfo(num_components, 'softmax')],
            output_dimensions=1 + num_components,
        )

    def _fit_discrete(self, data):
        column_name = data.columns[0]
        ohe = OneHotEncoder()
        ohe.fit(data, column_name)
        num_categories = len(ohe.dummies)

        return ColumnTransformInfo(
            column_name=column_name,
            column_type='discrete',
            transform=ohe,
            output_info=[SpanInfo(num_categories, 'softmax')],
            output_dimensions=num_categories,
        )

    def fit(self, raw_data, discrete_columns=()):
        """
        Fit the DataTransformer:
          - Identify discrete vs continuous columns.
          - Prepare transformations.
        """
        self.output_info_list = []
        self.output_dimensions = 0
        self.dataframe = True

        if not isinstance(raw_data, pd.DataFrame):
            self.dataframe = False
            # Convert discrete column indices to string for RDT
            discrete_columns = [str(column) for column in discrete_columns]
            column_names = [str(num) for num in range(raw_data.shape[1])]
            raw_data = pd.DataFrame(raw_data, columns=column_names)

        self._column_raw_dtypes = raw_data.infer_objects().dtypes
        self._column_transform_info_list = []

        for column_name in raw_data.columns:
            if column_name in discrete_columns:
                cti = self._fit_discrete(raw_data[[column_name]])
            else:
                cti = self._fit_continuous(raw_data[[column_name]])

            self.output_info_list.append(cti.output_info)
            self.output_dimensions += cti.output_dimensions
            self._column_transform_info_list.append(cti)

    def _transform_continuous(self, column_transform_info, data):
        column_name = data.columns[0]
        flattened = data[column_name].to_numpy().flatten()
        data = data.assign(**{column_name: flattened})
        gm = column_transform_info.transform
        transformed = gm.transform(data)

        # First col is normalized, second col is integer cluster -> one-hot
        output = np.zeros((len(transformed), column_transform_info.output_dimensions))
        output[:, 0] = transformed[f'{column_name}.normalized'].to_numpy()
        index = transformed[f'{column_name}.component'].to_numpy().astype(int)
        output[np.arange(index.size), index + 1] = 1.0

        return output

    def _transform_discrete(self, column_transform_info, data):
        ohe = column_transform_info.transform
        return ohe.transform(data).to_numpy()

    def _synchronous_transform(self, raw_data, ctinfo_list):
        column_data_list = []
        for info in ctinfo_list:
            colname = info.column_name
            subset = raw_data[[colname]]
            if info.column_type == 'continuous':
                column_data_list.append(self._transform_continuous(info, subset))
            else:
                column_data_list.append(self._transform_discrete(info, subset))
        return column_data_list

    def _parallel_transform(self, raw_data, ctinfo_list):
        processes = []
        for info in ctinfo_list:
            colname = info.column_name
            subset = raw_data[[colname]]
            if info.column_type == 'continuous':
                proc = delayed(self._transform_continuous)(info, subset)
            else:
                proc = delayed(self._transform_discrete)(info, subset)
            processes.append(proc)
        return Parallel(n_jobs=-1)(processes)

    def transform(self, raw_data):
        """Convert input DataFrame/ndarray to the numeric array for SynPro training."""
        if not isinstance(raw_data, pd.DataFrame):
            column_names = [str(num) for num in range(raw_data.shape[1])]
            raw_data = pd.DataFrame(raw_data, columns=column_names)

        if raw_data.shape[0] < 500:
            # For smaller data, parallel overhead is bigger than the benefit
            column_data_list = self._synchronous_transform(raw_data, self._column_transform_info_list)
        else:
            column_data_list = self._parallel_transform(raw_data, self._column_transform_info_list)

        return np.concatenate(column_data_list, axis=1).astype(float)

    def _inverse_transform_continuous(self, cti, column_data, sigmas, st):
        gm = cti.transform
        out_cols = list(gm.get_output_sdtypes())
        data = pd.DataFrame(column_data[:, :2], columns=out_cols).astype(float)
        data[data.columns[1]] = np.argmax(column_data[:, 1:], axis=1)

        if sigmas is not None:
            selected_normalized_value = np.random.normal(data.iloc[:, 0], sigmas[st])
            data.iloc[:, 0] = selected_normalized_value

        return gm.reverse_transform(data)

    def _inverse_transform_discrete(self, cti, column_data):
        ohe = cti.transform
        dummy_cols = list(ohe.get_output_sdtypes())
        data = pd.DataFrame(column_data, columns=dummy_cols)
        return ohe.reverse_transform(data)[cti.column_name]

    def inverse_transform(self, data, sigmas=None):
        """
        Convert numeric output back to the original space or DataFrame.
        """
        st = 0
        recovered_cols = []
        col_names = []

        for cti in self._column_transform_info_list:
            dim = cti.output_dimensions
            col_slice = data[:, st: st + dim]
            if cti.column_type == 'continuous':
                rec_col = self._inverse_transform_continuous(cti, col_slice, sigmas, st)
            else:
                rec_col = self._inverse_transform_discrete(cti, col_slice)

            recovered_cols.append(rec_col)
            col_names.append(cti.column_name)
            st += dim

        recovered_data = np.column_stack(recovered_cols)
        recovered_data = pd.DataFrame(recovered_data, columns=col_names).astype(self._column_raw_dtypes)

        if not self.dataframe:
            return recovered_data.to_numpy()
        return recovered_data

    def convert_column_name_value_to_id(self, column_name, value):
        """
        Convert (column_name, discrete_value) to
        (discrete_column_id, column_id, value_id).
        """
        discrete_counter = 0
        column_id = 0
        for cti in self._column_transform_info_list:
            if cti.column_name == column_name:
                break
            if cti.column_type == 'discrete':
                discrete_counter += 1
            column_id += 1
        else:
            raise ValueError(f"Column name `{column_name}` not found in the data.")

        ohe = cti.transform
        tmp_df = pd.DataFrame([value], columns=[cti.column_name])
        one_hot = ohe.transform(tmp_df).to_numpy()[0]
        if sum(one_hot) == 0:
            raise ValueError(f"Value `{value}` does not exist in column `{column_name}`.")

        return {
            'discrete_column_id': discrete_counter,
            'column_id': column_id,
            'value_id': int(np.argmax(one_hot)),
        }
