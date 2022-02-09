#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-09 11:27

@author: johannes
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QApplication


class DirectoryWindow(QFileDialog):
    """Dialog window for directory selection."""

    def __init__(self, folder=None):
        """Initiate."""
        super().__init__()
        self.folder = folder or 'C:/'

    def open_dialog(self, *args):
        """Set selected directory path."""
        path = self.getExistingDirectory(
            self, 'Select a directory', self.folder
        )
        if Path(path).is_dir():
            self.folder = path


def get_folder_path_from_user():
    """Return the selected directory path.

    Opens up a diolog window.
    """
    app = QApplication(sys.argv)  # noqa: F841
    dir_selector = DirectoryWindow()
    dir_selector.open_dialog()
    return dir_selector.folder


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # dir_selector = DirectoryWindow()
    # dir_selector.open_dialog()
    # sys.exit(app.exec_())
    p = get_folder_path_from_user()
    print(p)
