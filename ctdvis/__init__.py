# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:33

@author: a002028

"""
import sys
import os

from ctdvis import callbacks
from ctdvis import readers
from ctdvis import sources
from ctdvis import widgets

package_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(package_path)

name = "ctdvis"
