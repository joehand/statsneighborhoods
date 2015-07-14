# -*- coding: utf-8 -*-
"""
    neighborhood information
    ~~~~~~~~~

    The module calculates various information theory metrics about census-like data.

    Data should be in neighborhood-like units and have an aggregation key (e.g. city).
    Metrics will be calculated along two axes: neighborhood and other binned data.

    Calculations:
    - Entropy
    - KL Divergence
    - Mutual Information

    :copyright: (c) 2014-2015 by Joe Hand, Santa Fe Institute.
    :license: MIT
"""

from functools import wraps

from pandas import DataFrame, Series, concat
from scipy import stats
import numpy as np


class CensusFrame(DataFrame):

    """ Extends Pandas DataFrame for Information Theory Calculations!
        This class takes input data and exposes three main functions:
        - Entropy Calculation
        - DKL Calculation
        - Mutual Information Calculations

        Each of these returns a dataframe.
        The returned dimension will depend on the calculation.

        Data is expected to have these characteristics:
        - Be a Pandas DataFrame or DataFrame-like object (e.g. a csv)
        - Index should have n rows per city (or group)
        - Columns should include:
            - y Bins of data
            - Total column (if different from sum of y bins)
            - A groupby column (e.g. city name)

    Examples
    --------
    """

    LOG_BASE = 2  # Log Base for Entropy/Information Calculations

    def __init__(self, bin_regex='^ACSHINC([0-9])+$', tot_col='ACSTOTHH',
                 group_col='CITY_NAME', group_name='CITY', **kwargs):

        DataFrame.__init__(self, **kwargs)

        self.bin_regex = bin_regex
        self.tot_col = tot_col
        self.group_col = group_col
        # used to for column suffix
        self.group_name = group_name

        # TODO: where should i keep track of these DFs?
        self.nhood_df = self.copy()

    def _filter(self, df=None, regex=None):
        """ Returns a filtered df using regex.
            Shortcut to Pandas DataFrame.filter()
        """
        if df is None:
            df = self
        if regex is None:
            regex = self.bin_regex
        return df.filter(regex=regex)

    def _grouped(self):
        """ Return a grouped df using self.group_col
            Stores grouped df for later use
        """
        if hasattr(self, 'grouped'):
            return self.grouped
        self.grouped = self.groupby(self.group_col)
        return self.grouped

    def _join_group_sums(self, rsuffix=None, join_on=None, **kwargs):
        """ Returns DataFrame of same shape with
                columns matching filter summed by group
        """
        if rsuffix is None:
            rsuffix = '_' + self.group_name
        if join_on is None:
            join_on = self.group_col
        df_grouped = self._filter(df=self._grouped().sum(), **kwargs)
        self.df_summed = self.join(df_grouped, on=join_on, rsuffix=rsuffix)
        return self.df_summed

    def _append_to_df(f):
        """ Appends/creates new DF to two main existing DFs (neighborhood and city)
        """
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            # wrapped function must return the new DF/Series
            new_df = f(self, *args, **kwargs)

            if len(new_df) == len(self.nhood_df):
                nhood = True
                df_name = 'nhood_df'
            else:
                # TODO: HACK!!!! How to tell nbhood df vs citydf
                if not hasattr(self, 'city_df') and len(new_df) < 10000:
                    setattr(self, 'city_df', new_df)
                    return getattr(self, 'city_df')
                elif len(new_df) == len(self.city_df):
                    nhood = False
                    df_name = 'city_df'
                else:
                    # TODO: Fall back on this by default. Another HACK.
                    nhood = True
                    df_name = 'nhood_df'

            df = getattr(self, df_name)

            # old cols that don't need replacing
            old_cols = df.columns.difference(new_df.columns)

            # This overwrites matching columns with NEW DATA!!!
            try:
                setattr(self, df_name,
                        df[old_cols.tolist()].join(new_df, how='outer'))
            except:
                # TODO: Real try/except
                raise Exception
            return new_df  # TODO: or do we want to return full DF?
        return wrapper

    def _entropy(self, *args):
        """ Sets default base for entropy calculation """
        return stats.entropy(*args, base=self.LOG_BASE)

    def weighted_mean(self, val_col_name, wt_col_name):
        def inner(group):
            return (group[val_col_name] *
                    (group[wt_col_name]/group[wt_col_name].mean())).mean()
        inner.__name__ = 'weighted_mean'
        return inner

    def weighted_variance(self, val_col_name, wt_col_name, log=True):
        def inner(group):
            if log:
                return np.log((group[val_col_name] *
                               (group[wt_col_name]/group[wt_col_name].mean()))).var()
            else:
                return (group[val_col_name] *
                        (group[wt_col_name]/group[wt_col_name].mean())).var()
        inner.__name__ = 'weighted_var'
        return inner

    @_append_to_df
    def calculate_group_sums(self, var_list=[], var_regex=None):
        """ Sum the list of vars across the group. """
        if len(var_list) == 0 and not var_regex:
            raise Exception
        if var_regex:
            var_list.extend(self._filter(regex=var_regex).columns.values)
        df_grouped = self._grouped()[var_list].sum()
        return df_grouped

    @_append_to_df
    def calculate_group_means(self, weighted=True, var_list=[], var_regex=None):
        """ Calculates mean/adjusted mean for each group
            Adjustement uses population variable to properly adjust means
        """
        if len(var_list) == 0 and not var_regex:
            raise Exception
        if var_regex:
            var_list.extend(self._filter(regex=var_regex).columns.values)
        df_grouped = self._grouped()[var_list].mean()
        if weighted:
            # Adjust by multiplying each row value by
            #    % of mean population (e.g. block_pop / nyc_mean_block_pop)
            for var in var_list:
                df_grouped[var + '_weighted'] = self._grouped().apply(
                    self.weighted_mean(var, self.tot_col))
        return df_grouped

    @_append_to_df
    def calculate_group_variance(self, weighted=True,
                                 var_list=[], var_regex=None, **kwargs):
        """ Calculates mean/adjusted mean for each group
            Adjustement uses population variable to properly adjust means
        """
        if len(var_list) == 0 and not var_regex:
            raise Exception
        if var_regex:
            var_list.extend(self._filter(regex=var_regex).columns.values)
        df_grouped = self._grouped()[var_list].var()
        df_grouped = df_grouped.rename(
            columns={var: var+'_variance' for var in var_list})
        if weighted:
            # Adjust by multiplying each row value
            #   by % of mean population (e.g. block_pop / nyc_mean_block_pop)
            for var in var_list:
                df_grouped[var + '_weighted_var'] = self._grouped().apply(
                    self.weighted_variance(var, self.tot_col, **kwargs))
        return df_grouped

    @_append_to_df
    def p_n(self):
        """
        Calculates p_n

        Returns
        -------
        p(n) : DataFrame
        """
        df = self._join_group_sums(
            regex=self.tot_col)  # DF w/ sums across group

        p_n = df[self.tot_col]/df[self.tot_col + '_' + self.group_name]
        self.p_n = DataFrame({'p(n)': p_n}, index=df.index)
        return self.p_n

    @_append_to_df
    def nhood_weights(self):
        """
        Calculates weight across y bins of data (determined by self.bin_regex)

        Returns
        -------
        weights : DataFrame
        """
        regex = self.tot_col + '|' + self.bin_regex
        df = self._join_group_sums(regex=regex)
        nhood_total = df[self.tot_col]
        city_total = df[self.tot_col + '_CITY']
        for col in df.filter(regex=self.bin_regex).columns:
            df[col+'_W'] = (df[col]/nhood_total)/(df[col+'_CITY']/city_total)
        self.df_w = df.filter(regex='_W$').replace([np.inf, -np.inf], np.nan)
        return self.df_w

    @_append_to_df
    def entropy_y(self, conditional=True):
        """
        Calculates entropy across y bins of data (determined by self.bin_regex)

        Two separate returns because dimension changes for non-conditional

        Parameters
        ----------
        conditional : boolean, default True
            Calculate entropy conditionally on each neighborhood

        Returns
        -------
        entropy : DataFrame
        """
        if conditional:
            # Returns same number of rows of data as original DF
            df = self._filter()
            H = self._entropy(df.transpose())  # Entropy of y bins for each row
            self.H_y_n = DataFrame({'H(y|n)': H}, index=df.index)
            return self.H_y_n
        else:
            # Returns len(groups) rows of data
            df_grouped = self._filter(df=self._grouped().sum())
            # Entropy of y bins for each group
            H = self._entropy(df_grouped.transpose())
            self.H_y = DataFrame({'H(y)': H}, index=df_grouped.index)
            return self.H_y

    @_append_to_df
    def dkl_y(self):
        """
        Calculates conditional entropy/KL Divergence for y bins of data

        Returns
        -------
        KL Divergence : DataFrame
        """
        df = self._filter()  # DF with just y bins

        # Regex to get group columns
        regex = self.bin_regex[:-1] + '_' + self.group_name
        # DF w/ sums across group
        df_city = self._filter(df=self._join_group_sums(), regex=regex)
        # Calcuate conditional entropy/DKL
        DKL = self._entropy(df.transpose(), df_city.transpose())
        self.DKL_y = DataFrame({'DKL(y|n)': DKL}, index=df.index)
        return self.DKL_y

    @_append_to_df
    def entropy_n(self, calc_dkl=True):
        """
        Calcualte the entropy of neighborhoods conditional on each bin and overall

        Parameters
        ----------
        calc_dkl : boolean, default True
            Calculate KL Divergence at the same time (faster)

        Returns
        -------
        entropy : DataFrame
        """
        df_city = []
        if calc_dkl:
            df_city_dkl = []
        cols = self._filter().columns
        bin_num = len(cols)
        for name, group in self._grouped():
            group_tot = group[self.tot_col].sum()
            p_n = DataFrame(
                [group[self.tot_col]/group_tot]*bin_num).transpose()
            H_n = Series(self._entropy(p_n)[0], index=['H(n)'], name=name)

            group_filtered = self._filter(df=group)
            H_n_y = Series(
                self._entropy(group_filtered), index=cols, name=name)
            H_n_y.index = ['H(n|y)_' + str(item) for item in H_n_y.index]

            if calc_dkl:
                DKL_n = self._dkl_n_group(group_filtered, name, cols, p_n)
                df_city_dkl.append(DKL_n)

            df_city.append(H_n_y.append(H_n))

        self.H_n = DataFrame(df_city)
        if calc_dkl:
            self.DKL_n = DataFrame(df_city_dkl)
            # Return all the data
            return concat([self.H_n, self.DKL_n], axis=1)
        return self.H_n

    def _dkl_n_group(self, group_df, name, cols, p_n):
        """
        Calculate DKL(n|y) for a single group

        Parameters
        ----------
        group_df : DataFrame
        name : String
            Name of group (from Pandas.grouped())

        Returns
        -------
        DKL_n : Series
        """
        DKL_n = Series(self._entropy(group_df, p_n), index=cols, name=name)
        DKL_n.index = ['DKL(n|y)_' + str(item) for item in DKL_n.index]
        return DKL_n

    @_append_to_df
    def dkl_n(self):
        """
        Calculate (or return) KL Divergence(n|y)

        Returns
        -------
        KL Divergence : DataFrame
        """
        if hasattr(self, 'DKL_n'):
            return self.DKL_n

        df_city_dkl = []
        cols = self._filter().columns
        bin_num = len(cols)
        for name, group in self._grouped():
            group_tot = group[self.tot_col].sum()
            p_n = DataFrame(
                [group[self.tot_col]/group_tot]*bin_num).transpose()

            group_filtered = self._filter(df=group)
            DKL_n = self._dkl_n_group(group_filtered, name, cols, p_n)
            df_city_dkl.append(DKL_n)

        self.DKL_n = DataFrame(df_city_dkl)
        return self.DKL_n

    @_append_to_df
    def mutual_info(self):
        """
        Calculate Mutual Information

        MI = sum over l (Nl/N)*DKL

        Returns
        -------
        Mutual Information : Series
        """
        #
        grouped_sum = self._grouped().sum()
        N_l = self._filter(df=grouped_sum).div(
            grouped_sum[self.tot_col], axis='index').values
        DKL = self.dkl_n().values

        MI = DataFrame(N_l*DKL, index=self.DKL_n.index).sum(axis=1)
        self.MI = DataFrame(MI, index=self.DKL_n.index, columns=['MI'])
        return self.MI
