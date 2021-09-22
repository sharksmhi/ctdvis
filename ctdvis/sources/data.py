# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-09-07 13:02

@author: a002028
"""
import numpy as np
from bokeh.models import ColumnDataSource


def setup_data_source(df, pmap=None, key_list=None, parameter_list=None):
    """
    :param df: pd.DataFrame
    :param pmap: dictionary, parameter mapping
    :param key_list: array
    :param parameter_list: plot_keys and color_keys
    :return:
    """
    main_source = {}
    for p in parameter_list:
        if p.startswith('COMNT'):
            main_source[p] = ['']
        elif p.startswith('color'):
            main_source[p] = ['navy']
        else:
            main_source[p] = [1]

    data_dict = {'main_source': ColumnDataSource(main_source)}

    for key in key_list:
        data_boolean = df['KEY'] == key
        key_df = df.loc[data_boolean, :]
        key_dict = {}
        for p in parameter_list:
            if p.startswith('COMNT'):
                df_column = p
            else:
                df_column = pmap.get(p) if not p.startswith('color') else p

            if df_column and df_column in key_df:
                key_dict[p] = key_df[df_column].values
            else:
                v = 'navy' if p.startswith('color') else np.nan
                key_dict[p] = [v] * key_df.__len__()

        data_dict[key] = ColumnDataSource(key_dict, name=key)

    return data_dict
