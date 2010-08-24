#!/usr/bin/python

from PyQt4 import QtGui

from StageTransitions import *

def create_menubar_toolbar(mainWindow):

    #################################
    # Menu actions
    #################################

    ## file menu actions
    fileNewBulkAction = mainWindow.create_action("New...", mainWindow.create_new_project_bulk,
                                                 QtGui.QKeySequence.New, "filenew", "Create a new project with mulitple files")
    fileOpenAction = mainWindow.create_action("&Open...", mainWindow.open_existing_project,
                                              QtGui.QKeySequence.Open, "fileopen",
                                              "Open an existing project")
    fileSaveAction = mainWindow.create_action("&Save", mainWindow.fileSave,
                                              QtGui.QKeySequence.Save, "filesave", "Save the image")
    fileSaveAsAction = mainWindow.create_action("Save &As...",
                                                mainWindow.fileSaveAs, icon="filesaveas",
                                                tip="Save the project using a new name")
    filePrintAction = mainWindow.create_action("&Print", mainWindow.filePrint,
                                               QtGui.QKeySequence.Print, "fileprint", "Print the current image")
    fileQuitAction = mainWindow.create_action("&Quit", mainWindow.close,
                                              "Ctrl+Q", "filequit", "Close the application")
    ## edit menu actions
    editDataProcessing= mainWindow.create_action("&Data Processing", lambda a=mainWindow: mainWindow.move_to_data_processing(a),
                                                 "Ctrl+D", "dataprocessing", "Move to Data Processing")
    editQualityAssurance= mainWindow.create_action("Quality &Assurance", lambda a=mainWindow: move_to_quality_assurance(a),
                                                   "Ctrl+A", "qualityassurance", "Move to Quality Assurance")
    editModel= mainWindow.create_action("&Model", lambda a=mainWindow: move_to_model(a),
                                        "Ctrl+M", "model", "Move to Model")
    editResultsNavigation = mainWindow.create_action("&Results Navigation", lambda a=mainWindow: move_to_results_navigation(a),
                                                     "Ctrl+R", "resultsnavigation", "Move to Results Navigation")
    ## tool menu actions
    OneDimViewerAction = mainWindow.create_action("One Dimenstional Viewer ", lambda a=mainWindow: move_to_one_dim_viewer(a))
    ResultsHeatmapSummary = mainWindow.create_action("Results Heatmap Summary ", lambda a=mainWindow: move_to_results_heatmap_summary(a))

    ## help menu actions
    helpAboutAction = mainWindow.create_action("&About %s"%mainWindow.controller.appName,
                                         mainWindow.helpAbout)
    helpHelpAction = mainWindow.create_action("&Help", mainWindow.helpHelp,
                                        QtGui.QKeySequence.HelpContents)

    #################################
    # Menu definations
    #################################

    ## define file menu
    mainWindow.fileMenu = mainWindow.menuBar().addMenu("&File")
    mainWindow.fileMenuActions = (fileNewBulkAction,fileOpenAction,
                                  fileSaveAction, fileSaveAsAction, None,
                                  filePrintAction, fileQuitAction)
    mainWindow.addActions(mainWindow.fileMenu,mainWindow.fileMenuActions)

    ## define edit menu
    editMenu = mainWindow.menuBar().addMenu("&Edit")
    mirrorMenu = editMenu.addMenu(QtGui.QIcon(":/editmirror.png"),"&Go to")
    mainWindow.addActions(mirrorMenu, (editDataProcessing,editQualityAssurance, editModel, editResultsNavigation))

    ## define tool menu
    mainWindow.toolMenu = mainWindow.menuBar().addMenu("&Tools")
    mainWindow.toolMenuActions = (None,OneDimViewerAction, ResultsHeatmapSummary)
    mainWindow.addActions(mainWindow.toolMenu,mainWindow.toolMenuActions)

    ## define help menu
    helpMenu = mainWindow.menuBar().addMenu("&Help")
    mainWindow.addActions(helpMenu, (helpAboutAction, helpHelpAction))
    mainWindow.addActions(mainWindow.mainWidget,(editDataProcessing,
                                     editQualityAssurance,editModel,
                                     editResultsNavigation))


