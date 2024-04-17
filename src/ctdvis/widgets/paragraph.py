# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-09-11 15:33

@author: a002028
"""
from bokeh.models import Div


def header_line():
    """Return Div object."""
    html_text = """
    <html>
    <body>
    <hr>
    </body>
    </html>
    """
    return Div(text=html_text)


def standard_block_header(text=None, width=300, height=40):
    """Return Div object."""
    html_text = """
    <style>
        body {
            text-align: left;
            vertical-align: text-top;
        }
        .centered {
            text-align: text-top;
            vertical-align: text-top;
        }
    </style>
    <div class="centered">
        <h4>""" + text + """</h4>
    </div>
    """
    return Div(text=html_text, width=width, height=height)


def get_info_block():
    """Return Div object."""
    text = """
    <h4>Info links</h4>
    <ul>
      <li><a href="https://docs.bokeh.org/en/latest/docs/user_guide/tools.html" target="_blank">Bokeh toolbar info</a></li>
      <li><a href="https://github.com/sharksmhi/sharkpylib/tree/master/sharkpylib/qc" target="_blank">SHARK-QC-library</a></li>
    </ul>

    <h4>QC routines</h4>
    <ol>
      <li>Range check</li>
      <li>Increase check</li>
      <li>Decrease check</li>
      <li>Sensor diff check</li>
      <li>Spike check</li>
    </ol>
    """  # noqa: E501
    return Div(text=text, width=200, height=100)


def get_export_info_block(export_folder):
    """Return Div object."""
    if export_folder:
        text = f"""
        <h4>Download steps:</h4>
        <ol>
          <li>Select series using "map-lasso" or "Shift-table-select"</li>
          <li>Click on Download below</li>
        </ol>
        Datafiles will be downloaded to your data folder ({export_folder})
        """  # noqa: E501
    else:
        text = """
        <h4>Download steps:</h4>
        <ol>
          <li>Select series using "map-lasso" or "Shift-table-select"</li>
          <li>Click on Download below</li>
        </ol>
        Select a folder for download after clicking on the green button below. If no valid folder is selected, datafiles will be downloaded to your computers download-folder (eg. "Hämtade filer")
        """  # noqa: E501
    return Div(text=text)
