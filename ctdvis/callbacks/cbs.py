# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-06 15:33

@author: a002028
"""
from functools import partial
from bokeh.models import Button, FileInput, CustomJS, CrosshairTool
from bokeh.layouts import row, Spacer
from bokeh.models.widgets import Select
from bokeh.plotting import figure
from bokeh.events import ButtonClick
from ctdvis.utils import get_time_as_format


def callback_test(source):
    """Return a CustomJS callback.

    Intended for test use. printing 'console print callback_test!'.
    """
    code = """
    // CALLBACK TESTING, WITH PRINT
    console.log('console print callback_test!')
    """
    # Create a CustomJS callback
    return CustomJS(args={'source': source},
                    code=code)


def month_selection_callback(position_source=None, position_plot_source=None):
    """Return a CustomJS callback."""
    # TODO We need to rewrite the JScallback code.. not very versatile..
    #  simply use all columns from position_source to begin with?
    code = """
    console.log('month_selection_callback');
    // Get data from ColumnDataSource
    var selected_data = {LATIT: [], LONGI: [], STATION: [], KEY: [], MONTH: [], COMNT_VISIT: []};
    var data = source.data;

    var month_mapping = {'All': 'All',
                         'January': '01', 'February': '02',
                         'March': '03', 'April': '04',
                         'May': '05', 'June': '06',
                         'July': '07', 'August': '08',
                         'September': '09', 'October': '10',
                         'November': '11', 'December': '12'};

    var selected_month = month_mapping[month.value];

    var key_val, lat_val, lon_val, statn_val, mon_val, cvis_val;
    for (var i = 0; i < data.KEY.length; i++) {
        key_val = data.KEY[i];
        lat_val = data.LATIT[i];
        lon_val = data.LONGI[i];
        statn_val = data.STATION[i];
        mon_val = data.MONTH[i];
        cvis_val = data.COMNT_VISIT[i];

        if (selected_month == 'All') {
            selected_data.KEY.push(key_val);
            selected_data.LATIT.push(lat_val);
            selected_data.LONGI.push(lon_val);
            selected_data.STATION.push(statn_val);
            selected_data.MONTH.push(mon_val);
            selected_data.COMNT_VISIT.push(cvis_val);
        } else if (mon_val == selected_month) {
            selected_data.KEY.push(key_val);
            selected_data.LATIT.push(lat_val);
            selected_data.LONGI.push(lon_val);
            selected_data.STATION.push(statn_val);
            selected_data.MONTH.push(mon_val);
            selected_data.COMNT_VISIT.push(cvis_val);
        }
    }

    plot_source.data = selected_data;
    """
    # Create a CustomJS callback.
    return CustomJS(args={'source': position_source,
                          'plot_source': position_plot_source},
                    code=code)


def station_callback_2(position_source=None, data_source=None,
                       figures=None, seconds=None, pmap=None,
                       single_select=None):
    """Return a CustomJS callback."""
    # assert position_source, data_source
    code = """
    //console.log('station_callback_2');
    // Set column name to select similar glyphs
    var key = 'KEY';
    var statn_key = 'STATION';
    var sec = seconds.data;

    // Get data from ColumnDataSource
    var position_data = position_source.data;
    //var data = data_source.data;
    var parameter_mapping = parameter_mapping;
    var figures = figures;
    var single_select = single_select;

    //console.log('parameter_mapping', parameter_mapping);

    // Get indices array of all selected items
    var selected = position_source.selected.indices;

    //console.log('data[y].length', data['y'].length)
    //console.log('selected', selected);

    // Update figure titles flag_color_mapping
    var station_name = position_data[statn_key][selected[0]];
    var selected_key = position_data[key][selected[0]];

    //console.log('station_name', station_name);
    //console.log('selected_key', selected_key);

    // Update active keys in data source
    if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
        for (var fig_key in figures){
            figures[fig_key].title.text = station_name + ' - ' + selected_key
        }
        data_source['main_source'].data = data_source[selected_key].data;

        // Save changes to ColumnDataSource
        data_source['main_source'].change.emit();
    } else {
        data_source['main_source'].data = data_source['default_source'].data;
        console.log('We can only work with one serie at a time', selected.length)
    }

    var d = new Date();
    var t = d.getTime();
    var new_seconds = Math.round(t / 1000);
    sec.tap_time[0] = new_seconds;
    sec.reset_time[0] = new_seconds;
    seconds.change.emit();
    for (var fig_key in figures){
        figures[fig_key].reset.emit();
    }
    //console.log('station_callback_2 - DONE');
    """
    # Create a CustomJS callback with the code and the data
    return CustomJS(args={'position_source': position_source,
                          'data_source': data_source,
                          'figures': figures,
                          'seconds': seconds,
                          'parameter_mapping': pmap,
                          'single_select': single_select,
                          },
                    code=code)


def lasso_callback(monthly_keys=None, in_data=None, plot_data=None, x_range=None, y_range=None):
    """Return a CustomJS callback."""
    code = """
    //console.log('lasso_callback');
    var month_mapping = {'All': 'All',
                         'January': '01', 'February': '02',
                         'March': '03', 'April': '04',
                         'May': '05', 'June': '06',
                         'July': '07', 'August': '08',
                         'September': '09', 'October': '10',
                         'November': '11', 'December': '12'};

    var selected_month = month_mapping[month.value];

    var data = {x: [], y: [], color: [], key: []};
    var indices = cb_obj.indices;
    var selected_keys = [];
    for (var i = 0; i < indices.length; i++) {
        selected_keys.push(monthly_keys[selected_month][indices[i]]);
    }

    //console.log('selected_keys', selected_keys)

    var key_val, x_val, y_val, c_val;
    for (var i = 0; i < in_data.KEY.length; i++) {
        key_val = in_data.KEY[i];
        x_val = in_data.x[i];
        y_val = in_data.y[i];
        c_val = in_data.color[i];

        if (selected_keys.indexOf(key_val) !== -1) {
            data.x.push(x_val);
            data.y.push(y_val);
            data.color.push(c_val);
            data.key.push(key_val);
        }
    }
    if (data.x.length > 1) {
        //console.log('Update!')
        plot_data.data = data;
        x_range.start = Math.min.apply(Math, data.x)-0.5;
        x_range.end = Math.max.apply(Math, data.x)+0.5;
        y_range.start = Math.min.apply(Math, data.y)-0.5;
        y_range.end = Math.max.apply(Math, data.y)+0.5;
        x_range.change.emit();
        y_range.change.emit();
        //console.log('x_range.start', x_range.start)
    }
    """
    return CustomJS(args=dict(monthly_keys=monthly_keys,
                              in_data=in_data.data,
                              plot_data=plot_data,
                              x_range=x_range,
                              y_range=y_range),
                    code=code)


def comnt_callback(position_source=None, comnt_obj=None, single_select=None):
    """Return a CustomJS callback."""
    code = """
    //console.log('comnt_callback');
    // Set column name to select similar glyphs
    var key = 'KEY';
    var statn_key = 'STATION';
    var comnt_key = 'COMNT_VISIT';

    // Set Sources
    var position_data = position_source.data;
    var comnt_obj = comnt_obj;
    var title_obj = title_obj;
    var single_select = single_select;

    // Get indices array of all selected items
    var selected = position_source.selected.indices;

    // Update figure title
    var station_name = position_data[statn_key][selected[0]];
    var selected_key = position_data[key][selected[0]];
    var comnt = position_data[comnt_key][selected[0]];

    // Update active keys in data source
    if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
        comnt_obj.value = comnt;
        comnt_obj.title = 'COMNT_VISIT: ' + station_name + ' - ' + selected_key;
    }

    """
    # Create a CustomJS callback with the code and the data
    return CustomJS(args={'position_source': position_source,
                          'comnt_obj': comnt_obj,
                          'single_select': single_select,
                          },
                    code=code)


def comnt_samp_callback(position_source=None, comnt_obj=None, data_source=None,
                        comnt_selector=None, single_select=None):
    """Return a CustomJS callback."""
    code = """
    // Set column name to select similar glyphs
    var key = 'KEY';
    var statn_key = 'STATION';

    // Set Sources
    var position_data = position_source.data;
    var data = data_source.data;
    var comnt_obj = comnt_obj;
    var single_select = single_select;

    // Get indices array of all selected items
    var selected = position_source.selected.indices;

    // Update active keys in data source
    if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
        // Update figure title
        var station_name = position_data[statn_key][selected[0]];
        var selected_key = position_data[key][selected[0]];
        comnt_obj.title = 'COMNT_SAMP:  ' + station_name + ' - ' + selected_key;
        comnt_obj.value = '';
        function onlyUnique(value, index, self) {
          return self.indexOf(value) === index;
        }
        var unique_values = data['COMNT_SAMP'].filter(onlyUnique);
        unique_values = unique_values.filter(function(item) {
            return item !== ""
        })
        var using = [''];
        using.push(...unique_values);
        comnt_selector.options = using;
    }

    """
    return CustomJS(
        args={
            'position_source': position_source,
            'comnt_obj': comnt_obj,
            'comnt_selector': comnt_selector,
            'data_source': data_source,
            'single_select': single_select,
        },
        code=code
    )


def change_button_type_callback(button=None, btype=None):
    """Return a CustomJS callback."""
    code = """
    button.button_type = btype;
    """
    return CustomJS(args={'button': button, 'btype': btype}, code=code)


def select_button(data_source=None):
    """Return a button."""
    code = """
    var data = data_source.data;
    var indices = [];

    var i = 0;
    while ( ! isNaN(data.y[i]) ) {
        indices.push(i)
        i++
    }
    data_source.selected.indices = indices;
    button.button_type = 'success';
    //console.log('select_button DONE');
    """
    button = Button(label="Select all indices", width=30, button_type="default")
    callback = CustomJS(args={'data_source': data_source, 'button': button}, code=code)
    button_type_callback = change_button_type_callback(button=button, btype='success')
    button.js_on_event(ButtonClick, callback, button_type_callback)
    return button


def deselect_button(data_source=None):
    """Return a button."""
    code = """
    data_source.selected.indices = [];
    """
    callback = CustomJS(args={'data_source': data_source}, code=code)
    button = Button(label="Deselect all indices", width=30, button_type="default")
    button.js_on_event(ButtonClick, callback)
    return button


def range_slider_update_callback(slider=None, data_source=None):
    """Return a CustomJS callback."""
    code = """
    var data = data_source.data;
    var values = [];
    var i = 0;
    while ( ! isNaN(data.y[i]) ) {
        values.push(data.y[i])
        i++
    }
    slider.start = Math.min.apply(Math, values);
    if (slider.start !== Math.max.apply(Math, values)) {
            slider.end = Math.max.apply(Math, values);
    } else {
        slider.end = Math.max.apply(Math, values) + 1;
    }
    slider.value = [slider.start, slider.end];
    slider.change.emit();
    """
    return CustomJS(args={'slider': slider, 'data_source': data_source},
                    code=code)


def range_selection_callback(data_source=None):
    """Return a CustomJS callback."""
    code = """
    var data = data_source.data;
    var min_pres = cb_obj.value[0];
    var max_pres = cb_obj.value[1];
    var indices = [];
    for (var i = 0; i < data.y.length; i++) {
        if ((data.y[i] >= min_pres) && (data.y[i] <= max_pres)) {
            indices.push(i)
        }
    }
    data_source.selected.indices = indices;
    """
    return CustomJS(args={'data_source': data_source},
                    code=code)


def get_flag_widget(position_source, data_source, flag_key=None, color_key=None):
    """Return a bokeh row layout.

    Flag selector.
    """
    code = """
    console.log('get_flag_widget');
    var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                              'B-flag': {'c':'red', 'flag': 'B'},
                              'E-flag': {'c':'green', 'flag': 'E'},
                              'S-flag': {'c':'orange', 'flag': 'S'}};

    // Get data from ColumnDataSource
    var position_data = position_source.data;
    var data = data_source.data;

    // Set variables attributes
    var color_column = color_key;
    var selected_flag = flag_selection.value;

    var selected_position = position_source.selected.indices;
    var selected_key = position_data['KEY'][selected_position[0]];
    var flag_column = selected_key+'_'+flag_key;

    // Get indices array of all selected items
    var selected_indices = data_source.selected.indices;

    for (var i = 0; i < selected_indices.length; i++) {
        data[color_column][selected_indices[i]] = flag_color_mapping[selected_flag]['c'];
        data[flag_column][selected_indices[i]] = flag_color_mapping[selected_flag]['flag'];
        // console.log('data[flag_column][selected_indices[i]]', data[flag_column][selected_indices[i]])
    }

    // Save changes to ColumnDataSource
    data_source.change.emit();
    """  # noqa: E501
    callback = CustomJS(args={'position_source': position_source,
                              'data_source': data_source},
                        code=code)
    flag_selector = Select(value='A-flag',
                           options=['A-flag', 'B-flag', 'E-flag', 'S-flag'],
                           width=100, height=50)
    callback.args["flag_selection"] = flag_selector
    callback.args["color_key"] = color_key
    callback.args["flag_key"] = flag_key
    button = Button(label="Flag Data", width=50)
    button.js_on_event(ButtonClick, callback)

    return row([flag_selector, button], sizing_mode="stretch_width")


def get_flag_buttons_widget(position_source, data_source, datasets, flag_keys=None,
                            color_keys=None, figure_objs=None, select_button=None):
    """Return a list of buttons.

    Each button represents a QC-flag which will be applied when the button is pressed.
    """
    code = """
    //console.log('get_flag_buttons_widget');
    var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                              'B-flag': {'c':'red', 'flag': 'B'},
                              'E-flag': {'c':'green', 'flag': 'E'},
                              'S-flag': {'c':'orange', 'flag': 'S'}};

    // Get data from ColumnDataSource
    var position_data = position_source.data;
    var data = data_source.data;
    var select_button_type = select_button.button_type;

    // Set variables attributes
    var color_columns = color_keys;
    var flag_keys = flag_keys;
    var selected_flag = flag;

    var selected_position = position_source.selected.indices;
    var selected_key = position_data['KEY'][selected_position[0]];

    // Get indices array of all selected items
    var selected_indices = data_source.selected.indices;

    var flag_value = flag_color_mapping[selected_flag]['flag'];
    var color_value = flag_color_mapping[selected_flag]['c'];

    if (selected_position.length == 1) {
        for (var i = 0; i < selected_indices.length; i++) {
            //console.log('selected_indices[i]', selected_indices[i])
            //console.log('index_value', index_value)
            for (var j = 0; j < color_columns.length; j++) {
                data[color_columns[j]][selected_indices[i]] = color_value;
                //data[flag_keys[j]][selected_indices[i]] = flag_value;
            }
        }

        // Save changes to ColumnDataSource (only on the plotting side of ColumnDataSource)
        data_source.change.emit();
        for (var key in figure_objs) {
            figure_objs[key].reset.emit();
        }
        data_source.selected.indices = selected_indices;
        select_button.button_type = select_button_type;

        // Trigger python callback inorder to save changes to the actual datasets
        dummy_trigger.glyph.size = {'value': Math.random(), 'units': 'screen'};
        dummy_trigger.glyph.change.emit();

    } else {
        console.log('To many selected stations!! We can only work with one at a time', selected_position.length)
    }
    """  # noqa: E501
    flag_color_mapping = {'A-flag': {'c': 'navy', 'flag': ''},
                          'B-flag': {'c': 'red', 'flag': 'B'},
                          'E-flag': {'c': 'green', 'flag': 'E'},
                          'S-flag': {'c': 'orange', 'flag': 'S'}}

    def callback_py(attr, old, new, flag=None):
        selected_position = position_source.selected.indices
        if len(selected_position) > 1:
            print('multi serie selection, no good! len(selected_position) = {}'
                  ''.format(len(selected_position)))
            return

        selected_key = position_source.data['KEY'][selected_position[0]]
        selected_indices = data_source.selected.indices
        ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
        flag_value = flag_color_mapping[flag].get('flag')
        datasets[ds_key]['data'].loc[selected_indices, flag_keys] = flag_value

    # button_types = default, primary, success, warning or danger
    button_types = ['primary', 'danger', 'success', 'warning']
    flag_list = ['A-flag', 'B-flag', 'E-flag', 'S-flag']
    button_list = [Spacer(width=10, height=10)]
    dummy_figure = figure()
    for flag, b_type in zip(flag_list, button_types):
        dummy_trigger = dummy_figure.circle(x=[1], y=[1], alpha=0)
        dummy_trigger.glyph.on_change('size', partial(callback_py, flag=flag))

        callback = CustomJS(args={'position_source': position_source,
                                  'data_source': data_source,
                                  'figure_objs': figure_objs,
                                  'flag': flag,
                                  'dummy_trigger': dummy_trigger,
                                  'select_button': select_button},
                            code=code)

        callback.args["color_keys"] = color_keys
        callback.args["flag_keys"] = flag_keys

        button = Button(label=flag, width=30, button_type=b_type)
        button.js_on_event(ButtonClick, callback)

        button_list.append(button)

    button_list.append(Spacer(width=10, height=10))

    return row(button_list, sizing_mode="stretch_width")


def get_multi_serie_flag_widget(position_source, data_source, datasets, parameter_selector=None,
                                parameter_mapping=None, figure_objs=None):
    """Return a list of buttons.

    Each button represents a QC-flag which will be applied when the button is pressed.
    """
    code = """
    console.log('get_multi_serie_flag_widget');
    var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                              'B-flag': {'c':'red', 'flag': 'B'},
                              'E-flag': {'c':'green', 'flag': 'E'},
                              'S-flag': {'c':'orange', 'flag': 'S'}};

    // Get data from ColumnDataSource
    var position_data = position_source.data;
    // var data = data_source.data;

    // Set variables attributes
    var selected_flag = flag;

    var flag_keys = parameter_mapping[parameter_selector.value]['q_flags']
    var color_columns = parameter_mapping[parameter_selector.value]['color_keys']

    var flag_value = flag_color_mapping[selected_flag]['flag'];
    var color_value = flag_color_mapping[selected_flag]['c'];

    var selected_position_indices = position_source.selected.indices;
    var selected_key = 0;
    var value_array = [];
    var valid_indices = [];

    for (var i_pos = 0; i_pos < selected_position_indices.length; i_pos++) { 
        var selected_key = position_data['KEY'][selected_position_indices[i_pos]];
        var value_array = data_source[selected_key].data['x1'];

        for (var i = 0; i < value_array.length; i++) {
            for (var j = 0; j < color_columns.length; j++) {
                data_source[selected_key].data[color_columns[j]][i] = color_value;
            }
        }
        data_source[selected_key].change.emit();
    }

    for (var key in figure_objs) {
        figure_objs[key].reset.emit();
    }

    // Trigger python callback inorder to save changes to the actual datasets
    dummy_trigger.glyph.size = {'value': Math.random(), 'units': 'screen'};
    dummy_trigger.glyph.change.emit();
    console.log('DONE - get_multi_serie_flag_widget');
    """
    flag_color_mapping = {'A-flag': {'c': 'navy', 'flag': ''},
                          'B-flag': {'c': 'red', 'flag': 'B'},
                          'E-flag': {'c': 'green', 'flag': 'E'},
                          'S-flag': {'c': 'orange', 'flag': 'S'}}

    def callback_py(attr, old, new, flag=None):
        flag_keys = parameter_mapping[parameter_selector.value].get('q_flags')

        selected_position = position_source.selected.indices
        for pos_source_index in selected_position:
            selected_key = position_source.data['KEY'][pos_source_index]
            ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
            flag_value = flag_color_mapping[flag].get('flag')
            datasets[ds_key]['data'].loc[:, flag_keys] = flag_value

    # button_types = default, primary, success, warning or danger
    button_types = ['primary', 'danger', 'success', 'warning']
    flag_list = ['A-flag', 'B-flag', 'E-flag', 'S-flag']
    button_list = []
    dummy_figure = figure()
    for flag, b_type in zip(flag_list, button_types):
        dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
        dummy_trigger.glyph.on_change('size', partial(callback_py, flag=flag))

        callback = CustomJS(args={'position_source': position_source,
                                  'data_source': data_source,
                                  'figure_objs': figure_objs,
                                  'parameter_mapping': parameter_mapping,
                                  'parameter_selector': parameter_selector,
                                  'flag': flag,
                                  'dummy_trigger': dummy_trigger},
                            code=code)

        button = Button(label=flag, width=30, button_type=b_type)
        button.js_on_event(ButtonClick, callback)

        button_list.append(button)

    return row(button_list, sizing_mode="stretch_width")


def get_download_widget(datasets, series, session, savepath):
    """Return a download button."""
    def callback_download(event):
        def serie_generator(datasets_filelist, selected_keylist):
            for name in datasets_filelist:
                for key in selected_keylist:
                    if key in name:
                        yield name, key

        def append_qc_comment(meta):
            time_stamp = get_time_as_format(now=True, fmt='%Y%m%d%H%M')
            meta[len(meta) + 1] = '//COMNT_QC; MANUAL QC PERFORMED BY {}; TIMESTAMP {}'.format(
                session.settings.user, time_stamp)

        if not any(series.selected.indices):
            print('No selected series to download')
            print('len(series.selected.indices)', series.selected.indices)
            return

        generator = serie_generator(
            datasets.keys(),
            [series.data['KEY'][idx] for idx in series.selected.indices]
        )

        datasets_to_update = {}
        for ds_name, _ in generator:
            append_qc_comment(datasets[ds_name]['metadata'])
            datasets_to_update[ds_name] = datasets[ds_name]

        if any(datasets_to_update):
            session.save_data(
                [datasets_to_update],
                save_path=savepath or 'C:/QC_CTD',
                writer='ctd_standard_template',
            )
        else:
            print('No download!')

    button = Button(label="Download selected data", button_type="success", width=40)
    button.on_event(ButtonClick, callback_download)
    return button


def comnt_visit_change_button(datasets=None, position_source=None, comnt_obj=None):
    """Return a button."""
    def callback_py(attr, old, new, comnt_obj=None):
        selected_indices = position_source.selected.indices
        if len(selected_indices) > 1:
            print('multi serie selection, no good! len(selected_position) = {}'
                  ''.format(len(selected_indices)))
            return
        selected_key = position_source.data['KEY'][selected_indices[0]]
        ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
        cv_boolean = datasets[ds_key]['metadata'].str.startswith('//METADATA;COMNT_VISIT;')
        datasets[ds_key]['metadata'][cv_boolean] = '//METADATA;COMNT_VISIT;' + comnt_obj.value

    js_code = """
    console.log('comnt_visit_change_button')
    // Get data from ColumnDataSource
    var comnt_column = 'COMNT_VISIT';
    var position_data = position_source.data;

    // Set variables attributes
    var new_comnt = comnt_obj.value;
    var selected_indices = position_source.selected.indices;

    if (selected_indices.length == 1) {
        position_data[comnt_column][selected_indices[0]] = new_comnt;

        // Save changes to ColumnDataSource
        position_source.change.emit();

        // Trigger python callback inorder to save changes to the actual datasets
        dummy_trigger.glyph.size = {'value': Math.random(), 'units': 'screen'};
        dummy_trigger.glyph.change.emit();

    } else {
        console.log('To many selected stations!! We can only work with one at a time', selected_indices.length)
    }
    """  # noqa: E501
    dummy_figure = figure()
    dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
    dummy_trigger.glyph.on_change('size', partial(callback_py, comnt_obj=comnt_obj))

    callback = CustomJS(args={'position_source': position_source,
                              'comnt_obj': comnt_obj,
                              'dummy_trigger': dummy_trigger},
                        code=js_code)

    button = Button(label="Commit visit comnt", width=30, button_type="success")
    button.js_on_event(ButtonClick, callback)
    return button


def comnt_samp_change_button(datasets=None, position_source=None, data_source=None, comnt_obj=None):
    """Return a button."""
    def callback_py(attr, old, new, comnt_obj=None):
        selected_indices = position_source.selected.indices
        if len(selected_indices) > 1:
            print('multi serie selection, no good! len(selected_position) = {}'
                  ''.format(len(selected_indices)))
            return
        selected_key = position_source.data['KEY'][selected_indices[0]]
        selected_data_indices = data_source.selected.indices
        # data_source[selected_key].data['COMNT_SAMP'][selected_data_indices] = comnt_obj.value
        ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
        # TODO add '; '.join(...)
        # datasets[ds_key]['data']['COMNT_SAMP'].iloc[selected_data_indices] = \
        #     datasets[ds_key]['data']['COMNT_SAMP'].iloc[selected_data_indices].apply(
        #         lambda x: '; '.join((x, comnt_obj.value))
        #     )
        datasets[ds_key]['data']['COMNT_SAMP'].iloc[selected_data_indices] = comnt_obj.value
        # datasets[ds_key]['data'][cv_boolean] = comnt_obj.value

    js_code = """
    console.log('comnt_visit_change_button')
    // Get data from ColumnDataSource
    var position_data = position_source.data;
    var data = data_source.data;

    // Set variables attributes
    var selected_position_indices = position_source.selected.indices;

    if (selected_position_indices.length == 1) {
        var selected_water_indices = data_source.selected.indices;
        var selected_key = position_data['KEY'][selected_position_indices[0]];

        for (var i = 0; i < selected_water_indices.length; i++) {
            data['COMNT_SAMP'][selected_water_indices[i]] = comnt_obj.value;
        }

        // Save changes to ColumnDataSource
        data_source.change.emit();

        // Trigger python callback inorder to save changes to the actual datasets
        dummy_trigger.glyph.size = {'value': Math.random(), 'units': 'screen'};
        dummy_trigger.glyph.change.emit();

    } else {
        console.log('To many selected stations!! We can only work with one at a time', selected_indices.length)
    }
    """  # noqa: E501
    dummy_figure = figure()
    dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
    dummy_trigger.glyph.on_change('size', partial(callback_py, comnt_obj=comnt_obj))

    callback = CustomJS(args={'position_source': position_source,
                              'data_source': data_source,
                              'comnt_obj': comnt_obj,
                              'dummy_trigger': dummy_trigger},
                        code=js_code)

    button = Button(label="Commit sample comnt", width=30, button_type="success")
    button.js_on_event(ButtonClick, callback)
    return button


def comnt_samp_selection(data_source=None, comnt_obj=None):
    """Return a select widget."""
    code = """
    //console.log('select: value=' + this.value, this.toString())
    comnt_obj.value = this.value;
    var data = data_source.data;
    var selected_indices = [];
    var comnt_value;
    for (var i = 0; i < data.COMNT_SAMP.length; i++) {
        comnt_value = data.COMNT_SAMP[i];
        if (comnt_value == this.value) {
            selected_indices.push(i);
        }
    }
    data_source.selected.indices = selected_indices;
    """
    callback = CustomJS(
        code=code,
        args={'data_source': data_source,
              'comnt_obj': comnt_obj}
    )
    select = Select(
        title="Select comnt incl. index",
        value='None',
        options=[],
    )
    select.js_on_change("value", callback)
    return select


def get_file_widget():
    """Return a file input button."""
    # button_input = FileInput(accept=".csv,.txt")
    button_input = FileInput()

    return button_input


def add_hlinked_crosshairs(*figs):
    """Link crosshair between figures."""
    cht = CrosshairTool(line_alpha=0.5, dimensions="width")
    for f in figs:
        f.add_tools(cht)


def x_range_callback(x_range_obj=None, delta=4, seconds=None):
    """Return a CustomJS callback."""
    code = """
    //console.log('x_range_callback');
    var sec = seconds.data;
    var d = new Date();
    var t = d.getTime();
    var new_seconds = t / 1000;
    var tap_time_delta = new_seconds - sec.tap_time[0];
    var reset_time_delta = new_seconds - sec.reset_time[0];
    var delta_add;
    if (tap_time_delta < 1.5 || reset_time_delta < 1.5) {
        var start = xr.start;
        var end = xr.end;
        var x_delta = end - start;
        if (x_delta < accepted_delta) {
            delta_add = (accepted_delta - x_delta) / 2;
            end = end + delta_add;
            start = start - delta_add;
        }
        xr.end = end;
        xr.start = start;
    }
    """
    return CustomJS(args={'xr': x_range_obj,
                          'seconds': seconds,
                          'accepted_delta': delta},
                    code=code)


def reset_callback(seconds):
    """Return a CustomJS callback."""
    code = """
    //console.log('reset_callback');
    var sec = seconds.data;
    var d = new Date();
    var t = d.getTime();
    sec.reset_time[0] = t / 1000;
    //console.log('sec.reset_time[0]', sec.reset_time[0])
    seconds.change.emit();
    """
    return CustomJS(args={'seconds': seconds},
                    code=code)


def reset_all_callback(figures):
    """Return a CustomJS callback."""
    code = """
    console.log('reset_all_callback');
    for (var i = 0; i < figure_objs.length; i++) {
        figure_objs[i].reset.emit();
    }
    """
    return CustomJS(args={'figure_objs': figures},
                    code=code)
