#!/usr/bin/python

from PyQt4 import QtGui,QtCore
from cytostream import *
from cytostream import FileSelector

def add_left_dock(mainWindow):
    if mainWindow.dockWidget != None:
        mainWindow.clear_dock()

    if mainWindow.fileSelector != None and mainWindow.log.log['selectedFile'] == None:
        mainWindow.set_selected_file()

    masterChannelList = mainWindow.model.get_master_channel_list()
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    transformList = ['transform1', 'transform2', 'transform3']
    compensationList = ['compensation1', 'compensation2']
    subsetList = ["1e3", "1e4","5e4","All Data"]

    mainWindow.mainDockWidget = QtGui.QDockWidget(mainWindow.controller.projectID, mainWindow)
    mainWindow.mainDockWidget.setObjectName("MainDockWidget")
    mainWindow.mainDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
    
    mainWindow.dockWidget = QtGui.QWidget(mainWindow)
    palette = mainWindow.dockWidget.palette()
    role = mainWindow.dockWidget.backgroundRole()
    palette.setColor(role, QtGui.QColor('black'))
    mainWindow.dockWidget.setPalette(palette)
    mainWindow.dockWidget.setAutoFillBackground(True)
    hbl2 = QtGui.QHBoxLayout()
    hbl2.setAlignment(QtCore.Qt.AlignTop)
    mainWindow.dockWidget.setMaximumWidth(0.15 * mainWindow.screenWidth)
    mainWindow.dockWidget.setMinimumWidth(0.15 * mainWindow.screenWidth)

    if mainWindow.log.log['currentState'] in ['Results Navigation']:
        showModelSelector = True
        modelsRun = get_models_run(mainWindow.controller.homeDir,mainWindow.possibleModels)
    else:
        showModelSelector = False
        modelsRun = None

    if mainWindow.log.log['currentState'] in ['Data Processing','Quality Assurance','Model','Results Navigation']:
        mainWindow.fileSelector = FileSelector(fileList,parent=mainWindow.dockWidget,selectionFn=mainWindow.set_selected_file,fileDefault=mainWindow.log.log['selectedFile'],
                                             showModelSelector=showModelSelector,modelsRun=modelsRun)
        mainWindow.fileSelector.setAutoFillBackground(True)
        hbl2.addWidget(mainWindow.fileSelector)

        subsamplingDefault = mainWindow.log.log['subsample']

    if mainWindow.log.log['currentState'] == "Data Processing":
        mainWindow.dock = DataProcessingDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                           contBtnFn=lambda runNew=True: mainWindow.move_to_quality_assurance(runNew),subsetDefault=subsamplingDefault)
    elif mainWindow.log.log['currentState'] == "Quality Assurance":
        mainWindow.dock = QualityAssuranceDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                             contBtnFn=mainWindow.move_to_model,subsetDefault=subsamplingDefault,viewAllFn=mainWindow.display_thumbnails)
    elif mainWindow.log.log['currentState'] == "Model":
        modelList = ['DPMM','K-means']
        mainWindow.dock = ModelDock(modelList,parent=mainWindow.dockWidget,contBtnFn=mainWindow.move_to_results_navigation,componentsFn=mainWindow.set_num_components)
    elif mainWindow.log.log['currentState'] == "Results Navigation":
        mainWindow.dock = ResultsNavigationDock(mainWindow.resultsModeList,masterChannelList,parent=mainWindow.dockWidget,resultsModeFn=mainWindow.set_selected_results_mode,
                                          resultsModeDefault=mainWindow.log.log['resultsMode'],viewAllFn=mainWindow.display_thumbnails,
                                          infoBtnFn=mainWindow.show_model_log_info)
    if mainWindow.log.log['currentState'] in ['Quality Assurance', 'Results Navigation']:
        mainWindow.fileSelector.set_refresh_thumbs_fn(mainWindow.display_thumbnails)

    if mainWindow.log.log['currentState'] == 'OneDimViewer':
        mainWindow.dock = OneDimViewerDock(fileList,masterChannelList,callBack=mainWindow.odv.paint)

    mainWindow.dock.setAutoFillBackground(True)
    hbl1 = QtGui.QHBoxLayout()  

    ## finalize dock layout 
    if mainWindow.log.log['currentState'] == 'OneDimViewer':
        hbl1.setAlignment(QtCore.Qt.AlignTop)
    else:
        hbl1.setAlignment(QtCore.Qt.AlignBottom)
    
    hbl1.addWidget(mainWindow.dock)
    vbl = QtGui.QVBoxLayout(mainWindow.dockWidget)
    vbl.addLayout(hbl2)
    vbl.addLayout(hbl1)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)
