# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-03 11:37

@author: a002028
"""
import os
from pathlib import Path
import sys
import requests
from ctdvis.readers import JSONreader, load_json
try:
    from profileqc.config import Settings as shark_qc_settings
except ModuleNotFoundError as error:
    print(error)
    print('Could not import sharkpylib.qc.settings.',
          'Trying to catch parameter_dependencies via github..')
    shark_qc_settings = None


class Settings:
    """Setting class for CTDvis."""

    def __init__(self, visualize_setting=None):
        """Initiate."""
        self.multi_sensors = None
        self.combo_plots = None
        self.file_name_elements = None
        self.visualize_setting = visualize_setting or 'smhi_viz'
        self.base_directory = os.path.dirname(os.path.realpath(__file__))
        self.user_download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        etc_path = os.path.join(self.base_directory, 'etc')
        self._load_settings(etc_path)

        if shark_qc_settings:
            qc_settings = shark_qc_settings()
            self.parameter_dependencies = qc_settings.parameter_dependencies.copy()
        else:
            file_path = os.path.join(etc_path, 'parameter_dependencies.json')
            if not os.path.exists(file_path):
                try:
                    r = requests.get(
                        'https://raw.githubusercontent.com/sharksmhi/profileqc/master/profileqc/etc/parameter_dependencies.json',  # noqa: E501
                        allow_redirects=True,
                    )
                    open(file_path, 'wb').write(r.content)
                    print('Download completed! file saved here: {}'.format(file_path))
                except ConnectionError as error:
                    raise error(
                        'Was not able to download https://raw.githubusercontent.com/sharksmhi/profileqc/master/profileqc/etc/parameter_dependencies.json'  # noqa: E501
                        'and could not import profileqc.config\n '
                        'Try again when you have access to the internet!'
                    )
            self.parameter_dependencies = load_json(file_path)

    def __setattr__(self, name, value):
        """Define the setattr method for object self."""
        if name == 'dir_path':
            pass
        elif isinstance(value, str) and 'path' in name:
            name = os.path.join(self.base_directory, value)
        elif isinstance(value, dict) and 'paths' in name:
            self._check_for_paths(value)
        super().__setattr__(name, value)

    def _add_py_paths_to_system(self):
        """Append local python paths."""
        # TODO: Should not be needed.
        if hasattr(self, 'local_py_paths'):
            for item in self.local_py_paths.values():
                self._append_path_to_system(item)

    def _append_path_to_system(self, item):
        """Append local python paths."""
        # TODO: Should not be needed.
        if isinstance(item, str):
            if item not in sys.path:
                sys.path.append(item)
        elif isinstance(item, dict):
            for it in item.values():
                self._append_path_to_system(it)

    def _check_for_paths(self, dictionary):
        """Update the given dictionary with the ctdvis base folder.

        Since default path settings are set to ctdvis base folder
        we need to add that base folder to all paths.
        """
        for item, value in dictionary.items():
            if isinstance(value, dict):
                self._check_for_paths(value)
            elif 'path' in item:
                dictionary[item] = os.path.join(self.base_directory, value)

    def _load_settings(self, etc_path):
        """Load settings."""
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
        settings = JSONreader().load_json(config_files=path_list, return_dict=True)
        self.set_attributes(self, **settings)

        paths = self.generate_filepaths(etc_path, pattern='.png')
        icon_paths = {'icons': {}}
        for p in paths:
            icon_paths['icons'].setdefault(Path(p).stem, p)
        self.set_attributes(self, **icon_paths)

    @staticmethod
    def set_attributes(obj, **kwargs):
        """Set attribute to the given object.

        With the possibility to add attributes to an object which is not 'self'.
        """
        # TODO Move to utils?
        for key, value in kwargs.items():
            setattr(obj, key, value)

    @staticmethod
    def generate_filepaths(directory, pattern=''):
        """Create generator for file paths."""
        # TODO Move to utils?
        for path, _, fids in os.walk(directory):
            for f in fids:
                if pattern in f:
                    yield os.path.abspath(os.path.join(path, f))

    @staticmethod
    def get_subdirectories(directory):
        """Return list of sub directories."""
        # TODO Move to utils?
        return [subdir for subdir in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, subdir))]

    @staticmethod
    def get_filepaths_from_directory(directory):
        """Return list of file paths.

        Filter: only path of files, not folders.
        """
        # TODO Move to utils?
        return [os.path.join(directory, fid) for fid in os.listdir(directory)
                if not os.path.isdir(os.path.join(directory, fid))]

    @property
    def q_parameters(self):
        """Return Q-field-name of each parameter."""
        return [item.get('q_flag') for item in self.data_parameters.values()]

    @property
    def q0_parameters(self):
        """Return Q0-field-name of each parameter."""
        return [item.get('q0_flag') for item in self.data_parameters.values()]

    @property
    def q_colors(self):
        """Return color-field-name of each parameter."""
        return [item.get('plot_color_key') for item in self.data_parameters.values()]

    @property
    def q0_plot_keys(self):
        """Return Q0-plot-key of each parameter."""
        return [item.get('plot_q0_key') for item in self.data_parameters.values()]

    @property
    def plot_keys(self):
        """Return plot-key of each parameter."""
        return [item.get('plot_key') for item in self.data_parameters.values()]

    @property
    def scatter_size(self):
        """Return scatter-size-field-name of each parameter."""
        return [item.get('plot_size_key') for item in self.data_parameters.values()]

    @property
    def data_parameters_with_units(self):
        """Return list of paramter names including there respective unit."""
        return [' '.join((key, item.get('unit'))) for key, item in self.data_parameters.items()]

    @property
    def selected_keys(self):
        """Return selected data keys."""
        return self.q_parameters + self.q0_parameters + self.q_colors + self.scatter_size + self.data_parameters_with_units + self.meta_parameters  # noqa: E501

    @property
    def q_colors_mapper(self):
        """Return mapper."""
        return {
            item.get('q_flag'): item.get('plot_color_key')
            for item in self.data_parameters.values()
        }

    @property
    def q_size_mapper(self):
        """Return mapper."""
        return {
            item.get('q_flag'): item.get('plot_size_key')
            for item in self.data_parameters.values()
        }

    @property
    def plot_parameters_mapping(self):
        """Return parameter mapping dictionary."""
        d = {}
        for key, item in self.data_parameters.items():
            d[item.get('plot_key')] = ' '.join((key, item.get('unit')))
            d[item.get('plot_q0_key')] = item.get('q0_flag')
            d[item.get('plot_color_key')] = item.get('q_flag')
            d[item.get('plot_size_key')] = item.get('q_flag')
            d[key] = {
                'q_flags': [
                    self.data_parameters[k].get('q_flag') for k in self.parameter_dependencies[key]
                    if k in self.data_parameters
                ],
                'color_keys': [
                    self.data_parameters[k].get('plot_color_key')
                    for k in self.parameter_dependencies[key] if k in self.data_parameters
                ],
                'size_keys': [
                    self.data_parameters[k].get('plot_size_key')
                    for k in self.parameter_dependencies[key] if k in self.data_parameters
                ]
            }
        return d

    @property
    def parameter_formats(self):
        """Return data type mapper."""
        d = {key: float for key in self.data_parameters_with_units}
        d.setdefault('COMNT_SAMP', str)
        return d


class InfoLog:
    """Basic information logger."""

    missing_stations = []

    def __init__(self, station=None):
        """Initiate."""
        if station:
            self.missing_stations.append(station)

    @classmethod
    def append_missing_station(cls, station):
        """Append station."""
        return cls('\t-' + station)

    @classmethod
    def print_missing_stations(cls):
        """Print missing station."""
        print('Missing stations:')
        print('\n'.join(cls.missing_stations))

    @classmethod
    def reset(cls):
        """Reset class.missing_stations."""
        cls.missing_stations = []


class ErrorCapturing:
    """Basic error logger."""

    errors = []

    def __init__(self, error=None):
        """Initiate."""
        if error:
            self.errors.append(error)

    @classmethod
    def append_error(cls, **error_kwargs):
        """Append error."""
        string = '\t-' + ', '.join(
            (': '.join((key, str(item))) for key, item in error_kwargs.items())
        )
        return cls(string)

    @classmethod
    def print_errors(cls):
        """Print error."""
        print('Errors:')
        print('\n'.join(cls.errors))

    @classmethod
    def reset(cls):
        """Reset class.errors."""
        cls.errors = []
