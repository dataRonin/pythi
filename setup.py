#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="pythi",
    version="0.1.0",
    description="PYthon-based Time Harmonization and Interpolation",
    author="Fox Peterson",
    author_email="<fox@tinybike.net>",
    maintainer="Fox Peterson",
    maintainer_email="<fox@tinybike.net>",
    license="MIT",
    url="https://github.com/dataRonin/pythi",
    download_url = "https://github.com/dataRonin/pythi/tarball/0.1.0",
    packages=["pythi"],
    install_requires=["pymssql", "bottle"],
    keywords = ["glitch","pythi","time-series"]
)