#!/usr/local/bin
"""
setup.py - script for building MyApplication
Usage:
% sudo /usr/local/bin/python setup.py py2app
"""
from setuptools import setup
import os, sys, shutil,re

## checking the system
if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Couchapp requires Python 2.5 or later.")


# remember to add sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.6', 'lib-dynload')] + sys.path
# to dist/yourApplication.app/Contents/Resources/__boot__.py
APPNAME="Cytostream"
BASEDIR=os.path.join("/","Library","Frameworks","Python.framework","Versions","2.6","lib","python2.6","site-packages")
MYPYTHON=os.path.join("/","Users","adamrichards","MyPython")
CYTODIR=os.path.join("/","Users","adamrichards","research","cytostream","cytostream")
LOCALLIB=os.path.join("/","usr","local","lib")
VERSION = '0.1'
OSXVERSION = "10.6"
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
        name=APPNAME,
        version=VERSION,
        description=DESCRIPTION,
        author='Adam Richards',
        author_email='adam.richards@stat.duke.edu',
        license='GPLv3',
        app=['Main.py'],
        setup_requires=['py2app'],
        options=dict(py2app=dict(
            includes=['os','sys','time','re','PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'numpy',
                      'cytostream','fcm','fcm.statistics', 'matplotlib','matplotlib.cm','PIL',
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
                
            plist=dict(
                CFBundleName               = APPNAME,
                CFBundleShortVersionString = VERSION,     # must be in X.X.X format
                CFBundleGetInfoString      = APPNAME + " " + VERSION,
                CFBundleExecutable         = APPNAME,
                #CFBundleIdentifier         = "com.example.myappname",
                ),


            ))
    )


## print complete
print '\nbuild complete.'

## create a file that tells the os to use the bundled Qt
print "\ncreating qt config file..."
fid = open(os.path.join(".","dist","Cytostream.app","Contents","Resources","qt.conf"),'w')
fid.write("[Paths]\nPlugins = plugin")
fid.close()

## edit __boot__.py
print "\nediting __boot__.py.."
origFile = os.path.join(".","dist","Cytostream.app","Contents","Resources","__boot__.py")
newFile = os.path.join(".","dist","Cytostream.app","Contents","Resources","temp.py")
ofile = open(origFile,'r')
nfile = open(newFile,'w')
nfile.write("import sys,os"+"\n")
nfile.write("sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.6', 'lib-dynload')] + sys.path\n\n")

for linja in ofile:
    nfile.write(linja)
ofile.close()
nfile.close()
os.system("mv %s %s"%(newFile,origFile))


## shared libs
print "\ncopying dylibs (shared libs) that are not bundled automatically..."
#os.system("cp %s %s"%(os.path.join(LOCALLIB,"libfreetype.dylib"),os.path.join(".","dist","Cytostream.app","Contents","Resources","lib","python2.6","lib-dynload")))
#os.system("cp %s %s"%(os.path.join(LOCALLIB,"libgcc_s.1.dylib"),os.path.join(".","dist","Cytostream.app","Contents","Resources","lib","python2.6","lib-dynload")))
#os.system("cp %s %s"%(os.path.join(LOCALLIB,"libpng.dylib"),os.path.join(".","dist","Cytostream.app","Contents","Resources","lib","python2.6","lib-dynload")))
#os.system("cp %s %s"%(os.path.join(LOCALLIB,'*.dylib',os.path.join(".","dist","Cytostream.app","Contents","Resources","lib","python2.6","lib-dynload")))
#os.system("cp %s %s"%(os.path.join(LOCALLIB,'*.dylib'),os.path.join(".","dist","Cytostream.app","Contents","Frameworks")))


## building dmg
print "\ncreating disk img..."
imgName = "Cytostream%s_OSX%s.dmg"%(re.sub("\.","-",VERSION),re.sub("\.","-",OSXVERSION))
if os.path.isfile(imgName):
    os.remove(imgName)
os.system("hdiutil create -srcfolder dist/Cytostream.app %s"%imgName )
print "process complete."
