# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:33

@author: a002028
"""
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
from ctdvis import callbacks  # noqa: F401
from ctdvis import readers  # noqa: F401
from ctdvis import sources  # noqa: F401
from ctdvis import widgets  # noqa: F401

name = "ctdvis"
