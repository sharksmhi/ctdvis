# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:24

@author: a002028

"""
from abc import ABC

import pandas as pd
import numpy as np
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths

from ctdvis.filter import Filter


class Datadict(dict):
    """
    Data Dictionary
    We intend to use filenames as keys with profile dataframes as items
    """
    def __init__(self, data_directory=None):
        super().__init__()
        self.data_directory = data_directory

    def load_data(self, return_session=False, filters=None):
        """
        :return:
        """
        files = generate_filepaths(self.data_directory,
                                   endswith='.txt',
                                   only_from_dir=True)

        ctd_session = Session(filepaths=files,
                              reader='ctd_stdfmt')

        datasets = ctd_session.read()

        filter_obj = None
        if filters:
            # TODO Move filters to ctdpy ?
            filter_obj = Filter(list(datasets[0].keys()))
            filter_obj.add_filter(**filters)

        for key, item in datasets[0].items():
            if filters:
                if key in filter_obj.valid_file_names:
                    self.append_item(key, item)
            else:
                self.append_item(key, item)

        if return_session:
            return ctd_session

    def append_item(self, key, item):
        print('Appending data for key: {}'.format(key))
        self.setdefault(key, item)


class Frame(pd.DataFrame, ABC):
    """
    Subclassing pandas.DataFrame
    We intend to use Frame as a DataFrame for all selected profile dataset
    """
    @property
    def _constructor(self):
        """
        Constructor for DataFrame, overides method in pd.DataFrame
        :return: DataFrame
        """
        return Frame

    def convert_formats(self):
        self['SDATE'] = self[['YEAR', 'MONTH', 'DAY']].astype(str).apply('-'.join, axis=1)
        self['STIME'] = self[['HOUR', 'MINUTE']].astype(str).apply(':'.join, axis=1)

    def set_column_format(self, **kwargs):
        """
        :param kwargs: {'para_1': float,
                        'para_2': str}
        :return:
        """
        for key, value in kwargs.items():
            if key in self.columns:
                try:
                    self[key] = self[key].astype(value)
                except ValueError:
                    self[key] = self[key].replace('', np.nan).astype(value)

    def add_color_columns(self, qflags, mapper=None):
        """
        :param qflags:
        :param mapper:
        :return:
        """
        color = 'navy'
        for qf in qflags:
            color_key = mapper.get(qf)
            self[color_key] = self[qf].fillna('').apply(lambda x: color if x != 'B' else 'red')


class DataHandler(object):
    """
    Stores rawdata (ctd-standard-format)
    Appends selected filtered datasets (self.raw_data) to Frame (self.df)
    Conform self.df in order to use it in bokeh tools..
    """
    def __init__(self, filters):
        self.filters = filters
        self.raw_data = Datadict()
        self.df = Frame(index=[])
        self.ctd_session = None

    def load_profile_data(self, directory):
        """"""
        self.raw_data.data_directory = directory
        self.ctd_session = self.raw_data.load_data(return_session=True, filters=self.filters)

    def construct_dataframe(self, settings):
        """"""
        for key, item in self.raw_data.items():
            df = item['data'].copy()
            df['KEY'] = key.strip('ctd_profile|.txt')

            self.df = self.df.append(Frame(df))

        self.df.reset_index(drop=True, inplace=True)

        self.df.convert_formats()
        self.df.add_color_columns(settings.q_parameters,
                                  mapper=settings.q_colors_mapper)
        self.df.set_column_format(**settings.parameter_formats)
