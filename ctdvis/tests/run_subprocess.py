# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-03-17 15:27
@author: johannes

https://www.kite.com/python/answers/how-to-terminate-a-subprocess-in-python

Run bokeh-server via subprocess:
    command:
        "bokeh", "serve"

    python-script to run:
        "app_to_serve.py"  (or PATH TO PY-FILE)
"""
import subprocess


if __name__ == "__main__":
    child_process = subprocess.Popen(["bokeh", "serve", "app_to_serve.py"])
    # child_process = subprocess.Popen(["bokeh", "serve", "--port", "5002", "app_to_serve.py"])

    # Terminate the subprocess (via GUI?)
    # child_process.terminate()
