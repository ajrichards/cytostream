#!/usr/bin/env python
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import os,sys,time
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui
#import helpform
#import qrc_resources

sys.path.append("..")
from Controller import Controller
from BasicWidgets import *
from FileControls import *
from BulkNewProject import BulkNewProject
from OpenExistingProject import OpenExistingProject
from ScatterPlotter import ScatterPlotter
from FileSelector import FileSelector
#from ModelSelector import ModelSelector
from DataProcessingCenter import DataProcessingCenter
from DataProcessingDock import DataProcessingDock
from QualityAssuranceDock import QualityAssuranceDock
from ThumbnailViewer import ThumbnailViewer
from ModelCenter import ModelCenter
from ModelDock import ModelDock
from PipelineDock import PipelineDock
from ResultsNavigationDock import ResultsNavigationDock
#from ResultsNavigationCenter import ResultsNavigationCenter
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

__version__ = "0.1"

class MainWindow(QMainWindow):

    def __init__(self):

        ## construct and set main variables
        QtGui.QMainWindow.__init__(self)
        
        ## variables
        self.myWidth = 800
        self.myHeight = 600
        self.eSize = 50
        self.buff = 2.0
        self.controller = Controller()
        self.mainWidget = QtGui.QWidget(self)
        self.reset_view_workspace()
        self.stateList = ['Data Processing', 'Quality Assurance', 'Model', 'Results Navigation']
        self.modelList = ['dpmm-cpu','dpmm-gpu']
        
        self.move_to_initial()
        #self.add_pipeline_dock()
        self.printer = None

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        
        self.create_statusbar()
        self.create_menubar_toolbar()

        ## settings
        self.showMaximized()
        self.setWindowTitle(self.controller.appName)
        
    def reset_view_workspace(self):
        self.log = self.controller.log
        self.model = self.controller.model
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.dockWidget = None
        self.fileSelector = None
        #self.modelSelector = None


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
    
    def create_menubar_toolbar(self):
        fileNewBulkAction = self.create_action("New...", self.create_new_project_bulk,
                QKeySequence.New, "filenew", "Create a new project with mulitple files")
        fileOpenAction = self.create_action("&Open...", self.open_existing_project,
                QKeySequence.Open, "fileopen",
                "Open an existing project")
        fileSaveAction = self.create_action("&Save", self.fileSave,
                QKeySequence.Save, "filesave", "Save the image")
        fileSaveAsAction = self.create_action("Save &As...",
                self.fileSaveAs, icon="filesaveas",
                tip="Save the project using a new name")
        filePrintAction = self.create_action("&Print", self.filePrint,
                QKeySequence.Print, "fileprint", "Print the current image")
        fileQuitAction = self.create_action("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")
        editDataProcessing= self.create_action("&Data Processing", self.move_to_data_processing, 
                                              "Ctrl+D", "dataprocessing", "Move to Data Processing") 
        editQualityAssurance= self.create_action("Quality &Assurance", self.move_to_quality_assurance, 
                                              "Ctrl+A", "qualityassurance", "Move to Quality Assurance") 
        editModel= self.create_action("&Model", self.move_to_model, 
                                      "Ctrl+M", "model", "Move to Model") 
        editResultsNavigation = self.create_action("&Results Navigation", self.move_to_results_navigation, 
                                                   "Ctrl+R", "resultsnavigation", "Move to Results Navigation")

        helpAboutAction = self.create_action("&About %s"%self.controller.appName,
                self.helpAbout)
        helpHelpAction = self.create_action("&Help", self.helpHelp,
                QKeySequence.HelpContents)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewBulkAction,fileOpenAction,
                fileSaveAction, fileSaveAsAction, None,
                filePrintAction, fileQuitAction)
        self.addActions(self.fileMenu,self.fileMenuActions)

        editMenu = self.menuBar().addMenu("&Edit")
        
        mirrorMenu = editMenu.addMenu(QIcon(":/editmirror.png"),"&Go to")
        self.addActions(mirrorMenu, (editDataProcessing,editQualityAssurance, editModel, editResultsNavigation))
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpAboutAction, helpHelpAction))
        self.addActions(self.mainWidget,(editDataProcessing,
                                         editQualityAssurance,editModel,
                                         editResultsNavigation))
    def add_pipeline_dock(self):
        self.pipelineDock = QDockWidget(self)
        self.pipelineDock.setObjectName("PipelineDockWidget")
        self.pipelineDock.setAllowedAreas(Qt.TopDockWidgetArea|Qt.BottomDockWidgetArea)
        self.pipelineDock.setGeometry(self.eSize*7.0+self.buff, self.eSize+2.0+self.buff, self.eSize*7.0+self.buff, self.eSize+2.0+self.buff)
 
        self.pipelineDockWidget = QtGui.QWidget(self)
        self.pipelineDockWidget.setGeometry(self.eSize*7.0+self.buff, self.eSize+2.0+self.buff, self.eSize*7.0+self.buff, self.eSize+2.0+self.buff)
        self.pDock = PipelineDock(parent=self.pipelineDockWidget,eSize=self.eSize)
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
        self.addDockWidget(Qt.RightDockWidgetArea, self.pipelineDock)
        self.pipelineDock.setMinimumWidth(self.eSize*2)
        self.pipelineDock.setMaximumWidth(self.eSize*2)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)

        if icon is not None:
            if os.path.isfile(os.path.join(".","qtlib","images",icon+".png")) == False:
                print "WARNING: bad icon specified", icon + ".png"
            action.setIcon(QIcon(os.path.join("qtlib","images","%s.png"%icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_new_project(self):
        #QtGui.QMessageBox.information(self,self.controller.appName,"Load a FCS file")
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open FCS file')
        goFlag = self.controller.create_new_project(self.fileName,self)
        if goFlag == True:
            self.add_pipeline_dock()
            self.move_to_data_processing()

    def remove_project(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()

        reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                           "Are you sure you want to completely remove '%s'?"%projectID, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            homeDir = os.path.join("projects",projectID)
            self.controller.remove_project(homeDir)
            self.open_existing_project()
        else:
            pass

    def create_new_project_bulk(self):
        #QtGui.QMessageBox.information(self,self.controller.appName,"Use shift and cntl to select multiple FCS files")
        allFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open file(s)')
        firstFile = True
        goFlag = True
        for fileName in allFiles:
            fileName = str(fileName)
            if firstFile == True:
                self.controller.create_new_project(fileName,self)
                firstFile = False
            else:
                goFlag = self.controller.load_additional_fcs_files(fileName,self)

        if goFlag == True:
            self.move_to_data_processing()
        else:
            print "ERROR: not moving to data processing bad goflag"

    def open_existing_project(self):        
        if self.controller.projectID != None:
            reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                               "Are you sure you want to close the current project - '%s'?"%self.controller.projectID, 
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
            
        self.controller.reset_workspace()
        if self.dockWidget != None:
            self.clear_dock()

        self.mainWidget = QtGui.QWidget(self)
        projectList = get_project_names()
        self.existingProjectOpener = OpenExistingProject(projectList,parent=self.mainWidget,openBtnFn=self.open_existing_project_handler,
                                                         closeBtnFn=self.move_to_initial,rmBtnFn=self.remove_project)
        hbl = QtGui.QHBoxLayout(self.mainWidget)
        hbl.setAlignment(QtCore.Qt.AlignTop)
        hbl.addWidget(self.existingProjectOpener)
        self.refresh_main_widget()

    def open_existing_project_handler(self):
        existingProjects = get_project_names()
        projectID,projectInd = self.existingProjectOpener.get_selected_project()
        self.controller.initialize_project(projectID,loadExisting=True)
        self.reset_view_workspace()
        
        if self.log.log['currentState'] == 'Date Processing':
            self.add_pipeline_dock()
            self.move_to_data_processing()
        elif self.log.log['currentState'] == 'Quality Assurance':
            self.add_pipeline_dock()
            self.move_to_quality_assurance()
        elif self.log.log['currentState'] == 'Model':
            self.add_pipeline_dock()
            self.move_to_model()
        elif self.log.log['currentState'] == 'Results Navigation':
            self.add_pipeline_dock()
            self.move_to_results_navigation()
        else:
            self.move_to_initial()
            print 'hmmm... ', self.log.log['currentState']

        

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
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.image)

    def show_image(self, percent=None):
        if self.image.isNull():
            return
        
        image = self.image
        self.pngViewer.setPixmap(QPixmap.fromImage(image))

    def helpAbout(self):
        QMessageBox.about(self, "About %s"%self.controller.appName,
                """<b>%s</b> v %s
                <p>Copyright &copy; 2010 Duke University. 
                All rights reserved.
                <p>This application can be used to perform
                model based analysis of flow cytometry data.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (self.controller.appName,
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def show_model_log_info(self):
        self.set_selected_model(withRefresh=False)
        selectedModel, selectedModelIndex = self.fileSelector.get_selected_model()

        modelLogFile = self.log.read_model_log(selectedModel) 
        QMessageBox.about(self, "%s - Model Information"%self.controller.appName,
                          """<br><b>Project ID</b> - %s
                             <br><b>Model name</b> - %s
                             <br><b>Date time</b>  - %s
                             <br><b>Full  name</b> - %s
                             <br><b>File name</b>  - %s 
                             <br><b>Components</b> - %s
                             <br><b>Run time</b>   - %s"""%(modelLogFile['project id'],selectedModel,modelLogFile['timestamp'],
                                                     modelLogFile['full model name'],modelLogFile['file name'],
                                                     modelLogFile['number components'],modelLogFile['model runtime'])
                          )
    def helpHelp(self):
        self.display_info("The help is not yet implimented")
        #form = helpform.HelpForm("index.html", self)
        #form.show()

    ################################################################################################3
    def move_to_initial(self):
        if self.dockWidget != None:
            self.clear_dock()
      
        self.pngViewer = QLabel(self.mainWidget)
        self.pngViewer.setAlignment(Qt.AlignCenter)
        self.pngViewer.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.mainWidget = self.pngViewer
        self.refresh_main_widget()
        self.setCentralWidget(self.mainWidget)
        self.image = QImage("applications-science.png")
        self.show_image()

    def move_to_data_processing(self):
        if self.controller.homeDir == None:
            self.display_info('To begin either load an existing project or create a new one')
            return

        if self.dockWidget != None:
            self.clear_dock()

        self.log.log['currentState'] = "Data Processing"
        masterChannelList = self.model.get_master_channel_list()
        fileList = get_fcs_file_names(self.controller.homeDir)
        transformList = ['transform1', 'transform2', 'transform3']
        compensationList = ['compensation1', 'compensation2']
        self.mainWidget = QtGui.QWidget(self)
        dpc = DataProcessingCenter(fileList,masterChannelList,transformList,compensationList, parent=self.mainWidget)
        hbl = QtGui.QHBoxLayout(self.mainWidget)
        hbl.setAlignment(QtCore.Qt.AlignTop)
        hbl.addWidget(dpc)
        self.refresh_main_widget()
        self.add_dock()
        self.track_highest_state()
        self.controller.save()

    def move_to_quality_assurance(self,runNew=False):
        nextState = self.stateList.index('Quality Assurance')
        proceed = self.check_state_status(nextState)
        if proceed == False:
            return

        self.set_subsample()
        if self.dockWidget != None:
            self.clear_dock()
        self.mainWidget = QtGui.QWidget(self)
        self.log.log['currentState'] = "Quality Assurance"
        thumbDir = os.path.join(self.controller.homeDir,"figs",self.log.log['selectedFile'][:-4]+"_thumbs")

        if os.path.isdir(thumbDir) == True and len(os.listdir(thumbDir)) > 1:
            self.display_thumbnails()
        else:
            self.mainWidget = QtGui.QWidget(self)
            self.progressBar = ProgressBar(parent=self.mainWidget,buttonLabel="Create the figures")
            self.progressBar.set_callback(self.run_progress_bar)
            hbl = QtGui.QHBoxLayout(self.mainWidget)
            hbl.addWidget(self.progressBar)
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            
            self.refresh_main_widget()
            self.add_dock()
        
        self.track_highest_state()
        self.refresh_main_widget()
        self.add_dock()
        self.controller.save()

    def move_to_model(self):
        nextState = self.stateList.index('Model')
        proceed = self.check_state_status(nextState)
        if proceed == False:
            return

        if self.dockWidget != None:
            self.clear_dock()
        self.mainWidget = QtGui.QWidget(self)
        self.log.log['currentState'] = "Model"
        self.mc = ModelCenter(parent=self.mainWidget, runModelFn=self.run_progress_bar)
        hbl = QtGui.QHBoxLayout(self.mainWidget)
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mc)
        self.refresh_main_widget()
        self.add_dock()
        self.track_highest_state()
        self.controller.save()

    def move_to_results_navigation(self,runNew=False):
        nextState = self.stateList.index('Results Navigation')
        proceed = self.check_state_status(nextState)
        if proceed == False:
            return

        if self.dockWidget != None:
            self.clear_dock()

        fileList = get_fcs_file_names(self.controller.homeDir)
        self.log.log['currentState'] = "Results Navigation"
        self.clear_dock()
        self.display_thumbnails(runNew)
        self.add_dock()
        self.track_highest_state()
        self.controller.save()
        
    def generic_callback(self):
        print "this button/widget does not do anything yet"

    #################################################
    #
    # Dock functions
    #
    #################################################

    def add_dock(self):
        if self.dockWidget != None:
            self.clear_dock()

        if self.fileSelector != None and self.log.log['selectedFile'] == None:
            self.set_selected_file(withRefresh=False)

        masterChannelList = self.model.get_master_channel_list()
        fileList = get_fcs_file_names(self.controller.homeDir)
        transformList = ['transform1', 'transform2', 'transform3']
        compensationList = ['compensation1', 'compensation2']
        subsetList = ["1e3", "1e4","5e4","All Data"]

        self.mainDockWidget = QDockWidget(self.controller.projectID, self)
        self.mainDockWidget.setObjectName("MainDockWidget")
        self.mainDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)

        self.dockWidget = QtGui.QWidget(self)
        palette = self.dockWidget.palette()
        role = self.dockWidget.backgroundRole()
        palette.setColor(role, QtGui.QColor('black'))
        self.dockWidget.setPalette(palette)
        self.dockWidget.setAutoFillBackground(True)
        hbl2 = QtGui.QHBoxLayout()
        hbl2.setAlignment(QtCore.Qt.AlignTop)
       
        if self.log.log['currentState'] in ['Results Navigation']:
            showModelSelector = True
            modelsRun = get_models_run(self.controller.homeDir)
        else:
            showModelSelector = False
            modelsRun = None

        if self.log.log['currentState'] not in ['Model']:
            self.fileSelector = FileSelector(fileList,parent=self.dockWidget,selectionFn=self.set_selected_file,fileDefault=self.log.log['selectedFile'],
                                             showModelSelector=showModelSelector,modelsRun=modelsRun)
            self.fileSelector.setAutoFillBackground(True)
            hbl2.addWidget(self.fileSelector)

            subsamplingDefault = self.log.log['subsample']

        if self.log.log['currentState'] == "Data Processing":
            self.dock = DataProcessingDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=self.dockWidget,
                                           contBtnFn=lambda runNew=True: self.move_to_quality_assurance(runNew),subsetDefault=subsamplingDefault)
        elif self.log.log['currentState'] == "Quality Assurance":
            self.dock = QualityAssuranceDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=self.dockWidget,
                                             contBtnFn=self.move_to_model,subsetDefault=subsamplingDefault,viewAllFn=self.display_thumbnails)
        elif self.log.log['currentState'] == "Model":
            modelList = ['DPMM-CPU','DPMM-GPU']
            self.dock = ModelDock(modelList,parent=self.dockWidget,contBtnFn=self.move_to_results_navigation,componentsFn=self.set_num_components)
        elif self.log.log['currentState'] == "Results Navigation":
            self.dock = ResultsNavigationDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=self.dockWidget,
                                              contBtnFn=self.generic_callback,subsetDefault=subsamplingDefault,viewAllFn=self.display_thumbnails,
                                              infoBtnFn=self.show_model_log_info)
        self.dock.setAutoFillBackground(True)
        
        hbl1 = QtGui.QHBoxLayout()
        hbl1.setAlignment(QtCore.Qt.AlignBottom)
        hbl1.addWidget(self.dock)
        vbl = QtGui.QVBoxLayout(self.dockWidget)
        vbl.addLayout(hbl2)
        vbl.addLayout(hbl1)
        
        self.mainDockWidget.setWidget(self.dockWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.mainDockWidget)

    def clear_dock(self):
        self.removeDockWidget(self.mainDockWidget)

    #################################################
    #
    # Setters and handlers
    #
    #################################################

    def set_subsample(self):
        if self.log.log['currentState'] == "Data Processing":
            ss, ssInd = self.dock.get_subsample()
            self.log.log['subsample'] = ss
            self.controller.handle_subsampling()
            self.refresh_state()

    def set_num_components(self,value):
        diff = value % 8
        #print value, diff
        if diff == 0:
            newValue = value
        elif (value - diff) % 8 == 0:
            newValue = value - diff
        elif (value + diff) % 8 == 0:
            newValue = value + diff

        self.log.log['numComponents'] = newValue

    def set_model_to_run(self):
        sm, smInd = self.dock.get_selected_model()
        if sm == 'DPMM-CPU':
            self.log.log['modelToRun'] = 'dpmm-cpu'
        elif sm == 'DPMM-GPU':
            self.log.log['modelToRun'] = 'dpmm-gpu'
        else:
            print "ERROR: invalid selection for modelToRun"

    def track_highest_state(self):
        ## keep track of the highest state
        if self.stateList.__contains__(self.log.log['currentState']):
            if self.stateList.index(self.log.log['currentState']) > self.log.log['highestState']:
                self.log.log['highestState'] = self.stateList.index(self.log.log['currentState'])

    def run_progress_bar(self,runNew=False):
        mode = self.log.log['currentState']

        if self.controller.subsampleIndices == None:
            self.controller.handle_subsampling()

        fileList = get_fcs_file_names(self.controller.homeDir)
        if mode == 'Quality Assurance':
            self.controller.process_images('qa',progressBar=self.progressBar,view=self)
            self.display_thumbnails(runNew)
        if mode == 'Model':
            self.set_model_to_run()
            self.controller.run_selected_model(progressBar=self.mc.progressBar)
            self.clear_dock()
            self.mainWidget = QtGui.QWidget(self)
            self.progressBar = ProgressBar(parent=self.mainWidget,buttonLabel="Create the figures")
            self.progressBar.set_callback(self.create_results_thumbs)
            hbl = QtGui.QHBoxLayout(self.mainWidget)
            hbl.addWidget(self.progressBar)
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            
            self.refresh_main_widget()
            self.add_dock()

    def create_results_thumbs(self):
        self.controller.process_images('results',progressBar=self.progressBar,view=self)
        self.move_to_results_navigation(runNew=True)
 
    def display_thumbnails(self,runNew=False):
        mode = self.log.log['currentState']
        if mode == 'Quality Assurance':
            self.mainWidget = QtGui.QWidget(self)
            imgDir = os.path.join(self.controller.homeDir,"figs")
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 
            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
            tv = ThumbnailViewer(thumbDir,fileChannels,parent=self.mainWidget,viewScatterFn=self.handle_show_scatter)
            hbl = QtGui.QHBoxLayout()
            vbl = QtGui.QVBoxLayout()
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            hbl.addWidget(tv)
            vbl.setAlignment(QtCore.Qt.AlignTop)
            vbl.addLayout(hbl)
            self.refresh_main_widget()
            self.add_dock()
            QtCore.QCoreApplication.processEvents() # experimental

        elif mode == 'Results Navigation':
            if self.log.log['selectedModel'] == None or self.log.log['selectedModel'] == '':
                self.log.log['selectedModel'] = self.log.log['modelToRun']

            ## set basic variables 
            selectedModel = self.log.log['selectedModel']
            fileList = get_fcs_file_names(self.controller.homeDir)
            self.mainWidget = QtGui.QWidget(self)

            ## get the model name
            modelName = None
            for possibleModelUsed in self.modelList:
                print possibleModelUsed, selectedModel
                if re.search(possibleModelUsed,selectedModel):
                    modelName = possibleModelUsed

            ## get the file channels
            #fileUsed = re.sub("\_%s"%modelName,"",selectedModel)
            #fileUsed = re.sub("\_sub\d+","",fileUsed) + ".fcs"
            #fileChannels = self.model.get_file_channel_list(fileUsed) 
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 
            if modelName == None:
                print "ERROR: could not find model type used"

            if self.log.log['subsample'] == None or self.log.log['subsample'] == 'All Data':
                imgDir = os.path.join(self.controller.homeDir,'figs',modelName)
            else:
                imgDir = os.path.join(self.controller.homeDir,'figs',"sub%s_"%int(float(self.log.log['subsample']))+modelName)

            if os.path.isdir(imgDir) == False:
                print "ERROR: a bad imgDir has been specified"

            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
            tv = ThumbnailViewer(thumbDir,fileChannels,parent=self.mainWidget,viewScatterFn=self.handle_show_scatter)
            hbl = QtGui.QHBoxLayout(self.mainWidget)
            hbl.addWidget(tv)
            hbl.setAlignment(QtCore.Qt.AlignTop)
            self.refresh_main_widget()
            self.add_dock()
            QtCore.QCoreApplication.processEvents() # experimental

    def set_selected_file(self,withRefresh=True):
        selectedFile, selectedFileInd = self.fileSelector.get_selected_file() 
        self.log.log['selectedFile'] = selectedFile
        if withRefresh == True:
            self.refresh_state()
        
    def set_selected_model(self,withRefresh=True):
        try:
            selectedModel, selectedModleInd = self.fileSelector.get_selected_model()
            self.log.log['selectedModel'] = selectedModel
            if withRefresh == True:
                self.refresh_state()
        except:
            print 'no selected model available'

    def refresh_state(self):
        if self.log.log['currentState'] == "Data Processing":
            self.move_to_data_processing()
        elif self.log.log['currentState'] == "Quality Assurance":
            self.move_to_quality_assurance()
        elif self.log.log['currentState'] == "Model":
            self.move_to_model()
        elif self.log.log['currentState'] == "Results Navigation":
            self.move_to_results_navigation()

    def handle_show_scatter(self,img=None):
        mode = self.log.log['currentState']
        print 'handling show scatter',mode
        self.set_selected_file(withRefresh=False)
        
        if img != None:
            print img
            print self.log.log['selectedFile']
            channels = re.sub("%s\_|\_thumb.png"%re.sub("\.fcs","",self.log.log['selectedFile']),"",img)
            print channels
            chanI,chanJ = re.split("\_",channels)
        
        if mode == "Quality Assurance":
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)
            sp = ScatterPlotter(self.mainWidget,self.controller.projectID,self.log.log['selectedFile'],chanI,chanJ,subset=self.log.log['subsample'])
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
            self.clear_dock()
            self.refresh_main_widget()
            self.add_dock()
            QtCore.QCoreApplication.processEvents() # experimental
            
        elif mode == "Results Navigation":
            self.set_selected_model(withRefresh=False)
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)
            sp = ScatterPlotter(self.mainWidget,self.controller.projectID,self.log.log['selectedFile'],chanI,chanJ,subset=self.log.log['subsample'],
                                modelName=self.log.log['selectedModel'])
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
            self.clear_dock()
            self.refresh_main_widget()
            self.add_dock()
            QtCore.QCoreApplication.processEvents() # experimental

    def display_info(self,msg):
        reply = QtGui.QMessageBox.information(self, 'Information',msg)
    def display_warning(self,msg):
        reply = QtGui.QMessageBox.warning(self, "Warning", msg)

    # check state status
    # nextState is the int index of the next state
    # state counting begins at 0
    def check_state_status(self,nextState):
        if self.controller.projectID == None:
            self.display_info('To begin create a new project or open an existing one')
            return False
        elif self.log.log['currentState'] == 'initial' and nextState == 0:
            self.move_to_data_processing()
            return True
        elif self.stateList.__contains__(self.log.log['currentState']) == False: 
            self.display_info('User may not change stage at this time')
            print self.log.log['currentState'], nextState
            return False
        elif nextState > int(self.log.log['highestState']) + 1:
            print 'nextstate', nextState, int(self.log.log['highestState']) 
            self.display_info('User must follow the flow of the pipeline \n i.e. please do not skip steps')
            return False
        else:
            return True
    def refresh_main_widget(self):
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.activateWindow()
        self.mainWidget.update()
        self.show()
        #QtCore.QCoreApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Duke University")
    app.setOrganizationDomain("duke.edu")
    app.setApplicationName("cytostream")
    form = MainWindow()
    form.show()
    app.exec_()

main()
