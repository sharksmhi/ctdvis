#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-04-05 09:26

@author: johannes
"""
from ctdvis.session import Session


if __name__ == "__main__":
    data_dir = r'C:\Temp\CTD_DV\test_standalone'

    s = Session(
        visualize_setting='deep_vis',
        data_directory=data_dir,
    )
    s.setup_datahandler()
    s.run_tool(output_as_standalone=True)
