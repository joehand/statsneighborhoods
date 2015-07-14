# -*- coding: utf-8 -*-
"""
    cumulant calculations
    ~~~~~~~~~

    :copyright: (c) 2015 by Joe Hand, Santa Fe Institute.
    :license: MIT
"""
from pandas import DataFrame
import scipy.stats as st
import numpy as np


def _bin_area(count, bin_edges):
    """ Returns the area of a single histogram bin (width * height)
    """
    return count * abs(bin_edges[1] - bin_edges[0])


def _total_area(hist_data, bin_edges):
    """ Returns float total area of a hisogram
        Can calculate total area directly from what np.hist() returns.

        Parameters
        ----------
        hist_data : list, numpy array
            histogram data
        bin_edges: list, np array
            edges of the bins used for hisogram
    """
    total_area = 0.0
    for i, val in enumerate(hist_data):
        bin_len = abs(bin_edges[i+1] - bin_edges[i])
        area = _bin_area(val, (bin_edges[i+1], bin_edges[i]))
        total_area += area
    return total_area


def moment_hist(hist_data, bin_edges=BINS_EDGES, n=1, central=True):
    """ Uses the method of hisogram integration to calculate moments of a distribution

        Returns: float
    """
    if len(hist_data) + 1 != len(bin_edges):
        raise Exception('bin edges must be one larger than data')

    n = int(n)
    if central and n > 1:
        mean = moment_hist(hist_data, bin_edges)

    moment_val = 0
    for i, k in enumerate(hist_data):
        area_k = _bin_area(k, (bin_edges[i+1], bin_edges[i]))
        x_k = np.mean([bin_edges[i+1], bin_edges[i]])
        if n > 1:
            moment_val += (x_k - mean)**n * area_k
        else:
            moment_val += (x_k) * area_k
    if n > 2:
        std = math.sqrt(moment_hist(hist_data, bin_edges, n=2))
        return (moment_val/_total_area(hist_data, bin_edges))/std**n
    else:
        return (moment_val/_total_area(hist_data, bin_edges))


def cumulant_hist(hist_data, bin_edges, n=1, satndardized=False):
    """ Calculates cumulants using hisogram method. Assumes moments are centralized.
    """
    if n > 6 or n < 1:
        raise ValueError("cumulants only supported for 1<=n<=6")
    n = int(n)
    mu = {}
    for k in range(1, n+1):
        mu[k] = moment_hist(hist_data, bin_edges, n=k)
        if isinstance(mu[k], list):
            mu[k] = mu[k][0]
    if standardized and n > 2:
        mu[2] = 1
    if n == 1:
        mean = moment_hist(hist_data, bin_edges)
        if isinstance(mean, float):
            return mean
        else:
            return mean.values[0]
    elif n == 2:
        return mu[2]
    elif n == 3:
        return mu[3]
    elif n == 4:
        return mu[4] - 3 * mu[2]**2
    elif n == 5:
        return mu[5] - 10 * mu[3] * mu[2]
    elif n == 6:
        return mu[6] - 15 * mu[4] * mu[2] - 10 * mu[3]**2 + 30 * mu[2]**3
    else:
        raise ValueError("Should not be here.")


def cumulant(data, n=1, standardized=False):
    if n > 6 or n < 1:
        raise ValueError("cumulants only supported for 1<=n<=6")
    n = int(n)
    mu = {}
    for k in range(1, n+1):
        mu[k] = st.moment(data, moment=k)
        if k > 2:
            mu[k] = mu[k]
    if standardized and n > 2:
        mu[2] = 1
    if n == 1:
        return np.mean(data)
    elif n == 2:
        return mu[2]
    elif n == 3:
        return mu[3]
    elif n == 4:
        return mu[4] - 3 * mu[2]**2
    elif n == 5:
        return mu[5] - 10 * mu[3] * mu[2]
    elif n == 6:
        return mu[6] - 15 * mu[4] * mu[2] - 10 * mu[3]**2 + 30 * mu[2]**3
    else:
        raise ValueError("Should not be here.")
