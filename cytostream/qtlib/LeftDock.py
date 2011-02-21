#!/usr/bin/python

'''
Cytostream
LeftDock 

based on the state these functions control which widget appear in the left dock

'''

__author__ = "A. Richards"

import sys,os
from PyQt4 import QtGui,QtCore

from cytostream import get_fcs_file_names
from cytostream.qtlib import FileSelector,SubsetSelector, ModeSelector

def remove_left_dock(mainWindow):
    mainWindow.removeDockWidget(mainWindow.mainDockWidget)

def add_left_dock(mainWindow):
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.fileSelector != None and mainWindow.log.log['selected_file'] == None:
        mainWindow.set_selected_file()

    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    if len(fileList) > 0:
        masterChannelList = mainWindow.model.get_master_channel_list()

    ## declare variables
    subsetList = ["1e03", "1e04","5e04","All Data"]
    if mainWindow.controller.projectID == None:
        projectID = "no project loaded"
    else:
        projectID = mainWindow.controller.projectID
    
    excludedFiles = None

    ## prepare dock widget
    mainWindow.mainDockWidget = QtGui.QDockWidget(projectID, mainWindow)
    mainWindow.mainDockWidget.setObjectName("MainDockWidget")
    mainWindow.mainDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
    mainWindow.dockWidget = QtGui.QWidget(mainWindow)
    palette = mainWindow.dockWidget.palette()
    role = mainWindow.dockWidget.backgroundRole()

    ## set colors
    try:
        appColor = self.controller.log.log['app_color']
    except:
        appColor = '#999999'
            
    palette.setColor(role, QtGui.QColor(appColor))
    mainWindow.dockWidget.setPalette(palette)
    mainWindow.dockWidget.setAutoFillBackground(True)
    
    # setup alignments
    vbl = QtGui.QVBoxLayout()
    vboxTop = QtGui.QVBoxLayout()
    vboxTop.setAlignment(QtCore.Qt.AlignTop)
    vboxCenter = QtGui.QVBoxLayout()
    vboxCenter.setAlignment(QtCore.Qt.AlignCenter) 
    vboxBottom = QtGui.QVBoxLayout()
    vboxBottom.setAlignment(QtCore.Qt.AlignBottom)

    widgetWidth = 0.13 * mainWindow.screenWidth
    alignWidth = 0.1175 * mainWindow.screenWidth
    mainWindow.dockWidget.setMaximumWidth(widgetWidth)
    mainWindow.dockWidget.setMinimumWidth(widgetWidth)

    ## check to see if fileList needs adjusting
    if mainWindow.log.log['current_state'] in ['Results Navigation']:
        showModelSelector = True
        modelsRun = get_models_run(mainWindow.controller.homeDir,mainWindow.possibleModels)
    else:
        showModelSelector = False
        modelsRun = None

    if mainWindow.log.log['current_state'] == 'Initial':
        pass
    elif mainWindow.log.log['current_state'] == 'Quality Assurance':
        excludedFiles = mainWindow.log.log['excluded_files_qa']
        subsampleDefault = mainWindow.log.log['subsample_qa']
    else:
        excludedFiles = mainWindow.log.log['excluded_files_analysis']
        subsampleDefault = mainWindow.log.log['subsample_analysis']

    ## check to see if fileList needs adjusting
    if type(excludedFiles) == type([]) and len(excludedFiles) > 0:
        for f in excludedFiles:
            fileList.remove(f)

    ## file selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model','Results Navigation']:
        mainWindow.fileSelector = FileSelector(fileList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_file,
                                               fileDefault=mainWindow.log.log['selected_file'])
        fsLayout = QtGui.QHBoxLayout()
        fsLayout.setAlignment(QtCore.Qt.AlignLeft)
        fsLayout.addWidget(mainWindow.fileSelector)
        vboxTop.addLayout(fsLayout)
        mainWindow.fileSelector.setAutoFillBackground(True)
        mainWindow.fileSelector.setMaximumWidth(alignWidth)
        mainWindow.fileSelector.setMinimumWidth(alignWidth)
       
    ## subset selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance']:

        if mainWindow.log.log['current_state'] == 'Data Processing':
            subsetDefault = mainWindow.log.log['subsample_qa']
        else:
            subsetDefault = mainWindow.log.log['subsample_analysis']

        mainWindow.subsetSelector = SubsetSelector(subsetList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_subsample,
                                               subsetDefault=subsetDefault)
        ssLayout = QtGui.QHBoxLayout()
        ssLayout.setAlignment(QtCore.Qt.AlignLeft)
        ssLayout.addWidget(mainWindow.subsetSelector)
        vboxTop.addLayout(ssLayout)
        mainWindow.subsetSelector.setAutoFillBackground(True)
        mainWindow.subsetSelector.setMaximumWidth(alignWidth)
        mainWindow.subsetSelector.setMinimumWidth(alignWidth)
       
    ## mode selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Results Navigation']:
        visualizationMode = mainWindow.log.log['visualization_mode']
        btnLabels = ['histogram','thumbnails','plot-1','plot-2','plot-3','plot-4','plot-6']
        modeVizCallback = mainWindow.handle_visualization_modes
        mainWindow.modeSelector = ModeSelector(btnLabels,parent=mainWindow.dockWidget,modeDefault=visualizationMode,
                                               modeVizCallback=modeVizCallback)
        rbwLayout = QtGui.QHBoxLayout()
        rbwLayout.setAlignment(QtCore.Qt.AlignLeft)
        rbwLayout.addWidget(mainWindow.modeSelector)
        vboxCenter.addLayout(rbwLayout)
        mainWindow.modeSelector.setAutoFillBackground(True)
        mainWindow.modeSelector.setMaximumWidth(alignWidth)
        mainWindow.modeSelector.setMinimumWidth(alignWidth)

    ## more recreate figures
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Results Navigation']:
        mainWindow.recreateBtn = QtGui.QPushButton("recreate figures")
        mainWindow.recreateBtn.setMaximumWidth(120)
        mainWindow.recreateBtn.setMinimumWidth(120)
        
        rbLayout = QtGui.QHBoxLayout()
        rbLayout.setAlignment(QtCore.Qt.AlignCenter)
        rbLayout.addWidget(mainWindow.recreateBtn)
        vboxBottom.addLayout(rbLayout)

    ## more info btn
    if mainWindow.log.log['current_state'] in ['Initial','Data Processing','Quality Assurance']:
        mainWindow.moreInfoBtn = QtGui.QPushButton("more info")
        mainWindow.moreInfoBtn.setMaximumWidth(120)
        mainWindow.moreInfoBtn.setMinimumWidth(120)
        miLayout = QtGui.QHBoxLayout()
        miLayout.setAlignment(QtCore.Qt.AlignCenter)
        miLayout.addWidget(mainWindow.moreInfoBtn)
        vboxBottom.addLayout(miLayout)

    ## finalize alignments
    vbl.addLayout(vboxTop)
    vbl.addLayout(vboxCenter)
    vbl.addLayout(vboxBottom)
    mainWindow.dockWidget.setLayout(vbl)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)
