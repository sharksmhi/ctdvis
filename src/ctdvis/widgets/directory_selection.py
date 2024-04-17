#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-09 11:27

@author: johannes
"""
import sys
from pathlib import Path
# from PyQt5.QtWidgets import QFileDialog, QApplication, QMessageBox
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtCore import Qt

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
root = tk.Tk()
root.withdraw()


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


def old_get_folder_path_from_user():
    """Return the selected directory path.

    Opens up a diolog window.
    """
    app = QApplication(sys.argv)  # noqa: F841
    dir_selector = DirectoryWindow()
    dir_selector.open_dialog()
    return dir_selector.folder


def old_message_box(text, icon_path=None):
    """Return dialog window.

    Args:
        text: Text.
        picture_path: Path to file.
    """
    app = QApplication(sys.argv)  # noqa: F841
    msgbox = QMessageBox()
    msgbox.setWindowTitle("Profile QC-tool")
    msgbox.setText(text)
    if icon_path:
        msgbox.setIconPixmap(QPixmap(icon_path))
    msgbox.setWindowFlags(Qt.WindowStaysOnTopHint)
    msgbox.exec_()


def get_folder_path_from_user():
    return filedialog.askdirectory()


def message_box(text, icon_path=None):
    messagebox.showinfo('', text)