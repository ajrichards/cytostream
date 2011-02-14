#!/usr/bin/env python

'''
  This program or module is free software: you can redistribute it and/or
  modify it under the terms of the GNU General Public License as published
  by the Free Software Foundation, either version 2 of the License, or
  version 3 of the License, or (at your option) any later version. It is
  provided for educational purposes and is distributed in the hope that
  it will be useful, but WITHOUT ANY WARRANTY; without even the implied
  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
  the GNU General Public License for more details.

  Adam Richards
  adam.richards@stat.duke.edu
'''

import os,sys,time,re
import platform
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
#import helpform
#import qrc_resources

if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'qtlib'))

from cytostream import Controller
from cytostream import get_project_names, get_fcs_file_names
from cytostream.qtlib import create_menubar_toolbar, move_to_initial, move_to_data_processing, move_to_open
from cytostream.qtlib import move_to_quality_assurance, move_transition
from cytostream.qtlib import add_left_dock, remove_left_dock, ProgressBar, PipelineDock, BlankPage
from cytostream.qtlib import ThumbnailViewer, MultiplePlotter
#from BlankPage import BlankPage
#from PipelineDock import PipelineDock
#from Controller import Controller
#from MenuFunctions import *#
#from LeftDock import *
#from FileControls import *
#from StateTransitions import *
#from ThumbnailViewer import ThumbnailViewer
#from ScatterPlotter import ScatterPlotter
##from ReadFileThreader import ReadFileThreader

__version__ = "0.2"

