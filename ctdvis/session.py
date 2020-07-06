# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:24

@author: a002028

"""
from ctdvis.config import Settings


class Session:
    """
    """
    def __init__(self, visualize_setting=None, data_directory=None):
        self.data_directory = data_directory
        self.settings = Settings(visualize_setting=visualize_setting)
        # why here? well, we need to append local python paths from
        # Settings() first (eg. path to: ctdpy, sharkpylib)
        from ctdvis.datahandler import DataHandler
        global DataHandler

        self.dh = DataHandler()

    def setup_datahandler(self):
        """"""
        self.dh.load_profile_data(self.data_directory)
        self.dh.construct_dataframe(self.settings)


data_dir = 'C:\\Temp\\CTD_DV\\qc_SMHI_2018\\ctd_std_fmt_20200622_130128_april_2020'
s = Session(visualize_setting='smhi_vis')
# s.setup_datahandler(data_dir)

# data_transformer.append_dataframes(dataframes)
# data_transformer.add_columns()
# data_transformer.add_color_columns(auto_q_flag_parameters, mapper=q_colors_mapper)
# data_transformer.set_column_format(**parameter_formats)
#
# dataframe = data_transformer.get_dataframe(columns=df_parameter_list)