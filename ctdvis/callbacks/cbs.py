# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-06 15:33

@author: a002028

"""
import time
from functools import partial
from bokeh.models import Button, FileInput, CustomJS, CrosshairTool
from bokeh.layouts import row, Spacer
from bokeh.models.widgets import Select
from bokeh.plotting import figure
from bokeh.events import ButtonClick

from ctdvis.utils import get_time_as_format


def callback_test(source):
    code = """
    // CALLBACK TESTING WITH PRINT
    console.log('console print callback_test!')        

    """
    # Create a CustomJS callback
    return CustomJS(args={'source': source},
                    code=code)


def month_selection_callback(position_source=None, position_plot_source=None):
    """
    # TODO We need to rewrite the JScallback code.. not very versatile..
    # simply use all columns from position_source to begin with?

    :param position_source:
    :param position_plot_source:
    :return:
    """
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
    # Create a CustomJS callback with the code and the data
    return CustomJS(args={'source': position_source,
                          'plot_source': position_plot_source},
                    code=code)


def station_callback_2(position_source=None, data_source=None,
                       figures=None, seconds=None, pmap=None,
                       single_select=None):
    # assert position_source, data_source
    code = """
    //console.log('station_callback_2');
    // Set column name to select similar glyphs
    var key = 'KEY';
    var statn_key = 'STATION';
    var sec = seconds.data;

    // Get data from ColumnDataSource
    var position_data = position_source.data;
    var data = data_source.data;
    var parameter_mapping = parameter_mapping;
    var figures = figures;
    var single_select = single_select;

    //console.log('parameter_mapping', parameter_mapping);

    // Get indices array of all selected items
    var selected = position_source.selected.indices;

    //console.log('data[y].length', data['y'].length)
    //console.log('selected', selected);

    // Update figure titlesflag_color_mapping 
    var station_name = position_data[statn_key][selected[0]];
    var selected_key = position_data[key][selected[0]];

    //console.log('station_name', station_name);
    //console.log('selected_key', selected_key);

    // Update active keys in data source    
    if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
        var data_parameter_name, q0_key, color_key;
        for (var fig_key in figures){
            if ( ! fig_key.startsWith("COMBO")) {
                data_parameter_name = parameter_mapping[fig_key];
                q0_key = fig_key+'_q0';
                color_key = 'color_'+fig_key;

                data[fig_key] = data[selected_key+'_'+data_parameter_name];
                data[q0_key] = data[selected_key+'_'+parameter_mapping[q0_key]];
                data[color_key] = data[selected_key+'_'+color_key];
            }
            figures[fig_key].title.text = station_name + ' - ' + selected_key
        }
        data['y'] = data[selected_key+'_'+parameter_mapping['y']];

        // Save changes to ColumnDataSource
        data_source.change.emit();
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
    """"""
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
    # assert position_source, data_source
    code = """
    //console.log('comnt_callback');
    // Set column name to select similar glyphs
    var key = 'KEY';
    var statn_key = 'STATION';
    var comnt_key = 'COMNT_VISIT';

    // Set Sources
    var position_data = position_source.data;
    var comnt_obj = comnt_obj;
    var single_select = single_select;

    // Get indices array of all selected items
    var selected = position_source.selected.indices;

    // Update figure title
    var station_name = position_data[statn_key][selected[0]];
    var selected_key = position_data[key][selected[0]];
    var comnt = position_data[comnt_key][selected[0]];

    // Update active keys in data source    
    if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
        comnt_obj.value = comnt
        comnt_obj.title = comnt_key + ':  ' + station_name + ' - ' + selected_key
    }

    """
    # Create a CustomJS callback with the code and the data
    return CustomJS(args={'position_source': position_source,
                          'comnt_obj': comnt_obj,
                          'single_select': single_select,
                          },
                    code=code)


def change_button_type_callback(button=None, btype=None):
    """"""
    code = """
    button.button_type = btype;
    """
    return CustomJS(args={'button': button, 'btype': btype}, code=code)


def select_button(data_source=None):
    """"""
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
    button = Button(label="Select all", width=30, button_type="default")
    callback = CustomJS(args={'data_source': data_source, 'button': button}, code=code)
    button_type_callback = change_button_type_callback(button=button, btype='success')
    button.js_on_event(ButtonClick, callback, button_type_callback)
    return button


