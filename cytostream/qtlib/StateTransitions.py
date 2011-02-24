#!/usr/bin/python

'''
Cytostream
StateTransitions

functions that handle the transitions from one software state to another
                                                                                                                             
'''

__author__ = "A Richards"

import os,sys,re
import numpy as np
from PyQt4 import QtGui,QtCore

from cytostream import get_fcs_file_names, get_project_names
from cytostream.qtlib import remove_left_dock, add_left_dock
from cytostream.qtlib import ProgressBar, Imager, move_transition
from cytostream.qtlib import OpenExistingProject, DataProcessingCenter
from cytostream.qtlib import QualityAssuranceCenter, ModelCenter
from cytostream.qtlib import ResultsNavigationCenter, EditMenu
from cytostream.qtlib import OneDimViewer

def move_to_initial(mainWindow):

    ## remove docks
    if mainWindow.pDock != None:
        mainWindow.removeDockWidget(mainWindow.pipelineDock)
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)
        
    ## set the state
    mainWindow.controller.log.log['current_state'] = 'Initial'
    mainWindow.reset_layout()

    ## adds if not initial initial
    if mainWindow.controller.homeDir != None:
        add_left_dock(mainWindow)
        
    ## declare layouts
    hbl1 = QtGui.QHBoxLayout()
    hbl1.setAlignment(QtCore.Qt.AlignCenter)
    hbl2 = QtGui.QHBoxLayout()
    hbl2.setAlignment(QtCore.Qt.AlignCenter)

    ## add main label
    mainWindow.titleLabel = QtGui.QLabel('Cytostream')
    hbl1.addWidget(mainWindow.titleLabel)

    ## add image widget(s)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    scienceImg =  os.path.join(mainWindow.controller.baseDir,"applications-science.png")
    si = Imager(scienceImg,mainWindow.mainWidget)
    hbl2.addWidget(si)

    ## finalize layout
    mainWindow.vboxCenter.addLayout(hbl1)
    mainWindow.vboxCenter.addLayout(hbl2)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()

def move_to_open(mainWindow):

    if mainWindow.controller.projectID != None:
        reply = QtGui.QMessageBox.question(mainWindow, mainWindow.controller.appName,
                                           "Are you sure you want to close the current project - '%s'?"%mainWindow.controller.projectID,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return None
        else:
            mainWindow.controller.save()
    
    mainWindow.controller.reset_workspace()
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    closeBtnFn = lambda a=mainWindow: move_to_initial(a)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    projectList = get_project_names(mainWindow.controller.baseDir)
    mainWindow.existingProjectOpener = OpenExistingProject(projectList,parent=mainWindow.mainWidget,openBtnFn=mainWindow.open_existing_project_handler,
                                                           closeBtnFn=closeBtnFn,rmBtnFn=mainWindow.remove_project)
    ## add right dock
    if mainWindow.pDock == None:
        mainWindow.add_pipeline_dock()

    ## enable disable other widgets
    mainWindow.pDock.inactivate_all()
    mainWindow.pDock.contBtn.setEnabled(False)

    ## add left dock
    add_left_dock(mainWindow)

    ## layout
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.existingProjectOpener)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()


'''
def move_to_results_navigation(mainWindow,runNew=False):
    if mainWindow.controller.verbose == True:
        print "moving to results navigation"
 
    ## error checking
    modelsRun = get_models_run(mainWindow.controller.homeDir,mainWindow.possibleModels)
    if len(modelsRun) == 0:
        mainWindow.display_info("No models have been run yet -- so results cannot be viewed")
        return False

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)
    mainWindow.log.log['current_state'] = "Results Navigation"
    goFlag = mainWindow.display_thumbnails(runNew)

    if goFlag == False:
        print "WARNING: failed to display thumbnails not moving to results navigation"
        return False

    add_left_dock(mainWindow)

    ## disable buttons
    mainWindow.dock.disable_all()
    mainWindow.track_highest_state()
    mainWindow.controller.save()
    if mainWindow.pDock != None:
        mainWindow.pDock.set_btn_highlight('results navigation')
    return True
'''

