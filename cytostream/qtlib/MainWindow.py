#!/usr/bin/env python
'''
  This program or module is free software: you can redistribute it and/or
  modify it under the terms of the GNU General Public License as published
  by the Free Software Foundation version 3 of the License, or 
  (at your option) any later version. It is provided for educational purposes 
  and is distributed in the hope that it will be useful, but WITHOUT ANY 
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

  Adam Richards
  adam.richards@stat.duke.edu
'''

__author__ = "A Richards"

import os,sys,time,re
import platform
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import PYQT_VERSION_STR, QT_VERSION_STR

if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'qtlib'))

from cytostream import Controller,SaveSubplots
from cytostream import get_project_names, get_fcs_file_names
from cytostream.qtlib import create_menubar_toolbar,move_transition
from cytostream.qtlib import Transitions
from cytostream.qtlib import add_left_dock, remove_left_dock, ProgressBar, PipelineDock, restore_docks
from cytostream.qtlib import ThumbnailViewer, NWayViewer
from cytostream.qtlib import moreInfoDict

__version__ = "0.9"

class MainWindow(QtGui.QMainWindow):

    def __init__(self,debug=False,projectID=None):
        '''
        constructor
        '''

        ## construct and set main variables
        QtGui.QMainWindow.__init__(self)

        ## variables
        self.buff = 2.0
        self.controller = Controller(debug=debug)
        self.mainWidget = QtGui.QWidget(self)
        self.reset_view_workspace()
        self.stateList = ['Initial','Data Processing','Quality Assurance','Model Run','Model Results',
                          'Analysis','Analysis Results','Reports']
        self.resultsModeList = ['modes','components']

        ## enable the transition class
        self.transitions = Transitions(self)
        self.transitions.move_to_initial()
        
        ## settings
        self.showMaximized()
        self.setWindowTitle(self.controller.appName)
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()
        self.eSize = 0.04 * self.screenWidth

        self.printer = None
        self.sizeLabel = QtGui.QLabel()
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.create_statusbar()
        create_menubar_toolbar(self)

        ## error check and use shortcut to open existing project if specified form cmd line
        if projectID != None:
            if os.path.isdir(projectID) == False:
                homeDir = os.path.join(self.controller.baseDir,"projects",projectID)
            else:
                homeDir = projectID
            if os.path.isdir(homeDir) == False:
                print "Controller: ERROR: home dir specified not found: fatal error"
                print "\t", homeDir
                sys.exit()
                if os.path.exists(os.path.join(homeDir,os.path.split(homeDir)[-1]+".log")) == False:
                    print "Controller: ERROR: home dir specified not a valid cytostream dir: fatal error"
                    print "\t", homeDir
                    sys.exit()
            self.open_existing_project_handler(homeDir)
       
    def reset_view_workspace(self):
        self.log = self.controller.log
        self.model = self.controller.model
        self.image = QtGui.QImage()
        self.dirty = False
        self.filename = None
        self.dockWidget = None
        self.fileSelector = None
        self.plotSelector = None
        self.plotTickControls = None
        self.channelSelector = None
        self.vizModeSelector = None
        self.subsampleSelector = None
        self.clusterSelector = None
        self.gateSelector = None
        self.saveImgsBtn = None
        self.dpc = None
        self.pDock = None
        self.dock = None
        self.tv = None
        self.nwv = None
        self.allFilePaths = []
        self.controller.masterChannelList = None
        self.reset_layout()

    def reset_layout(self):
        ''' 
        reset the main widget layouts
        '''
        
        self.vbl = QtGui.QVBoxLayout()
        self.vboxTop = QtGui.QVBoxLayout()
        self.vboxTop.setAlignment(QtCore.Qt.AlignTop)
        self.vboxCenter = QtGui.QVBoxLayout()
        self.vboxCenter.setAlignment(QtCore.Qt.AlignCenter)
        self.vboxBottom = QtGui.QVBoxLayout()
        self.vboxBottom.setAlignment(QtCore.Qt.AlignBottom)        
        self.vbl.addLayout(self.vboxTop)
        self.vbl.addLayout(self.vboxBottom)
        self.vbl.addLayout(self.vboxCenter)

    def create_statusbar(self):
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        self.status.addPermanentWidget(self.sizeLabel)
        self.status.showMessage("Ready", 5000)

    def restore_docks(self,override=False):
        '''
        a dummy function to restore the application docks
        '''
        restore_docks(self,override=override)

    def add_pipeline_dock(self,noBtns=False):
        
        ## prepare widget
        self.pipelineDock = QtGui.QDockWidget(self)
        self.pipelineDock.setObjectName("PipelineDockWidget")
        self.pipelineDock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea|QtCore.Qt.BottomDockWidgetArea)
 
        try:
            appColor = self.controller.log.log['app_color']
        except:
            appColor = '#999999'

        self.pipelineDockWidget = QtGui.QWidget(self)
        self.pDock = PipelineDock(self.controller.log, self.stateList,parent=self.pipelineDockWidget,eSize=0.07*self.screenWidth,mainWindow=self,
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
            self.transitions.move_to_open()
        else:
            pass

    def create_new_project(self):
        ## ask for project name
        projectID, ok = QtGui.QInputDialog.getText(self, 'Name designation', 'Enter the name of your new project:')
        projectID = re.sub("\s+","_",str(projectID))
        idValid = True

        if projectID == '':
            self.status.showMessage("New project creation aborted", 5000)
            return None

        defaultDir = self.controller.defaultDir
        projectDir = QtGui.QFileDialog.getExistingDirectory(self, 'Select a location to save your project', 
                                                            options=QtGui.QFileDialog.ShowDirsOnly, directory=defaultDir)
        projectID = re.sub("\s+","_",str(projectID))

        if projectDir == '':
            self.status.showMessage("New project creation aborted", 5000)
            return None
        
        projectDir = str(projectDir)

        if os.path.isdir(projectDir) == False:
            print "ERROR: MainWindow - specified project directory does not exist"
            self.status.showMessage("New project creation aborted", 5000)
            return None

        ## ensure project name is valid and not alreaedy used
        homeDir = os.path.join(projectDir,projectID)
        if os.path.isdir(homeDir) == True:
            idValid = False

        while idValid == False: 
            reply = QtGui.QMessageBox.question(self, 'Message', "A project named\n'%s'\nalready exists. Do you want to overwrite it?"%homeDir, 
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                idValid = True
                if self.controller.verbose == True:
                    print 'INFO: overwriting old project'
            else:
                self.status.showMessage("New project creation aborted", 5000)
                return None

        ## check to see if project creation was canceled
        if projectID == '':
            self.status.showMessage("New project creation aborted", 5000)
            return None

        if self.controller.verbose == True:
            print 'INFO: creating new project', projectID
        
        ## initialize and load project
        goFlag = self.controller.create_new_project(homeDir)
        if goFlag == True:
            self.transitions.move_to_data_processing()
            self.status.showMessage("New project successfully created", 5000)
        else:
            print "ERROR: create new project did not succeed"

    def open_existing_project(self):
        '''
        a reference function to move to the open screen

        '''
        
        if self.controller.verbose == True:
            print 'INFO: open existing project'
           
        self.transitions.move_to_open()
        self.status.showMessage("Existing project successfully loaded", 5000)

    def open_existing_project_handler(self,homeDir):
        '''
        from the open projects page open a selected project

        '''

        ## error check
        if homeDir == None:
            print "ERROR: mainWindow.open_existing_projects_handler - homeDir is None"
            return
        
        if os.path.isdir(homeDir) == False:
            print "ERROR: mainWindow.open_existing_projects_handler - homeDir does not exist"
            return
    
        projectID = os.path.split(homeDir)[-1]
        projectLog = os.path.join(homeDir,projectID+".log")
        if os.path.exists(projectLog) == False:
            print "ERROR: mainWindow.open_existing_projects_handler - homeDir not a cytostream project"
            self.display_warning("Specified project dir is not a valid cytostream project")
            return
    
        ## prepare variables and move
        print 'open existing project handler'        
        move_transition(self)
        print '...move transition made'
        self.reset_view_workspace()
        print '...reset workspace'
        self.controller.initialize_project(homeDir,loadExisting=True)
        print '...initializing controller'
        self.controller.masterChannelList = self.model.get_master_channel_list()
        print '...getting master channel list'
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


        if len(self.dpc.fileUploader.loadedFilePaths) > 0:
            compensationFilePath = self.dpc.fileUploader.loadedFilePaths[0]
            self.controller.compensationFilePath = compensationFilePath

        self.controller.load_files_handler(self.allFilePaths,progressBar=progressBar,view=self)
        self.allFilePaths = []
        move_transition(self)
        self.refresh_state()

    def fileSave(self):
        '''
        saves current state of software
        '''

        if self.controller.homeDir != None:
            self.controller.save()
        else:
            self.display_warning("Must open project first before saving")
            return None

        self.display_info("Progress saved")

    def fileSaveAs(self):
        self.display_info("This function is not yet implemented")

    def filePrint(self):
        self.display_info("This function is not yet implemented")
        #if self.image.isNull():
        #    return
        #if self.printer is None:
        #    self.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        #    self.printer.setPageSize(QtGui.QPrinter.Letter)
        #form = QtGui.QPrintDialog(self.printer, self)
        #if form.exec_():
        #    painter = QtGui.QPainter(self.printer)
        #    rect = painter.viewport()
        #    size = self.image.size()
        #    size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        #    painter.setViewport(rect.x(), rect.y(), size.width(),
        #                        size.height())
        #    painter.drawImage(0, 0, self.image)

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
        QtGui.QMessageBox.about(self, "%s - Model Information"%self.controller.appName,
                         """<br><b>Project ID</b> - %s
                             <br><b>Model name</b> - %s
                             <br><b>Date time</b>  - %s
                             <br><b>Full  name</b> - %s
                             <br><b>File name</b>  - %s 
                             <br><b>Components</b> - %s
                             <br><b>Modes</b>      - %s
                             <br><b>Run time</b>   - %s"""%(modelLogFile['project id'],selectedModel,modelLogFile['timestamp'],
                                                     modelLogFile['full model name'],modelLogFile['file name'],
                                                     modelLogFile['number components'], modelLogFile['number modes'],modelLogFile['model runtime'])
                          )

    def show_more_info(self):
        currentState = self.log.log['current_state']
        if moreInfoDict.has_key(currentState):
            msg = moreInfoDict[currentState]
        else:
            msg = """<br>Helpful information not yet present... %s"""%currentState   

        QtGui.QMessageBox.about(self, "%s - Information"%self.controller.appName,msg)
        
    def helpHelp(self):
        self.display_info("The help is not yet implimented")
        #form = helpform.HelpForm("index.html", self)
        #form.show()

    ################################################################################################3
    def generic_callback(self):
        print "this button/widget does not do anything yet"

    def set_num_components(self,value):
        diff = value % 16
        if diff == 0:
            newValue = value
        elif (value - diff) % 16 == 0:
            newValue = value - diff
        elif (value + diff) % 16 == 0:
            newValue = value + diff

        self.log.log['selected_k'] = newValue

    
    def handle_model_to_run_callback(self,item=None):
        '''
        handles the selection of model to run

        '''

        if item in ['dpmm']:
            self.log.log['model_to_run'] == item
        else:
            self.display_info("Selected model is not yet available")
            self.modelToRunSelector.set_checked('dpmm')

    def handle_model_mode_callback(self,item=None):
        '''
        handles the selection of model to run
        normal, onefit, pooled, target

        '''
        if item in ['normal']:
            self.log.log['model_mode'] == item
            self.log.log('file_in_focus','all')
        else:
            self.display_info("Selected model mode is not yet available")
            self.modelModeSelector.set_checked('normal')
            
    def handle_model_edit_return(self):
        '''
        handles the model edit return
        '''
        self.move_to_model_run(self,modelMode='progressbar')

    def handle_save_images_callback(self):

        if self.log.log['current_state'] == 'Quality Assurance':
            figMode = 'qa'
        else:
            figMode = 'analysis'

        validViews = ['plot']
        currentPlotView = str(self.controller.currentPlotView)

        if currentPlotView in validViews:
            defaultDir = os.path.join(self.controller.homeDir,'documents')
            fileFilter = "*.png;;*.jpg;;*.pdf"
            imgFileName, extension = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save As', directory=defaultDir, filter=fileFilter) 
            imgFileName = str(imgFileName)
            extension = str(extension)[1:]
            figName = re.sub(extension,"",imgFileName) + extension    
            numSubplots = int(re.sub('plot-','',currentPlotView))
            figTitle = None
            ss = SaveSubplots(self.controller.homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)
            print 'plot saved as ', figName
        else:
            print "WARNING: MainWindow.handle_save_images_callback - call to save from invalid mode",

    def update_highest_state(self):
        '''
        keep track of the highest state achieved in software
        '''

        ## keep track of the highest state
        if self.stateList.__contains__(self.controller.log.log['current_state']):
            if self.stateList.index(self.controller.log.log['current_state']) > int(self.controller.log.log['highest_state']):
                self.controller.log.log['highest_state'] = self.stateList.index(self.controller.log.log['current_state'])
                self.controller.save()
    
    def run_file_aligner(self):
        '''
        handles the running of the file aligner
        '''

        print 'this is where we run the file aligner'


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
            self.qac.progressBar.button.setText('Please wait...')
            self.qac.progressBar.button.setEnabled(False)
            self.fileSelector.setEnabled(False)
            self.subsampleSelector.setEnabled(False)
            self.channelSelector.setEnabled(False)
            self.moreInfoBtn.setEnabled(False)
            QtCore.QCoreApplication.processEvents()
            self.controller.process_images('qa',progressBar=self.qac.progressBar,view=self)
            self.display_thumbnails()
        elif mode == 'Model Run':
            self.mc.set_disable()
            QtCore.QCoreApplication.processEvents()
            if  self.controller.log.log['model_to_run'] in ['dpmm-mcmc']:
                self.controller.run_selected_model_cpu(progressBar=self.mc.progressBar,view=self)
            else:
                self.controller.run_selected_model_cpu(progressBar=self.mc.progressBar,view=self)
        else:
            print "ERROR: got unexpected mode for MainWindow.run_progress_bar",mode

    def on_model_run_finish(self):
        '''
        after completion of model run automatically creatue figures
        '''

        self.transitions.move_to_model_run()
        self.mc.set_disable()
        QtCore.QCoreApplication.processEvents()
        self.mc.widgetSubtitle.setText("Creating figures...")
        self.mc.progressBar.progressLabel.setText("Creating figures...")
        subsample = self.controller.log.log['subsample_analysis']
        modelRunID = 'run' + str(self.log.log['models_run_count'])
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('analysis',modelRunID=modelRunID,progressBar=self.mc.progressBar,view=self)
        self.transitions.move_to_model_results(mode='menu')

    def recreate_figures(self):
        '''
        call back from state transtions to enable thumbnail figure recreation
        '''
        
        if self.log.log['current_state'] == 'Quality Assurance':
            self.transitions.move_to_quality_assurance(mode='progressbar')
        elif self.log.log['current_state'] == 'Model Results':
            self.transitions.move_to_model_results()
            #self.on_model_run_finish()

    def plots_enable_disable(self,mode='thumbnails'):
        '''
        enables and disables widgets for thumbnail and plot view modes

        '''

        ## docks check
        if self.dockWidget == None:
            add_left_dock(self)
        if self.pDock == None:
            self.add_pipeline_dock()

        if mode == 'thumbnails':
            if self.fileSelector:
                self.fileSelector.setEnabled(True)
            if self.plotSelector:
                self.plotSelector.setEnabled(False)
            if self.channelSelector:
                self.channelSelector.setEnabled(False)
            if self.plotTickControls:
                self.plotTickControls.setEnabled(False)
            if self.vizModeSelector:
                self.vizModeSelector.setEnabled(True)
                self.vizModeSelector.set_checked(mode)
            if self.subsampleSelector:
                self.subsampleSelector.setEnabled(False)
            if self.clusterSelector:
                self.clusterSelector.setEnabled(False)
            if self.gateSelector:
                self.gsScrollArea.setEnabled(False)
                self.gateSelector.setEnabled(False)

        elif mode == 'plot':
            if self.log.log['current_state'] == 'Quality Assurance':
                self.pDock.enable_continue_btn(self.transitions.move_to_model_run)
                self.plotTickControls.labelsCB.setEnabled(False)
            else:
                self.plotTickControls.labelsCB.setEnabled(True)
            
            if self.fileSelector:
                self.fileSelector.setEnabled(True)
            if self.plotSelector:
                self.plotSelector.setEnabled(True)
            if self.channelSelector:
                self.channelSelector.setEnabled(True)
            if self.plotTickControls:
                self.plotTickControls.setEnabled(True)
            if self.vizModeSelector:
                self.vizModeSelector.setEnabled(True)
                self.vizModeSelector.set_checked(mode)
            if self.subsampleSelector:
                self.subsampleSelector.setEnabled(True)
            if self.clusterSelector:
                self.clusterSelector.setEnabled(True)
            if self.gateSelector:
                self.gsScrollArea.setEnabled(True)
                self.gateSelector.setEnabled(True)          

            if self.saveImgsBtn and self.controller.log.log['num_subplots'] != '1':
                self.saveImgsBtn.setEnabled(True)

            self.pDock.contBtn.setEnabled(True)
            self.pDock.enable_disable_states()

    def display_thumbnails(self,runNew=False,forceMode=None):
        ''' 
        displays thumbnail images for quality assurance or results navigation states
        '''

        ## enable/disable
        if forceMode != None:
            mode = forceMode
        else:
            mode = self.log.log['current_state']

        ## setup layout
        self.reset_layout()
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        
        ## adjust the selected file
        fileList = get_fcs_file_names(self.controller.homeDir)
        if type(self.log.log['excluded_files']) == type([]) and len(self.log.log['excluded_files']) > 0:
            for f in self.log.log['excluded_files']:
                fileList.remove(f)
                
        self.log.log['selected_file'] == re.sub("\.txt|\.fcs","",fileList[0])

        if mode == 'Quality Assurance':
            excludedChannels = self.log.log['excluded_channels_qa']
            self.mainWidget = QtGui.QWidget(self)
            imgDir = os.path.join(self.controller.homeDir,"figs")
            fileChannels = self.log.log['alternate_channel_labels']
            channelsToView = np.array(fileChannels)[list(set(range(len(fileChannels))).difference(set(excludedChannels)))].tolist()
            thumbDir = os.path.join(imgDir,'qa',self.log.log['selected_file']+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,self.controller.channelDict,mainWindow=self)
        elif mode == 'Model Results':
            excludedChannels = self.log.log['excluded_channels_analysis']
            self.mainWidget = QtGui.QWidget(self)
            fileChannels = self.log.log['alternate_channel_labels']
            imgDir = os.path.join(self.controller.homeDir,'figs',self.log.log['selected_model'])
            
            if os.path.isdir(imgDir) == False:
                print "ERROR: MainWindow.display_thumbnails -- a bad imgDir has been specified", imgDir

            thumbDir = os.path.join(imgDir,self.log.log['selected_file']+"_thumbs")
            channelsToView = np.array(fileChannels)[list(set(range(len(fileChannels))).difference(set(excludedChannels)))].tolist()
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,channelsToView,self.controller.channelDict,mainWindow=self)
        else:
            print "ERROR: bad mode specified in display thumbnails", mode
            return

        ## for either mode
        self.plots_enable_disable(mode='thumbnails')
        self.tvScrollarea = QtGui.QScrollArea()
        self.tvScrollarea.setWidget(self.tv)
        self.tvScrollarea.setAlignment(QtCore.Qt.AlignCenter)

        #hbl.addWidget(self.tv)
        hbl.addWidget(self.tvScrollarea)
        self.vboxCenter.addLayout(hbl)
        self.mainWidget.setLayout(self.vbl)
        self.refresh_main_widget()
        
        ## disable buttons
        if self.dock != None:
            self.dock.disable_all()

        QtCore.QCoreApplication.processEvents()
        return True

    def models_run_btn_callback(self):
        '''
        Left dock button callback to return to Results Nav. menu
        '''

        self.transitions.move_to_model_results()

    def set_selected_file(self):
        '''
        set the selected file
        '''
    
        selectedFile = self.fileSelector.get_selected_file() 
        self.log.log['selected_file'] = re.sub("\.txt|\.fcs","",selectedFile)
        self.controller.save()

    def get_master_channel_list(self):
        ''' 
        returns the master channels list
        '''

        if self.controller.masterChannelList == None or len(self.controller.masterChannelList) == 0:
            self.controller.masterChannelList = self.model.get_master_channel_list()
        return self.controller.masterChannelList


    def refresh_state(self,withProgressBar=False,qaMode='thumbnails'):
        '''
        given the current state return to normal widget view
        '''

        if self.controller.log.log['current_state'] == "Data Processing":
            self.transitions.move_to_data_processing(withProgressBar=withProgressBar)
        elif self.controller.log.log['current_state'] == "Quality Assurance":
            self.transitions.move_to_quality_assurance(mode=qaMode)
        elif self.controller.log.log['current_state'] == "Model Run":
            self.transitions.move_to_model_run()
        elif self.controller.log.log['current_state'] == "Model Results":
            self.transitions.move_to_model_results()
        elif self.controller.log.log['current_state'] == "Analysis":
            self.transitions.move_to_analysis(self)
        elif self.controller.log.log['current_state'] == "Sample Aligner":
            self.transitions.move_to_sample_aligner(self)
        elif self.controller.log.log['current_state'] == "Basic Subsets":
            self.transitions.move_to_basic_subsets(self)
        elif self.controller.log.log['current_state'] == "Positivity":
            self.transitions.move_to_positivity(self)
        elif self.controller.log.log['current_state'] == "Analysis Results":
            self.transitions.move_to_analysis_results(self)
        elif self.controller.log.log['current_state'] == "Reports":
            self.transitions.move_to_reports(self)
        elif self.controller.log.log['current_state'] == "Initial":
            self.transitions.move_to_initial(self)
        else:
            print "ERROR: MainWindow.refresh_state was given invalid state", self.log.log['current_state']

        QtCore.QCoreApplication.processEvents()

    def handle_show_plot(self,img=None,gating=False):
        '''
        main handle to show a plot
        '''

        self.transitions.begin_wait()
        mode = self.log.log['current_state']
        self.set_selected_file()
        
        ## handle transition from thumbnails to plot view
        if img != None:
            self.log.log['num_subplots'] = 1
            self.vizModeSelector.update_num_subplots(1)
            chanInds = re.findall("\d+\_\d+\_thumb",img)
            i,j,k = chanInds[0].split("_")
            i,j = int(i),int(j)

            self.controller.log.log['plots_to_view_channels'][0] = (i,j)
            self.controller.log.log['plots_to_view_files'][0] = self.controller.fileNameList.index(self.log.log['selected_file'])
            self.controller.save()

        ## initialize transition
        fileChannels = self.log.log['alternate_channel_labels']
        self.reset_layout()
        self.mainWidget = QtGui.QWidget(self)

        ## set the model runs to view to be currently selected model
        self.log.log['plots_to_view_runs'] = [self.log.log['selected_model'] for i in self.log.log['plots_to_view_runs']]
        self.controller.save()

        ## mode specific variables for NWayViewer
        if self.log.log['current_state'] == "Quality Assurance":
            figMode = 'qa'
        elif self.log.log['current_state'] == "Model Results":
            figMode = 'model results'
        else:
            print "ERROR: MainWindow --- unspecified state"

        self.nwv = NWayViewer(self.controller,self.log.log['plots_to_view_channels'],self.log.log['plots_to_view_files'],
                         self.log.log['plots_to_view_runs'],self.log.log['plots_to_view_highlights'],
                         self.log.log['num_subplots'],figMode=figMode,background=True,modelType='components',
                         useScaled=self.log.log['use_scaled_plots'],parent=self,mainWindow=self,gating=gating)
        
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.nwv)

        ## enable/disable
        self.plots_enable_disable(mode='plot')

        ## finalize layout
        self.vboxCenter.addLayout(hbl)
        self.mainWidget.setLayout(self.vbl)
        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()
        self.transitions.end_wait()

    def display_info(self,msg):
        '''
        display info
        generic function to display info to user
        '''
        reply = QtGui.QMessageBox.information(self,'Information',msg)

    def display_warning(self,msg):
        '''
        display warning
        generic function to display a warning to user
        '''
        reply = QtGui.QMessageBox.warning(self, "Warning", msg)

    def refresh_main_widget(self):
        '''
        main function to reset main widget
        '''

        self.setCentralWidget(self.mainWidget)
        self.mainWidget.activateWindow()
        self.mainWidget.update()
        self.show()
