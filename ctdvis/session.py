# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:24

@author: a002028

"""
from ctdvis.config import Settings
from ctdvis.tools.quality_control import QCWorkTool


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

    def run_tool(self, tool='qc_smhi'):
        """"""
        # TODO settings in yaml-files.. dynamic obj-load..
        plot = QCWorkTool(self.dh.df[self.settings.selected_keys],
                          self.dh.raw_data,
                          parameters=self.settings.data_parameters_with_units,
                          plot_parameters_mapping=self.settings.plot_parameters_mapping,
                          color_fields=self.settings.q_colors,
                          qflag_fields=self.settings.q_parameters,
                          auto_q_flag_parameters=self.settings.q0_parameters,
                          #  output_filename="svea_2020.html",  # Save as html-file (will automatic open in chrome/firefox), only javascript callbacks can be used
                          output_as_notebook=True,
                          # Open in notebook.. Window size is not ideal for this, BUT! python callbacks works :D
                          ctdpy_session=self.dh.ctd_session,
                          multi_sensors=True,  # IMPORTANT!!! SMHI HAS MULTIPLE TEMP, SALT, DOXY SENSORS
                          combo_plots=True
                          )
        plot.plot_stations()
        plot.plot_data()

        return plot.return_layout()


# data_dir = 'C:\\Temp\\CTD_DV\\qc_SMHI_2018\\ctd_std_fmt_20200622_130128_april_2020'
# s = Session(visualize_setting='smhi_vis', data_directory=data_dir)
# s.setup_datahandler()

# layout = s.run_tool()
