"""
DataSampler module for SynPro.
"""

import numpy as np


class DataSampler:
    """
    DataSampler is responsible for sampling conditional vectors
    and corresponding real rows that match those discrete conditions.
    """

    def __init__(self, data, output_info, log_frequency):
        self._data_length = len(data)

        # Identify which columns are discrete
        def is_discrete_column(col_info):
            return len(col_info) == 1 and col_info[0].activation_fn == 'softmax'

        # Count how many discrete columns
        n_discrete_columns = sum(is_discrete_column(ci) for ci in output_info)

        self._discrete_column_matrix_st = np.zeros(n_discrete_columns, dtype='int32')
        self._rid_by_cat_cols = []

        # Build up rid_by_cat_cols
        st = 0
        discrete_id = 0
        for column_info in output_info:
            if is_discrete_column(column_info):
                span = column_info[0]
                ed = st + span.dim

                rid_list_for_cats = []
                for j in range(span.dim):
                    # Index of rows where that category is 1
                    rid_list_for_cats.append(np.nonzero(data[:, st + j])[0])
                self._rid_by_cat_cols.append(rid_list_for_cats)
                st = ed

                # This discrete column starts at (sum of previous categories)
                self._discrete_column_matrix_st[discrete_id] = 0  # (only used if needed for cond from col info)
                discrete_id += 1
            else:
                st += sum(sp.dim for sp in column_info)

        # Pre-compute probabilities for each discrete column
        max_category = 0
        for column_info in output_info:
            if is_discrete_column(column_info):
                dim = column_info[0].dim
                if dim > max_category:
                    max_category = dim

        self._discrete_column_cond_st = np.zeros(n_discrete_columns, dtype='int32')
        self._discrete_column_n_category = np.zeros(n_discrete_columns, dtype='int32')
        self._discrete_column_category_prob = np.zeros((n_discrete_columns, max_category))
        self._n_discrete_columns = n_discrete_columns
        self._n_categories = 0

        st = 0
        current_id = 0
        current_cond_st = 0
        for column_info in output_info:
            if is_discrete_column(column_info):
                span = column_info[0]
                ed = st + span.dim
                # frequency of each category
                freq = np.sum(data[:, st:ed], axis=0)
                if log_frequency:
                    freq = np.log(freq + 1)
                prob = freq / np.sum(freq)

                self._discrete_column_category_prob[current_id, :span.dim] = prob
                self._discrete_column_cond_st[current_id] = current_cond_st
                self._discrete_column_n_category[current_id] = span.dim
                current_cond_st += span.dim
                current_id += 1
                self._n_categories += span.dim
                st = ed
            else:
                st += sum(sp.dim for sp in column_info)

    def _random_choice_prob_index(self, discrete_column_id):
        """Sample categories from the discrete_column_category_prob, batch-wise."""
        # For each discrete column, we have a category probability distribution
        probs = self._discrete_column_category_prob[discrete_column_id]
        # We pick one category for each entry in the batch
        # Because we want a *vectorized* approach, let's do them one by one
        # If you have a big batch, you can rewrite in vector form
        chosen = []
        for p in discrete_column_id:
            cdf = probs[:]
            r = np.random.rand()
            cidx = (cdf.cumsum() > r).argmax()
            chosen.append(cidx)
        return np.array(chosen)

    def sample_condvec(self, batch):
        """
        Generate a conditional vector for training.

        Returns (cond, mask, discrete_column_id, category_id_in_col),
          where:
           - cond: (batch, #all_categories) 1-hot
           - mask: (batch, #discrete_columns) 1-hot specifying which column was chosen
           - discrete_column_id: (batch,) IDs of chosen discrete column
           - category_id_in_col: (batch,) chosen category ID *within* the chosen column
        """
        if self._n_discrete_columns == 0:
            return None

        # Choose which discrete column is active
        discrete_column_id = np.random.choice(np.arange(self._n_discrete_columns), size=batch)

        # Build cond (batch, n_categories), all zeros -> fill ones
        cond = np.zeros((batch, self._n_categories), dtype='float32')

        # Build mask (batch, n_discrete_columns)
        mask = np.zeros((batch, self._n_discrete_columns), dtype='float32')
        mask[np.arange(batch), discrete_column_id] = 1

        # Now choose a category within that column
        chosen_category_in_col = self._random_choice_prob_index(discrete_column_id)

        # Convert (column, category_in_col) -> global category index
        global_category_idx = (
            self._discrete_column_cond_st[discrete_column_id] + chosen_category_in_col
        )
        cond[np.arange(batch), global_category_idx] = 1

        return cond, mask, discrete_column_id, chosen_category_in_col

    def sample_original_condvec(self, batch):
        """
        For generating data (not training),
        sample a discrete category from the overall distribution of categories.
        """
        if self._n_discrete_columns == 0:
            return None

        # Flatten all columns' category probabilities:
        # shape = (n_discrete_columns, max_category) -> flatten
        flat = self._discrete_column_category_prob.flatten()

        # Some columns might have leftover 0’s if dim < max_category, so filter out 0-dim.
        nonzero_flat = flat[flat != 0]
        nonzero_flat = nonzero_flat / nonzero_flat.sum()

        cat_ids = np.random.choice(len(nonzero_flat), batch, p=nonzero_flat)
        cond = np.zeros((batch, self._n_categories), dtype='float32')
        cond[np.arange(batch), cat_ids] = 1
        return cond

    def sample_data(self, data, n, col, opt):
        """
        Sample data from the real data, matching the given discrete column conditions.
        """
        if col is None:
            # No condition -> pick random row IDs
            idx = np.random.randint(len(data), size=n)
            return data[idx]

        idx = []
        for c, o in zip(col, opt):
            # pick a random row index from rid_by_cat_cols
            idx.append(np.random.choice(self._rid_by_cat_cols[c][o]))
        return data[idx]

    def dim_cond_vec(self):
        """Return total #categories across all discrete columns."""
        return self._n_categories

    def generate_cond_from_condition_column_info(self, condition_info, batch):
        """
        For a specific (column, value),
        return a repeated one-hot vector (batch, n_categories).
        """
        vec = np.zeros((batch, self._n_categories), dtype='float32')
        # if we needed to keep track of matrix start, you would do so here
        # for now, we treat _discrete_column_matrix_st as 0
        col_id = condition_info['discrete_column_id']
        value_id = condition_info['value_id']

        # This example code does not offset by col start; if you used that logic,
        # set the correct offset for col_id. If each discrete column always starts at 0
        # in this code, we do:
        st_index = self._discrete_column_cond_st[col_id] + value_id
        vec[:, st_index] = 1
        return vec
