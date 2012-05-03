import sys,os,re,cPickle,time,ast
from PyQt4 import QtCore, QtGui

import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib import rc
rc('text', usetex=False)


from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.patches import Polygon, CirclePolygon
import matplotlib.cm as cm
from matplotlib.mlab import griddata

from matplotlib.lines import Line2D
from cytostream import Model, Logger, get_fcs_file_names 
from cytostream.tools import get_all_colors, Centroids, draw_plot
from cytostream.tools import DrawGateInteractor, PolyGateInteractor, get_fontsize, get_fontname
from cytostream.qtlib import RadioBtnWidget

class CytostreamPlotter(QtGui.QWidget):
    '''
    wrapper class that handles nearly all plotting in cytostream
    class is also stand alone -- working outside the cytostream environment
    '''

    def __init__(self,fileNameList,eventsList,channelList,channelDict,
                 drawState='heat',parent=None,background=True,selectedChannel1=0,
                 selectedChannel2=1,mainWindow=None,uniqueLabels=None,
                 enableGating=False,homeDir=None,compactMode=False,labelList=None,
                 minNumEvents=3,showNoise=False,subsample=70000,numSubplots=1,
                 axesLabels=True,plotTitle=None,useSimple=False,dpi=100,
                 transform='logicle',useScaled=False,modelRunID='run1',subplotNum=1):
        '''
        constructor

           INPUT:
               fileNameList <- a list of file names
               eventsList   <- a list of np.array [n,d] correpsonding to fileNameList
               fileChannels <- a list of file channels
        '''

        ## initialize
        QtGui.QWidget.__init__(self,parent)

        if parent == None:
            self.parent = self
        else:
            self.parent = parent
        
        ## required vaiables
        self.fileNameList = fileNameList
        self.eventsList = eventsList
        self.channelList = channelList
        self.channelDict = channelDict

        ## optional variables
        self.drawState = drawState.lower()
        self.background = background
        self.selectedChannel1 = selectedChannel1
        self.selectedChannel2 = selectedChannel2
        self.mainWindow = mainWindow
        self.uniqueLabels = uniqueLabels
        self.enableGating = enableGating
        self.homeDir = homeDir
        self.axesLabels = axesLabels
        self.compactMode = compactMode
        self.labelList = labelList
        self.minNumEvents = minNumEvents
        self.showNoise = showNoise
        self.numSubplots = numSubplots
        self.subplotNum = subplotNum
        self.plotTitle = plotTitle
        self.plotTitle = re.sub("_"," ",self.plotTitle)

        self.useSimple = useSimple
        self.dpi = dpi
        self.transform = transform
        self.useScaled = ast.literal_eval(str(useScaled))
        self.modelRunID = modelRunID

        ## additional class variables
        self.colors = get_all_colors()
        self.gateInteractor = None
        self.currentGate = 'None'
        self.gateSelector = None
        self.log = None
        self.model = None
        self.markerSize = 1
        self.fontName = get_fontname()
        self.fontSize = get_fontsize(self.numSubplots) 
        self.currentAxesLabels = None
        self.resultsMode = 'components'

        ## variables to be used when class is called for drawing
        self.selectedFileName = None
        self.subsample = subsample
        self.line = None
        self.labels = None
        self.selectedHighlight = None
        self.vizList = ['heat','scatter','contour']

        ## try to initialize a model
        if self.homeDir != None:
            self.model = Model()
            self.model.initialize(self.homeDir)
        else:
            self.model = None
            print "Model could not be initialized -- working as a non-cytostream project"

        ## get max and min number of events
        minNumEvents,maxNumEvents = 0,0

        for i,fileName in enumerate(self.fileNameList):
            events = self.eventsList[i]
            if events.shape[0] > maxNumEvents:
                maxNumEvents = events.shape[0]
            if events.shape[0] < minNumEvents:
                minNumEvents = events.shape[0]
            
        ## handle labels
        if self.modelRunID != None and self.model != None:
            self.labelList = []
            minNumEvents,maxNumEvents = 0,0
            for i,fileName in enumerate(self.fileNameList):                
                statModel, labels = self.model.load_model_results_pickle(fileName,self.modelRunID,modelType=self.resultsMode)
                self.labelList.append(labels)
                modelLog = self.model.load_model_results_log(fileName,self.modelRunID)
                self.subsample = modelLog['subsample']

        ## ensure only maximum num events are shown                  
        maxScatter = 70000
        if self.subsample == 'original' and maxNumEvents > maxScatter:
            self.subsample = maxScatter
            self.subsample = self.model.get_subsample_indices(self.subsample)
            for i in range(len(self.labelList)):
                self.labelList[i] = self.labelList[i][self.subsample]
        ## case where original is smaller than max scatter display
        elif self.subsample == 'original':
            #self.subsample = self.model.get_subsample_indices(self.subsample)
            #self.subsample = np.arange(events.shape[0])
            self.subsample = 'original'
        ## case where we have a subsample but no labels 
        elif self.labelList == None:
            self.subsample = self.model.get_subsample_indices(self.subsample)
        ## case where labels are smaller than subsample (usually means model was run on a subsample) 
        elif len(self.labelList[i]) < self.subsample:
            self.subsample = len(labels)
            self.subsample = self.model.get_subsample_indices(self.subsample)
        ## case where labels and subsample match 
        elif len(self.labelList[i]) == self.subsample:
            self.subsample = self.model.get_subsample_indices(self.subsample)
        else:
            print "WARNING: something unexpected occured in CytostreamPlotter subsample handeling"        

        ## error checking
        if type([]) != type(self.fileNameList):
            print "INPUT ERROR: CytostreamPlotter - fileNameList must be of type list"
        if type([]) != type(self.eventsList):
            print "INPUT ERROR: CytostreamPlotter - eventsList must be of type list"
        if self.labelList != None and type([]) != type(self.labelList):
            print "INPUT ERROR: CytostreamPlotter - labelList must be of type list"
        if len(self.fileNameList) != len(self.eventsList):
            print "INPUT ERROR: CytostreamPlotter - fileNameList and eventsList size mismatch"
        if self.drawState not in self.vizList:
            print "INPUT ERROR: CytostreamPlotter - drawState not valid",self.drawState

        ## save an instance of the centroids to speed up plotting
        if self.labelList != None:
            self.savedCentroids = Centroids()

        ## prepare figure widget for drawing
        self.create_figure_widget()

    def draw(self,cbInt=None,selectedFile=None):
        '''
        args[0]  = ax                       [required]  matplotlib axes
        args[1]  = events                   [required]  np.array (N,D)
        args[2]  = channelList              [required]  ['chan1','chan2']
        args[3]  = channelDict              [required]  {'ssc':0,'fsc':1}
        args[4]  = channel1Index            [required]  int
        args[5]  = channel2Index            [required]  int
        args[6]  = subsample                [required]  float | 'original'
        args[7]  = transform                [required]  'log' | 'logicle'
        args[8]  = labels                   [optional]  np.array (N,1)
        args[9]  = highlight                [optional]  None|clusterID (str(int))
        args[10] = logger                   [optional]  Logger instance
        args[11] = drawState                [optional]  'scatter' | 'heat' | 'contour'
        args[12] = numSubplots              [optional]  int 1-16
        args[13] = axesLabels               [optional]  True | False
        args[14] = plotTitle                [optional]  None | str
        args[15] = showNoise                [optional]  True | False
        args[16] = useSimple                [optional]  False | True
        args[17] = useScaled                [optional]  False | True
        args[18] = isGui                    [optional]  False | True
           
        '''

        ## error checking
        if selectedFile != None:
            self.selectedFileName = selectedFile
        if self.selectedFileName not in self.fileNameList:
            print "ERROR: CytostreamPlotter.draw() - Invalid selectedFile specified", self.selectedFileName

        ## ensure clean axis
        self.ax.clear()
        self.gate_clear_callback()

        ## handle args
        args = [None for i in range(19)]
        args[0] = self.ax
        args[1] = self.eventsList[self.fileNameList.index(self.selectedFileName)]
        self.selectedEvents = self.eventsList[self.fileNameList.index(self.selectedFileName)]
        args[2] = self.channelList
        args[3] = self.channelDict
        args[4] = self.selectedChannel1
        args[5] = self.selectedChannel2
        args[6] = self.subsample
        args[7] = self.transform
        if self.labelList != None:
            args[8] = self.labelList[self.fileNameList.index(self.selectedFileName)]
            self.selectedLabels = self.labelList[self.fileNameList.index(self.selectedFileName)]
        args[9] = self.selectedHighlight
        args[10] = self.log
        args[11] = self.drawState
        args[12] = self.numSubplots
        args[13] = self.axesLabels
        if self.plotTitle == 'default':
            args[14] = self.selectedFileName
        else:
            args[14] = self.plotTitle
        args[15] = self.showNoise
        args[16] = self.useSimple
        args[17] = self.useScaled
        args[18] = True

        ## draw on canvas
        draw_plot(args,parent=self)
        self.fig.canvas.draw()

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()
        self.fig = Figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.figureWidget)
        self.ax = self.fig.add_subplot(111)

        ## set the plot number
        self.subplotLabel = QtGui.QLabel(str(int(self.subplotNum)))

        ## upper controls
        maxWidth = 100
        #channelsLabel = QtGui.QLabel('Channels')
        #self.channel1Selector = QtGui.QComboBox(self)
        #for channel in self.channelList:
        #    self.channel1Selector.addItem(channel)
        #self.channel1Selector.setMaximumWidth(maxWidth)
        #self.channel1Selector.setMinimumWidth(maxWidth)
        #self.channel1Selector.setCurrentIndex(self.selectedChannel1)
        #self.connect(self.channel1Selector, QtCore.SIGNAL('activated(int)'),self.channel1_selector_callback)
        #
        #self.channel2Selector = QtGui.QComboBox(self)
        #for channel in self.channelList:
        #    self.channel2Selector.addItem(channel)
            
        #self.channel2Selector.setMaximumWidth(maxWidth)
        #self.channel2Selector.setMinimumWidth(maxWidth)
        #self.channel2Selector.setCurrentIndex(self.selectedChannel2)
        #self.connect(self.channel2Selector, QtCore.SIGNAL('activated(int)'),self.channel2_selector_callback)

        #if self.fileNameList != None or self.uniqueLabels != None:
        #    additionalSelectorLabel = QtGui.QLabel('Additional Selectors')

        #if self.uniqueLabels != None:                                                                         
        #    self.highlightSelector = QtGui.QComboBox(self)
        #    for hl in ["None"] + self.uniqueLabels:
        #        self.highlightSelector.addItem(str(hl))
        #
        #    self.highlightSelector.setCurrentIndex(0)
        #    self.connect(self.highlightSelector, QtCore.SIGNAL('activated(int)'),self.highlight_selector_callback)
        #    
        #    self.highlightSelector.setMaximumWidth(maxWidth)
        #    self.highlightSelector.setMinimumWidth(maxWidth)

        ## lower controls 
        if self.enableGating == True:
            self.gateSelector = QtGui.QComboBox(self)
            for gt in ["None","Draw","Polygon", "Rectangle", "Square"]:
                self.gateSelector.addItem(gt)

            self.gateSelector.setCurrentIndex(0)
            self.connect(self.gateSelector, QtCore.SIGNAL('activated(int)'),self.gate_select_callback)

            self.gate_set = QtGui.QPushButton("Set")
            self.connect(self.gate_set, QtCore.SIGNAL('clicked()'), self.gate_set_callback)
            self.gate_set.setEnabled(False)
            self.gate_set.setMaximumWidth(maxWidth*0.6)
            self.gate_set.setMinimumWidth(maxWidth*0.6)

            self.gate_clear = QtGui.QPushButton("Clear")
            self.connect(self.gate_clear, QtCore.SIGNAL('clicked()'), self.gate_clear_callback)
            self.gate_clear.setEnabled(False)
            self.gate_clear.setMaximumWidth(maxWidth*0.6)
            self.gate_clear.setMinimumWidth(maxWidth*0.6)

            self.gate_save = QtGui.QPushButton("Save Gate")
            self.connect(self.gate_save, QtCore.SIGNAL('clicked()'), self.gate_save_callback)
            self.gate_save.setEnabled(False)
            #self.gate_set.setMaximumWidth(maxWidth*0.6)
            #self.gate_set.setMinimumWidth(maxWidth*0.6)

            defaultVert = 6
            self.vertSliderLabel = QtGui.QLabel(str(defaultVert))
            self.vertSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.vertSlider.setRange(3,8)
            self.vertSlider.setValue(defaultVert)
            self.vertSlider.setTracking(True)
            self.vertSlider.setTickPosition(QtGui.QSlider.TicksBothSides)
            self.connect(self.vertSlider, QtCore.SIGNAL('valueChanged(int)'), self.gate_vert_selector_callback)
            self.vertSlider.setEnabled(False)

        if self.compactMode == False:
            self.vizSelector = RadioBtnWidget(self.vizList,parent=self.parent,callbackFn=self.plot_viz_callback,vertical=True)
            self.vizSelector.btns[self.drawState].setChecked(True)
            self.vizSelector.selectedItem = self.drawState
            self.vizSelector.setMaximumWidth(maxWidth)
            self.vizSelector.setMinimumWidth(maxWidth)
            self.fig_save = QtGui.QPushButton("Save")
            self.connect(self.fig_save, QtCore.SIGNAL('clicked()'), self.figure_save)

        ## prepare layout
        hboxPlotLabel = QtGui.QHBoxLayout()
        hboxPlotLabel.setAlignment(QtCore.Qt.AlignCenter)

        if self.compactMode == False:
            hboxVizSelector = QtGui.QHBoxLayout()
            hboxVizSelector.setAlignment(QtCore.Qt.AlignCenter)
            hboxVizSelector = QtGui.QHBoxLayout()
            hboxVizSelector.setAlignment(QtCore.Qt.AlignCenter)
            hboxSaveBtn = QtGui.QHBoxLayout()
            hboxSaveBtn.setAlignment(QtCore.Qt.AlignCenter)
       
        controlBoxTop = QtGui.QVBoxLayout()
        controlBoxTop.setAlignment(QtCore.Qt.AlignTop)

        if self.compactMode == False:
            controlBoxBottom = QtGui.QVBoxLayout()
            controlBoxBottom.setAlignment(QtCore.Qt.AlignBottom)

        controlBox = QtGui.QVBoxLayout()
        canvasBox = QtGui.QHBoxLayout()
        canvasBox.setAlignment(QtCore.Qt.AlignRight)
        plotBox = QtGui.QVBoxLayout()
        masterBox = QtGui.QHBoxLayout()
        
        ## figure draw layout
        hboxPlotLabel.addWidget(self.subplotLabel)
        if self.compactMode == False:
            hboxVizSelector.addWidget(self.vizSelector)
            hboxSaveBtn.addWidget(self.fig_save)
        controlBoxTop.addLayout(hboxPlotLabel)
        if self.compactMode == False:
            controlBoxBottom.addLayout(hboxVizSelector)
            controlBoxBottom.addLayout(hboxSaveBtn)
        controlBox.addLayout(controlBoxTop)
        if self.compactMode == False:
            controlBox.addLayout(controlBoxBottom)
     
        ## set color
        if self.log != None:
            appColor = self.log.log['app_color']
        else:
            appColor = '#999999'

        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(appColor))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
        ## font color
        fontPalette = self.subplotLabel.palette()
        fontRole = self.subplotLabel.backgroundRole()
        fontPalette.setColor(fontRole, QtGui.QColor('#FFFFFF'))
        self.subplotLabel.setPalette(fontPalette)
        self.subplotLabel.setAutoFillBackground(True)

        ## finalize layout
        canvasBox.addWidget(self.canvas)
        plotBox.addLayout(canvasBox)
        masterBox.addLayout(controlBox)
        masterBox.addLayout(plotBox)
        self.setLayout(masterBox)

    def channel1_selector_callback(self,selectedInd):
        print '......'
        timeStart = time.time()
        if self.enableGating == True:
            self.gate_clear_callback()

        selectedTxt = str(self.channel1Selector.currentText())
        self.selectedChannel1 = selectedInd
        self.draw()

        if self.mainWindow != None:
            origTuple = self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex]
            newTuple = (self.channelList.index(selectedTxt),int(origTuple[1]))
            self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex] = newTuple
            self.mainWindow.controller.save()
        
        timeStop = time.time()
        print "\t", timeStop - timeStart

    def channel2_selector_callback(self,selectedInd):
        if self.enableGating == True:
            self.gate_clear_callback()

        selectedTxt = str(self.channel2Selector.currentText())
        self.selectedChannel2 = selectedInd
        self.draw()

        if self.mainWindow != None:
            origTuple = self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex]
            newTuple = (int(origTuple[0]),self.channelList.index(selectedTxt))
            self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex] = newTuple
            self.mainWindow.controller.save()

    def file_selector_callback(self,selectedInd):
        selectedTxt = str(self.fileSelector.currentText())
        self.selectedFileName=selectedTxt
        self.draw()

        if self.mainWindow != None:
            fileNames = get_fcs_file_names(self.mainWindow.controller.homeDir)
            selectedIndex = fileNames.index(selectedTxt)
            self.mainWindow.log.log['plots_to_view_files'][self.subplotIndex] = selectedIndex
            self.mainWindow.controller.save()

    def highlight_selector_callback(self,selectedInd):
        selectedTxt = str(self.highlightSelector.currentText())
        self.selectedHighlight = selectedTxt
        self.draw()

        if self.mainWindow != None:
            if self.selectedHighlight == 'None':
                self.mainWindow.log.log['plots_to_view_highlights'][self.subplotIndex] = 'None'
            else:
                self.mainWindow.log.log['plots_to_view_highlights'][self.subplotIndex] = int(self.selectedHighlight)
            self.mainWindow.controller.save()

    def grid_toggle_callback(self,showGrid):
        '''
        function called from left dock to toggle grid
        '''
        self.ax.grid(showGrid) 
        self.canvas.draw()

    def title_toggle_callback(self,showTitle):
        '''
        function called from left dock to toggle title without replot
        '''

        if self.plotTitle != None:
            if self.plotTitle != 'default':
                self.ax.set_title(re.sub("_"," ",self.plotTitle),fontname=self.fontName,fontsize=self.fontSize,visible=showTitle)
            else:
                self.ax.set_title(re.sub("_"," ",self.selectedFileName),fontname=self.fontName,fontsize=self.fontSize,visible=showTitle)
        self.canvas.draw()

    def axes_labels_toggle_callback(self,showAxisLabels):
        '''
        function called from left dock to toggle axis without replot
        '''

        self.ax.set_xlabel(self.channelList[self.selectedChannel1],fontname=self.fontName,fontsize=self.fontSize,visible=showAxisLabels)
        self.ax.set_ylabel(self.channelList[self.selectedChannel2],fontname=self.fontName,fontsize=self.fontSize,visible=showAxisLabels)
        self.canvas.draw()

    def gate_select_callback(self,ind):

        currentGateInd = int(self.gateSelector.currentIndex())
        self.currentGate= str(self.gateSelector.currentText())
        self.gate_clear_callback()

        fileInd = self.fileNameList.index(self.selectedFileName)
        mid1 = 0.5 * self.eventsList[fileInd][:,self.selectedChannel1].max()
        mid2 = 0.5 * self.eventsList[fileInd][:,self.selectedChannel2].max()
        a = mid1 - (mid1 * 0.5)
        b = mid1 + (mid1 * 0.5)
        c = mid2 - (mid2 * 0.5)
        d = mid2 + (mid2 * 0.5)
        e = mid2 + (mid2 * 0.6)
        f = mid2 - (mid2 * 0.6)

        self.gateSelector.setCurrentIndex(0)
        self.vertSlider.setEnabled(False)
        self.gate_save.setEnabled(False)
        self.gate_clear.setEnabled(False)
        self.gate_set.setEnabled(False)
            
        if self.currentGate == 'None':
            return
        else:
            self.gate_save.setEnabled(True)
            self.gate_clear.setEnabled(True)

        if self.currentGate == 'Draw':
            self.gateInteractor = DrawGateInteractor(self.ax, self.canvas, self.eventsList[fileInd], self.selectedChannel1, self.selectedChannel2)
        elif self.currentGate == 'Polygon':
            self.vertSlider.setEnabled(True)
            self.gate_save.setEnabled(True)
            self.gate_clear.setEnabled(True)
            self.gate_set.setEnabled(True)
            self.currentPolyVerts = 6
            self.poly = Polygon(([a,c],[mid1,f],[b,c],[b,d],[mid1,e],[a,d]), animated=True,alpha=0.2)
            self.ax.add_patch(self.poly)
            self.gateInteractor = PolyGateInteractor(self.ax,self.poly,self.canvas)
            self.vertSlider.setValue(6)
            self.vertSliderLabel.setText(str(6))
            self.canvas.draw()            
        else:
            msg = "This gate tool is not yet available"
            reply = QtGui.QMessageBox.information(self,'Information',msg)

        self.gateSelector.setCurrentIndex(currentGateInd)

    def gate_vert_selector_callback(self, value):
        self.vertSliderLabel.setText(str(value))
        
        if int(value) < self.currentPolyVerts:
            self.gateInteractor.remove_vert()
        if int(value) > self.currentPolyVerts:
            self.gateInteractor.add_vert()
        
        self.currentPolyVerts = int(value)
        self.canvas.draw()
        
    def gate_set_callback(self):
        self.gate_clear_callback()
        gate =  self.gateInteractor.gate

        gx = np.array([g[0] for g in gate])
        gy = np.array([g[1] for g in gate])
        self.line = Line2D(gx,gy,linewidth=3.0,alpha=0.8)
        self.ax.add_line(self.line)
        self.canvas.draw()

    def gate_clear_callback(self):
        if self.gateInteractor != None:
            self.gateInteractor.clean()

        if self.line != None:
            self.line.set_visible(False)

        if self.gateSelector != None:
            self.gateSelector.setCurrentIndex(0)
        else:
            return

        self.canvas.draw()
        
    def gate_save_callback(self):
        currentGateInd = int(self.gateSelector.currentIndex())
        currentGate= str(self.gateSelector.currentText())

        if self.homeDir == None:
            defaultDir = os.getcwd()#os.getenv("HOME")
        else:
            defaultDir = os.path.join(self.homeDir,'data')

        fileFilter = "*.gate"
        gateFileName, extension = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save As', directory=defaultDir,filter=fileFilter)
        gateFileName = str(gateFileName)
        extension = str(extension)[1:]
        gateFilePath = re.sub(extension,"",gateFileName) + extension

        gateToSave = {'verts':self.gateInteractor.gate,
                      'channel1':self.selectedChannel1,
                      'channel2':self.selectedChannel2,
                      'fileName':self.selectedFileName}
        
        if gateFilePath == None or gateFilePath == '':
            return 
        tmp1 = open(gateFilePath,'w')
        cPickle.dump(gateToSave,tmp1)
        tmp1.close()

    def figure_save(self,figName=None):
        if figName == None:
            defaultDir = os.getenv("HOME")
            fileFilter = "*.png;;*.jpg;;*.pdf"
            imgFileName, extension = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save As', directory=defaultDir,filter=fileFilter)
            imgFileName = str(imgFileName)
            extension = str(extension)[1:]
            figName = re.sub(extension,"",imgFileName) + extension
            
        if figName != '' and figName != None:
            self.fig.savefig(figName,transparent=False,dpi=self.dpi)
    
    def plot_viz_callback(self,item=None):
        if item in self.vizList:
            self.drawState = item
            self.draw()

    def generic_callback(self):
        print 'this is a generic callback'