def move_to_results_navigation(mainWindow,mode='menu'):
    if mainWindow.controller.verbose == True:
        print "moving to results navigation", mode

    ## error checking
    modeList = ['menu']

    if mode not in modeList:
        print "ERROR: move_to_results_navigation - bad mode", mode

    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    if len(fileList) == 0:
        mainWindow.display_info("No files have been loaded -- so results navigation mode cannot be displayed")
        return False

    ## check that thumbs are made
    if mainWindow.log.log['selected_file'] == None:
        mainWindow.log.log['selected_file'] = fileList[0]

    runID = 'run1'
    thumbDir = os.path.join(mainWindow.controller.homeDir,"figs",runID,mainWindow.log.log['selected_file']+"_thumbs")

    if os.path.isdir(thumbDir) == False or len(os.listdir(thumbDir)) == 0:
        print 'ERROR: move_to_results_navigation -- results have not been produced'

    ## clean the layout
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)
    
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    
    ## prepare variables
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)

    if mainWindow.pDock == None:
        mainWindow.add_pipeline_dock()

    ## handle state
    mainWindow.controller.log.log['current_state'] = 'Results Navigation'
    mainWindow.update_highest_state()
    mainWindow.controller.save()
    masterChannelList = mainWindow.controller.masterChannelList
    mainWindow.rnc = ResultsNavigationCenter(fileList,masterChannelList,parent=mainWindow.mainWidget,mode=mode,
                                             mainWindow=mainWindow)
    ## add left dock
    add_left_dock(mainWindow)
    mainWindow.rnc.set_enable_disable()
    #mainWindow.connect(mainWindow.recreateBtn,QtCore.SIGNAL('clicked()'),mainWindow.recreate_figures)

    ## handle layout
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.rnc)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()

    return True

def move_to_model(mainWindow,modelMode='progressbar'):
    if mainWindow.controller.verbose == True:
        print "moving to model", mode

    ## error checking
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    if len(fileList) == 0:
        mainWindow.display_info("No files have been loaded -- so model stage cannot be displayed")
        return False
    
    ## clean the layout
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow) 
    
    ## manage the state
    mainWindow.log.log['current_state'] = "Model"
    mainWindow.update_highest_state()
    mainWindow.controller.save()

    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    channelList = mainWindow.controller.masterChannelList
    mainWindow.mc = ModelCenter(fileList,channelList,mode=modelMode,parent=mainWindow.mainWidget,
                                runModelFn=mainWindow.run_progress_bar,mainWindow=mainWindow)
    ## handle docks
    add_left_dock(mainWindow)
    
    if mainWindow.pDock == None:
        mainWindow.add_pipeline_dock()

    mainWindow.mc.set_enable_disable()
    mainWindow.pDock.enable_disable_states()

    ## finalize layout
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.mc)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()

    return True  

def move_to_quality_assurance(mainWindow,mode='thumbnails'):
    if mainWindow.controller.verbose == True:
        print "moving to quality assurance", mode

    ## error checking
    modeList = ['progressbar','histogram','thumbnails','plot-1','plot-2','plot-3','plot-4','plot-6']

    if mode not in modeList:
        print "ERROR: move_to_quality_assurance - bad mode", mode

    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    if len(fileList) == 0:
        mainWindow.display_info("No files have been loaded -- so quality assurance cannot be carried out")
        return False

    ## check that thumbs are made
    if mainWindow.log.log['selected_file'] == None:
        mainWindow.log.log['selected_file'] = fileList[0]

    thumbDir = os.path.join(mainWindow.controller.homeDir,"figs","qa",mainWindow.log.log['selected_file']+"_thumbs")

    if os.path.isdir(thumbDir) == False or len(os.listdir(thumbDir)) == 0:
        mode = 'progressbar'
        print 'INFO: changing thumbnails tag to progressbar'

    if mode == 'thumbnails':
        mainWindow.display_thumbnails()
        return True

    ## clean the layout
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)
    
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    
    ## prepare variables
    masterChannelList = mainWindow.controller.masterChannelList
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)

    if mainWindow.pDock == None:
        mainWindow.add_pipeline_dock()

    ## handle state
    mainWindow.controller.log.log['current_state'] = 'Quality Assurance'
    mainWindow.update_highest_state()
    mainWindow.controller.save()

    mainWindow.qac = QualityAssuranceCenter(fileList,masterChannelList,parent=mainWindow.mainWidget,
                                            mainWindow=mainWindow)
    
    mainWindow.qac.progressBar.set_callback(mainWindow.run_progress_bar)

    ## add left dock
    add_left_dock(mainWindow)
    mainWindow.qac.set_enable_disable()
    mainWindow.connect(mainWindow.recreateBtn,QtCore.SIGNAL('clicked()'),mainWindow.recreate_figures)

    ## handle layout
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.qac)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()

    return True

