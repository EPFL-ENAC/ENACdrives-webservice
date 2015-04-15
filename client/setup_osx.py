"""
This is a setup.py script generated by py2applet

Usage:
    python setup_osx.py py2app
"""

from setuptools import setup

APP = ["mount_filers.py"]
DATA_FILES = ["mount_filers.png"]
OPTIONS = {
    "argv_emulation": True,
    # "frameworks": ["libQtCore.4.dylib", "libQtGui.4.dylib"],
    "iconfile": "/Users/bancal/mount_filers_client/mount_filers.icns",
    "includes": ["sip", "PyQt4", "PyQt4.QtCore", "PyQt4.QtGui"],
    "qt_plugins": ["QtGui", "QtCore"]
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)