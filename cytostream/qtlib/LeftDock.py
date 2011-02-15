#!/usr/bin/python

'''
Cytostream
LeftDock 
                  
'''

__author__ = "A. Richards"

import sys,os
from PyQt4 import QtGui,QtCore

from cytostream import get_fcs_file_names
from cytostream.qtlib import FileSelector,SubsetSelector

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
    hbl = QtGui.QVBoxLayout(mainWindow.dockWidget)
    
    hboxTop = QtGui.QHBoxLayout()
    hboxTop.setAlignment(QtCore.Qt.AlignCenter)
    vboxTop = QtGui.QVBoxLayout()
    vboxTop.addLayout(hboxTop)
    vboxTop.setAlignment(QtCore.Qt.AlignTop)
    
    hboxCenter = QtGui.QHBoxLayout()
    hboxCenter.setAlignment(QtCore.Qt.AlignCenter)
    vboxCenter = QtGui.QVBoxLayout()
    vboxCenter.addLayout(hboxCenter)
    vboxCenter.setAlignment(QtCore.Qt.AlignCenter)
 
    hboxBottom = QtGui.QHBoxLayout()
    hboxBottom.setAlignment(QtCore.Qt.AlignCenter)
    vboxBottom = QtGui.QVBoxLayout()
    vboxBottom.addLayout(hboxBottom)
    vboxBottom.setAlignment(QtCore.Qt.AlignBottom)

    widgetWidth = 0.13 * mainWindow.screenWidth
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
                                               fileDefault=mainWindow.log.log['selected_file'],
                                               showModelSelector=showModelSelector,modelsRun=modelsRun)
        mainWindow.fileSelector.setAutoFillBackground(True)
        hboxTop.addWidget(mainWindow.fileSelector)
        
    ## subset selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance']:

        if mainWindow.log.log['current_state'] == 'Data Processing':
            subsetDefault = mainWindow.log.log['subsample_qa']
        else:
            subsetDefault = mainWindow.log.log['subsample_analysis']

        mainWindow.subsetSelector = SubsetSelector(subsetList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_subsample,
                                               subsetDefault=subsetDefault)

        mainWindow.subsetSelector.setAutoFillBackground(True)
        hboxTop.addWidget(mainWindow.subsetSelector)

    ## more recreate figures
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Results Navigation']:
        mainWindow.recreateBtn = QtGui.QPushButton("recreate figures")
        mainWindow.recreateBtn.setMaximumWidth(100)
        hboxBottom.addWidget(mainWindow.recreateBtn)

    ## more info btn
    if mainWindow.log.log['current_state'] in ['Initial','Data Processing','Quality Assurance']:
        mainWindow.moreInfoBtn = QtGui.QPushButton("more info")
        mainWindow.moreInfoBtn.setMaximumWidth(100)
        hboxBottom.addWidget(mainWindow.moreInfoBtn)

    ## finalize alignments
    hbl.addLayout(vboxTop)
    hbl.addLayout(vboxCenter)
    hbl.addLayout(vboxBottom)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)