def move_to_data_processing(mainWindow,withProgressBar=False):
    if mainWindow.controller.verbose == True:
        print "moving to data processing"
    
    if mainWindow.controller.homeDir == None:
        mainWindow.display_info('To begin either load an existing project or create a new one')
        return False

    ## clean the layout
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    ## prepare variables
    masterChannelList = mainWindow.controller.masterChannelList
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)

    ## create a edit menu function
    def move_to_edit_menu(mainWindow):

        ## clean the layout
        mainWindow.reset_layout()

        if mainWindow.pDock != None:
            mainWindow.pDock.unset_all_highlights()
        if mainWindow.dockWidget != None:
            remove_left_dock(mainWindow)

        closeBtnFn = lambda a=mainWindow: move_to_data_processing(a)
        mainWindow.mainWidget = QtGui.QWidget(mainWindow)
        defaultTransform = mainWindow.log.log['selected_transform']
        mainWindow.editMenu = EditMenu(parent=mainWindow.mainWidget,closeBtnFn=closeBtnFn,defaultTransform=defaultTransform,
                                       mainWindow=mainWindow)

        ## add right dock
        if mainWindow.pDock == None:
            mainWindow.add_pipeline_dock()

        ## add left dock
        add_left_dock(mainWindow)
        mainWindow.editMenu.set_enable_disable()

        ## layout
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(mainWindow.editMenu)
        mainWindow.vboxCenter.addLayout(hbl)
        mainWindow.mainWidget.setLayout(mainWindow.vbl)
        mainWindow.refresh_main_widget()

    ## ready a DataProcessingCenter class
    def load_files():
        allFiles = QtGui.QFileDialog.getOpenFileNames(mainWindow, 'Open file(s)')
        for fileName in allFiles:
            if not re.search("\.fcs|\.csv",os.path.split(str(fileName))[-1]):
                print "WARNING: loaded file is not of type fcs or csv", fileName

        return allFiles

    showProgressBar = False

    if len(mainWindow.allFilePaths) > 0 or withProgressBar == True:
        showProgressBar = True
    else:
        showProgressBar = False

    ## update highest state
    mainWindow.controller.log.log['current_state'] = 'Data Processing'
    mainWindow.update_highest_state()
    mainWindow.controller.save()

    ## create widgets
    mainWindow.dpc = DataProcessingCenter(fileList,masterChannelList,loadFileFn=load_files,parent=mainWindow.mainWidget,
                                          mainWindow=mainWindow,showProgressBar=showProgressBar,editBtnFn=lambda a=mainWindow: move_to_edit_menu(a))

    ## handle docks
    add_left_dock(mainWindow)
    if mainWindow.pDock == None:
        mainWindow.add_pipeline_dock()

    mainWindow.dpc.set_enable_disable()

    ## handle layout
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.dpc)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()
    
    ## handle state transfer
    mainWindow.pDock.enable_continue_btn(lambda a=mainWindow: move_to_quality_assurance(a))
    return True

def move_to_one_dim_viewer(mainWindow):
    if mainWindow.controller.verbose == True:
        print "moving to one dim viewer"

    if mainWindow.controller.homeDir == None:
        mainWindow.display_info('To begin either load an existing project or create a new one')
        return False

    ## clean the layout
    move_transition(mainWindow,repaint=True)
    mainWindow.reset_layout()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.log.log['current_state'] == 'Initial':
        pass
    elif mainWindow.log.log['current_state'] == 'Quality Assurance':
        excludedFiles = mainWindow.log.log['excluded_files_qa']
        subsample = mainWindow.log.log['subsample_qa']
    else:
        excludedFiles = mainWindow.log.log['excluded_files_analysis']
        subsample = mainWindow.log.log['subsample_analysis']
    
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    mainWindow.odv = OneDimViewer(mainWindow.controller.homeDir,subset=subsample,background=True,parent=mainWindow.mainWidget)
    add_left_dock(mainWindow)
    mainWindow.plots_enable_disable(mode='histogram')

    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(mainWindow.odv)
    mainWindow.vboxCenter.addLayout(hbl)
    mainWindow.mainWidget.setLayout(mainWindow.vbl)
    mainWindow.refresh_main_widget()


def move_to_results_summary(mainWindow,runNew=False):
    mainWindow.display_info("This stage is not available yet")
