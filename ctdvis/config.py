# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:37

@author: a002028

"""
import os
import sys
import requests
from ctdvis import utils
from ctdvis.readers import JSONreader, load_json
try:
    from sharkpylib.qc.settings import Settings as shark_qc_settings
except ModuleNotFoundError as error:
    print(error)
    print('Could not import sharkpylib.qc.settings. \nTrying to catch parameter_dependencies via github..')
    shark_qc_settings = None


class Settings:
    """
    """
    def __init__(self, visualize_setting=None):
        self.multi_sensors = None
        self.combo_plots = None
        self.visualize_setting = visualize_setting or 'smhi_viz'
        self.base_directory = os.path.dirname(os.path.realpath(__file__))
        self.user_download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        etc_path = '\\'.join([self.base_directory, 'etc', ''])
        self._load_settings(etc_path)

        if shark_qc_settings:
            qc_settings = shark_qc_settings()
            self.parameter_dependencies = qc_settings.parameter_dependencies.get('parameters')
        else:
            file_path = os.path.join(etc_path, 'parameter_dependencies.json')
            if not os.path.exists(file_path):
                try:
                    r = requests.get(
                        'https://raw.githubusercontent.com/sharksmhi/sharkpylib/master/sharkpylib/qc/etc/parameter_dependencies.json',
                        allow_redirects=True,
                    )
                    open(file_path, 'wb').write(r.content)
                    print('Download completed! file saved here: {}'.format(file_path))
                except:
                    raise ConnectionError(
                        'Was not able to download https://raw.githubusercontent.com/sharksmhi/sharkpylib/master/sharkpylib/qc/etc/parameter_dependencies.json'
                        'and could not import sharkpylib.qc.settings\n '
                        'Try again when you have access to the internet!'
                    )
            self.parameter_dependencies = load_json(file_path)

    def __setattr__(self, name, value):
        """
        Defines the setattr for object self
        :param name: str
        :param value: any kind
        :return:
        """
        if name == 'dir_path':
            pass
        elif isinstance(value, str) and 'path' in name:
            name = ''.join([self.base_directory, value])
        elif isinstance(value, dict) and 'paths' in name:
            self._check_for_paths(value)
        super().__setattr__(name, value)

    def _add_py_paths_to_system(self):
        """
        :return:
        """
        if hasattr(self, 'local_py_paths'):
            for key, item in self.local_py_paths.items():
                print(key, item)
                self._append_path_to_system(item)

    def _append_path_to_system(self, item):
        """"""
        if isinstance(item, str):
            if item not in sys.path:
                sys.path.append(item)
        elif isinstance(item, dict):
            for k, it in item.items():
                self._append_path_to_system(it)

    def _check_for_paths(self, dictionary):
        """
        Since default path settings are set to sirena base folder
        we need to add that base folder to all paths
        :param dictionary: Dictionary with paths as values and keys as items..
        :return: Updates dictionary with local path (self.dir_path)
        """
        for item, value in dictionary.items():
            if isinstance(value, dict):
                self._check_for_paths(value)
            elif 'path' in item:
                dictionary[item] = ''.join([self.base_directory, value])

    def _load_settings(self, etc_path):
        """
        :param etc_path: str, local path to settings
        :return: Updates attributes of self
        """
        paths = self.generate_filepaths(etc_path, pattern='.json')
        path_list = []
        for p in paths:
            if 'vis_setup' in p:
                if self.visualize_setting in p:
                    path_list.append(p)
                else:
                    pass
            else:
                path_list.append(p)
        # print(path_list)
        settings = JSONreader().load_json(config_files=path_list, return_dict=True)

        self.set_attributes(self, **settings)

    @staticmethod
    def set_attributes(obj, **kwargs):
        """
        #TODO Move to utils?
        With the possibility to add attributes to an object which is not 'self'
        :param obj: object
        :param kwargs: Dictionary
        :return: sets attributes to object
        """
        for key, value in kwargs.items():
            setattr(obj, key, value)

    @staticmethod
    def generate_filepaths(directory, pattern=''):
        """
        #TODO Move to utils?
        :param directory: str, directory path
        :param pattern: str
        :return: generator
        """
        for path, subdir, fids in os.walk(directory):
            for f in fids:
                if pattern in f:
                    yield os.path.abspath(os.path.join(path, f))

    @staticmethod
    def get_subdirectories(directory):
        """
        #TODO Move to utils?
        :param directory: str, directory path
        :return: list of existing directories (not files)
        """
        return [subdir for subdir in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, subdir))]

    @staticmethod
    def get_filepaths_from_directory(directory):
        """
        #TODO Move to utils?
        :param directory: str, directory path
        :return: list of files in directory (not sub directories)
        """
        return [''.join([directory, fid]) for fid in os.listdir(directory)
                if not os.path.isdir(directory+fid)]

    @property
    def q_parameters(self):
        return [item.get('q_flag') for _, item in self.data_parameters.items()]

    @property
    def q0_parameters(self):
        return [item.get('q0_flag') for _, item in self.data_parameters.items()]

    @property
    def q_colors(self):
        return [item.get('plot_color_key') for _, item in self.data_parameters.items()]

    @property
    def q0_plot_keys(self):
        return [item.get('plot_q0_key') for _, item in self.data_parameters.items()]

    @property
    def plot_keys(self):
        return [item.get('plot_key') for _, item in self.data_parameters.items()]

    @property
    def data_parameters_with_units(self):
        return [' '.join((key, item.get('unit'))) for key, item in self.data_parameters.items()]

    @property
    def selected_keys(self):
        return self.q_parameters + self.q0_parameters + self.q_colors + self.data_parameters_with_units + self.meta_parameters

    @property
    def q_colors_mapper(self):
        return {item.get('q_flag'): item.get('plot_color_key') for _, item in self.data_parameters.items()}

    @property
    def plot_parameters_mapping(self):
        d = {}
        for key, item in self.data_parameters.items():
            d[item.get('plot_key')] = ' '.join((key, item.get('unit')))
            d[item.get('plot_q0_key')] = item.get('q0_flag')
            d[item.get('plot_color_key')] = item.get('q_flag')
            d[key] = {'q_flags': [self.data_parameters[k].get('q_flag') for k in self.parameter_dependencies[key] if k in self.data_parameters],
                      'color_keys': [self.data_parameters[k].get('plot_color_key') for k in self.parameter_dependencies[key] if k in self.data_parameters]}
        return d

    @property
    def parameter_formats(self):
        return {key: float for key in self.data_parameters_with_units}


class InfoLog:
    """
    We don't intend to initialize this class into an object, hence classmethods
    """
    missing_stations = []

    def __init__(self, station=None):
        if station:
            self.missing_stations.append(station)

    @classmethod
    def append_missing_station(cls, station):
        return cls('\t-' + station)

    @classmethod
    def print_missing_stations(cls):
        print('Missing stations:')
        print('\n'.join(cls.missing_stations))

    @classmethod
    def reset(cls):
        cls.missing_stations = []


class ErrorCapturing:
    """
    We don't intend to initialize this class into an object, hence classmethods
    """
    errors = []

    def __init__(self, error=None):
        if error:
            self.errors.append(error)

    @classmethod
    def append_error(cls, **error_kwargs):
        string = '\t-' + ', '.join((': '.join((key, str(item))) for key, item in error_kwargs.items()))
        return cls(string)

    @classmethod
    def print_errors(cls):
        print('Errors:')
        print('\n'.join(cls.errors))

    @classmethod
    def reset(cls):
        cls.errors = []