if __name__ == '__main__':

    # how to use CytostreamPlotter
    from cytostream import NoGuiAnalysis

    ## check that unittests were run and necessary data is present
    baseDir = os.getcwd()
    selectedFile = "3FITC_4PE_004"
    filePath = os.path.join(baseDir,"..","example_data",selectedFile+".fcs")
    channelDict = {'FSCH':0,'SSCH':1}
    subsample = 10000

    ## setup class to run model
    homeDir = os.path.join(baseDir,"..","projects","utest")
    nga = NoGuiAnalysis(homeDir,channelDict,[filePath],useSubsample=True,makeQaFigs=False,record=False,transform='logicle')
    nga.set('num_iters_mcmc', 1200)
    nga.set('subsample_qa', 2000)
    nga.set('subsample_analysis', subsample)
    nga.set('dpmm_k',96)
    nga.set('thumbnail_results_default','components')
    
    ## declare the necessary variables
    transform = nga.get('selected_transform')
    fileNameList = [selectedFile]
    channelList = nga.get_file_channels()
    eventsList = [nga.get_events(fn) for fn in fileNameList]

    ## toggle qa and results mode
    modelRunID = None

    ## create plot
    app = QtGui.QApplication(sys.argv)
    cp = CytostreamPlotter(fileNameList,
                           eventsList,
                           channelList,
                           channelDict,
                           drawState='heat',
                           modelRunID=modelRunID,
                           parent=None,
                           background=True,
                           selectedChannel1=channelDict['FSCH'],
                           selectedChannel2=channelDict['SSCH'],
                           mainWindow=None,
                           uniqueLabels=None,
                           enableGating=False,
                           homeDir=homeDir,
                           compactMode=False,
                           labelList=None,
                           minNumEvents=3,
                           showNoise=False,
                           axesLabels=True,
                           useScaled=True,
                           plotTitle="default",
                           dpi=100,
                           subsample = subsample,
                           transform=transform
                           )

    cp.draw(selectedFile=selectedFile)

    ## show it
    cp.show()
    sys.exit(app.exec_())