def deselect_button(data_source=None):
    """"""
    code = """
    data_source.selected.indices = [];
    """
    callback = CustomJS(args={'data_source': data_source}, code=code)
    button = Button(label="Deselect all", width=30, button_type="default")
    button.js_on_event(ButtonClick, callback)
    return button


def range_slider_update_callback(slider=None, data_source=None):
    """"""
    code = """
    var data = data_source.data;        
    var values = [];
    var i = 0;
    while ( ! isNaN(data.y[i]) ) {
        values.push(data.y[i])
        i++
    }
    slider.start = Math.min.apply(Math, values);
    slider.end = Math.max.apply(Math, values);
    slider.value = [slider.start, slider.end];
    slider.change.emit();
    """
    return CustomJS(args={'slider': slider, 'data_source': data_source},
                    code=code)


def range_selection_callback(data_source=None):
    """"""
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
    """"""
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
    """
    callback = CustomJS(args={'position_source': position_source,
                              'data_source': data_source},
                        code=code)
    flag_selector = Select(value='A-flag',
                           options=['A-flag', 'B-flag', 'E-flag', 'S-flag'],
                           width=100)
    callback.args["flag_selection"] = flag_selector
    callback.args["color_key"] = color_key
    callback.args["flag_key"] = flag_key
    button = Button(label="Flag Data", width=50)
    button.js_on_event(ButtonClick, callback)

    return row([flag_selector, button], sizing_mode="stretch_width")


def get_flag_buttons_widget(position_source, data_source, datasets, flag_key=None,
                            color_key=None, figure_objs=None, select_button=None):
    """"""
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
    var color_column = color_key;
    var selected_flag = flag;

    var selected_position = position_source.selected.indices;
    var selected_key = position_data['KEY'][selected_position[0]];
    var flag_column = selected_key+'_'+flag_key;

    // Get indices array of all selected items
    var selected_indices = data_source.selected.indices;

    var patches = {
        color_column : [],
        flag_column : [],
    };

    var flag_value = flag_color_mapping[selected_flag]['flag'];
    var color_value = flag_color_mapping[selected_flag]['c'];
    var color_tuple, flag_tuple, index_value;

    //console.log('flag_value', flag_value)
    //console.log('color_value', color_value)
    //console.log('patches', patches)
    //console.log('selected_indices.length', selected_indices.length)

    if (selected_position.length == 1) {
        for (var i = 0; i < selected_indices.length; i++) {
            index_value = selected_indices[i];
            color_tuple = (index_value, color_value);
            flag_tuple = (index_value, flag_value);

            //console.log('index_value', index_value)
            //console.log('color_tuple', color_tuple)
            //console.log('flag_tuple', flag_tuple)

            data[color_column][index_value] = color_value;
            data[flag_column][index_value] = flag_value;
        }

        // Save changes to ColumnDataSource (only on the plotting side of ColumnDataSource)
        data_source.change.emit();
        for (var key in figure_objs) {
            figure_objs[key].reset.emit();
        }
        data_source.selected.indices = selected_indices;
        select_button.button_type = select_button_type;

        // Trigger python callback inorder to save changes to the actual datasets
        dummy_trigger.glyph.size = Math.random();
        dummy_trigger.glyph.change.emit();

    } else {
        console.log('To many selected stations!! We can only work with one at a time', selected_position.length)
    }
    """
    flag_color_mapping = {'A-flag': {'c': 'navy', 'flag': ''},
                          'B-flag': {'c': 'red', 'flag': 'B'},
                          'E-flag': {'c': 'green', 'flag': 'E'},
                          'S-flag': {'c': 'orange', 'flag': 'S'}}

    def callback_py(attr, old, new, flag=None):
        start_time = time.time()
        selected_position = position_source.selected.indices
        if len(selected_position) > 1:
            print('multi serie selection, no good! len(selected_position) = {}'.format(len(selected_position)))
            return

        selected_key = position_source.data['KEY'][selected_position[0]]
        selected_indices = data_source.selected.indices
        # ds_key = self.key_ds_mapper.get(selected_key)
        ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
        flag_value = flag_color_mapping[flag].get('flag')
        datasets[ds_key]['data'][flag_key].iloc[selected_indices] = flag_value
        print('datasets update in -- %.3f sec' % (time.time() - start_time))

    # button_types = default, primary, success, warning or danger
    button_types = ['primary', 'danger', 'success', 'warning']
    flag_list = ['A-flag', 'B-flag', 'E-flag', 'S-flag']
    button_list = [Spacer(width=10)]
    dummy_figure = figure()
    for flag, b_type in zip(flag_list, button_types):
        dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
        dummy_trigger.glyph.on_change('size', partial(callback_py, flag=flag))

        callback = CustomJS(args={'position_source': position_source,
                                  'data_source': data_source,
                                  'figure_objs': figure_objs,
                                  'flag': flag,
                                  'dummy_trigger': dummy_trigger,
                                  'select_button': select_button},
                            code=code)

        callback.args["color_key"] = color_key
        callback.args["flag_key"] = flag_key

        button = Button(label=flag, width=30, button_type=b_type)
        button.js_on_event(ButtonClick, callback)

        button_list.append(button)

    button_list.append(Spacer(width=10))

    return row(button_list, sizing_mode="stretch_width")


