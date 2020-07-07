# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-07 17:05

@author: a002028

"""
import pandas as pd


class Name:
    """

    """
    splitter = '_'

    def __init__(self, file_name):
        args = file_name.strip('.txt').split(self.splitter)
        self.date = pd.Timestamp(args[2])
        self.shipc = args[3]
        self.serno = float(args[4])


class Filter:
    """
    ctd_profile_20181208_34AR_0171.txt
    """
    date = None
    shipc = None
    serno = None
    name_structure = 'ctd_profile_{}_{}_{}.txt'.format(date, shipc, serno)

    def add_filter(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

    def set_list(self, name_list):
        """

        :param name_list:
        :return:
        """
        self.serie = pd.Series(name_list)
