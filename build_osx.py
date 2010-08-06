#!/usr/local/bin
"""
setup.py - script for building MyApplication
Usage:
% sudo /usr/local/bin/python setup.py py2app
"""
from setuptools import setup
import os, sys, shutil

## checking the system
if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Couchapp requires Python 2.5 or later.")


# remember to add sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.6', 'lib-dynload')] + sys.path
# to dist/yourApplication.app/Contents/Resources/__boot__.py
BASEDIR=os.path.join("/","Library","Frameworks","Python.framework","Versions","2.6","lib","python2.6","site-packages")
MYPYTHON=os.path.join("/","Users","adamrichards","MyPython")
CYTODIR=os.path.join("/","Users","adamrichards","research","cytostream","cytostream")
VERSION = '0.1'
DESCRIPTION = 'A graphical user interface to carry out analyses of flow cytometry data.'

print os.path.isdir(os.path.join(CYTODIR,'qtlib'))

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
        version=VERSION,
        description=DESCRIPTION,
        author='Adam Richards',
        author_email='adam.richards@stat.duke.edu',
        license='GPLv3',
        app=['Main.py'],
        setup_requires=['py2app'],
        options=dict(py2app=dict(
                includes=['os','sys','time','re','PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'numpy',
                          'cytostream','fcm','fcm.statistics', 'matplotlib','matplotlib.cm',
                          'matplotlib.figure','enthought.traits','enthought.traits.api',
                          'matplotlib.backends.backend_qt4agg'],
                packages=[os.path.join(CYTODIR,'qtlib','images')],
                resources=[os.path.join(MYPYTHON,'fcm'),
                           os.path.join(CYTODIR,'qtlib','BasicWidgets.py'),
                           os.path.join(CYTODIR,'qtlib','BulkNewProject.py'),
                           os.path.join(CYTODIR,'qtlib','OpenExistingProject.py'),
                           os.path.join(CYTODIR,'qtlib','ScatterPlotter.py'),
                           os.path.join(CYTODIR,'qtlib','FileSelector.py'),
                           os.path.join(CYTODIR,'qtlib','DataProcessingCenter.py'),
                           os.path.join(CYTODIR,'qtlib','DataProcessingDock.py'),
                           os.path.join(CYTODIR,'qtlib','QualityAssuranceDock.py'),
                           os.path.join(CYTODIR,'qtlib','ThumbnailViewer.py'),
                           os.path.join(CYTODIR,'qtlib','ModelCenter.py'),
                           os.path.join(CYTODIR,'qtlib','ModelDock.py'),
                           os.path.join(CYTODIR,'qtlib','PipelineDock.py'),
                           os.path.join(CYTODIR,'qtlib','BlankPage.py'),
                           os.path.join(CYTODIR,'qtlib','ResultsNavigationDock.py'),
                           os.path.join(CYTODIR,'qtlib','MainWindow.py'),
                           os.path.join(CYTODIR,'RunMakeFigures.py'),
                           os.path.join(CYTODIR,'RunDPM-CPU.py'),
                           os.path.join(CYTODIR,'RunDPM-GPU.py'),
                           os.path.join(CYTODIR,'applications-science.png'),
                           os.path.join(CYTODIR,'qtlib','images','filenew.png')],
                excludes=['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql',
                          'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
            ))
    )

#setup(
#    app=["Main.py"],
#    setup_requires=["py2app"],
#)