def get_download_widget(datasets, series, session):
    """"""

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

        generator = serie_generator(datasets.keys(),
                                    [series.data['KEY'][idx] for idx in series.selected.indices])

        datasets_to_update = {}
        for ds_name, serie_key in generator:
            append_qc_comment(datasets[ds_name]['metadata'])
            datasets_to_update[ds_name] = datasets[ds_name]

        if any(datasets_to_update):
            session.save_data([datasets_to_update], writer='ctd_standard_template')
        else:
            print('No download!')

    button = Button(label="Download selected data", button_type="success", width=40)
    button.on_event(ButtonClick, callback_download)
    return button


def comnt_visit_change_button(datasets=None, position_source=None, comnt_obj=None):
    """"""

    def callback_py(attr, old, new, comnt_obj=None):
        selected_indices = position_source.selected.indices
        if len(selected_indices) > 1:
            print('multi serie selection, no good! len(selected_position) = {}'.format(len(selected_indices)))
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
        dummy_trigger.glyph.size = Math.random();
        dummy_trigger.glyph.change.emit();

    } else {
        console.log('To many selected stations!! We can only work with one at a time', selected_indices.length)
    }
    """
    dummy_figure = figure()
    dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
    dummy_trigger.glyph.on_change('size', partial(callback_py, comnt_obj=comnt_obj))

    callback = CustomJS(args={'position_source': position_source,
                              'comnt_obj': comnt_obj,
                              'dummy_trigger': dummy_trigger},
                        code=js_code)

    button = Button(label="Commit", width=30, button_type="success")
    button.js_on_event(ButtonClick, callback)
    return button


def get_file_widget():
    # button_input = FileInput(accept=".csv,.txt")
    button_input = FileInput()

    return button_input


def add_hlinked_crosshairs(*figs):
    js_move = """
    for (var cross_key in other_crosses){
        other_crosses[cross_key].spans.width.computed_location = cb_obj.sy;
    }
    current_cross.spans.height.computed_location = null;
    """
    js_leave = """
    for (var cross_key in other_crosses){
        other_crosses[cross_key].spans.width.computed_location = null;
    }
    """
    cross_objs = {}
    fig_objs = {}
    for i, f in enumerate(figs):
        cross_objs[i] = CrosshairTool(line_alpha=0.5)
        fig_objs[i] = f
        fig_objs[i].add_tools(cross_objs[i])

    for i in range(len(cross_objs)):
        other_crosses = {ii: cross_objs[ii] for ii in range(len(cross_objs)) if ii != i}
        if i != len(cross_objs) - 1:
            args = {'current_cross': cross_objs[i], 'other_crosses': other_crosses, 'fig': fig_objs[i + 1]}
        else:
            args = {'current_cross': cross_objs[i], 'other_crosses': other_crosses, 'fig': fig_objs[0]}

        fig_objs[i].js_on_event('mousemove', CustomJS(args=args, code=js_move))
        fig_objs[i].js_on_event('mouseleave', CustomJS(args=args, code=js_leave))


def x_range_callback(x_range_obj=None, delta=4, seconds=None):
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
    code = """
    console.log('reset_all_callback');
    for (var i = 0; i < figure_objs.length; i++) {
        figure_objs[i].reset.emit();
    }
    """
    return CustomJS(args={'figure_objs': figures},
                    code=code)
