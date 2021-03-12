# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute
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
    :param parameter_list: array
    :return:
    """
    main_source = {}
    for p in pmap.keys():
        main_source[p] = [1]
        if p != 'y':
            main_source['color_' + p] = ['black']

    data_dict = {'main_source': ColumnDataSource(main_source)}

    for key in key_list:
        data_boolean = df['KEY'] == key
        data_dict[key] = ColumnDataSource(df.loc[data_boolean, parameter_list])

    return data_dict


if __name__ == "__main__":
    import pandas as pd
    mapping = {'x1': 'TEMP', 'x2': 'SALT', 'y': 'PRES'}
    # d = CTDDataSource()
    # d.setup_source(pd.DataFrame({'TEMP': [1, 2, 3],
    #                              'SALT': [1, 2, 3],
    #                              'PRES': [1, 2, 3],
    #                              'KEY': ['a', 'b', 'c']}),
    #                mapping)
    # print(d.data)
