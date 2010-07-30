#!/usr/local/bin
"""
setup.py - script for building MyApplication
Usage:
% sudo /usr/local/bin/python setup.py py2app
"""
from setuptools import setup
import os, sys, shutil

# remember to add sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.6', 'lib-dynload')] + sys.path
# to dist/yourApplication.app/Contents/Resources/__boot__.py
BASEDIR=os.path.join("/","Library","Frameworks","Python.framework","Versions","2.6","lib","python2.6","site-packages")


## remove build directories
print 'Deleting old build dirs...'
if os.path.isdir(os.path.join(".","build")):
    shutil.rmtree('./build')
if os.path.isdir(os.path.join(".","dist")):
    shutil.rmtree('./dist')

## build application
print 'Building app...'
if os.name == 'posix':
    setup(
        name='Cytostream',
        version='0.1',
        description='your fancy descripton',
        author='Adam Richards',
        author_email='adam.richards@stat.duke.edu',
        license='GPLv3',
        app=['cytostream.py'],
        setup_requires=['py2app'],
        options=dict(py2app=dict(
                includes=['PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'numpy', 'enthought.traits', 'enthought.traits.api',
                          'qtlib.MainWindow'],
                packages=[],
                resources=[], #os.path.join(BASEDIR,'qtlib')
                excludes=['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon']
            ))
    )

#setup(
#    app=["Main.py"],
#    setup_requires=["py2app"],
#)
