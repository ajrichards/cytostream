#!/usr/bin/python

'''
Cytostream
StateTransitions

functions that handle the transitions from one software state to another

stage notation

0 - Initial
1 - Data Processing
2 - Quality Assurance
3 - Model Run
4 - Model Results
5 - Analysis
6 - Analysis Results
7 - Reports
                                                 
'''

__author__ = "A Richards"

import os,sys,re
import numpy as np
from PyQt4 import QtGui,QtCore
from cytostream import get_fcs_file_names, get_project_names
from cytostream.opengl import LogoWidget
from cytostream.qtlib import remove_left_dock, add_left_dock
from cytostream.qtlib import ProgressBar, Imager, move_transition
from cytostream.qtlib import OpenExistingProject, DataProcessingCenter
from cytostream.qtlib import QualityAssuranceCenter, ModelCenter
from cytostream.qtlib import ResultsNavigationCenter, EditMenu
from cytostream.qtlib import FileAlignerCenter
from cytostream.qtlib import OneDimViewer, PreferencesDPMM, PreferencesKmeans
from cytostream.tools import get_official_name_match

class Transitions():
    '''
    class that handles the transitions between stages

    '''

    def __init__(self,mainWindow):
        self.mainWindow = mainWindow

    def begin_wait(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def end_wait(self):
        QtGui.QApplication.restoreOverrideCursor()

    def move_to_initial(self):

        ## handle docks
        self.mainWindow.restore_docks()
   
        ## set the state
        self.mainWindow.controller.log.log['current_state'] = 'Initial'
        self.mainWindow.reset_layout()

        ## adds if not initial initial
        if self.mainWindow.controller.homeDir != None:
            add_left_dock(self.mainWindow)
        
        ## declare layouts
        hbl1 = QtGui.QHBoxLayout()
        hbl1.setAlignment(QtCore.Qt.AlignCenter)
        hbl2 = QtGui.QHBoxLayout()
        hbl2.setAlignment(QtCore.Qt.AlignCenter)

        ## add main label
        self.mainWindow.titleLabel = QtGui.QLabel('Cytostream')
        self.mainWindow.titleLabel.setStyleSheet("font: 16pt")
        hbl1.addWidget(self.mainWindow.titleLabel)

        ## add image widget(s)
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
        logoWidget = LogoWidget()
        hbl2.addWidget(logoWidget)

        ## finalize layout
        self.mainWindow.vboxCenter.addLayout(hbl1)
        self.mainWindow.vboxCenter.addLayout(hbl2)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()

    def move_to_open(self):
        '''
        transition to the open project dialog
        '''

        if self.mainWindow.controller.projectID != None:
            reply = QtGui.QMessageBox.question(self.mainWindow, self.mainWindow.controller.appName,
                                               "Are you sure you want to close the current project - '%s'?"%self.mainWindow.controller.projectID,
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return None
            else:
                self.mainWindow.controller.save()
    

        ## get the project directory
        defaultDir = self.mainWindow.controller.defaultDir
        projectDir = QtGui.QFileDialog.getExistingDirectory(self.mainWindow, 'Select the project folder', 
                                                            options=QtGui.QFileDialog.ShowDirsOnly,directory=defaultDir)
        projectDir = str(projectDir)
        if projectDir == '' or projectDir == None:
            return None

        ## clean the layout
        self.mainWindow.controller.reset_workspace()
        self.mainWindow.reset_layout()
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)

        ## create open widget
        closeBtnFn = lambda a=self.mainWindow: move_to_initial(a)
        projectList = get_project_names(self.mainWindow.controller.baseDir)
    
        ## remove docks if necessary 
        if self.mainWindow.dockWidget != None:
            remove_left_dock(self.mainWindow)
        if self.mainWindow.pDock != None:
            self.mainWindow.removeDockWidget(self.mainWindow.pipelineDock)

        ## enable disable other widgets
        self.move_to_initial()
        self.mainWindow.status.showMessage("Open an existing project", 5000)
    
        self.mainWindow.open_existing_project_handler(projectDir)

    def move_to_model_results(self,mode='menu'):
        '''
        transition to model results state
        '''

        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to results navigation", mode

        ## error checking
        modeList = ['menu']

        if mode not in modeList:
            print "ERROR: move_to_model_resultsn - bad mode", mode

        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        if len(fileList) == 0:
            self.mainWindow.display_info("No files have been loaded -- so results navigation mode cannot be displayed")
            return False

        ## check that thumbs are made
        if self.mainWindow.log.log['selected_file'] == None:
            self.mainWindow.log.log['selected_file'] = fileList[0]

        runID = 'run1'
        thumbDir = os.path.join(self.mainWindow.controller.homeDir,"figs",runID,self.mainWindow.log.log['selected_file']+"_thumbs")

        if os.path.isdir(thumbDir) == False or len(os.listdir(thumbDir)) == 0:
            print 'ERROR: move_to_results_navigation -- results have not been produced'

        ## clean the layout and declare variables
        self.mainWindow.reset_layout()
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)

        ## handle state
        self.mainWindow.controller.log.log['current_state'] = 'Model Results'
        self.mainWindow.update_highest_state()
        self.mainWindow.controller.save()

        ## create center widget
        masterChannelList = self.mainWindow.get_master_channel_list()
        self.mainWindow.rnc = ResultsNavigationCenter(fileList,masterChannelList,parent=self.mainWindow.mainWidget,mode=mode,
                                                      mainWindow=self.mainWindow)
        ## handle docks
        self.mainWindow.restore_docks()

        ## handle layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.rnc)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Model Results", 5000)
        self.mainWindow.controller.log.log['highest_state'] = 4

        ## enable disable
        self.mainWindow.subsampleSelector.setEnabled(False)
        self.mainWindow.channelSelector.setEnabled(False)
        self.mainWindow.plotSelector.setEnabled(False)
        self.mainWindow.plotTickControls.setEnabled(False)
        self.mainWindow.vizModeSelector.setEnabled(False)
        self.mainWindow.clusterSelector.setEnabled(False)
        if self.mainWindow.gateSelector:
            self.mainWindow.gateSelector.setEnabled(False)

        return True

    def move_to_model_run(self):
        '''
        transition to model run state
        '''

        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to model run"

        ## error checking
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        if len(fileList) == 0:
            self.mainWindow.display_info("No files have been loaded -- so model stage cannot be displayed")
            return False
    
        ## clean the layout
        self.mainWindow.reset_layout()
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow) 
    
        ## manage the state
        self.mainWindow.log.log['current_state'] = "Model Run"
        self.mainWindow.update_highest_state()
        self.mainWindow.controller.save()

        ## create center widget
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        channelList = self.mainWindow.get_master_channel_list()
        self.mainWindow.mc = ModelCenter(fileList,channelList,parent=self.mainWindow.mainWidget,
                                         runModelFn=self.mainWindow.run_progress_bar,mainWindow=self.mainWindow)
        ## handle docks
        self.mainWindow.restore_docks()

        ## finalize layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.mc)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.controller.log.log['highest_state'] = 3
        self.mainWindow.status.showMessage("Model Run", 5000)
        return True

    def move_to_create_filter(self):
        '''
        transition to create filter state
        '''

        ## ensure we are in a valid view
        if self.mainWindow.controller.log.log['current_state'] not in ['Model Results']:
            self.mainWindow.display_info("Create filter only works from Model Results stage")
            return
        
        ## force num subplots to 1
        self.mainWindow.controller.log.log['num_subplots'] = 1
        self.mainWindow.controller.save()

        self.mainWindow.plots_enable_disable()
        self.mainWindow.handle_show_plot(gating=True)

    def move_to_quality_assurance(self,mode='thumbnails'):
        '''
        transition to quality assurance state
        '''

        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to quality assurance -- ", mode

        ## save channel dict
        if self.mainWindow.dpc:
            channelDict = {}
            #officialChannelList = [get_official_name_match(i) for i in self.mainWindow.controller.masterChannelList]
            n = len(self.mainWindow.controller.masterChannelList)
            chanLabels = [str(self.mainWindow.dpc.modelChannels.data(self.mainWindow.dpc.modelChannels.index(i,3)).toString()) for i in range(n)]
            for i,cl in enumerate(chanLabels):
                if cl != 'Unmatched':
                    channelDict[cl] = i
                else:
                    print "ERROR: Transitions: we have unmatched channel"
            self.mainWindow.model.save_channel_dict(channelDict)
            self.mainWindow.channelDict = self.mainWindow.model.load_channel_dict()

        ## error checking
        modeList = ['progressbar','thumbnails','plot']
        if mode not in modeList:
            print "ERROR: move_to_quality_assurance - bad mode", mode

        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        if len(fileList) == 0:
            self.mainWindow.display_info("No files have been loaded -- so quality assurance cannot be carried out")
            return False

        ## check that thumbs are made
        if self.mainWindow.log.log['selected_file'] == None:
            self.mainWindow.log.log['selected_file'] = fileList[0]

        thumbDir = os.path.join(self.mainWindow.controller.homeDir,"figs","qa",self.mainWindow.log.log['selected_file']+"_thumbs")

        if os.path.isdir(thumbDir) == False or len(os.listdir(thumbDir)) == 0:
            mode = 'progressbar'
            print 'INFO: changing thumbnails tag to progressbar'

        if mode == 'thumbnails':
            self.mainWindow.display_thumbnails(forceMode='Quality Assurance')
            self.mainWindow.pDock.set_btn_highlight("Quality Assurance")
            return True

        ## clean the layout
        self.mainWindow.reset_layout()    
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
    
        ## prepare variables
        masterChannelList = self.mainWindow.get_master_channel_list()
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)

        ## handle state
        self.mainWindow.controller.log.log['current_state'] = 'Quality Assurance'
        self.mainWindow.update_highest_state()
        self.mainWindow.controller.save()

        ## create center widget
        self.mainWindow.qac = QualityAssuranceCenter(fileList,masterChannelList,parent=self.mainWindow.mainWidget,
                                                     mainWindow=self.mainWindow)
    
        self.mainWindow.qac.progressBar.set_callback(self.mainWindow.run_progress_bar)

        ## handle docks
        self.mainWindow.restore_docks()

        ## handle layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.qac)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Quality Assurance", 5000)
        return True

    def move_to_data_processing(self,withProgressBar=False):
        '''
        function to transition view to 'Data Processing'
        '''

        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to data processing"
    
        if self.mainWindow.controller.homeDir == None:
            self.mainWindow.display_info('To begin either load an existing project or create a new one')
            return False

        ## clean the layout and prepare variables
        self.mainWindow.reset_layout()
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
        masterChannelList = self.mainWindow.get_master_channel_list()
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        
        ## create a edit menu function
        def move_to_edit_menu(self):
            '''
            the edit menu before preprocessing
            '''

            ## clean the layout
            self.mainWindow.reset_layout()
            self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
        
            if self.mainWindow.pDock != None:
                self.mainWindow.pDock.unset_all_highlights()
            if self.mainWindow.dockWidget != None:
                remove_left_dock(self.mainWindow)

            closeBtnFn = lambda a=self.mainWindow:self.move_to_data_processing(a)
            defaultTransform = self.mainWindow.log.log['load_transform']
            self.mainWindow.editMenu = EditMenu(parent=self.mainWindow.mainWidget,closeBtnFn=closeBtnFn,
                                                defaultTransform=defaultTransform,mainWindow=self.mainWindow)
            ## handle dock widgets
            self.mainWindow.restore_docks()

            ## layout
            hbl = QtGui.QHBoxLayout()
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            hbl.addWidget(self.mainWindow.editMenu)
            self.mainWindow.vboxCenter.addLayout(hbl)
            self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
            self.mainWindow.refresh_main_widget()
            
        ## ready a DataProcessingCenter class
        def load_files():
            defaultDir = os.path.join(self.mainWindow.controller.homeDir,os.path.pardir)
            print 'using default dir', defaultDir
            allFiles = QtGui.QFileDialog.getOpenFileNames(self.mainWindow,'Open file(s)',
                                                          directory=defaultDir)
            for fileName in allFiles:
                if not re.search("\.fcs|\.csv|\.txt",os.path.split(str(fileName))[-1]):
                    print "WARNING: loaded file is of unknown extension", fileName

            self.mainWindow.status.showMessage("Files selected", 5000)
            return allFiles

        ## determine whether or not to show progress bar
        if len(self.mainWindow.allFilePaths) > 0 or withProgressBar == True:
            showProgressBar = True
        else:
            showProgressBar = False

        ## update highest state
        self.mainWindow.controller.log.log['current_state'] = 'Data Processing'
        self.mainWindow.update_highest_state()
        self.mainWindow.controller.save()

        ## create center widget
        self.mainWindow.dpc = DataProcessingCenter(fileList,masterChannelList,loadFileFn=load_files,parent=self.mainWindow.mainWidget,
                                                   mainWindow=self.mainWindow,showProgressBar=showProgressBar,editBtnFn=lambda a=self:move_to_edit_menu(a))
        ## handle docks
        self.mainWindow.restore_docks()

        ## handle layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.dpc)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Data Processing", 5000)
        return True

    def move_to_one_dim_viewer(self):
        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to one dim viewer"

        if self.mainWindow.controller.homeDir == None:
            self.mainWindow.display_info('To begin either load an existing project or create a new one')
            return False

        ## clean the layout
        move_transition(self.mainWindow,repaint=True)
        self.mainWindow.reset_layout()    
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)
        subsample = 10000
        self.mainWindow.controller.handle_subsampling(subsample)
        self.mainWindow.odv = OneDimViewer(self.mainWindow.controller.homeDir,subset=subsample,background=True,parent=self.mainWindow.mainWidget)

        ## handle docks
        self.mainWindow.restore_docks()
        self.mainWindow.plots_enable_disable(mode='histogram')
        self.mainWindow.fileSelector.setEnabled(False)

        ## handle layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.odv)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Histogram viewer", 5000)

    def move_to_preferences(self):

        ## ensure there is a project present
        currentState = self.mainWindow.log.log['current_state']
        modelToRun =  self.mainWindow.log.log['model_to_run']
        if currentState == 'Initial':
            self.mainWindow.display_info('To begin either load an existing project or create a new one')
            return False

        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to preferences"
        
        validStates = ['Model Run','Sample Alignment']
        if currentState not in validStates:
            self.mainWindow.display_info('Preferences are only available from: %s'%validStates)
            return None

        ## clean the layout
        move_transition(self.mainWindow,repaint=True)
        self.mainWindow.reset_layout()

        ## preferences widget    
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow)

        if currentState == 'Data Processing':
            self.mainWindow.preferences = Preferences(parent=self.mainWindow.mainWidget,mainWindow=self.mainWindow)
        if currentState == 'Model Run':
            if modelToRun in ['dpmm-mcmc','dpmm-bem']:
                self.mainWindow.preferences = PreferencesDPMM(parent=self.mainWindow.mainWidget,mainWindow=self.mainWindow)
            elif modelToRun == 'kmeans':
                self.mainWindow.preferences = PreferencesKmeans(parent=self.mainWindow.mainWidget,mainWindow=self.mainWindow)

        ## handle docks
        self.mainWindow.restore_docks()
        self.mainWindow.plots_enable_disable(mode='histogram')

        ## handle layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.preferences)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Application preferences", 5000)

    def move_to_results_summary(self,runNew=False):
        self.mainWindow.display_info("This stage is not available yet")

    def move_to_file_aligner(self,faMode='progressbar'):
        if self.mainWindow.controller.verbose == True:
            print "INFO: moving to file aligner", faMode

        ## error checking
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        if len(fileList) == 0:
            self.mainWindow.display_info("No files have been loaded -- so model stage cannot be displayed")
            return False
    
        ## clean the layout
        self.mainWindow.reset_layout()
        self.mainWindow.mainWidget = QtGui.QWidget(self.mainWindow) 
    
        ## manage the state
        self.mainWindow.log.log['current_state'] = "Sample Alignment"
        self.mainWindow.update_highest_state()
        self.mainWindow.controller.save()

        ## create center widget
        fileList = get_fcs_file_names(self.mainWindow.controller.homeDir)
        channelList = self.mainWindow.get_master_channel_list()
        self.mainWindow.fac = FileAlignerCenter(fileList,channelList,mode=faMode,parent=self.mainWindow.mainWidget,
                                                runFileAlignerFn=self.mainWindow.run_file_aligner,mainWindow=self.mainWindow)
        ## handle docks
        self.mainWindow.restore_docks()

        ## finalize layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(self.mainWindow.fac)
        self.mainWindow.vboxCenter.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(self.mainWindow.vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.status.showMessage("Sample Alignment", 5000)
        return True
