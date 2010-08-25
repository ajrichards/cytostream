#!/usr/bin/env python
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
# Adam Richards
# adam.richards@stat.duke.edu
#

import os,sys,time,re
import platform
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4 import QtCore
from PyQt4 import QtGui
#import helpform
#import qrc_resources

sys.path.append("..")
from cytostream import *


from StageTransitions import *

__version__ = "0.1"

class MainWindow(QtGui.QMainWindow):

    def __init__(self):

        ## construct and set main variables
        QtGui.QMainWindow.__init__(self)
        
        ## variables
        self.buff = 2.0
        self.controller = Controller()
        self.mainWidget = QtGui.QWidget(self)
        self.reset_view_workspace()
        self.stateList = ['Data Processing', 'Quality Assurance', 'Model', 'Results Navigation','Summary and Reports']
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
    
    def add_pipeline_dock(self):
        self.pipelineDock = QtGui.QDockWidget(self)
        self.pipelineDock.setObjectName("PipelineDockWidget")
        self.pipelineDock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea|QtCore.Qt.BottomDockWidgetArea)
 
        self.pipelineDockWidget = QtGui.QWidget(self)
        btnCallBacks = [lambda a=self:move_to_data_processing(a), 
                        lambda a=self:move_to_quality_assurance(a), 
                        lambda a=self:move_to_model(a), 
                        lambda a=self:move_to_results_navigation(a), 
                        lambda a=self:move_to_results_summary(a)]
        self.pDock = PipelineDock(parent=self.pipelineDockWidget,eSize=self.eSize,btnCallBacks=btnCallBacks)
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
        self.pipelineDock.setMinimumWidth(0.10 * self.screenWidth)
        self.pipelineDock.setMaximumWidth(0.10 * self.screenWidth)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QtGui.QAction(text, self)

        if icon is not None:
            pathPass = False
            if os.path.isfile(os.path.join(self.controller.baseDir,"qtlib","images",icon+".png")) == True:
                action.setIcon(QtGui.QIcon(os.path.join(self.controller.baseDir,"qtlib","images","%s.png"%icon)))
                pathPass = True
            elif os.path.isfile(os.path.join(self.controller.baseDir,"lib","python2.6","images",icon+".png")) == True:
                action.setIcon(QtGui.QIcon(os.path.join(self.controller.baseDir,"lib", "python2.6","images","%s.png"%icon)))
                pathPass = True

            if pathPass == False:
                print "WARNING: bad icon specified", icon + ".png"
            
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def remove_project(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()

        reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                           "Are you sure you want to completely remove '%s'?"%projectID, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            homeDir = os.path.join(self.controller.baseDir,"projects",projectID)
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

        if self.controller.homeDir == None:
            return

        if goFlag == True:
            if self.model.homeDir == None:
                self.model.initialize(self.controller.projectID,self.controller.homeDir) 
                fileList = get_fcs_file_names(self.controller.homeDir)
                if len(fileList) > 0:
                    self.controller.log.log['selectedFile'] = fileList[0]
                self.controller.log.initialize(self.controller.projectID,self.controller.homeDir)
                self.log = self.controller.log

            if self.controller.homeDir != None:
                self.add_pipeline_dock()
                self.pDock.set_btn_highlight('data processing')
                move_to_data_processing(self)
   
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
            remove_left_dock(self)

        closeBtnFn = lambda a=self: move_to_initial(a)
        self.mainWidget = QtGui.QWidget(self)
        projectList = get_project_names(self.controller.baseDir)
        self.existingProjectOpener = OpenExistingProject(projectList,parent=self.mainWidget,openBtnFn=self.open_existing_project_handler,
                                                         closeBtnFn=closeBtnFn,rmBtnFn=self.remove_project)
        hbl = QtGui.QHBoxLayout(self.mainWidget)
        hbl.setAlignment(QtCore.Qt.AlignTop)
        hbl.addWidget(self.existingProjectOpener)
        self.refresh_main_widget()

    def open_existing_project_handler(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()
        self.controller.initialize_project(projectID,loadExisting=True)
        self.reset_view_workspace()
        self.add_pipeline_dock()
        self.refresh_state()
        self.refresh_state()  # done twice to force correct visualation in pipeline
        
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
        fullModelName = re.sub("\.fcs|\.pickle","",self.log.log['selectedFile']) + "_" + selectedModel

        modelLogFile = self.log.read_model_log(fullModelName) 
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
    def helpHelp(self):
        self.display_info("The help is not yet implimented")
        #form = helpform.HelpForm("index.html", self)
        #form.show()

    ################################################################################################3

    def move_transition(self):
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
        
    def generic_callback(self):
        print "this button/widget does not do anything yet"


    #################################################
    #
    # Setters and handlers
    #
    #################################################

    def set_subsample(self):
        if self.log.log['currentState'] == "Data Processing":
            ss, ssInd = self.dock1.get_subsample()

            # if changed remove old thumbs
            if ss != self.log.log['subsample']:
                imgDir = os.path.join(self.controller.homeDir,"figs")
                for img in os.listdir(imgDir):
                    if re.search("\.png",img):
                        os.remove(os.path.join(imgDir,img))
                    elif re.search("\_thumbs",img) and os.path.isdir(os.path.join(imgDir,img)):
                        for thumb in os.listdir(os.path.join(imgDir,img)):
                            if re.search("\.png",thumb):
                                os.remove(os.path.join(imgDir,img,thumb))
                        os.rmdir(os.path.join(imgDir,img))

            self.log.log['subsample'] = ss
            goFlag = self.controller.handle_subsampling()
            
            if goFlag == True:
                return True
            else:
                return False
            
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
        sm, smInd = self.dock.get_model_to_run()
        if sm == 'DPMM':
            self.log.log['modelToRun'] = 'dpmm'
        elif sm == 'K-means':
            self.log.log['modelToRun'] = 'kmeans'
        else:
            print "ERROR: invalid selection for modelToRun"

    def track_highest_state(self):
        ## keep track of the highest state
        if self.stateList.__contains__(self.log.log['currentState']):
            if self.stateList.index(self.log.log['currentState']) > self.log.log['highestState']:
                self.log.log['highestState'] = self.stateList.index(self.log.log['currentState'])

    def run_progress_bar(self):
        mode = self.log.log['currentState']

        self.set_widgets_enabled(False)

        if self.controller.subsampleIndices == None:
            self.controller.handle_subsampling()

        fileList = get_fcs_file_names(self.controller.homeDir)
        if mode == 'Quality Assurance':
            self.controller.process_images('qa',progressBar=self.progressBar,view=self)
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
        mode = self.log.log['currentState']
        hbl = QtGui.QHBoxLayout()
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        
        if mode == 'Quality Assurance':
            self.mainWidget = QtGui.QWidget(self)
            imgDir = os.path.join(self.controller.homeDir,"figs")
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 
            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
            
        elif mode == 'Results Navigation':
            ## error checking
            modelsRun = get_models_run(self.controller.homeDir,self.possibleModels)
            if len(modelsRun) == 0:
                self.display_info("No models have been run yet -- so results cannot be viewed")
                return False

            self.log.log['selectedModel'] = modelsRun[0] 

            if self.log.log['selectedModel'] not in modelsRun:
                print "ERROR selected model not in models run"

            ## thumbs viewer
            self.mainWidget = QtGui.QWidget(self)
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 

            if self.log.log['subsample'] == 'All Data':
                imgDir = os.path.join(self.controller.homeDir,'figs',self.log.log['selectedModel'])
            else:
                subset = str(int(float(self.log.log['subsample'])))
                imgDir = os.path.join(self.controller.homeDir,'figs',"sub%s_%s"%(subset,self.log.log['selectedModel']))
            
            if os.path.isdir(imgDir) == False:
                print "ERROR: a bad imgDir has been specified", imgDir

            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
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

    def handle_data_processing_mode_callback(self,item=None):
        if item != None:
            self.log.log['dataProcessingAction'] = item
            if item not in ['channel select']: 
                self.display_info("This stage is in beta testing and is not yet suggested for general use")
            move_to_data_processing(self)

    def set_selected_results_mode(self):
        #selectedMode, selectedModeInd = self.dock.get_selected_results_mode() 
        selectedMode = self.dock.get_results_mode()
        self.log.log['resultsMode'] = selectedMode
        self.handle_show_scatter(img=None)

    def set_selected_file(self):
        selectedFile, selectedFileInd = self.fileSelector.get_selected_file() 
        self.log.log['selectedFile'] = selectedFile
        
    def set_selected_model(self):
        selectedModel, selectedModleInd = self.fileSelector.get_selected_model()
        self.log.log['selectedModel'] = selectedModel

    def refresh_state(self):
        if self.log.log['currentState'] == "Data Processing":
            move_to_data_processing(self)
        elif self.log.log['currentState'] == "Quality Assurance":
            move_to_quality_assurance(self)
        elif self.log.log['currentState'] == "Model":
            move_to_model(self)
        elif self.log.log['currentState'] == "Results Navigation":
            move_to_results_navigation(self)
        elif self.log.log['currentState'] == "Results Summary":
            move_to_results_summary(self)

        QtCore.QCoreApplication.processEvents()

    def handle_show_scatter(self,img=None):
        mode = self.log.log['currentState']
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
            channels = re.sub("%s\_|\_thumb.png"%re.sub("\.fcs","",self.log.log['selectedFile']),"",img)
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
            sp = ScatterPlotter(self.controller.homeDir,self.log.log['selectedFile'],self.lastChanI,self.lastChanJ,
                                parent=self.mainWidget,subset=self.log.log['subsample'])
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
        elif mode == "Results Navigation":
            self.set_selected_model()
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)

            if self.log.log['subsample'] == 'All Data':
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selectedFile']) + "_" + self.log.log['selectedModel']
            else:
                subset = str(int(float(self.log.log['subsample'])))
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selectedFile']) + "_" + "sub%s_%s"%(subset,self.log.log['selectedModel'])

            sp = ScatterPlotter(self.controller.homeDir,self.log.log['selectedFile'],self.lastChanI,self.lastChanJ,subset=self.log.log['subsample'],
                                modelName=modelName,modelType=self.log.log['resultsMode'],parent=self.mainWidget)
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

    def set_widgets_enabled(self,flag):
        if flag not in [True, False]:
            print "ERROR: invalid flag sent to widgets_enable_all"
            return None

        

        if self.log.log['currentState'] == 'Data Processing':
            self.dock1.setEnabled(flag)
            self.dock2.setEnabled(flag)
            self.fileSelector.setEnabled(flag)
            self.pDock.setEnabled(flag)
        elif self.log.log['currentState'] == 'Quality Assurance':
            self.dock.setEnabled(flag)
            self.fileSelector.setEnabled(flag)
            self.pDock.setEnabled(flag)
       
