# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-06 15:29

@author: a002028

"""
from bokeh.io import output_notebook
from bokeh.models import TextInput, ColumnDataSource, Div, Circle, TapTool, HoverTool, WheelZoomTool, ResetTool, PanTool, SaveTool,  LassoSelectTool, ColorBar, LinearColorMapper
from bokeh.layouts import grid, row, column, Spacer
from bokeh.models.widgets import Select, RangeSlider, DataTable, TableColumn, Panel, Tabs
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors

from bokeh.core.validation import silence
from bokeh.core.validation.warnings import FIXED_SIZING_MODE
silence(FIXED_SIZING_MODE, True)

import numpy as np
import pandas as pd
from matplotlib import colors
from matplotlib import cm

import time

from ctdvis.utils import get_time_as_format, convert_projection, get_contour_data
from ctdvis.callbacks import cbs
from ctdvis.sources.ts import Source as TS_Source
from ctdvis.sources.data import setup_data_source
from ctdvis.widgets.paragraph import standard_block_header, header_line


class QCWorkTool:
    """
    # TODO
    Well, this is great, however.. we need to simplify and divide this class into widgets instead..
    to be continued..
    """
    def __init__(self, dataframe, datasets=None, parameters=None, color_fields=None, qflag_fields=None,
                 auto_q_flag_parameters=None,
                 tabs=None, plot_parameters_mapping=None, ctdpy_session=None, multi_sensors=False, combo_plots=False,
                 output_filename="CTD_QC_VIZ.html", output_as_notebook=False):

        self.seconds = ColumnDataSource(data=dict(tap_time=[None], reset_time=[None]))

        self.ctd_session = ctdpy_session
        self.multi_sensors = multi_sensors
        self.combo_plots = combo_plots

        self.map = None
        # self.selected_series = None
        # self.df = dataframe
        self.datasets = datasets
        self.key_ds_mapper = self.get_mapper_key_to_ds()
        self.parameters = parameters
        self.plot_parameters_mapping = plot_parameters_mapping
        self.color_fields = color_fields
        self.qflag_fields = qflag_fields
        self.auto_qflag_fields = auto_q_flag_parameters
        self.tabs = tabs
        self.output_as_notebook = output_as_notebook
        if self.output_as_notebook:
            output_notebook()
        else:
            output_file(output_filename)

        self.tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)

        self.figures = {}
        xrange_callbacks = {}
        y_range_setting = None
        for p in self.plot_parameters_mapping:
            if p == 'y' or 'q' in p or p[0].isupper():
                continue
            param = self.plot_parameters_mapping.get(p)
            self.figures[p] = figure(tools="pan,reset,wheel_zoom,lasso_select,save", active_drag="lasso_select",
                                     title="", height=400, width=400,
                                     y_range=y_range_setting,
                                     tooltips=[(param, "@{}".format(p)),
                                               ("Pressure [dbar]", "@y"),
                                               ("Auto-QC", "@{}_q0".format(p))])
            self.figures[p].title.align = 'center'
            self.figures[p].xaxis.axis_label = param
            self.figures[p].xaxis.axis_label_text_font_style = 'bold'
            self.figures[p].ygrid.band_fill_alpha = 0.05
            self.figures[p].ygrid.band_fill_color = "black"
            self.figures[p].toolbar.active_scroll = self.figures[p].select_one(WheelZoomTool)

            if not y_range_setting or (self.multi_sensors and p == 'x4'):
                self.figures[p].yaxis.axis_label = 'Pressure (dbar)'
                self.figures[p].yaxis.axis_label_text_font_style = 'bold'

            y_range_setting = y_range_setting or self.figures[p].y_range

            xrange_callbacks[p] = cbs.x_range_callback(x_range_obj=self.figures[p].x_range, seconds=self.seconds)
            self.figures[p].x_range.js_on_change('start', xrange_callbacks[p])

        if self.combo_plots and self.multi_sensors:
            for name, p1, p2 in zip(('COMBO_TEMP', 'COMBO_SALT', 'COMBO_DOXY'),
                                    ('x1', 'x2', 'x3'),
                                    ('x4', 'x5', 'x6')):
                param = self.plot_parameters_mapping.get(p1)
                self.figures[name] = figure(tools="pan,reset,wheel_zoom,lasso_select,save", active_drag="lasso_select",
                                            title="", height=400, width=400,
                                            y_range=y_range_setting,
                                            )
                self.figures[name].title.align = 'center'
                self.figures[name].xaxis.axis_label = param
                self.figures[name].xaxis.axis_label_text_font_style = 'bold'
                self.figures[name].ygrid.band_fill_alpha = 0.05
                self.figures[name].ygrid.band_fill_color = "black"
                self.figures[name].toolbar.active_scroll = self.figures[name].select_one(WheelZoomTool)

                if p1 == 'x1':
                    self.figures[name].yaxis.axis_label = 'Pressure (dbar)'
                    self.figures[name].yaxis.axis_label_text_font_style = 'bold'

        cbs.add_hlinked_crosshairs(*(fig_obj for i, fig_obj in self.figures.items()))

        self.ts = figure(title="CTD TS Diagram", tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool()],
                         tooltips=[("Serie", "@key")], height=400, width=400,
                         x_range=(2, 36), y_range=(-2, 20))
        self.ts.title.align = 'center'

        self._setup_position_source(dataframe)
        self.data_source = setup_data_source(dataframe,
                                             pmap=self.plot_parameters_mapping,
                                             key_list=np.unique(self.position_source.data['KEY']),
                                             parameter_list=self.parameters + self.color_fields + self.qflag_fields + self.auto_qflag_fields)

        self.ts_source = TS_Source()
        self.ts_source.setup_source(dataframe, self.plot_parameters_mapping)
        self.ts_plot_source = ColumnDataSource(data=dict(x=[], y=[], color=[], key=[]))

        self._setup_month_selector()
        self._setup_comnt_inputs()
        self._setup_selection_widgets()
        self._setup_multiflag_widget()
        self._setup_flag_widgets()
        self._setup_reset_callback(**xrange_callbacks)
        self._setup_datasource_callbacks()
        self._setup_download_button()
        self._setup_get_file_button()
        self._setup_serie_table()
        self._setup_info_block()
        self._setup_map()

        self.ts_axis_ranges = {'t_min': 0, 't_max': 25, 's_min': 2, 's_max': 36}

    def get_mapper_key_to_ds(self):
        # TODO would we like to create this mapper in any other way?
        # Let´s say that the dataset name doesnt starts with "ctd_profile_"
        # mapper = {}
        # for key, item in self.datasets.items():
        #
        return {ds_name.strip('ctd_profile_|.txt'): ds_name for ds_name in self.datasets}

    @staticmethod
    def _get_monthly_keys(position_df):
        """"""
        # FIXME Is this really necessary ?
        dictionary = {'All': position_df['KEY'].to_list()}
        for month in [str(m).zfill(2) for m in range(1, 13)]:
            boolean = position_df['MONTH'] == month
            dictionary[month] = position_df.loc[boolean, 'KEY'].to_list()
        return dictionary

    def _setup_position_source(self, df):
        """
        :return:
        """
        position_df = df[['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'KEY', 'MONTH']].drop_duplicates(
            keep='first').reset_index(drop=True)

        for i, row in position_df.iterrows():
            try:
                float(row['LATITUDE_DD'])
            except:
                print('not valid', row['KEY'])

        xs, ys = convert_projection(position_df['LATITUDE_DD'].astype(float).values,
                                    position_df['LONGITUDE_DD'].astype(float).values)
        position_df['LONGI'] = xs
        position_df['LATIT'] = ys

        comnts = []
        for key in position_df['KEY']:
            ds_meta = self.datasets[self.key_ds_mapper.get(key)]['metadata']
            cv_boolean = ds_meta.str.startswith('//METADATA;COMNT_VISIT;')
            value = ds_meta[cv_boolean].values[0].replace('//METADATA;COMNT_VISIT;', '')
            comnts.append(value)
        position_df['COMNT_VISIT'] = comnts

        self.monthly_keys = self._get_monthly_keys(position_df)
        self.position_source = ColumnDataSource(data=position_df)
        self.position_plot_source = ColumnDataSource(data=position_df)

    def _setup_month_selector(self):
        """"""
        callback = cbs.month_selection_callback(position_source=self.position_source,
                                                position_plot_source=self.position_plot_source)
        self.month_selector = Select(title="Select month",
                                     value='All',
                                     options=['All'] + pd.date_range(start='2020-01', freq='M',
                                                                     periods=12).month_name().to_list(),
                                     # callback=callback,
                                     # width=120,
                                     )
        self.month_selector.js_on_change('value', callback)
        # self.month_selector.title.text_align = 'center'
        callback.args["month"] = self.month_selector

    def _setup_download_button(self):
        """"""
        self.download_button = cbs.get_download_widget(self.datasets,
                                                       self.position_plot_source,
                                                       self.ctd_session)

    def _setup_get_file_button(self):
        """"""
        self.file_button = cbs.get_file_widget()

    def _setup_serie_table(self):
        """
        Create a data table associated to the plot object
        :param source: bokeh.models.ColumnDataSource
        :return: bokeh.models.widgets.DataTable
        """
        columns = [TableColumn(field="STATION", title="Station"),
                   TableColumn(field="KEY", title="Key"),
                   ]
        self.selected_series = DataTable(source=self.position_plot_source, columns=columns,
                                         width=300, height=322)

    def _setup_flag_widgets(self):
        """
        Options:
        self.get_flag_widget(*args, **kwargs)
        self.get_flag_buttons_widget(*args, **kwargs)
        """
        self.flag_widgets = {}
        for fig_key in self.figures.keys():
            if fig_key.startswith('COMBO'):
                continue
            parameter = self.plot_parameters_mapping.get(fig_key).split()[0]
            # q_key = 'Q_' + parameter
            self.flag_widgets[fig_key] = cbs.get_flag_buttons_widget(self.position_plot_source,
                                                                     self.data_source['main_source'],
                                                                     self.datasets,
                                                                     figure_objs=self.figures,
                                                                     flag_keys=self.plot_parameters_mapping[parameter].get('q_flags'),
                                                                     color_keys=self.plot_parameters_mapping[parameter].get('color_keys'),
                                                                     select_button=self.select_all_button)

    def _setup_data_source(self, df):
        """
        :return:
        """
        print('Setting up data source structure...')
        # self.df[self.parameters] = self.df[self.parameters].astype(float)
        data_dict = {}
        for key in self.position_source.data['KEY']:
            data_boolean = df['KEY'] == key
            for parameter in self.parameters + self.color_fields + self.qflag_fields + self.auto_qflag_fields:
                data_key = '_'.join((key, parameter))
                data_dict[data_key] = df.loc[data_boolean, parameter].values

        length = 0
        for key in data_dict:
            l = len(data_dict[key])
            if l > length:
                length = l
        for key in data_dict:
            if len(data_dict[key]) < length:
                data_dict[key] = np.pad(data_dict[key],
                                        (0, length - len(data_dict[key])),
                                        'constant',
                                        constant_values=np.nan)

        for p in self.plot_parameters_mapping.keys():
            data_dict[p] = [1] * length
            if p != 'y':
                data_dict['color_' + p] = ['black'] * length

        self.data_source = ColumnDataSource(data=data_dict)

        print('\nData source structure completed!\n')

    def _setup_comnt_inputs(self):
        """
        :return:
        """
        self.comnt_samp = TextInput(value="", title="COMNT_SAMP:")
        self.comnt_visit = TextInput(value="", title="COMNT_VISIT:")
        self.comnt_visit_button = cbs.comnt_visit_change_button(datasets=self.datasets,
                                                                position_source=self.position_plot_source,
                                                                comnt_obj=self.comnt_visit)

    def _setup_info_block(self):
        """
        :return:
        """
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
        """
        self.info_block = Div(text=text, width=200, height=100)

        self.text_index_selection = standard_block_header(text='Profile index selection', height=30)
        self.text_multi_serie_flagging = standard_block_header(text='Multi serie parameter flagging', height=30)
        # self.text_header_line = header_line(width=300, height=20)

    def _setup_selection_widgets(self):
        """
        :return:
        """
        self.select_all_button = cbs.select_button(data_source=self.data_source)
        self.deselect_all_button = cbs.deselect_button(data_source=self.data_source)

        self.pressure_slider = RangeSlider(start=0, end=100, value=(0, 100),
                                           step=0.5, title="Select with pressure range", width=300)
        callback = cbs.range_selection_callback(data_source=self.data_source)
        self.pressure_slider.js_on_change('value', callback)

    def _setup_multiflag_widget(self):
        """
        :return:
        """
        def sorted_params(plist):
            l = []
            i = 0
            while i < len(plist):
                if '2' in plist[i]:
                    l.extend([plist[i+1], plist[i]])
                    i += 2
                else:
                    l.append(plist[i])
                    i += 1
            return l

        parameter_list = []
        for p, item in self.figures.items():
            if not p.startswith('COMBO'):
                parameter_list.append(self.plot_parameters_mapping.get(p).split()[0])
                # self.plot_parameters_mapping.get(p).split()[0].replace('_CTD', '')
        parameter_list = sorted_params(sorted(parameter_list))

        self.parameter_selector = Select(title="Select parameter",
                                         value=parameter_list[0],
                                         options=parameter_list
                                         )

        self.multi_flag_widget = cbs.get_multi_serie_flag_widget(self.position_plot_source,
                                                                 self.data_source,
                                                                 self.datasets,
                                                                 parameter_selector=self.parameter_selector,
                                                                 parameter_mapping=self.plot_parameters_mapping,
                                                                 figure_objs=None)

    def _setup_reset_callback(self, **kwargs):
        """"""
        # Autoreset all figures on xrange
        for p, item in self.figures.items():
            xr_cbs = (xr_cb for i, xr_cb in kwargs.items())
            self.figures[p].js_on_event('reset', cbs.reset_callback(self.seconds),
                                        *xr_cbs)

    def _setup_datasource_callbacks(self):
        """"""
        set_button_type_callback = cbs.change_button_type_callback(button=self.select_all_button,
                                                                   btype='default')
        self.data_source['main_source'].selected.js_on_change('indices', set_button_type_callback)

    def _setup_map(self):
        """"""
        pan = PanTool()
        save = SaveTool()
        tap = TapTool()
        lasso = LassoSelectTool()
        reset = ResetTool()
        wheel = WheelZoomTool()

        tooltips = HoverTool(tooltips=[("Station", "@STATION"),
                                       ("Serie", "@KEY")])

        # range bounds supplied in web mercator coordinates
        self.map = figure(x_range=(0, 4000000), y_range=(7100000, 9850000),
                          x_axis_type="mercator", y_axis_type="mercator", plot_height=420, plot_width=1000,
                          # width=1210,
                          tools=[pan, wheel, tap, lasso, tooltips, reset, save])

        self.map.yaxis.axis_label = ' '  # in order to aline y-axis with figure window below
        self.map.toolbar.active_scroll = self.map.select_one(WheelZoomTool)
        self.map.add_tile(self.tile_provider)

        station_data_callback = cbs.station_callback_2(position_source=self.position_plot_source,
                                                       data_source=self.data_source,
                                                       figures=self.figures,
                                                       seconds=self.seconds,
                                                       pmap=self.plot_parameters_mapping,
                                                       single_select=0)
        tap.callback = station_data_callback

        # When we mark stations on the map using lasso selection, we activate the TS-diagram.
        lasso_callback = cbs.lasso_callback(monthly_keys=self.monthly_keys,
                                            in_data=self.ts_source,
                                            plot_data=self.ts_plot_source,
                                            x_range=self.ts.x_range,
                                            y_range=self.ts.y_range)

        station_data_callback_2 = cbs.station_callback_2(position_source=self.position_plot_source,
                                                         data_source=self.data_source,
                                                         figures=self.figures,
                                                         seconds=self.seconds,
                                                         pmap=self.plot_parameters_mapping,
                                                         single_select=1)

        comnt_callback = cbs.comnt_callback(position_source=self.position_plot_source,
                                            comnt_obj=self.comnt_visit,
                                            single_select=1)

        update_slider_callback = cbs.range_slider_update_callback(slider=self.pressure_slider,
                                                                  data_source=self.data_source)

        select_button_type_callback = cbs.change_button_type_callback(button=self.select_all_button, btype='default')

        lasso_callback.args["month"] = self.month_selector
        self.position_plot_source.selected.js_on_change('indices',
                                                        lasso_callback,
                                                        station_data_callback_2,
                                                        comnt_callback,
                                                        update_slider_callback,
                                                        select_button_type_callback)

    def plot_stations(self):
        """"""
        renderer = self.map.circle('LONGI', 'LATIT', source=self.position_plot_source,
                                   color="#5BC798", line_color="aquamarine", size=10, alpha=0.7)
        selected_circle = Circle(fill_alpha=0.5, fill_color="#FF0202", line_color="aquamarine")
        nonselected_circle = Circle(fill_alpha=0.3, fill_color="#5BC798", line_color="aquamarine")
        # selected_circle = Circle(fill_alpha=0.5, fill_color="#E39A1B", line_color="#E39A1B")
        # nonselected_circle = Circle(fill_alpha=0.5, fill_color="#E39A1B", line_color="black")

        renderer.selection_glyph = selected_circle
        renderer.nonselection_glyph = nonselected_circle

    def plot_data(self):
        """
        self.temp.circle('x1b', 'y', color="deepskyblue", size=8, alpha=0.5, source=self.data_source, legend='Sensor 2')
        self.temp.legend.location = "top_left"
        :return:
        """
        combo_mapping = {'COMBO_TEMP': ('x1', 'x4'), 'COMBO_SALT': ('x2', 'x5'), 'COMBO_DOXY': ('x3', 'x6')}
        legend_mapper = {'x1': 'TEMP 1', 'x2': 'SALT 1', 'x3': 'DOXY 1',
                         'x4': 'TEMP 2', 'x5': 'SALT 2', 'x6': 'DOXY 2'}

        nonselected_circle = Circle(fill_alpha=0.1, fill_color="#898989", line_color="lightgrey")

        for p, item in self.figures.items():
            if p.startswith('COMBO'):
                p1, p2 = combo_mapping.get(p)
                item.line(p1, 'y', color="color_{}".format(p1), line_color="navy", line_width=1, alpha=0.3,
                          source=self.data_source)
                item.circle(p1, 'y', color="color_{}".format(p1), line_color="white", size=6, alpha=0.5,
                            source=self.data_source)

                item.line(p2, 'y', color="color_{}".format(p2), line_color="navy", line_width=1, alpha=0.3,
                          source=self.data_source)
                item.cross(p2, 'y', color="color_{}".format(p2), size=6, alpha=0.5, source=self.data_source)

                item.y_range.flipped = True
                # item.legend.location = "top_right"
            else:
                item.line(p, 'y', color="color_{}".format(p), line_color="navy", line_width=1, alpha=0.3,
                          source=self.data_source)  # , legend_label=p)
                renderer = item.circle(p, 'y', color="color_{}".format(p), line_color="white", size=6, alpha=0.5,
                                       source=self.data_source)  # , legend_label=p)
                renderer.nonselection_glyph = nonselected_circle
                item.y_range.flipped = True

        # T/S - diagram
        self.ts.circle('x', 'y', color='color', size=3, alpha=0.8, source=self.ts_plot_source, legend_label='Sensor 1')
        self.ts.toolbar.active_scroll = self.ts.select_one(WheelZoomTool)
        self.ts.legend.location = "top_left"

        number_of_colors = int(self.ts_source.data[self.plot_parameters_mapping.get('y')].max()) * 2 + 1
        cm_map = cm.get_cmap('cool', number_of_colors)
        color_array = [colors.to_hex(cm_map(c)) for c in range(number_of_colors)]

        color_bar = ColorBar(color_mapper=LinearColorMapper(palette=color_array, low=0, high=self.ts_source.data[
            self.plot_parameters_mapping.get('y')].max()),
                             # border_line_color='black',
                             location=(0, 0),
                             )

        self.ts.add_layout(color_bar, 'right')

        x_min, x_max, y_min, y_max = 0, 40, -10, 30
        contour_data = get_contour_data(x_min, x_max, y_min, y_max)
        for key in contour_data.keys():
            self.ts.line(contour_data[key]['salt'], contour_data[key]['temp'],
                         line_color="grey", line_alpha=0.8, line_width=1.5)

    def append_qc_comment(self, meta_series):
        """
        :param metadata:
        :return:
        """
        time_stamp = get_time_as_format(now=True, fmt='%Y%m%d%H%M')
        meta_series[len(meta_series) + 1] = '//QC_COMNT; MANUAL QC PERFORMED BY {}; TIMESTAMP {}'.format(
            self.ctd_session.settings.user, time_stamp)

    def get_tab_layout(self):
        fig_tabs = [Panel(child=column([Spacer(height=30, width=20), self.ts]), title="TS")]
        for p, item in self.figures.items():
            if (self.multi_sensors and p not in ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'COMBO_TEMP', 'COMBO_SALT',
                                                 'COMBO_DOXY']) \
                    or (not self.multi_sensors and p not in ['x1', 'x2', 'x3']):
                tab_layout = column([self.flag_widgets[p], item])
                tab_name = self.plot_parameters_mapping.get(p).split()[0].replace('_CTD', '')
                pan = Panel(child=tab_layout, title=tab_name)
                fig_tabs.append(pan)

        return Tabs(tabs=fig_tabs)

    def get_tabs(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        tabs = []
        for name, item in kwargs.items():
            tab = self.get_column(item)
            pan = Panel(child=tab, title=name)
            tabs.append(pan)

        return Tabs(tabs=tabs)

    def get_column(self, item):
        c_list = []
        for attr in item:
            if type(attr) == str:
                c_list.append(self.__getattribute__(attr))
            elif type(attr) == tuple:
                r = row([self.__getattribute__(a) for a in attr], sizing_mode="stretch_width")
                c_list.append(r)
        return column(c_list)

    def get_std_parameter_tab_layout(self):
        def pan_title(string):
            return string.split()[0].replace('_CTD', '')

        columns = []

        if self.multi_sensors:
            for params in zip(('x1', 'x2', 'x3'), ('x4', 'x5', 'x6'), ('COMBO_TEMP', 'COMBO_SALT', 'COMBO_DOXY')):
                pans = []
                for p in params:
                    if p in self.figures:
                        tab_cols = []
                        if p in self.flag_widgets:
                            tab_cols.append(self.flag_widgets[p])
                        else:
                            tab_cols.append(Spacer(width=20, height=41))
                        tab_cols.append(self.figures[p])
                        tab = column(tab_cols)
                        pan = Panel(child=tab, title=pan_title(self.plot_parameters_mapping.get(p) or p))
                        pans.append(pan)
                columns.append(column([Tabs(tabs=pans)]))
        else:
            for p1 in ('x1', 'x2', 'x3'):
                columns.append(column([self.flag_widgets[p1], self.figures[p1]]))

        return columns

    def get_layout(self):
        """
        :return:
        """
        tabs = self.get_tab_layout()
        meta_tabs = self.get_tabs(Data=['text_index_selection',
                                        ('select_all_button', 'deselect_all_button'),
                                        'pressure_slider',
                                        'text_multi_serie_flagging',
                                        'parameter_selector',
                                        'multi_flag_widget'],
                                  Metadata=['comnt_visit',
                                            'comnt_visit_button'],
                                  Import_Export=['file_button',
                                                 'download_button'],
                                  Info=['info_block'])
        std_parameter_tabs = self.get_std_parameter_tab_layout()
        widgets_1 = column([self.month_selector, self.spacer, self.selected_series], sizing_mode="fixed", height=300,
                           width=200)
        widgets_2 = column([Spacer(height=10, width=125)], sizing_mode="fixed", height=10, width=125)
        widgets_3 = column([meta_tabs], sizing_mode="stretch_both", height=100, width=100)
        l = grid([row([self.map, widgets_1, widgets_2, widgets_3]),
                  row([*std_parameter_tabs,
                       column([tabs]),
                       ])],
                 )
        return l

    @property
    def spacer(self):
        return Spacer(height=10, width=20)

    def return_layout(self):
        """
        Return the layout in order to display in an Embedded bokeh server within a notebook
        :return:
        """
        return self.get_layout()

    def show_plot(self):
        """
        As a html-file or output_notebook
        :return:
        """
        l = self.get_layout()
        show(l)
