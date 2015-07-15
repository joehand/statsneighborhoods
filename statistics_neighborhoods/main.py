# -*- coding: utf-8 -*-
"""
    statistics of neighborhoods
    ~~~~~~~~~

    :copyright: (c) 2015 by Joe Hand, Santa Fe Institute.
    :license: MIT
"""

"""
    TODO:
    what needs to be here? in notebook I currently do:

    def run_information_calculations(df, **kwargs):
        _ = df.calculate_group_sums(**kwargs)
        _ = df.calculate_group_means(var_list=['ACSAVGHINC'])
        _ = df.calculate_group_variance(var_list=['ACSAVGHINC'])
        _ = df.nhood_weights()
        _ = df.dkl_y()
        _ = df.entropy_y()
        _ = df.entropy_y(conditional=False)
        _ = df.entropy_n()
        _ = df.mutual_info()
        return

    census2010['log_ACSAVGHINC'] = np.log(census2010['ACSAVGHINC'])
    census10 = information.CensusFrame(data=census2010)
    run_information_calculations(census10, var_regex = '^ACSHINC([0-9])+$', var_list=['ACSTOTPOP', 'ACSTOTHH'])
"""


def function():
    pass