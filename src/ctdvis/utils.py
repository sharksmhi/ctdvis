# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:25

@author: a002028
"""
from collections.abc import Mapping
from datetime import datetime
from pyproj import CRS, transform
import numpy as np
import pandas as pd
import gsw
from matplotlib import colors
from matplotlib import cm


def get_color_palette(dep_serie=None):
    """Return palette."""
    number_of_colors = int(dep_serie.max() * 2 + 1)
    cm_map = cm.get_cmap('cool', number_of_colors)
    color_array = pd.Series(
        [colors.to_hex(cm_map(c)) for c in range(number_of_colors)]
    )
    return [color_array[int(d * 2)] if d > 0 else 0 for d in dep_serie]


def convert_projection(lats, lons):
    """Return position in google projection."""
    project_projection = CRS('EPSG:4326')
    google_projection = CRS('EPSG:3857')
    x, y = transform(
        project_projection,
        google_projection,
        lons,
        lats,
        always_xy=True
    )
    return x, y


def get_contour_arrays(x_min, x_max, y_min, y_max):
    """Calculate how many gridcells we need in the x and y dimensions.

    Assuming x_key = Salinity and y_key = Temperature
    """
    xdim = int(round((x_max - x_min) / 0.1 + 1, 0))
    ydim = int(round((y_max - y_min) / 0.1 + 1, 0))
    t_m = np.zeros((ydim, xdim))
    s_m = np.zeros((ydim, xdim))
    dens = np.zeros((ydim, xdim))
    ti = np.linspace(1, ydim - 1, ydim) * 0.1 + y_min
    si = np.linspace(1, xdim - 1, xdim) * 0.1 + x_min
    for j in range(0, int(ydim)):
        for i in range(0, int(xdim)):
            dens[j, i] = gsw.rho(si[i], ti[j], 0)
            s_m[j, i] = si[i]
            t_m[j, i] = ti[j]
    dens = dens
    return dens, t_m, s_m


def get_contour_data(x_min, x_max, y_min, y_max):
    """Return dictionary of contour data.

    Used for TS diagram.
    Salinity as sigma-T.

    Example:
        x_min, x_max, y_min, y_max = 0, 40, -10, 30
        data = get_contour_df(x_min, x_max, y_min, y_max)
    """
    dens, t_m, s_m = get_contour_arrays(x_min, x_max, y_min, y_max)
    dens = np.round(dens, 2)
    data = {}
    selected_densities = np.arange(-6, 31, 2) + 1000
    for s_dens in selected_densities:
        index = dens == s_dens
        data[str(s_dens)] = {'temp': t_m[index],
                             'salt': s_m[index],
                             'dens': dens[index]}
    return data


def get_time_as_format(now=None, timestamp=None, fmt=None):
    """Return time as string format."""
    if now:
        d = datetime.now()
    elif timestamp:
        raise NotImplementedError

    if fmt:
        return d.strftime(fmt)
    else:
        raise KeyError


def recursive_dict_update(d, u):
    """Recursive dictionary update."""
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d.setdefault(k, r)
        else:
            d.setdefault(k, u[k])
    return d
