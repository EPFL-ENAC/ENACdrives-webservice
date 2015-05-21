"""
This is a setup.py script generated by py2applet

Usage:
    python setup_osx.py py2app
"""

import utility
from setuptools import setup

APP = ["enacdrives.py"]
DATA_FILES = ["enacdrives.png", "mounted.png", "umounted.png", "bookmark_on.png", "bookmark_off.png", "warning.png"]
OPTIONS = {
    "argv_emulation": True,
    # "frameworks": ["libQtCore.4.dylib", "libQtGui.4.dylib"],
    "iconfile": "/Users/bancal/enacdrives_client/enacdrives.icns",
    "includes": ["sip", "PyQt4", "PyQt4.QtCore", "PyQt4.QtGui"],
    "qt_plugins": ["QtGui", "QtCore"]
}

setup(
    app=APP,
    version=utility.CONST.VERSION,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
