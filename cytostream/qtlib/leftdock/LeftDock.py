#!/usr/bin/python

'''
Cytostream
LeftDock 

based on the state these functions control which widget appear in the left dock

'''

__author__ = "A. Richards"

import sys,os,ast
from PyQt4 import QtGui,QtCore
from cytostream import get_fcs_file_names,get_saved_gate_names
from cytostream.qtlib import FileSelector,SubsampleSelector,VizModeSelector,ModelToRunSelector
from cytostream.qtlib import PlotSelector,PlotTickControls,ChannelSelector,ClusterSelector
from cytostream.qtlib import GateSelector

def remove_left_dock(mainWindow):
    mainWindow.removeDockWidget(mainWindow.mainDockWidget)

def add_left_dock(mainWindow):
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.fileSelector != None and mainWindow.log.log['selected_file'] == None:
        mainWindow.set_selected_file()

    ## get file list and plot list
    fileList = get_fcs_file_names(mainWindow.controller.homeDir)
    if len(fileList) > 0:
        masterChannelList = mainWindow.model.get_master_channel_list()

    numPlots = int(mainWindow.log.log['num_subplots'])
    plotList = [str(i+1) for i in range(numPlots)]

    ## declare variables
    subsampleList = ["1e04", "7.5e04","1.5e05","All Data"]
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

    #if mainWindow.log.log['current_state'] == 'Initial':
    #    pass
    #elif mainWindow.log.log['current_state'] == 'Quality Assurance':
    #    excludedFiles = mainWindow.log.log['excluded_files_qa']
    #    subsampleDefault = mainWindow.log.log['subsample_qa']
    #else:
    #    excludedFiles = mainWindow.log.log['excluded_files_analysis']
    #    subsampleDefault = mainWindow.log.log['subsample_analysis']

    ## check to see if fileList needs adjusting
    if type(excludedFiles) == type([]) and len(excludedFiles) > 0:
        for f in excludedFiles:
            fileList.remove(f)

    ## plot selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results']:
        mainWindow.plotSelector = PlotSelector(plotList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.plot_selector_callback,
                                               plotDefault=mainWindow.log.log['selected_plot'])
        psLayout = QtGui.QHBoxLayout()
        psLayout.setAlignment(QtCore.Qt.AlignLeft)
        psLayout.addWidget(mainWindow.plotSelector)
        vboxTop.addLayout(psLayout)
        mainWindow.plotSelector.setAutoFillBackground(True)
        mainWindow.plotSelector.setMaximumWidth(alignWidth)
        mainWindow.plotSelector.setMinimumWidth(alignWidth)

    ## file selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results']:
        mainWindow.fileSelector = FileSelector(fileList,parent=mainWindow.dockWidget,mainWindow=mainWindow,
                                               fileDefault=mainWindow.controller.log.log['selected_file'])
        fsLayout = QtGui.QHBoxLayout()
        fsLayout.setAlignment(QtCore.Qt.AlignLeft)
        fsLayout.addWidget(mainWindow.fileSelector)
        vboxTop.addLayout(fsLayout)
        mainWindow.fileSelector.setAutoFillBackground(True)
        mainWindow.fileSelector.setMaximumWidth(alignWidth)
        mainWindow.fileSelector.setMinimumWidth(alignWidth)
       
    ## cluster selector
    if mainWindow.controller.log.log['current_state'] in ['Model Results']:
        modelRunID = mainWindow.controller.log.log['selected_model']
        if mainWindow.controller.uniqueLabels.has_key(modelRunID) == False:
            uniqueLabels = set([])
            for fileName in fileList:
                fileLabels = mainWindow.controller.get_labels(fileName,modelRunID,modelType='components',
                                                              subsample='original',getLog=False)
                uniqueLabels.update(set(fileLabels.tolist()))
            uniqueLabels = list(uniqueLabels)
            uniqueLabels.sort()
            mainWindow.controller.uniqueLabels[modelRunID] = uniqueLabels

        uniqueLabels = mainWindow.controller.uniqueLabels[modelRunID]
        mainWindow.clusterSelector = ClusterSelector(uniqueLabels,parent=mainWindow.dockWidget,mainWindow=mainWindow)
        csLayout = QtGui.QHBoxLayout()
        csLayout.setAlignment(QtCore.Qt.AlignLeft)
        csLayout.addWidget(mainWindow.clusterSelector)
        vboxTop.addLayout(csLayout)
        mainWindow.clusterSelector.setAutoFillBackground(True)
        mainWindow.clusterSelector.setMaximumWidth(alignWidth)
        mainWindow.clusterSelector.setMinimumWidth(alignWidth)
    
    ## gate selector
    if mainWindow.controller.log.log['current_state'] in ['Model Results']:
        
        gateList = get_saved_gate_names(mainWindow.controller.homeDir)
        if len(gateList) > 0:
            mainWindow.gateSelector = GateSelector(gateList,parent=mainWindow.dockWidget,mainWindow=mainWindow)
            mainWindow.gsScrollArea = QtGui.QScrollArea()
            mainWindow.gsScrollArea.setWidget(mainWindow.gateSelector)
            mainWindow.gsScrollArea.setAlignment(QtCore.Qt.AlignCenter)

            gsLayout = QtGui.QHBoxLayout()
            gsLayout.setAlignment(QtCore.Qt.AlignLeft)
            #gsLayout.addWidget(mainWindow.gateSelector)
            gsLayout.addWidget(mainWindow.gsScrollArea)
            vboxTop.addLayout(gsLayout)
            mainWindow.gateSelector.setAutoFillBackground(True)
            mainWindow.gateSelector.setMaximumWidth(alignWidth)
            mainWindow.gateSelector.setMinimumWidth(alignWidth)

    ## subsample selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results','Analysis Results']:

        if mainWindow.log.log['current_state'] == 'Data Processing':
            subsampleDefault = mainWindow.controller.log.log['subsample_qa']
        else:
            subsampleDefault = mainWindow.controller.log.log['subsample_analysis']

        mainWindow.subsampleSelector = SubsampleSelector(subsampleList,parent=mainWindow.dockWidget,
                                                         mainWindow=mainWindow,subsampleDefault=subsampleDefault)
        ssLayout = QtGui.QHBoxLayout()
        ssLayout.setAlignment(QtCore.Qt.AlignLeft)
        ssLayout.addWidget(mainWindow.subsampleSelector)
        vboxTop.addLayout(ssLayout)
        mainWindow.subsampleSelector.setAutoFillBackground(True)
        mainWindow.subsampleSelector.setMaximumWidth(alignWidth)
        mainWindow.subsampleSelector.setMinimumWidth(alignWidth)

    ## channel selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results','Analysis Results']:
        channelList = mainWindow.controller.fileChannels

        if mainWindow.controller.log.log['selected_plot'] == None:
            mainWindow.controller.log.log['selected_plot'] = '1'
            mainWindow.controller.save()
        if mainWindow.controller.log.log['selected_plot'] == '*':
            selectedPlot = '1'
        else:
            selectedPlot = mainWindow.controller.log.log['selected_plot']

        selectedPlot = int(selectedPlot)

        channel1Default = mainWindow.controller.log.log['plots_to_view_channels'][selectedPlot - 1][0]
        channel2Default = mainWindow.controller.log.log['plots_to_view_channels'][selectedPlot - 1][1]
        mainWindow.channelSelector = ChannelSelector(channelList,parent=mainWindow.dockWidget,mainWindow=mainWindow,
                                                     channel1Default=channel1Default,channel2Default=channel2Default)
        csLayout = QtGui.QHBoxLayout()
        csLayout.setAlignment(QtCore.Qt.AlignLeft)
        csLayout.addWidget(mainWindow.channelSelector)
        vboxTop.addLayout(csLayout)
        mainWindow.channelSelector.setAutoFillBackground(True)
        mainWindow.channelSelector.setMaximumWidth(alignWidth)
        mainWindow.channelSelector.setMinimumWidth(alignWidth)

    ## PlotTickControls
    scaleDefault = ast.literal_eval(str(mainWindow.controller.log.log['use_scaled_plots']))
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results','Analysis Results']:
        mainWindow.plotTickControls = PlotTickControls(parent=mainWindow.dockWidget,mainWindow=mainWindow,
                                                       scaleDefault=scaleDefault)
        ptcLayout = QtGui.QHBoxLayout()
        ptcLayout.setAlignment(QtCore.Qt.AlignLeft)
        ptcLayout.addWidget(mainWindow.plotTickControls)
        vboxTop.addLayout(ptcLayout)
        mainWindow.plotTickControls.setAutoFillBackground(True)
        mainWindow.plotTickControls.setMaximumWidth(alignWidth)
        mainWindow.plotTickControls.setMinimumWidth(alignWidth)

    ## visualization mode selector
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results','Analysis Results']:
        visualizationMode = mainWindow.controller.log.log['visualization_mode']
        btnLabels = ['thumbnails','plot',]
        mainWindow.vizModeSelector = VizModeSelector(btnLabels,parent=mainWindow.dockWidget,mainWindow=mainWindow,
                                                     modeDefault=visualizationMode,numSubplotsDefault=mainWindow.log.log['num_subplots'])
        vmsLayout = QtGui.QHBoxLayout()
        vmsLayout.setAlignment(QtCore.Qt.AlignLeft)
        vmsLayout.addWidget(mainWindow.vizModeSelector)
        vboxTop.addLayout(vmsLayout)
        mainWindow.vizModeSelector.setAutoFillBackground(True)
        mainWindow.vizModeSelector.setMaximumWidth(alignWidth)
        mainWindow.vizModeSelector.setMinimumWidth(alignWidth)

    ## model to run selector
    if mainWindow.log.log['current_state'] in ['Model Run']:
        mtrDefault = mainWindow.log.log['model_to_run']
        mainWindow.modelToRunSelector = ModelToRunSelector(parent=mainWindow.dockWidget,mainWindow=mainWindow)
        mtrLayout = QtGui.QHBoxLayout()
        mtrLayout.setAlignment(QtCore.Qt.AlignLeft)
        mtrLayout.addWidget(mainWindow.modelToRunSelector)
        vboxTop.addLayout(mtrLayout)
        mainWindow.modelToRunSelector.setAutoFillBackground(True)
        mainWindow.modelToRunSelector.setMaximumWidth(alignWidth)
        mainWindow.modelToRunSelector.setMinimumWidth(alignWidth)
    
    ## more info btn
    if mainWindow.log.log['current_state'] in ['Model Run','Sample Alignment']:
        mainWindow.modelSettingsBtn = QtGui.QPushButton("Edit settings")
        mainWindow.modelSettingsBtn.setMaximumWidth(140)
        mainWindow.modelSettingsBtn.setMinimumWidth(140)
        msbLayout = QtGui.QHBoxLayout()
        msbLayout.setAlignment(QtCore.Qt.AlignCenter)
        msbLayout.addWidget(mainWindow.modelSettingsBtn)
        msBtnFn = mainWindow.transitions.move_to_preferences
        mainWindow.connect(mainWindow.modelSettingsBtn,QtCore.SIGNAL('clicked()'),msBtnFn)
        vboxCenter.addLayout(msbLayout)

    ## more recreate figures
    if mainWindow.log.log['current_state'] in ['Quality Assurance']:
        mainWindow.recreateBtn = QtGui.QPushButton("Recreate thumbs")
        mainWindow.recreateBtn.setMaximumWidth(140)
        mainWindow.recreateBtn.setMinimumWidth(140)
        rbLayout = QtGui.QHBoxLayout()
        rbLayout.setAlignment(QtCore.Qt.AlignCenter)
        rbLayout.addWidget(mainWindow.recreateBtn)
        mainWindow.connect(mainWindow.recreateBtn,QtCore.SIGNAL('clicked()'),mainWindow.recreate_figures)
        vboxBottom.addLayout(rbLayout)

    ## models run btn
    if mainWindow.log.log['current_state'] in ['Model Rusults']:
        mainWindow.modelsRunBtn = QtGui.QPushButton("Models run")
        mainWindow.modelsRunBtn.setMaximumWidth(140)
        mainWindow.modelsRunBtn.setMinimumWidth(140)
        mrbLayout = QtGui.QHBoxLayout()
        mrbLayout.setAlignment(QtCore.Qt.AlignCenter)
        mrbLayout.addWidget(mainWindow.modelsRunBtn)
        vboxBottom.addLayout(mrbLayout)
        modelsRunBtnFn = mainWindow.models_run_btn_callback
        mainWindow.connect(mainWindow.modelsRunBtn,QtCore.SIGNAL('clicked()'),modelsRunBtnFn)

    ## save images
    if mainWindow.log.log['current_state'] in ['Quality Assurance','Model Results']:
        mainWindow.saveImgsBtn = QtGui.QPushButton("Save figures")
        mainWindow.saveImgsBtn.setMaximumWidth(140)
        mainWindow.saveImgsBtn.setMinimumWidth(140)
        sibLayout = QtGui.QHBoxLayout()
        sibLayout.setAlignment(QtCore.Qt.AlignCenter)
        sibLayout.addWidget(mainWindow.saveImgsBtn)
        vboxBottom.addLayout(sibLayout)
        mainWindow.saveImgsBtn.setEnabled(False)
        saveImgsBtnFn = mainWindow.handle_save_images_callback
        mainWindow.connect(mainWindow.saveImgsBtn,QtCore.SIGNAL('clicked()'),saveImgsBtnFn)

    ## more info btn
    if mainWindow.log.log['current_state'] in ['Initial','Data Processing','Quality Assurance','Model Run', 
                                               'Model Results','File Alignment']:
        mainWindow.moreInfoBtn = QtGui.QPushButton("More info")
        mainWindow.moreInfoBtn.setMaximumWidth(140)
        mainWindow.moreInfoBtn.setMinimumWidth(140)
        miLayout = QtGui.QHBoxLayout()
        miLayout.setAlignment(QtCore.Qt.AlignCenter)
        miLayout.addWidget(mainWindow.moreInfoBtn)
        vboxBottom.addLayout(miLayout)
        moreInfoBtnFn = mainWindow.show_more_info
        mainWindow.connect(mainWindow.moreInfoBtn,QtCore.SIGNAL('clicked()'),moreInfoBtnFn)

    ## finalize alignments
    vbl.addLayout(vboxTop)
    vbl.addLayout(vboxCenter)
    vbl.addLayout(vboxBottom)
    mainWindow.dockWidget.setLayout(vbl)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)
