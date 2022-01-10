# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-03-17 09:17

@author: johannes
"""
from bokeh.plotting import curdoc
from ctdvis.session import Session


"""
Ref: https://stackoverflow.com/questions/55049175/running-bokeh-server-on-local-network

In a conda-prompt run:
    cd "PATH_TO_THIS_SCRIPT"
    bokeh serve app_to_serve.py

Bokeh app running at: http://localhost:5006/app_to_serve
"""


def bokeh_qc_tool():
    """Return bokeh layout.

    Path to CTD-standard-format (including auto-QC-fields).
    """
    data_dir = r'C:\Temp\CTD_DV\test_flex_format'

    filters = None
    # filters = dict(
    #     # month_list=[1, 2, 3],
    #     month_list=[4],
    #     # month_list=[7, 8, 9],
    #     # month_list=[10, 11, 12],
    #     # ship_list=['77SE', '34AR']
    #     # serno_min=311,
    #     # serno_max=355,
    # )

    s = Session(
        # visualize_setting='slua_vis',
        visualize_setting='smhi_expedition_vis',
        # visualize_setting='smhi_vis',
        data_directory=data_dir,
        filters=filters,
    )
    s.setup_datahandler()
    layout = s.run_tool(return_layout=True)
    return layout


bokeh_layout = bokeh_qc_tool()
doc = curdoc()
doc.add_root(bokeh_layout)
