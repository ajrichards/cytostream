#!/usr/bin/python

import sys,re,os
from PyQt4 import QtGui,QtCore
from cytostream.qtlib import remove_left_dock, add_left_dock

def add_actions(mainWindow, target, actions):
    '''
    add menu actions
    
    '''
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)

def create_action(mainWindow, text, slot=None, shortcut=None, icon=None,
                  tip=None, checkable=False, signal="triggered()"):
    
    '''
    create menu actions

    '''

    action = QtGui.QAction(text, mainWindow)

    if icon is not None:
        iconPath = os.path.join(mainWindow.controller.baseDir,"qtlib","images",icon+".png") 
        if os.path.isfile(iconPath) == True:
            action.setIcon(QtGui.QIcon(iconPath))
        else:
            print "WARNING: bad icon specified", icon + ".png"

    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        mainWindow.connect(action, QtCore.SIGNAL(signal), slot)
    if checkable:
        action.setCheckable(True)
    return action

def create_menubar_toolbar(mainWindow):

    '''
    create menubar where each toolbar contains the actions
    
    '''

    ## file menu actions
    fileNewAction = create_action(mainWindow,"New...", slot=mainWindow.create_new_project,
                                  shortcut=QtGui.QKeySequence.New,icon="filenew", tip="Create a new project")
    fileOpenAction = create_action(mainWindow,"&Open...", mainWindow.open_existing_project,
                                   QtGui.QKeySequence.Open, "fileopen",
                                   "Open an existing project")
    fileSaveAction = create_action(mainWindow,"&Save", mainWindow.fileSave,
                                   QtGui.QKeySequence.Save, "filesave", "Save the image")
    fileSaveAsAction = create_action(mainWindow,"Save &As...",
                                     mainWindow.fileSaveAs, icon="filesaveas",
                                     tip="Save the project using a new name")
    filePrintAction = create_action(mainWindow,"&Print", mainWindow.filePrint,
                                    QtGui.QKeySequence.Print, "fileprint", "Print the current image")
    fileQuitAction = create_action(mainWindow,"&Quit", mainWindow.close,
                                   "Ctrl+Q", "filequit", "Close the application")
    ## edit menu actions
    editDataProcessing= create_action(mainWindow,"&Data Processing", lambda a=mainWindow: mainWindow.move_to_data_processing(a),
                                                 "Ctrl+D", "dataprocessing", "Move to Data Processing")
    editQualityAssurance= create_action(mainWindow,"Quality &Assurance", lambda a=mainWindow: move_to_quality_assurance(a),
                                                   "Ctrl+A", "qualityassurance", "Move to Quality Assurance")
    editModel= create_action(mainWindow,"&Model", lambda a=mainWindow: move_to_model(a),
                             "Ctrl+M", "model", "Move to Model")
    editResultsNavigation = create_action(mainWindow,"&Results Navigation", lambda a=mainWindow: move_to_results_navigation(a),
                                          "Ctrl+R", "resultsnavigation", "Move to Results Navigation")
    ## tool menu actions
    OneDimViewerAction = create_action(mainWindow,"One Dimenstional Viewer ", lambda a=mainWindow: move_to_one_dim_viewer(a))
    ResultsHeatmapSummary = create_action(mainWindow,"Results Heatmap Summary ", lambda a=mainWindow: move_to_results_heatmap_summary(a))

    ## help menu actions
    helpAboutAction = create_action(mainWindow,"&About %s"%mainWindow.controller.appName,
                                    mainWindow.helpAbout)
    helpHelpAction = create_action(mainWindow,"&Help", mainWindow.helpHelp,
                                   QtGui.QKeySequence.HelpContents)

    #################################
    # Menu definations
    #################################

    ## define file menu
    mainWindow.fileMenu = mainWindow.menuBar().addMenu("&File")
    mainWindow.fileMenuActions = (fileNewAction,fileOpenAction,
                                  fileSaveAction, fileSaveAsAction, None,
                                  filePrintAction, fileQuitAction)
    add_actions(mainWindow,mainWindow.fileMenu,mainWindow.fileMenuActions)

    ## define edit menu
    editMenu = mainWindow.menuBar().addMenu("&Edit")
    mirrorMenu = editMenu.addMenu(QtGui.QIcon(":/editmirror.png"),"&Go to")
    add_actions(mainWindow,mirrorMenu, (editDataProcessing,editQualityAssurance, editModel, editResultsNavigation))

    ## define tool menu
    mainWindow.toolMenu = mainWindow.menuBar().addMenu("&Tools")
    mainWindow.toolMenuActions = (None,OneDimViewerAction, ResultsHeatmapSummary)
    add_actions(mainWindow,mainWindow.toolMenu,mainWindow.toolMenuActions)

    ## define help menu
    helpMenu = mainWindow.menuBar().addMenu("&Help")
    add_actions(mainWindow,helpMenu, (helpAboutAction, helpHelpAction))
