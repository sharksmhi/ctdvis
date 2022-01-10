# Copyright (c) 2021 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-02-18 13:52

@author: johannes

"""
import os
import setuptools


requirements = []
with open('requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())

NAME = 'ctdvis'
VERSION = "0.1.9"
README = open('READMEpypi.rst', 'r').read()

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="SMHI - NODC",
    author_email="johannes.johansson@smhi.se",
    description="Quality control CTD/MVP data at the Swedish NODC",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sharksmhi/ctdvis",
    packages=setuptools.find_packages(),
    package_data={'ctdvis': [
        os.path.join('etc', '*.json'),
        os.path.join('etc', 'vis_setup', '*.json'),
    ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)
