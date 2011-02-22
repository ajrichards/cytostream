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
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import PYQT_VERSION_STR, QT_VERSION_STR

if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'qtlib'))

from cytostream import Controller
from cytostream import get_project_names, get_fcs_file_names
from cytostream.qtlib import create_menubar_toolbar, move_to_initial, move_to_data_processing, move_to_open
from cytostream.qtlib import move_to_quality_assurance, move_transition, move_to_one_dim_viewer
from cytostream.qtlib import move_to_model, move_to_results_navigation
from cytostream.qtlib import add_left_dock, remove_left_dock, ProgressBar, PipelineDock
from cytostream.qtlib import ThumbnailViewer, MultiplePlotter, TwoWayViewer,ThreeWayViewer,FourWayViewer
from cytostream.qtlib import SixWayViewer

__version__ = "0.2"

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        '''
        constructor

        '''

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

    #################################################
    #
    # Statusbar
    #
    #################################################
    
    def create_statusbar(self):
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        self.status.addPermanentWidget(self.sizeLabel)
        self.status.showMessage("Ready", 5000)

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
                if self.controller.verbose == True:
                    print 'INFO: overwriting old project'
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
        goFlag = False
        self.controller.initialize_project(projectID)
        goFlag = self.controller.create_new_project(projectID)
        if goFlag == True:
            move_to_data_processing(self)
        else:
            print "ERROR: create new project did not succeed"

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
        self.removeDockWidget(self.pipelineDock)

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
    def generic_callback(self):
        print "this button/widget does not do anything yet"

    #################################################
    #
    # setters and handlers
    #
    #################################################

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

        print 'handeling model mode callback'
    
    def handle_visualization_modes(self,item=None):
        '''
        handles the switching between visualization modes for qa and results

        '''

        modeList = ['histogram','thumbnails','plot-1','plot-2','plot-3','plot-4','plot-6']
        
        if item == 'histogram':
            move_to_one_dim_viewer(self)
        elif item == 'thumbnails' and self.log.log['current_state'] == 'Quality Assurance':
            move_to_quality_assurance(self,mode='thumbnails')
        elif item == 'thumbnails' and self.log.log['current_state'] == 'Results Navigaiton':
            print 'should be moving to results navigation thumbs'
        elif item == 'plot-1':
            self.handle_show_scatter()
        elif item == 'plot-2':
            self.handle_nway_viewer(item)
        elif item == 'plot-3':
            self.handle_nway_viewer(item)
        elif item == 'plot-4':
            self.handle_nway_viewer(item)
        elif item == 'plot-6':
            self.handle_nway_viewer(item)
        else:
            self.display_info("not available yet")

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
        
        ## save selected variables
        self.set_selected_file()                                                                                                                          
        self.set_selected_subsample()   

        ## handle subsampling
        if self.log.log['current_state'] == 'Quality Assurance':
            subsample = self.log.log['subsample_qa']
        else:
            subsample = self.log.log['subsample_analysis']

        print 'running for subsample', subsample

        self.controller.handle_subsampling(subsample)

        fileList = get_fcs_file_names(self.controller.homeDir)
        if mode == 'Quality Assurance':
            self.controller.process_images('qa',progressBar=self.qac.progressBar,view=self)
            self.display_thumbnails()
        if mode == 'Model':
            self.set_model_to_run()
            self.controller.run_selected_model(progressBar=self.mc.progressBar,view=self)
            #remove_left_dock(self)
            #self.mainWidget = QtGui.QWidget(self)
            #self.progressBar = ProgressBar(parent=self.mainWidget,buttonLabel="Create the figures")
            #self.progressBar.set_callback(self.create_results_thumbs)
            #add_left_dock(self)
            #hbl = QtGui.QHBoxLayout()
            #hbl.setAlignment(QtCore.Qt.AlignCenter)
            #hbl.addWidget(self.progressBar)
            #self.vboxCenter.addLayout(hbl)
            #self.mainWidget.setLayout(self.vbl)
            #self.refresh_main_widget()

    def create_results_thumbs(self):
        self.controller.process_images('results',progressBar=self.progressBar,view=self)
        move_to_results_navigation(self,runNew=True)
 
    def recreate_figures(self):
        '''
        call back from state transtions to enable thumbnail figure recreation

        '''
        
        print 'should be recreating figures'

        if self.log.log['current_state'] == 'Quality Assurance':
            move_to_quality_assurance(self,mode='progressbar')
        elif self.log.log['current_state'] == 'Results Navigation':
            print 'should be moving to results navigation progress bar'

    def plots_enable_disable(self,mode='thumbnails'):
        '''
        enables and disables widgets for thumbnail view mode

        '''

        if self.dockWidget == None:
            add_left_dock(self)

        if self.pDock == None:
            self.add_pipeline_dock()

        self.subsampleSelector.setEnabled(False)
        self.fileSelector.setEnabled(True)
        self.recreateBtn.setEnabled(True)
        self.modeSelector.setEnabled(True)
        self.connect(self.recreateBtn,QtCore.SIGNAL('clicked()'),self.recreate_figures)
        self.modeSelector.set_checked(mode)
        
        if self.log.log['current_state'] == 'Quality Assurance':
            self.pDock.enable_continue_btn(lambda a=self: move_to_model(a))
        
    def display_thumbnails(self,runNew=False):
        ''' 
        displays thumbnail images for quality assurance or results navigation states

        '''

        ## enable/disable
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
                subsample = str(int(float(self.log.log['subsample_analysis'])))
                imgDir = os.path.join(self.controller.homeDir,'figs',"sub%s_%s"%(subsample,self.log.log['selected_model']))
            
            if os.path.isdir(imgDir) == False:
                print "ERROR: a bad imgDir has been specified", imgDir

            thumbDir = os.path.join(imgDir,self.log.log['selected_file']+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
        
        else:
            print "ERROR: bad mode specified in display thumbnails"

        ## ensure docks are present
        if self.dockWidget != None:
            add_left_dock(self)
        if self.pDock == None:
            self.add_pipeline_dock()

        ## for either mode
        self.plots_enable_disable(mode='thumbnails')
        hbl.addWidget(self.tv)
        self.vboxCenter.addLayout(hbl)
        self.mainWidget.setLayout(self.vbl)
        self.refresh_main_widget()
        
        ## disable buttons
        if self.dock != None:
            self.dock.disable_all()

        QtCore.QCoreApplication.processEvents()
        return True

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

        selectedSubsample, selectedSubsampleInd = self.subsampleSelector.get_selected_subsample() 
        if selectedSubsample == 'All Data':
            selectedSubsample = 'original'

        print 'setting selected subsample...', selectedSubsample, self.log.log['current_state']

        if self.log.log['current_state'] == 'Quality Assurance':
            self.log.log['subsample_qa'] = selectedSubsample
        if self.log.log['current_state'] == 'Model':
            self.log.log['subsample_analysis'] = selectedSubsample
            
        self.controller.save()

    def refresh_state(self,withProgressBar=False,qaMode='thumbnails'):
        '''
        given the current state return to normal widget view

        '''

        print 'refreshing state', self.log.log['current_state']
        if self.log.log['current_state'] == "Data Processing":
            move_to_data_processing(self,withProgressBar=withProgressBar)
        elif self.log.log['current_state'] == "Quality Assurance":
            move_to_quality_assurance(self,mode=qaMode)
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
        
        ## layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        move_transition(self,repaint=True)
        self.reset_layout()

        if img != None:
            channels = re.sub("%s\_|\_thumb.png"%re.sub("\.fcs|\.txt","",self.log.log['selected_file']),"",img)
            channels = re.split("\_",channels)
            chanI = channels[-2]
            chanJ = channels[-1]
            self.lastChanI = chanI
            self.lastChanJ = chanJ
        elif self.lastChanI == None or self.lastChanJ == None:
            masterChannelList = self.model.get_master_channel_list()
            self.lastChanI = masterChannelList[0]
            self.lastChanJ = masterChannelList[1]

        if self.lastChanI == None or self.lastChanJ == None:
            print "ERROR: lastChanI or lastChanJ not defined"
            return False

        if mode == "Quality Assurance":
            self.mainWidget = QtGui.QWidget(self)
            subsample=self.log.log['subsample_qa']
            modelType=None
            masterChannelList = self.model.get_master_channel_list()
            channelI = masterChannelList.index(self.lastChanI)
            channelJ = masterChannelList.index(self.lastChanJ)
            mp = MultiplePlotter(self.controller.homeDir,self.log.log['selected_file'],channelI,channelJ,subsample,background=True,
                                 modelType=modelType,mode='qa')
            hbl.addWidget(mp)

        elif mode == "Results Navigation":
            print 'should be handling results nav scatter'
            #self.set_selected_model()
            #self.mainWidget = QtGui.QWidget(self)
            #
            #if self.log.log['subsample_analysis'] == 'original':
            #    modelName = re.sub("\.pickle|\.fcs","",self.log.log['selected_file']) + "_" + self.log.log['selected_model']
            #else:
            #    subset = str(int(float(self.log.log['subsample'])))
            #    modelName = re.sub("\.pickle|\.fcs","",self.log.log['selected_file']) + "_" + "sub%s_%s"%(subset,self.log.log['selectedModel'])
            #
            #sp = ScatterPlotter(self.controller.homeDir,self.log.log['selected_file'],self.lastChanI,self.lastChanJ,subset=self.log.log['subsample'],
            #                    modelName=modelName,modelType=self.log.log['results_mode'],parent=self.mainWidget)
            #ntb = NavigationToolbar(sp, self.mainWidget)
            #vbl.addWidget(sp)
            #vbl.addWidget(ntb)
        
            ## enable buttons
            #self.dock.enable_all()

        ## enable/disable
        self.plots_enable_disable(mode='plot-1') 

        ## finalize layout
        self.vboxCenter.addLayout(hbl)
        self.mainWidget.setLayout(self.vbl)
        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()

    def handle_nway_viewer(self,viewMode):
        mode = self.log.log['current_state']
        self.set_selected_file()
        
        ## layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        move_transition(self,repaint=True)
        self.reset_layout()

        plotsToView = self.log.log['plots_to_view']
        chans1 = [plt[0] for plt in plotsToView]
        chans2 = [plt[1] for plt in plotsToView]

        if mode == "Quality Assurance":
            mode = 'qa'
            subsample=self.log.log['subsample_qa']
            modelType,modelName= None,None
        if mode == "ReultsNavigation":
            mode = 'results'
            subsample=self.log.log['subsample_qa']
            modelType,modelName= None,None

        self.mainWidget = QtGui.QWidget(self)
        masterChannelList = self.model.get_master_channel_list()
        if viewMode == 'plot-2':
           nwv = TwoWayViewer(self.controller.homeDir,self.log.log['selected_file'],chans1,chans2,subsample,background=True,
                              modelType=modelType,mode=mode,modelName=modelName)
        elif viewMode == 'plot-3':
            nwv = ThreeWayViewer(self.controller.homeDir,self.log.log['selected_file'],chans1,chans2,subsample,background=True,
                                 modelType=modelType,mode=mode,modelName=modelName)
        elif viewMode == 'plot-4':
            nwv = FourWayViewer(self.controller.homeDir,self.log.log['selected_file'],chans1,chans2,subsample,background=True,
                                 modelType=modelType,mode=mode,modelName=modelName)
        elif viewMode == 'plot-6':
            nwv = SixWayViewer(self.controller.homeDir,self.log.log['selected_file'],chans1,chans2,subsample,background=True,
                                 modelType=modelType,mode=mode,modelName=modelName)
        hbl.addWidget(nwv)

        ## enable/disable
        self.plots_enable_disable(mode=viewMode) 

        ## finalize layout
        self.vboxCenter.addLayout(hbl)
        self.mainWidget.setLayout(self.vbl)
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
