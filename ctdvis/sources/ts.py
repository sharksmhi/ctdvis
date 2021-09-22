# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-09-07 11:38

@author: a002028
"""
from bokeh.models import ColumnDataSource
from ctdvis.utils import get_color_palette


class Source(ColumnDataSource):
    """
    """
    def setup_source(self, df, pmap):
        """
        :param df: pd.DataFrame
        :param pmap: dictionary, parameter mapping
        :return:
        """
        parameters = [pmap.get(p) for p in ('y', 'x1', 'x2')]
        parameters.append('KEY')
        ts_df = df.loc[:, parameters].copy()
        ts_df.loc[:, 'x'] = ts_df.loc[:, pmap.get('x2')]  # x2 = SALT
        ts_df.loc[:, 'y'] = ts_df.loc[:, pmap.get('x1')]  # x1 = TEMP
        ts_df.loc[:, 'color'] = get_color_palette(dep_serie=ts_df.loc[:, pmap.get('y')])

        self.data.update(ts_df)
