# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-07 17:05

@author: a002028
"""
import pandas as pd


class Name:
    """Name properties object."""

    splitter = '_'

    def __init__(self, file_name, name_elements):
        """Initiate."""
        args = file_name.replace('.txt', '').split(self.splitter)
        key_mapper = {k: v for k, v in zip(name_elements, args)}
        self.date = pd.Timestamp(key_mapper.get('SDATE'))
        self.shipc = key_mapper.get('SHIPC')
        self.serno = float(key_mapper.get('SERNO'))


class SplitNameList:
    """Name object handler."""

    dates = []
    ships = []
    sernos = []

    def __init__(self, name_list, name_elements):
        """Initiate."""
        self.names = name_list
        for name in name_list:
            name_obj = Name(name, name_elements)
            self.append_date(name_obj.date)
            self.append_shipc(name_obj.shipc)
            self.append_serno(name_obj.serno)

    @classmethod
    def append_date(cls, d):
        """Append date."""
        cls.dates.append(d)

    @classmethod
    def append_shipc(cls, s):
        """Append ship code."""
        cls.ships.append(s)

    @classmethod
    def append_serno(cls, s):
        """Append serie number."""
        cls.sernos.append(s)


class Filter:
    """Filter filenames according to ctd-standard format.

    Filename example: 'ctd_profile_20181208_34AR_0171.txt'.
    """

    def __init__(self, name_list, file_name_elements):
        """Initiate."""
        lists = SplitNameList(name_list, file_name_elements)
        self.serie_names = pd.Series(lists.names)
        self.serie_dates = pd.Series(lists.dates)
        self.serie_ships = pd.Series(lists.ships)
        self.serie_sernos = pd.Series(lists.sernos)

        self._boolean = True

    def add_filter(self, **kwargs):
        """Set boolean filter.

        If any valid filter arguments we append boolean according to:
        @boolean.setter (property.setter).
        """
        if 'month_list' in kwargs:
            print('month', self.serie_dates.dt.month)
            self.boolean = self.serie_dates.dt.month.isin(kwargs.get('month_list'))

        if 'ship_list' in kwargs:
            self.boolean = self.serie_ships.isin(kwargs.get('ship_list'))

        if 'serno_max' in kwargs:
            self.boolean = self.serie_sernos <= kwargs.get('serno_max')

        if 'serno_min' in kwargs:
            self.boolean = self.serie_sernos >= kwargs.get('serno_min')

    @property
    def valid_file_names(self):
        """Return valid filenames."""
        return self.serie_names[self.boolean].values

    @property
    def boolean(self):
        """Return boolean."""
        return self._boolean

    @boolean.setter
    def boolean(self, add_bool):
        """Set boolean."""
        self._boolean = self._boolean & add_bool