class MainWindow(QtGui.QMainWindow):

    def __init__(self):

        ## construct and set main variables
        QtGui.QMainWindow.__init__(self)
        
        ## variables
        self.buff = 2.0
        self.controller = Controller()
        self.mainWidget = QtGui.QWidget(self)
        self.reset_view_workspace()
        self.stateList = ['Initial','Data Processing', 'Quality Assurance', 'Model', 'Results Navigation','Summary and Reports']
        self.possibleModels = ['dpmm']
        self.resultsModeList = ['modes','components']
        
        move_to_initial(self)
        self.printer = None
        self.sizeLabel = QtGui.QLabel()
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.create_statusbar()
        create_menubar_toolbar(self)

        ## settings
        self.showMaximized()
        self.setWindowTitle(self.controller.appName)
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()
        self.eSize = 0.04 * self.screenWidth
            
    def reset_view_workspace(self):
        self.log = self.controller.log
        self.model = self.controller.model
        self.image = QtGui.QImage()
        self.dirty = False
        self.filename = None
        self.dockWidget = None
        self.fileSelector = None
        self.pDock = None        
        self.dock = None
        self.tv = None
        self.lastChanI = None
        self.lastChanJ = None
        self.allFilePaths = []

    #################################################
    #
    # Statusbar
    #
    #################################################
    
    def create_statusbar(self):
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

    #################################################
    #
    # menubar and toolbar
    #
    #################################################
    
    def add_pipeline_dock(self,noBtns=False):
        self.pipelineDock = QtGui.QDockWidget(self)
        self.pipelineDock.setObjectName("PipelineDockWidget")
        self.pipelineDock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea|QtCore.Qt.BottomDockWidgetArea)
 
        try:
            appColor = self.controller.log.log['app_color']
        except:
            appColor = '#999999'

        self.pipelineDockWidget = QtGui.QWidget(self)
        btnCallBacks = [lambda a=self:move_to_data_processing(a), 
                        lambda a=self:move_to_quality_assurance(a), 
                        lambda a=self:move_to_model(a), 
                        lambda a=self:move_to_results_navigation(a), 
                        lambda a=self:move_to_results_summary(a)]
        self.pDock = PipelineDock(self.controller.log, self.stateList,parent=self.pipelineDockWidget,eSize=0.07*self.screenWidth,btnCallBacks=btnCallBacks,
                                  appColor=appColor,noBtns=noBtns)
        palette = self.pipelineDockWidget.palette()
        role = self.pipelineDockWidget.backgroundRole()
        palette.setColor(role, QtGui.QColor('black'))
        self.pipelineDockWidget.setPalette(palette)
        self.pipelineDockWidget.setAutoFillBackground(True)
        hbl1 = QtGui.QHBoxLayout()
        hbl1.setAlignment(QtCore.Qt.AlignCenter)
        hbl1.addWidget(self.pipelineDock)
        vbl = QtGui.QVBoxLayout(self.pipelineDockWidget)
        vbl.addLayout(hbl1)
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        
        self.pipelineDock.setWidget(self.pDock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.pipelineDock)
        self.pipelineDock.setMinimumWidth(0.08 * self.screenWidth)
        self.pipelineDock.setMaximumWidth(0.08 * self.screenWidth)

    def remove_project(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()

        reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                           "Are you sure you want to completely remove '%s'?"%projectID, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            homeDir = os.path.join(self.controller.baseDir,"projects",projectID)
            self.controller.remove_project(homeDir)
            move_to_open(self)
        else:
            pass

    def create_new_project(self):
        ## ask for project name
        projectID, ok = QtGui.QInputDialog.getText(self, self.controller.appName, 'Enter the name of your new project:')
        projectID = re.sub("\s+","_",str(projectID))
        idValid = True

        ## ensure project name is valid and not already used
        existingProjects = get_project_names(self.controller.baseDir)
        if projectID in existingProjects:
            idValid = False
        
        while idValid == False: 
            reply = QtGui.QMessageBox.question(self, 'Message', "A project named '%s' already exists. \nDo you want to overwrite it?"%projectID, 
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                idValid = True
                print 'overwriting anyway'
            else:
                projectID, ok = QtGui.QInputDialog.getText(self, self.controller.appName, 'Enter another project name:')
                projectID = re.sub("\s+","_",str(projectID))
                if projectID not in existingProjects:
                    idValid = True

        ## check to see if project creation was canceled
        if projectID == '':
            return None

        if self.controller.verbose == True:
            print 'INFO: creating new project', projectID
        
        ## initialize and load project
        self.controller.initialize_project(projectID)
        self.controller.create_new_project(projectID)
        move_to_data_processing(self)
        
    def open_existing_project(self):
        '''
        a reference function to move to the open screen
        '''
        move_to_open(self)

    def open_existing_project_handler(self):
        '''
        from the open projects page open a selected project
        '''
        selectedProject = self.existingProjectOpener.selectedProject 
        if selectedProject == None:
            print "ERROR: mainWindow.open_existing_projects_handler - selected project is none"
            return
        else:
            projectID = selectedProject

        ## remove old docks
        remove_left_dock(self)
        self.removeDockWidget(self.pDock)

        self.controller.initialize_project(projectID,loadExisting=True)
        self.reset_view_workspace()
        
        move_transition(self)
        self.refresh_state()
        
    def load_files_with_progressbar(self,progressBar):
        '''
        callback for loading files from data processing

        '''

        ## error check
        if type(self.allFilePaths) != type([]):
            print "ERROR: MainWindow -- load_files_with_progressbar -- bad input type"
        if len(self.allFilePaths) < 1:
            print "WARNING: MainWindow -- load_files_with_progressbar -- allFilePaths is empty"

        self.controller.load_files_handler(self.allFilePaths,progressBar=progressBar)
        self.allFilePaths = []
        move_transition(self)
        self.refresh_state()

    def fileSave(self):
        if self.controller.homeDir != None:
            self.controller.save()
        else:
            self.display_warning("Must open project first before saving")

    def fileSaveAs(self):
        self.display_info("This function is not yet implimented")

    def filePrint(self):
        if self.image.isNull():
            return
        if self.printer is None:
            self.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            self.printer.setPageSize(QtGui.QPrinter.Letter)
        form = QtGui.QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.image)

    def show_image(self, percent=None):
        if self.image.isNull():
            return
        
        image = self.image
        self.pngViewer.setPixmap(QtGui.QPixmap.fromImage(image))

    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About %s"%self.controller.appName,
                """<b>%s</b> v %s
                <p>Copyright &copy; 2010 Duke University. 
                All rights reserved.
                <p>This application can be used to perform
                model based analysis of flow cytometry data.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (self.controller.appName,
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def show_model_log_info(self):
        self.set_selected_model()

        selectedModel, selectedModelIndex = self.fileSelector.get_selected_model()
        fullModelName = re.sub("\.fcs|\.pickle","",self.log.log['selected_file']) + "_" + selectedModel

        print "suppose to show model log file.................."
        #QtGui.QMessageBox.about(self, "%s - Model Information"%self.controller.appName,
        #                  """<br><b>Project ID</b> - %s
        #                     <br><b>Model name</b> - %s
        #                     <br><b>Date time</b>  - %s
        #                     <br><b>Full  name</b> - %s
        #                     <br><b>File name</b>  - %s 
        #                     <br><b>Components</b> - %s
        #                     <br><b>Modes</b>      - %s
        #                     <br><b>Run time</b>   - %s"""%(modelLogFile['project id'],selectedModel,modelLogFile['timestamp'],
        #                                             modelLogFile['full model name'],modelLogFile['file name'],
        #                                             modelLogFile['number components'], modelLogFile['number modes'],modelLogFile['model runtime'])
        #                  )
    def helpHelp(self):
        self.display_info("The help is not yet implimented")
        #form = helpform.HelpForm("index.html", self)
        #form.show()

    ################################################################################################3

    #def move_transition(self):
    #    self.mainWidget = QtGui.QWidget(self)
    #    bp = BlankPage(parent=self.mainWidget)
    #    self.bp = BlankPage(parent=self.mainWidget)
    #    vbl = QtGui.QVBoxLayout()
    #    vbl.setAlignment(QtCore.Qt.AlignCenter)
    #    hbl = QtGui.QHBoxLayout()
    #    hbl.setAlignment(QtCore.Qt.AlignCenter)
    #    hbl.addWidget(bp)
    #    vbl.addLayout(hbl)
    #    self.mainWidget.setLayout(vbl)
    #    self.refresh_main_widget()
    #    #QtCore.QCoreApplication.processEvents()

    def generic_callback(self):
        print "this button/widget does not do anything yet"


    #################################################
    #
    # Setters and handlers
    #
    #################################################

    def set_subsample(self):
        if self.log.log['current_state'] == "Data Processing":
            ss, ssInd = self.dock1.get_subsample()

            # if changed remove old thumbs
            if ss != self.log.log['subsample_qa']:
                imgDir = os.path.join(self.controller.homeDir,"figs")
                for img in os.listdir(imgDir):
                    if re.search("\.png",img):
                        os.remove(os.path.join(imgDir,img))
                    elif re.search("\_thumbs",img) and os.path.isdir(os.path.join(imgDir,img)):
                        for thumb in os.listdir(os.path.join(imgDir,img)):
                            if re.search("\.png",thumb):
                                os.remove(os.path.join(imgDir,img,thumb))
                        os.rmdir(os.path.join(imgDir,img))

            self.log.log['subsample_qa'] = ss
            goFlag = self.controller.handle_subsampling()
            
            if goFlag == True:
                return True
            else:
                return False
    

    def set_excluded_files_channels(self):
        print "debug setting excluded file channels"
        #if type(self.log.log['checksArray']) != type(np.array([])):
        #    print "ERROR cannot set excluded files or channels bad checksArray"
        #
        #excludedFiles = []
        #excludedChannels = []
        #masterChannelList = self.model.get_master_channel_list()
        #fileList = get_fcs_file_names(self.controller.homeDir)
        #sumCols = self.log.log['checksArray'].sum(axis=0)
        #sumRows = self.log.log['checksArray'].sum(axis=1)
        #excludedChannels =  np.array(masterChannelList)[[int(i) for i in np.where(sumCols == 0)[0]]]
        #excludedFiles =  np.array(fileList)[[int(i) for i in np.where(sumRows == 0)[0]]]
        #
        #self.log.log['excludedChannels'] = excludedChannels.tolist()
        #self.log.log['excludedFiles'] = excludedFiles.tolist()
        #
        #if self.controller.verbose == True:
        #    print 'setting excluding channels', excludedChannels
        #    print 'setting excluding files', excludedFiles

        ## adjust the selected file
        #fileList = get_fcs_file_names(self.controller.homeDir)
        #if type(self.log.log['excludedFiles']) == type([]) and len(self.log.log['excludedFiles']) > 0:
        #    for f in self.log.log['excludedFiles']:
        #        fileList.remove(f)
        #    self.log.log['selectedFile'] == fileList[0]

    def set_num_components(self,value):
        diff = value % 8
        if diff == 0:
            newValue = value
        elif (value - diff) % 8 == 0:
            newValue = value - diff
        elif (value + diff) % 8 == 0:
            newValue = value + diff

        self.log.log['selected_k'] = newValue

    def set_model_to_run(self):
        #sm, smInd = self.dock.get_model_to_run()
        #if sm == 'DPMM':
        #    self.log.log['model_to_run'] = 'dpmm'
        #elif sm == 'K-means':
        #    self.log.log['model_to_run'] = 'kmeans'
        #else:
        #    print "ERROR: invalid selection for modelToRun"
        print 'INFO: need to setup model to run'
        self.log.log['model_to_run'] = 'dpmm'


    def update_highest_state(self):
        '''
        keep track of the highest state achieved in software

        '''

        ## keep track of the highest state
        if self.stateList.__contains__(self.log.log['current_state']):
            if self.stateList.index(self.log.log['current_state']) > int(self.log.log['highest_state']):
                self.log.log['highest_state'] = self.stateList.index(self.log.log['current_state'])
                self.controller.save()

    def run_progress_bar(self):
        mode = self.log.log['current_state']
        
        ## handle subsampling
        if self.log.log['current_state'] == 'Quality Assurance':
            subsample = self.log.log['subsample_qa']
        else:
            subsample = self.log.log['subsample_analysis']

        self.controller.handle_subsampling(subsample)

        fileList = get_fcs_file_names(self.controller.homeDir)
        if mode == 'Quality Assurance':
            self.controller.process_images('qa',progressBar=self.qac.progressBar,view=self)
            self.display_thumbnails()
        if mode == 'Model':
            self.set_model_to_run()
            self.controller.run_selected_model(progressBar=self.mc.progressBar,view=self)
            remove_left_dock(self)
            self.mainWidget = QtGui.QWidget(self)
            self.progressBar = ProgressBar(parent=self.mainWidget,buttonLabel="Create the figures")
            self.progressBar.set_callback(self.create_results_thumbs)
            hbl = QtGui.QHBoxLayout(self.mainWidget)
            hbl.addWidget(self.progressBar)
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            self.refresh_main_widget()
            add_left_dock(self)

    def create_results_thumbs(self):
        self.controller.process_images('results',progressBar=self.progressBar,view=self)
        move_to_results_navigation(self,runNew=True)
 
    def display_thumbnails(self,runNew=False):
        mode = self.log.log['current_state']
        hbl = QtGui.QHBoxLayout()
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        
        ## adjust the selected file
        fileList = get_fcs_file_names(self.controller.homeDir)
        if type(self.log.log['excluded_files']) == type([]) and len(self.log.log['excluded_files']) > 0:
            for f in self.log.log['excluded_files']:
                fileList.remove(f)
                
        self.log.log['selected_file'] == re.sub("\.txt|\.fcs","",fileList[0])

        if mode == 'Quality Assurance':
            self.mainWidget = QtGui.QWidget(self)
            imgDir = os.path.join(self.controller.homeDir,"figs")
            fileChannels = self.model.get_file_channel_list(self.log.log['selected_file']) 
            thumbDir = os.path.join(imgDir,'qa',self.log.log['selected_file']+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
            
        elif mode == 'Results Navigation':
            ## error checking
            modelsRun = get_models_run(self.controller.homeDir,self.possibleModels)
            if len(modelsRun) == 0:
                self.display_info("No models have been run yet -- so results cannot be viewed")
                return False

            self.log.log['selected_model'] = modelsRun[0] 

            if self.log.log['selected_model'] not in modelsRun:
                print "ERROR selected model not in models run"

            ## thumbs viewer
            self.mainWidget = QtGui.QWidget(self)
            fileChannels = self.model.get_file_channel_list(self.log.log['selected_file']) 

            if self.log.log['subsample_analysis'] == 'original':
                imgDir = os.path.join(self.controller.homeDir,'figs',self.log.log['selected_model'])
            else:
                subset = str(int(float(self.log.log['subsample_analysis'])))
                imgDir = os.path.join(self.controller.homeDir,'figs',"sub%s_%s"%(subset,self.log.log['selected_model']))
            
            if os.path.isdir(imgDir) == False:
                print "ERROR: a bad imgDir has been specified", imgDir

            thumbDir = os.path.join(imgDir,self.log.log['selected_file']+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
        
        else:
            print "ERROR: bad mode specified in display thumbnails"

        ## for either mode
        hbl.addWidget(self.tv)
        vbl.addLayout(hbl)
        self.mainWidget.setLayout(vbl)
        self.refresh_main_widget()
        
        if self.dock != None:
            ## disable buttons
            self.dock.disable_all()

        QtCore.QCoreApplication.processEvents()
        return True

    def set_selected_results_mode(self):
        print "setting selected results mode"
        #selectedMode = self.dock.get_results_mode()
        #self.log.log['results_mode'] = selectedMode
        #self.handle_show_scatter(img=None)

    def set_selected_file(self):
        '''
        set the selecte file
        '''

        selectedFile, selectedFileInd = self.fileSelector.get_selected_file() 
        self.log.log['selected_file'] = re.sub("\.txt|\.fcs","",selectedFile)
        self.controller.save()

    def set_selected_subsample(self):
        '''
        set the selected subsample

        '''

        selectedSubset, selectedSubsetInd = self.subsetSelector.get_selected_subset() 
        if selectedSubset == 'All Data':
            selectedSubset = 'original'


        if self.log.log['current_state'] == 'Data Processing':
            self.log.log['subsample_qa'] = selectedSubset
        if self.log.log['current_state'] == 'Model':
            self.log.log['subsample_analysis'] = selectedSubset
            
        self.controller.save()

    def set_selected_model(self):
        print 'setting selected model'
        #selectedModel, selectedModleInd = self.fileSelector.get_selected_model()
        #self.log.log['selected_model'] = selectedModel

    def refresh_state(self):
        print 'refreshing state', self.log.log['current_state']
        if self.log.log['current_state'] == "Data Processing":
            move_to_data_processing(self)
        elif self.log.log['current_state'] == "Quality Assurance":
            move_to_quality_assurance(self)
        elif self.log.log['current_state'] == "Model":
            move_to_model(self)
        elif self.log.log['current_state'] == "Results Navigation":
            move_to_results_navigation(self)
        elif self.log.log['current_state'] == "Results Summary":
            move_to_results_summary(self)

        QtCore.QCoreApplication.processEvents()

    def handle_show_scatter(self,img=None):
        mode = self.log.log['current_state']
        self.set_selected_file()
        
        ## layout and widget setup
        self.mainWidget = QtGui.QWidget(self)
        bp = BlankPage(parent=self.mainWidget)
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(bp)
        vbl.addLayout(hbl)
        self.mainWidget.setLayout(vbl)
        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()

        if img != None:
            channels = re.sub("%s\_|\_thumb.png"%re.sub("\.fcs","",self.log.log['selected_file']),"",img)
            channels = re.split("\_",channels)
            chanI = channels[-2]
            chanJ = channels[-1]
            self.lastChanI = chanI
            self.lastChanJ = chanJ
            
        if self.lastChanI == None or self.lastChanJ == None:
            print "ERROR: lastChanI or lastChanJ not defined"
            return False

        if mode == "Quality Assurance":
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)
            subsample=self.log.log['subsample_qa']
            modelType=None
            masterChannelList = self.model.get_master_channel_list()
            channelI = masterChannelList.index(self.lastChanI)
            channelJ = masterChannelList.index(self.lastChanJ)
            mp = MultiplePlotter(self.controller.homeDir,self.log.log['selected_file'],channelI,channelJ,subsample,background=True,
                                 modelType=modelType,mode='qa')
            vbl.addWidget(mp)

        elif mode == "Results Navigation":
            self.set_selected_model()
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)

            if self.log.log['subsample_analysis'] == 'original':
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selected_file']) + "_" + self.log.log['selected_model']
            else:
                subset = str(int(float(self.log.log['subsample'])))
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selected_file']) + "_" + "sub%s_%s"%(subset,self.log.log['selectedModel'])

            sp = ScatterPlotter(self.controller.homeDir,self.log.log['selected_file'],self.lastChanI,self.lastChanJ,subset=self.log.log['subsample'],
                                modelName=modelName,modelType=self.log.log['results_mode'],parent=self.mainWidget)
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
        
            ## enable buttons
            self.dock.enable_all()

        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()

    def display_info(self,msg):
        '''
        display info
        generic function to display info to user
        '''
        reply = QtGui.QMessageBox.information(self, 'Information',msg)

    def display_warning(self,msg):
        '''
        display warning
        generic function to display a warning to user
        '''
        reply = QtGui.QMessageBox.warning(self, "Warning", msg)

    def refresh_main_widget(self):
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.activateWindow()
        self.mainWidget.update()
        self.show()
        #QtCore.QCoreApplication.processEvents()
