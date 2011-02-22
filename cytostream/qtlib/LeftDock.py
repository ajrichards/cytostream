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
from cytostream.qtlib import FileSelector,SubsampleSelector, ModeSelector, ModelToRunSelector
from cytostream.qtlib import ModelTypeSelector

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
    subsampleList = ["1e03", "1e04","5e04","All Data"]
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
       
    ## subsample selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model']:

        if mainWindow.log.log['current_state'] == 'Data Processing':
            subsampleDefault = mainWindow.log.log['subsample_qa']
        else:
            subsampleDefault = mainWindow.log.log['subsample_analysis']

        mainWindow.subsampleSelector = SubsampleSelector(subsampleList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_subsample,
                                               subsampleDefault=subsampleDefault)
        ssLayout = QtGui.QHBoxLayout()
        ssLayout.setAlignment(QtCore.Qt.AlignLeft)
        ssLayout.addWidget(mainWindow.subsampleSelector)
        vboxTop.addLayout(ssLayout)
        mainWindow.subsampleSelector.setAutoFillBackground(True)
        mainWindow.subsampleSelector.setMaximumWidth(alignWidth)
        mainWindow.subsampleSelector.setMinimumWidth(alignWidth)
       
    ## visualization mode selector
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

    ## model mode (type) selector
    if mainWindow.log.log['current_state'] in ['Model']:
        mmDefault = mainWindow.log.log['model_mode']
        btnLabels = ['normal','onefit','pooled','target']
        mmCallback = mainWindow.handle_model_mode_callback
        mainWindow.modelModeSelector = ModelTypeSelector(btnLabels,parent=mainWindow.dockWidget,modelTypeDefault=mmDefault,
                                                         modelTypeCallback=mmCallback)
        rbwLayout = QtGui.QHBoxLayout()
        rbwLayout.setAlignment(QtCore.Qt.AlignLeft)
        rbwLayout.addWidget(mainWindow.modelModeSelector)
        vboxCenter.addLayout(rbwLayout)
        mainWindow.modelModeSelector.setAutoFillBackground(True)
        mainWindow.modelModeSelector.setMaximumWidth(alignWidth)
        mainWindow.modelModeSelector.setMinimumWidth(alignWidth)

    ## model to run selector
    if mainWindow.log.log['current_state'] in ['Model']:
        mtrDefault = mainWindow.log.log['model_to_run']
        btnLabels = ['dpmm','k-means','upload']
        mtrCallback = mainWindow.handle_model_to_run_callback
        mainWindow.modelToRunSelector = ModelToRunSelector(btnLabels,parent=mainWindow.dockWidget,mtrDefault=mtrDefault,
                                                           mtrCallback=mtrCallback)
        rbwLayout = QtGui.QHBoxLayout()
        rbwLayout.setAlignment(QtCore.Qt.AlignLeft)
        rbwLayout.addWidget(mainWindow.modelToRunSelector)
        vboxCenter.addLayout(rbwLayout)
        mainWindow.modelToRunSelector.setAutoFillBackground(True)
        mainWindow.modelToRunSelector.setMaximumWidth(alignWidth)
        mainWindow.modelToRunSelector.setMinimumWidth(alignWidth)
    
    ## more info btn
    if mainWindow.log.log['current_state'] in ['Model']:
        mainWindow.modelSettingsBtn = QtGui.QPushButton("Edit settings")
        mainWindow.modelSettingsBtn.setMaximumWidth(120)
        mainWindow.modelSettingsBtn.setMinimumWidth(120)
        miLayout = QtGui.QHBoxLayout()
        miLayout.setAlignment(QtCore.Qt.AlignCenter)
        miLayout.addWidget(mainWindow.modelSettingsBtn)
        vboxCenter.addLayout(miLayout)

    ## more recreate figures
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Results Navigation']:
        mainWindow.recreateBtn = QtGui.QPushButton("Recreate figures")
        mainWindow.recreateBtn.setMaximumWidth(120)
        mainWindow.recreateBtn.setMinimumWidth(120)
        
        rbLayout = QtGui.QHBoxLayout()
        rbLayout.setAlignment(QtCore.Qt.AlignCenter)
        rbLayout.addWidget(mainWindow.recreateBtn)
        vboxBottom.addLayout(rbLayout)

    ## more info btn
    if mainWindow.log.log['current_state'] in ['Initial','Data Processing','Quality Assurance','Model']:
        mainWindow.moreInfoBtn = QtGui.QPushButton("More info")
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
