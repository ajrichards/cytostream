#!/usr/bin/python

'''
Cytostream
StageTransitions
                                                                                                                                                
Adam Richards
adam.richards@stat.duke.edu
                                                                                                                                     
'''

import os,sys,re
import numpy as np
from PyQt4 import QtGui,QtCore

from LeftDock import *
from FileControls import *
from BasicWidgets import ProgressBar
from DataProcessingCenter import DataProcessingCenter
from ModelCenter import ModelCenter
from OneDimViewer import OneDimViewer
from BlankPage import BlankPage

def move_to_initial(mainWindow):
    if mainWindow.pDock != None:
        mainWindow.pDock.unset_all_highlights()
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    mainWindow.pngViewer = QtGui.QLabel(mainWindow.mainWidget)
    mainWindow.pngViewer.setAlignment(QtCore.Qt.AlignCenter)
    mainWindow.pngViewer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    mainWindow.mainWidget = mainWindow.pngViewer
    mainWindow.refresh_main_widget()
    mainWindow.setCentralWidget(mainWindow.mainWidget)
    mainWindow.image = QtGui.QImage(os.path.join(mainWindow.controller.baseDir,"applications-science.png"))
    mainWindow.show_image()

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

def move_to_model(mainWindow):                                                                                                                                 
    if mainWindow.controller.verbose == True:
        print "moving to model"

    fileList = get_fcs_file_names(mainWindow.controller.homeDir)                                                                                               
    if len(fileList) == 0:                                                                                                                               
        mainWindow.display_info("No files have been loaded -- so no models can yet be run")                                                                    
        return False                                                                                                                                     
                                                                                                                                                             
    if mainWindow.dockWidget != None:                                                                                                                          
        remove_left_dock(mainWindow)                                                                                                                           
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)                                                                                                                
    mainWindow.log.log['current_state'] = "Model"                                                                                                               
    mainWindow.mc = ModelCenter(parent=mainWindow.mainWidget,runModelFn=mainWindow.run_progress_bar)                                                                      
    hbl = QtGui.QHBoxLayout(mainWindow.mainWidget)                                                                                                             
    hbl.setAlignment(QtCore.Qt.AlignCenter)                                                                                                              
    hbl.addWidget(mainWindow.mc)                                                                                                                               
    mainWindow.refresh_main_widget()                                                                                                                           
    add_left_dock(mainWindow)                                                                                                                                  
    mainWindow.track_highest_state()                                                                                                                           
    mainWindow.controller.save()                                                                                                                               
    if mainWindow.pDock != None:                                                                                                                               
        mainWindow.pDock.set_btn_highlight('model')                                                                                                            
    return True  

def move_to_quality_assurance(mainWindow,runNew=False):
    if mainWindow.controller.verbose == True:
        print "moving to quality assurance"

    #fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    #if len(fileList) == 0:
    #    mainWindow.display_info("No files have been loaded -- so quality assurance cannot be carried out")
    #    return False

    ## set the subsample                                                                                                                
    #goFlag = mainWindow.set_subsample()

    #if goFlag == False:
    #    mainWindow.display_info("The num. of samples that you have selected is > than all events in at least one file -- to continue select another value")
    #    return False
    
    ### set the files and channels
    #goFlag = mainWindow.set_checks_array()
    # 
    #if goFlag == False:
    #    print "ERROR: there was an error trying to set checks array from StateTransitions"
    #    return False
    
    ### check that at least one file and one channel have been selected
    #if mainWindow.log.log['checksArray'].sum() == 0:
    #    mainWindow.display_info("There are no selected files or channels -- to continue make selections first")
    #    return False
    
    #if mainWindow.dockWidget != None:
    #    remove_left_dock(mainWindow)
    #mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    #mainWindow.log.log['current_state'] = "Quality Assurance"
    #if mainWindow.log.log['selectedFile'] == None:
    #    mainWindow.log.log['selectedFile'] = fileList[0]
    #
    #thumbDir = os.path.join(mainWindow.controller.homeDir,"figs",mainWindow.log.log['selectedFile'][:-4]+"_thumbs")
    #
    #if os.path.isdir(thumbDir) == True and len(os.listdir(thumbDir)) > 1:
    #    goFlag = mainWindow.display_thumbnails()
    #
    #    if goFlag == False:
    #        print "WARNING: failed to display thumbnails not moving to results navigation"
    #        return False
    #
    #    add_left_dock(mainWindow)
    #else:
    #    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    #    mainWindow.progressBar = ProgressBar(parent=mainWindow.mainWidget,buttonLabel="Create the figures")
    #    mainWindow.progressBar.set_callback(mainWindow.run_progress_bar)
    #    hbl = QtGui.QHBoxLayout(mainWindow.mainWidget)
    #    hbl.addWidget(mainWindow.progressBar)
    #    hbl.setAlignment(QtCore.Qt.AlignCenter)
    #    mainWindow.refresh_main_widget()
    #    add_left_dock(mainWindow)
    #
    #mainWindow.dock.enable_continue_btn(lambda a=mainWindow: move_to_model(a))
    #mainWindow.track_highest_state()
    #mainWindow.controller.save()
    #if mainWindow.pDock != None:
    #    mainWindow.pDock.set_btn_highlight('quality assurance')
    #xsreturn True

