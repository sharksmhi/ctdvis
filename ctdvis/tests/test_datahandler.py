# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-11-02 11:15

@author: a002028

"""
from ctdvis.session import Session


if __name__ == "__main__":
    data_dir = 'C:\\Temp\\CTD_DV\\ctd_std_fmt_20200526_095058'

    filters = dict(
        month_list=[5],
        serno_max=385,
    )

    s = Session(
        visualize_setting='smhi_vis',
        data_directory=data_dir,
        filters=filters,
    )

    s.setup_datahandler()
