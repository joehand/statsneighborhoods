# -*- coding: utf-8 -*-
"""
    price calculations
    ~~~~~~~~~
    WARNING: This is specific to US income data.

    If this needs to be changed,
    you will need to update the BINS values and some of the regex expressions.

    :copyright: (c) 2015 by Joe Hand, Santa Fe Institute.
    :license: MIT
"""
import numpy as np
from pandas import concat, DataFrame, Series
from scipy import stats


LOW_BINS = [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000,
            50000, 60000, 75000, 100000, 125000, 150000, 200000]

MID_BINS = [5000, 12500, 17500, 22500, 27500, 32500, 37500, 42500, 47500,
            55000, 67500, 87500, 112500, 137500, 175000, 225000]


def adjust_rich_bin(df, col_suffix, inc_bin=200000):
    col = 'ACSHINC200'
    df['new_mid_pt' + col_suffix] = (df['ACSAVGHINC'] * df['Total_Households'] -
                                     df['mean_inc' + col_suffix] * df['Total_Households'] + df[col] * inc_bin)/df[col]
    df['new_mid_pt' + col_suffix] = df['new_mid_pt' +
                                       col_suffix].replace([np.inf, -np.inf], inc_bin)
    df[col + col_suffix] = df[col] * df['new_mid_pt' + col_suffix]
    df['adjusted' + col_suffix] = df.filter(
        regex='^ACSHINC([0-9])+' + col_suffix).sum(axis=1)//df['Total_Households']
    df['adjusted' + col_suffix] = df['adjusted' + col_suffix].astype(int)
    return df


def calculate_mean_income(df, inc_bins, col_suffix):
    df = df.copy()
    cols = df.filter(regex='^ACSHINC([0-9])+$').columns
    for i, col in enumerate(cols):
        df[col + col_suffix] = df[col] * inc_bins[i]
    df['total_inc' +
        col_suffix] = df.filter(regex='^ACSHINC([0-9])+' + col_suffix).sum(axis=1)
    df['mean_inc' + col_suffix] = df['total_inc' +
                                     col_suffix]//df['Total_Households']

    df = adjust_rich_bin(df, col_suffix, inc_bin=inc_bins[i])
    return df


def calculate_a(df, reported_mean='ACSAVGHINC', calc_mean_low='mean_inc_low',
                calc_mean_mid='mean_inc_mid'):
    df = df.copy()
    df['a'] = (df[reported_mean] - df[calc_mean_low]) / \
        (df[calc_mean_mid] - df[calc_mean_low])
    return df


def calculate_price(df):
    df = calculate_mean_income(df, LOW_BINS, '_low')
    df = calculate_mean_income(df, MID_BINS, '_mid')
    df = calculate_a(df, calc_mean_low='adjusted_low')
    return df