def move_to_data_processing(mainWindow):
    if mainWindow.controller.verbose == True:
        print "moving to data processing"
    
    if mainWindow.controller.homeDir == None:
        mainWindow.display_info('To begin either load an existing project or create a new one')
        return False

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    ## prepare variables
    mainWindow.log.log['current_state'] = "Data Processing"
    masterChannelList = mainWindow.model.get_master_channel_list()
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    currentAction = mainWindow.log.log['data_processing_mode']

    ## ready a DataProcessingCenter class
    def load_files():
        allFiles = QtGui.QFileDialog.getOpenFileNames(mainWindow, 'Open file(s)')
        for fileName in allFiles:
            if not re.search("\.fcs|\.csv",os.path.split(str(fileName))[-1]):
                print "WARNING: loaded file is not of type fcs or csv", fileName

        return allFiles

    showProgressBar = False

    if len(mainWindow.allFilePaths) > 0:
        showProgressBar = True
    else:
        showProgressBar = False

    mainWindow.dpc = DataProcessingCenter(fileList,masterChannelList,loadFileFn=load_files,parent=mainWindow.mainWidget,mainWindow=mainWindow,showProgressBar=showProgressBar)
    
    hbl = QtGui.QHBoxLayout(mainWindow.mainWidget)
    hbl.setAlignment(QtCore.Qt.AlignTop)
    hbl.addWidget(mainWindow.dpc)
    mainWindow.refresh_main_widget()
    if len(mainWindow.dpc.allFilePaths) > 0:
        add_left_dock(mainWindow)
        mainWindow.dock1.enable_continue_btn(lambda a=mainWindow: move_to_quality_assurance(a))
    
    mainWindow.track_highest_state()
    mainWindow.controller.save()
    if mainWindow.pDock != None:
        mainWindow.pDock.set_btn_highlight('data processing')

    return True

def move_to_one_dim_viewer(mainWindow):
    if mainWindow.controller.verbose == True:
        print "moving to one dim viewer"

    if mainWindow.controller.homeDir == None:
        mainWindow.display_info('To begin either load an existing project or create a new one')
        return False

    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    bp = BlankPage(parent=mainWindow.mainWidget)
    vbl = QtGui.QVBoxLayout()
    vbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(bp)
    vbl.addLayout(hbl)
    mainWindow.mainWidget.setLayout(vbl)
    mainWindow.refresh_main_widget()
    QtCore.QCoreApplication.processEvents()

    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.pDock != None:
        mainWindow.pDock.unset_all_highlights()

    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    mainWindow.odv = OneDimViewer(mainWindow.controller.homeDir,subset=mainWindow.log.log['subsample'],background=True,parent=mainWindow.mainWidget)
    bp.change_label('1D Data Viewer')
    ntb = NavigationToolbar(mainWindow.odv,mainWindow.mainWidget)
    vbl.addWidget(mainWindow.odv)
    vbl.addWidget(ntb)
    mainWindow.mainWidget.setLayout(vbl)
    QtCore.QCoreApplication.processEvents()
    mainWindow.log.log['current_state'] = "OneDimViewer"
    mainWindow.refresh_main_widget()
    add_left_dock(mainWindow)

def move_to_results_summary(mainWindow,runNew=False):
    mainWindow.display_info("This stage is not available yet")




