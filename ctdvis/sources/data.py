# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-09-07 13:02

@author: a002028

"""
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource


def setup_data_source(df, pmap=None, key_list=None, parameter_list=None):
    """
    :param df: pd.DataFrame
    :param pmap: dictionary, parameter mapping
    :param key_list: array
    :param parameter_list: array
    :return:
    """
    data_dict = {}
    for key in key_list:
        data_boolean = df['KEY'] == key
        for parameter in parameter_list:
            data_key = '_'.join((key, parameter))
            data_dict[data_key] = df.loc[data_boolean, parameter].values

    length = 0
    for key in data_dict:
        l = len(data_dict[key])
        if l > length:
            length = l
    for key in data_dict:
        if len(data_dict[key]) < length:
            data_dict[key] = np.pad(data_dict[key],
                                    (0, length - len(data_dict[key])),
                                    'constant',
                                    constant_values=np.nan)

    for p in pmap.keys():
        data_dict[p] = [1] * length
        if p != 'y':
            data_dict['color_' + p] = ['black'] * length

    return ColumnDataSource(data_dict)


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
