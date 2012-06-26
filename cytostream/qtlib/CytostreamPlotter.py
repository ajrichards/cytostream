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
from cytostream.tools import get_all_colors, Centroids, draw_plot,get_file_sample_stats
from cytostream.tools import DrawGateInteractor, PolyGateInteractor, get_fontsize, get_fontname
from cytostream.qtlib import RadioBtnWidget,FilterControls

class CytostreamPlotter(QtGui.QWidget):
    '''
    wrapper class that handles nearly all plotting in cytostream
    class is also stand alone -- working outside the cytostream environment
    '''

    def __init__(self,fileNameList,eventsList,channelList,channelDict,
                 drawState='heat',parent=None,background=True,selectedChannel1=0,
                 selectedChannel2=1,mainWindow=None,uniqueLabels=None,
                 enableGating=False,homeDir=None,compactMode=False,controller=None,
                 minNumEvents=3,showNoise=False,subsample='7.5e04',numSubplots=1,
                 axesLabels=True,plotTitle=None,useSimple=False,dpi=100,
                 transform='logicle',useScaled=False,modelRunID='run1',subplotNum=1,
                 selectedFileName=None):
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
        self.controller = controller
        self.compactMode = compactMode
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
        self.savedCentroids = {}
        self.drawLabels = True

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
        self.selectedFileName = selectedFileName
        self.subsample = subsample
        self.line = None
        self.labels = None
        self.selectedHighlight = None
        self.vizList = ['heat','scatter','contour']

        if self.mainWindow != None:
            self.controller = self.mainWindow.controller

        ## initialize labels and subsamples
        if self.selectedFileName != None:
            self.initialize(self.selectedFileName)

        ## prepare figure widget for drawing
        self.create_figure_widget()

    def initialize(self,selectedFileName):

        ## handle labels (assumes that there is one label for each event)
        if self.modelRunID != None:
            if self.controller != None:
                self.labels = self.controller.get_labels(selectedFileName,self.modelRunID,subsample='original',getLog=False)
            else:
                print "ERROR CytostreamPlotter: either mainWindow or controller needs to be specified to get labels"

            if self.labels == None:
                print "WARNING: CytostreamPlotter had trouble getting specified labels", self.modelRunID, selectedFileName
            else:
                if self.savedCentroids.has_key(selectedFileName) == False:
                    eventsToPlot = self.eventsList[self.fileNameList.index(selectedFileName)]
                    centroids,variances,sizes = get_file_sample_stats(eventsToPlot,self.labels)
                    self.savedCentroids[selectedFileName] = centroids,variances,sizes
                self.currentCentroids = self.savedCentroids[selectedFileName]

        ## Handle subsample
        if self.subsample == 'original':
            self.subsample = 'original'
            events = self.eventsList[self.fileNameList.index(selectedFileName)]
            self.subsampleIndices = np.arange(events.shape[0])
        else:
            if self.controller != None:
                self.subsampleIndices = self.controller.get_subsample_indices(self.subsample)
                if self.labels != None:
                    self.labels = self.labels[self.subsampleIndices]
            else:
                print "ERROR: cannot use subsampling without specfied controller"

        ## error checking
        if type([]) != type(self.fileNameList):
            print "INPUT ERROR: CytostreamPlotter - fileNameList must be of type list"
        if type([]) != type(self.eventsList):
            print "INPUT ERROR: CytostreamPlotter - eventsList must be of type list"
        if len(self.fileNameList) != len(self.eventsList):
            print "INPUT ERROR: CytostreamPlotter - fileNameList and eventsList size mismatch"
        if self.drawState not in self.vizList:
            print "INPUT ERROR: CytostreamPlotter - drawState not valid",self.drawState

        ## save an instance of the centroids to speed up plotting
        #if self.labels != None and self.savedCentroids != None:
        #    self.savedCentroids = Centroids()

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
        args = [None for i in range(20)]
        args[0] = self.ax
        args[1] = self.eventsList[self.fileNameList.index(self.selectedFileName)]
        self.selectedEvents = self.eventsList[self.fileNameList.index(self.selectedFileName)]
        args[2] = self.channelList
        args[3] = self.channelDict
        args[4] = self.selectedChannel1
        args[5] = self.selectedChannel2
        args[6] = self.subsampleIndices
        args[7] = self.transform
        args[8] = self.labels
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
        args[19] = self.drawLabels

        ## set the text for num events
        if self.subsample == 'original':
            subsampleLabel = '%.1e' % self.selectedEvents.shape[0]
        else:
            try:
                x = float(self.subsample)
                subsampleLabel = '%.1e' % float(self.subsample)
            except:
                subsampleLabel = self.subsample

        self.subplotLabel2.setText(subsampleLabel)
        self.subplotLabel3.setText('%.1e' % self.selectedEvents.shape[0])

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
        self.subplotLabel1 = QtGui.QLabel(str(int(self.subplotNum))) 
        self.subplotLabel2 = QtGui.QLabel('None')
        self.subplotLabel2.setStyleSheet("font: 6pt")
        totalEvents = 'None'
        self.subplotLabel3 = QtGui.QLabel('None')
        self.subplotLabel3.setStyleSheet("font: 6pt")

        ## upper controls
        maxWidth = 100
      
        ## lower controls
        if self.enableGating == True:
            self.fc = FilterControls(parent=self,mainWindow=self.mainWindow)

        if self.compactMode == False:
            tooltips = ['heat scatter plot','colored scatter plot','contour plot']
            self.vizSelector = RadioBtnWidget(self.vizList,parent=self.parent,callbackFn=self.plot_viz_callback,
                                              tooltips=tooltips,vertical=True,useText=False)
            self.vizSelector.btns[self.drawState].setChecked(True)
            self.vizSelector.selectedItem = self.drawState
            self.vizSelector.setMaximumWidth(maxWidth)
            self.vizSelector.setMinimumWidth(maxWidth)
            self.fig_save = QtGui.QPushButton("Save")
            self.connect(self.fig_save, QtCore.SIGNAL('clicked()'), self.figure_save)

        ## prepare layout
        hboxPlotLabel1 = QtGui.QHBoxLayout()
        hboxPlotLabel1.setAlignment(QtCore.Qt.AlignCenter)
        hboxPlotLabel2 = QtGui.QHBoxLayout()
        hboxPlotLabel2.setAlignment(QtCore.Qt.AlignCenter)
        hboxPlotLabel3 = QtGui.QHBoxLayout()
        hboxPlotLabel3.setAlignment(QtCore.Qt.AlignCenter)

        if self.compactMode == False:
            hboxVizSelector = QtGui.QHBoxLayout()
            hboxVizSelector.setAlignment(QtCore.Qt.AlignCenter)
            hboxVizSelector = QtGui.QHBoxLayout()
            hboxVizSelector.setAlignment(QtCore.Qt.AlignCenter)
            hboxSaveBtn = QtGui.QHBoxLayout()
            hboxSaveBtn.setAlignment(QtCore.Qt.AlignCenter)
       
        controlBoxTop = QtGui.QVBoxLayout()
        controlBoxTop.setAlignment(QtCore.Qt.AlignTop)

        if self.enableGating == True:
            controlBoxCenter = QtGui.QVBoxLayout()
            controlBoxCenter.setAlignment(QtCore.Qt.AlignCenter)

        if self.compactMode == False:
            controlBoxBottom = QtGui.QVBoxLayout()
            controlBoxBottom.setAlignment(QtCore.Qt.AlignBottom)

        controlBox = QtGui.QVBoxLayout()
        canvasBox = QtGui.QHBoxLayout()
        canvasBox.setAlignment(QtCore.Qt.AlignRight)
        plotBox = QtGui.QVBoxLayout()
        masterBox = QtGui.QHBoxLayout()
        
        ## figure draw layout
        hboxPlotLabel1.addWidget(self.subplotLabel1)
        hboxPlotLabel2.addWidget(self.subplotLabel2)
        hboxPlotLabel3.addWidget(self.subplotLabel3)

        if self.compactMode == False:
            hboxVizSelector.addWidget(self.vizSelector)
            hboxSaveBtn.addWidget(self.fig_save)
        controlBoxTop.addLayout(hboxPlotLabel1)
        controlBoxTop.addLayout(hboxPlotLabel2)
        controlBoxTop.addLayout(hboxPlotLabel3)

        if self.enableGating == True:
            controlBoxCenter.addWidget(self.fc)
        if self.compactMode == False:
            controlBoxBottom.addLayout(hboxVizSelector)
            controlBoxBottom.addLayout(hboxSaveBtn)
        controlBox.addLayout(controlBoxTop)
        
        if self.enableGating == True:
            controlBox.addLayout(controlBoxCenter)

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
        fontPalette = self.subplotLabel1.palette()
        fontRole = self.subplotLabel1.backgroundRole()
        fontPalette.setColor(fontRole, QtGui.QColor('#FFFFFF'))
        self.subplotLabel1.setPalette(fontPalette)
        self.subplotLabel1.setAutoFillBackground(True)

        if self.enableGating == True:
            fontPalette = self.fc.vertSliderLabel.palette()
            fontRole = self.fc.vertSliderLabel.backgroundRole()
            fontPalette.setColor(fontRole, QtGui.QColor('#FFFFFF'))
            self.fc.vertSliderLabel.setPalette(fontPalette)
            self.fc.vertSliderLabel.setAutoFillBackground(True)

        fontPalette = self.subplotLabel2.palette()
        fontRole = self.subplotLabel2.backgroundRole()
        fontPalette.setColor(fontRole, QtGui.QColor('#FFCC00'))
        self.subplotLabel2.setPalette(fontPalette)
        self.subplotLabel2.setAutoFillBackground(True)

        fontPalette = self.subplotLabel3.palette()
        fontRole = self.subplotLabel3.backgroundRole()
        fontPalette.setColor(fontRole, QtGui.QColor('#0088FF'))
        self.subplotLabel3.setPalette(fontPalette)
        self.subplotLabel3.setAutoFillBackground(True)

        ## finalize layout
        if self.enableGating == True:
            self.fc.setMaximumWidth(self.fc.maxWidth*1.5)

        canvasBox.addWidget(self.canvas)
        plotBox.addLayout(canvasBox)
        masterBox.addLayout(controlBox)
        masterBox.addLayout(plotBox)
        self.setLayout(masterBox)

    def channel1_selector_callback(self,selectedInd):
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

        currentGateInd = int(self.fc.gateSelector.currentIndex())
        self.currentGate= str(self.fc.gateSelector.currentText())
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

        self.fc.gateSelector.setCurrentIndex(0)
        self.fc.vertSlider.setEnabled(False)
        self.fc.gate_save.setEnabled(False)
        self.fc.gate_clear.setEnabled(False)
        self.fc.gate_set.setEnabled(False)
            
        if self.currentGate == 'None':
            return
        else:
            self.fc.gate_save.setEnabled(True)
            self.fc.gate_clear.setEnabled(True)

        if self.currentGate == 'Draw':
            self.gateInteractor = DrawGateInteractor(self.ax, self.canvas, self.eventsList[fileInd], self.selectedChannel1, self.selectedChannel2)
            self.fc.vertSlider.setEnabled(False)
            self.fc.gate_set.setEnabled(True)
        elif self.currentGate == 'Polygon':
            self.fc.vertSlider.setEnabled(True)
            self.fc.gate_save.setEnabled(True)
            self.fc.gate_clear.setEnabled(True)
            self.fc.gate_set.setEnabled(True)
            self.currentPolyVerts = self.fc.defaultVert
            self.poly = Polygon(([a,c],[mid1,f],[b,c],[b,d],[mid1,e],[a,d]), animated=True,alpha=0.0)
            self.ax.add_patch(self.poly)
            self.gateInteractor = PolyGateInteractor(self.ax,self.poly,self.canvas)
            self.fc.vertSlider.setValue(self.fc.defaultVert)
            self.fc.vertSliderLabel.setText(str(self.fc.defaultVert))
            self.canvas.draw()            
        else:
            msg = "This gate tool is not yet available"
            reply = QtGui.QMessageBox.information(self,'Information',msg)

        self.fc.gateSelector.setCurrentIndex(currentGateInd)

    def gate_vert_selector_callback(self, value):
        self.fc.vertSliderLabel.setText(str(value))
        
        if int(value) < self.currentPolyVerts:
            self.fc.gateInteractor.remove_vert()
        if int(value) > self.currentPolyVerts:
            self.fc.gateInteractor.add_vert()
        
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

        if self.enableGating == True:
            self.fc.gateSelector.setCurrentIndex(0)
        else:
            return

        self.canvas.draw()
        
    def gate_save_callback(self):
        currentGateInd = int(self.fc.gateSelector.currentIndex())
        currentGate= str(self.fc.gateSelector.currentText())

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

        selectedPlotType = self.vizSelector.selectedItem
        print 'plot viz callback', selectedPlotType

        if selectedPlotType == 'scatter' and self.labels == None:
            if self.mainWindow != None:
                self.mainWindow.display_warning("Draw state 'scatter' only available once labels are present")
            else:
                print "WARNING: Draw state 'scatter' only available once labels are present"
            self.drawState = 'heat'
            self.vizSelector.set_checked(self.drawState)
            return

        if selectedPlotType == 'contour':
            if self.mainWindow != None:
                self.mainWindow.display_warning("Draw state 'contour' not yet available")
            else:
                print "WARNING: Draw state 'contour' only not yet available"
            self.drawState = 'heat'
            self.vizSelector.set_checked(self.drawState)
            return

        self.drawState = selectedPlotType
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
    nga.set('subsample_qa', 2000)
    nga.set('subsample_analysis', subsample)
    nga.set('dpmm_k',96)
    
    ## declare the necessary variables
    transform = nga.get('plots_transform')
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
                           minNumEvents=3,
                           showNoise=False,
                           axesLabels=True,
                           useScaled=True,
                           plotTitle="default",
                           dpi=100,
                           subsample = subsample,
                           transform=transform,
                           controller = nga.controller
                           )

    cp.initialize(selectedFile)
    cp.draw(selectedFile=selectedFile)

    ## show it
    cp.show()
    sys.exit(app.exec_())
