#!/usr/bin/python

'''
Cytostream
LeftDock        
Adam Richards
adam.richards@stat.duke.edu
                   
'''

import sys,os
from PyQt4 import QtGui,QtCore

if hasattr(sys,'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)

sys.path.append(os.path.join(baseDir,'..'))

from FileControls import *
from FileSelector import FileSelector
from DataProcessingDock1 import DataProcessingDock1
from DataProcessingDock2 import DataProcessingDock2
from QualityAssuranceDock import QualityAssuranceDock
from ModelDock import ModelDock
from ResultsNavigationDock import ResultsNavigationDock
from OneDimViewerDock import OneDimViewerDock

def remove_left_dock(mainWindow):
    mainWindow.removeDockWidget(mainWindow.mainDockWidget)

def add_left_dock(mainWindow):
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.fileSelector != None and mainWindow.log.log['selected_file'] == None:
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
    
    # setup alignments
    hbl = QtGui.QVBoxLayout(mainWindow.dockWidget)
    
    hbl1 = QtGui.QHBoxLayout()
    hbl1.setAlignment(QtCore.Qt.AlignCenter)
    vbl1 = QtGui.QVBoxLayout()
    vbl1.addLayout(hbl1)
    vbl1.setAlignment(QtCore.Qt.AlignTop)
    
    hbl2 = QtGui.QHBoxLayout()
    hbl2.setAlignment(QtCore.Qt.AlignCenter)
    vbl2 = QtGui.QVBoxLayout()
    vbl2.addLayout(hbl2)
    vbl2.setAlignment(QtCore.Qt.AlignCenter)
 
    hbl3 = QtGui.QHBoxLayout()
    hbl3.setAlignment(QtCore.Qt.AlignCenter)
    vbl3 = QtGui.QVBoxLayout()
    vbl3.addLayout(hbl3)
    vbl3.setAlignment(QtCore.Qt.AlignBottom)

    widgetWidth = 0.15 * mainWindow.screenWidth
    mainWindow.dockWidget.setMaximumWidth(widgetWidth)
    mainWindow.dockWidget.setMinimumWidth(widgetWidth)

    ## check to see if fileList needs adjusting
    if mainWindow.log.log['currentState'] in ['Results Navigation']:
        showModelSelector = True
        modelsRun = get_models_run(mainWindow.controller.homeDir,mainWindow.possibleModels)
    else:
        showModelSelector = False
        modelsRun = None

    if mainWindow.log.log['current_state'] == 'qa':
        excludedFiles = mainWindow.log.log['excluded_files_qa']
        subsampleDefault = mainWindow.log.log['subsample_qa']
    else:
        excludedFiles = mainWindow.log.log['excluded_files_analysis']
        subsampleDefault = mainWindow.log.log['subsample_analysis']

    ## check to see if fileList needs adjusting
    if type(excludedFiles) == type([]) and len(excludedFiles) > 0:
        for f in excludedFiles:
            fileList.remove(f)

        mainWindow.log.log['selected_file'] = fileList[0]

    ## file selector
    if mainWindow.log.log['current_state'] in ['Data Processing','Quality Assurance','Model','Results Navigation']:
        mainWindow.fileSelector = FileSelector(fileList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_file,
                                               fileDefault=mainWindow.log.log['selected_file'],
                                               showModelSelector=showModelSelector,modelsRun=modelsRun)
        mainWindow.fileSelector.setAutoFillBackground(True)
        vbl1.addWidget(mainWindow.fileSelector)
        
    ## data processing
    if mainWindow.log.log['current_state'] == "Data Processing":
        mainWindow.dock1 = DataProcessingDock1(masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                              contBtnFn=None,subsetDefault=subsampleDefault)
        callBackfn = mainWindow.handle_data_processing_mode_callback
        mainWindow.dock2 = DataProcessingDock2(callBackfn,parent=mainWindow.dockWidget,default=mainWindow.log.log['data_processing_mode'])
        mainWindow.dock1.setAutoFillBackground(True)
        mainWindow.dock2.setAutoFillBackground(True)
        hbl2.addWidget(mainWindow.dock2)
        hbl3.addWidget(mainWindow.dock1)

    ## quality assurance
    elif mainWindow.log.log['current_state'] == "Quality Assurance":
        
        mainWindow.dock = QualityAssuranceDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                               contBtnFn=None,subsetDefault=subsampleDefault,viewAllFn=mainWindow.display_thumbnails)
        vbl3.addWidget(mainWindow.dock)
        mainWindow.dock.setAutoFillBackground(True)
   
    ## model
    elif mainWindow.log.log['current_state'] == "Model":
        modelList = ['DPMM','K-means']
        mainWindow.dock = ModelDock(modelList,parent=mainWindow.dockWidget,componentsFn=mainWindow.set_num_components)
        mainWindow.dock.setAutoFillBackground(True)
        vbl3.addWidget(mainWindow.dock)

    ## results navigation
    elif mainWindow.log.log['current_state'] == "Results Navigation":
        mainWindow.dock = ResultsNavigationDock(mainWindow.resultsModeList,masterChannelList,parent=mainWindow.dockWidget,
                                                resultsModeFn=mainWindow.set_selected_results_mode,
                                                resultsModeDefault=mainWindow.log.log['results_mode'],viewAllFn=mainWindow.display_thumbnails,
                                                infoBtnFn=mainWindow.show_model_log_info)
        mainWindow.dock.setAutoFillBackground(True)
        vbl3.addWidget(mainWindow.dock)

    ## one dimensional viewer
    if mainWindow.log.log['current_state'] == 'OneDimViewer':
        mainWindow.dock = OneDimViewerDock(fileList,masterChannelList,callBack=mainWindow.odv.paint)
        mainWindow.dock.setAutoFillBackground(True)
        vbl1.addWidget(mainWindow.dock)
        
    ## stages with thumbnails
    if mainWindow.log.log['current_state'] in ['Quality Assurance', 'Results Navigation']:
        mainWindow.fileSelector.set_refresh_thumbs_fn(mainWindow.display_thumbnails)

    ## finalize alignments
    hbl.addLayout(vbl1)
    hbl.addLayout(vbl2)
    hbl.addLayout(vbl3)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)
