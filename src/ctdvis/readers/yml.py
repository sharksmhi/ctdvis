# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-12-15 13:59

@author: johannes
"""
import yaml


def yaml_reader(file_path):
    """Return data from yaml file."""
    with open(file_path, encoding='utf8') as fd:
        data = yaml.load(fd, Loader=yaml.Loader)
    return data
