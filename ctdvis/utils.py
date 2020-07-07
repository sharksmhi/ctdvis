# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:25

@author: a002028

"""
from collections import Mapping
from datetime import datetime
import pyproj


def convert_projection(lats, lons):
    """

    :param lats:
    :param lons:
    :return:
    """
    # project_projection = pyproj.Proj("EPSG:4326")  # wgs84
    # google_projection = pyproj.Proj("EPSG:3857")  # default google projection
    project_projection = pyproj.Proj({'init': 'epsg:4326', 'no_defs': True}, preserve_flags=True)  # wgs84
    google_projection = pyproj.Proj({'init': 'epsg:3857', 'no_defs': True}, preserve_flags=True)  # default google projection

    x, y = pyproj.transform(project_projection, google_projection, lons, lats)
    return x, y


def get_time_as_format(**kwargs):
    if kwargs.get('now'):
        d = datetime.now()
    elif kwargs.get('timestamp'):
        raise NotImplementedError

    if kwargs.get('fmt'):
        return d.strftime(kwargs.get('fmt'))
    else:
        raise NotImplementedError


def recursive_dict_update(d, u):
    """ Recursive dictionary update using
    Copied from:
        http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        via satpy
    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d.setdefault(k, r)
        else:
            d.setdefault(k, u[k])
    return d
