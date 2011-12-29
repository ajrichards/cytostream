import sys,os,re,cPickle
from PyQt4 import QtCore, QtGui

import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.patches import Polygon, CirclePolygon
import matplotlib.cm as cm
from matplotlib.mlab import griddata

from matplotlib.lines import Line2D
from cytostream import Model, Logger, get_fcs_file_names 
from cytostream.tools import fetch_plotting_events, get_all_colors, Centroids, draw_plot
from cytostream.tools import DrawGateInteractor, PolyGateInteractor, get_fontsize, get_fontname
from cytostream.qtlib import RadioBtnWidget

class CytostreamPlotter(QtGui.QWidget):
    '''
    wrapper class that handles nearly all plotting in cytostream
    class is also stand alone -- working outside the cytostream environment

    '''

    def __init__(self,fileNameList,eventsList,fileChannels,channelDict,
                 drawState='heat',parent=None,background=True,selectedChannel1=0,
                 selectedChannel2=1,mainWindow=None,uniqueLabels=None,
                 enableGating=False,homeDir=None,compactMode=False,labelList=None,
                 minNumEvents=3,showNoise=False,subsample=70000,numSubplots=1,
                 axesLabels=None,plotTitle=None,useSimple=False,dpi=100,
                 transform='logicle'):
        '''
        constructor

           INPUT:
               fileNameList <- a list of file names
               eventsList   <- a list of np.array [n,d] correpsonding to fileNameList
               fileChannels <- a list of file channels
        '''

        ## initialize
        QtGui.QWidget.__init__(self,parent)
        
        ## required vaiables
        self.fileNameList = fileNameList
        self.eventsList = eventsList
        self.fileChannels = fileChannels
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
        self.compactMode = compactMode
        self.labelList = labelList
        self.minNumEvents = minNumEvents
        self.showNoise = showNoise
        self.numSubplots = numSubplots
        self.axesLabels = axesLabels
        self.plotTitle = plotTitle
        self.useSimple = useSimple
        self.dpi = dpi
        self.transform = transform

        ## additional class variables
        self.colors = get_all_colors()
        self.gateInteractor = None
        self.currentGate = 'None'
        self.gateSelector = None
        self.fileList = None
        self.log = None
        self.model = None
        self.markerSize = 1
        self.fontName = get_fontname()
        self.fontSize = get_fontsize(self.numSubplots) 
        
        ## variables to be used when class is called for drawing
        self.events = None
        self.selectedFileName = None
        self.subsample = None
        self.line = None
        self.labels = None
        self.selectedHighlight = None
        self.vizList = ['heat','scatter','contour']

        ## subsample 
        if subsample == 'original':
            self.subsample = 70000
        else:
            self.subsample = int(float(subsample))

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

        ## prepare figure widget for drawing
        self.create_figure_widget()

    def draw(self,cbInt=None,selectedFile=None):
        '''
        args[0] = ax                       [required]  matplotlib axes
        args[1] = events                   [required]  np.array (N,D)
        args[2] = channelDict              [required]  {'ssc':0,'fsc':1}
        args[3] = channel1Index            [required]  int
        args[4] = channel2Index            [required]  int
        args[5] = subsample                [required]  float | 'original'
        args[6] = transform                [required]  'log' | 'logicle'
        args[7] = labels                   [optional]  np.array (N,1)
        args[8] = highlight                [optional]  None|clusterID (str(int))
        args[9] = logger                   [optional]  Logger instance
        args[10] = drawState               [optional]  'scatter' | 'heat' | 'contour'
        args[11] = numSubplots             [optional]  int 1-16
        args[12] = axesLabels              [optional]  None | (xAxisLabel,yAxisLabel)
        args[13] = plotTitle               [optional]  None | str
        args[14] = showNoise               [optional]  True | False
        args[15] = useSimple               [optional]  False | True
        
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
        args = [None for i in range(16)]
        args[0] = self.ax
        args[1] = self.eventsList[self.fileNameList.index(self.selectedFileName)]
        args[2] = self.channelDict
        args[3] = self.selectedChannel1
        args[4] = self.selectedChannel2
        args[5] = self.subsample
        args[6] = self.transform
        if self.labelList != None:
            args[7] = self.labelList[self.fileNameList.index(self.selectedFileName)]
        args[8] = self.selectedHighlight
        args[9] = self.log
        args[10] = self.drawState
        args[11] = self.numSubplots
        args[12] = self.axesLabels
        args[13] = self.plotTitle
        args[14] = self.showNoise
        args[15] = self.useSimple

        ## draw on canvas
        draw_plot(args,parent=self)
        self.fig.canvas.draw()

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()
        self.fig = Figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.figureWidget)
        self.ax = self.fig.add_subplot(111)

        ## upper controls
        maxWidth = 100
        channelsLabel = QtGui.QLabel('Channels')
        self.channel1Selector = QtGui.QComboBox(self)
        for channel in self.fileChannels:
            self.channel1Selector.addItem(channel)
        self.channel1Selector.setMaximumWidth(maxWidth)
        self.channel1Selector.setMinimumWidth(maxWidth)
        self.channel1Selector.setCurrentIndex(self.selectedChannel1)
        self.connect(self.channel1Selector, QtCore.SIGNAL('activated(int)'),self.channel1_selector_callback)

        self.channel2Selector = QtGui.QComboBox(self)
        for channel in self.fileChannels:
            self.channel2Selector.addItem(channel)
            
        self.channel2Selector.setMaximumWidth(maxWidth)
        self.channel2Selector.setMinimumWidth(maxWidth)
        self.channel2Selector.setCurrentIndex(self.selectedChannel2)
        self.connect(self.channel2Selector, QtCore.SIGNAL('activated(int)'),self.channel2_selector_callback)

        if self.fileList != None or self.uniqueLabels != None:
            additionalSelectorLabel = QtGui.QLabel('Additional Selectors')

        if self.fileList != None: 
            self.fileSelector = QtGui.QComboBox(self)
            for f in self.fileList:
                self.fileSelector.addItem(f)
                
            self.fileSelector.setMaximumWidth(maxWidth)
            self.fileSelector.setMinimumWidth(maxWidth)
            if self.selectedFileName == None:
                self.selectedFileName = self.fileList[0]

            self.fileSelector.setCurrentIndex(self.fileList.index(self.selectedFileName))
            self.connect(self.fileSelector, QtCore.SIGNAL('activated(int)'),self.file_selector_callback)

        if self.uniqueLabels != None:                                                                         
            self.highlightSelector = QtGui.QComboBox(self)
            for hl in ["None"] + self.uniqueLabels:
                self.highlightSelector.addItem(str(hl))
        
            self.highlightSelector.setCurrentIndex(0)
            self.connect(self.highlightSelector, QtCore.SIGNAL('activated(int)'),self.highlight_selector_callback)
            
            self.highlightSelector.setMaximumWidth(maxWidth)
            self.highlightSelector.setMinimumWidth(maxWidth)

        ## lower controls 
        if self.enableGating == True:
            #gatingLabel = QtGui.QLabel('Gate Controls')
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

        self.grid_cb = QtGui.QCheckBox("Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)

        self.scale_cb = QtGui.QCheckBox("Scale")
        self.scale_cb.setChecked(False)
        self.connect(self.scale_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)
        
        self.axLab_cb = QtGui.QCheckBox("Axes")
        self.axLab_cb.setChecked(True)
        self.connect(self.axLab_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)

        self.title_cb = QtGui.QCheckBox("Title")
        self.title_cb.setChecked(True)
        self.connect(self.title_cb,QtCore.SIGNAL('stateChanged(int)'), self.title_set_callback)

        #defaultMS = 1
        #self.markerSliderLabel = QtGui.QLabel(str(defaultMS))
        #self.markerSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        #self.markerSlider.setRange(1,10)
        #self.markerSlider.setValue(defaultMS)
        #self.markerSlider.setTracking(True)
        #self.markerSlider.setTickPosition(QtGui.QSlider.TicksBothSides)
        #self.connect(self.markerSlider, QtCore.SIGNAL('valueChanged(int)'), self.marker_slider_callback)
        #self.markerSlider.setEnabled(True)
    
        self.vizSelector = RadioBtnWidget(self.vizList,parent=self,callbackFn=self.plot_viz_callback,vertical=True)
        self.vizSelector.btns[self.drawState].setChecked(True)
        self.vizSelector.selectedItem = self.drawState

        self.vizSelector.setMaximumWidth(maxWidth)
        self.vizSelector.setMinimumWidth(maxWidth)

        self.fig_save = QtGui.QPushButton("Save Figure")
        self.connect(self.fig_save, QtCore.SIGNAL('clicked()'), self.figure_save)

        ## prepare layout
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        hbox3_1 = QtGui.QHBoxLayout()
        hbox3_1.setAlignment(QtCore.Qt.AlignCenter)
        hbox3_2 = QtGui.QHBoxLayout()
        hbox3_2.setAlignment(QtCore.Qt.AlignCenter)
        hbox3_3 = QtGui.QHBoxLayout()
        hbox3_3.setAlignment(QtCore.Qt.AlignCenter)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.setAlignment(QtCore.Qt.AlignCenter)
        hbox1a = QtGui.QHBoxLayout()
        hbox1a.setAlignment(QtCore.Qt.AlignLeft)
        hbox2a = QtGui.QHBoxLayout()
        hbox2a.setAlignment(QtCore.Qt.AlignLeft)
        hbox3a = QtGui.QHBoxLayout()
        hbox3a.setAlignment(QtCore.Qt.AlignLeft)
        hbox4a = QtGui.QHBoxLayout()
        hbox4a.setAlignment(QtCore.Qt.AlignLeft)
        hbox5 = QtGui.QHBoxLayout()
        hbox5.setAlignment(QtCore.Qt.AlignCenter)
        hbox6a = QtGui.QHBoxLayout()
        hbox6a.setAlignment(QtCore.Qt.AlignCenter)
        hbox6 = QtGui.QHBoxLayout()
        hbox6.setAlignment(QtCore.Qt.AlignCenter)
        hbox7 = QtGui.QHBoxLayout()
        hbox7.setAlignment(QtCore.Qt.AlignCenter)
        hbox8 = QtGui.QHBoxLayout()
        hbox8.setAlignment(QtCore.Qt.AlignCenter)
        hbox9 = QtGui.QHBoxLayout()
        hbox9.setAlignment(QtCore.Qt.AlignCenter)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignTop)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignTop)
        vbox3 = QtGui.QVBoxLayout()
        vbox3.setAlignment(QtCore.Qt.AlignBottom)

        vboxLeft = QtGui.QVBoxLayout()
        vboxRight = QtGui.QVBoxLayout()
        masterBox = QtGui.QHBoxLayout()
        
        ## data controls layout
        dcBox1 = QtGui.QVBoxLayout()
        dcBox1.setAlignment(QtCore.Qt.AlignLeft)
        dcBox2 = QtGui.QVBoxLayout()
        dcBox2.setAlignment(QtCore.Qt.AlignLeft)
        hbox1a.addWidget(QtGui.QLabel('Data Controls')) 
        dcBox1.addWidget(QtGui.QLabel("x-ax"))
        dcBox2.addWidget(self.channel1Selector)
        dcBox1.addWidget(QtGui.QLabel("y-ax"))
        dcBox2.addWidget(self.channel2Selector)

        if self.uniqueLabels != None:
            dcBox1.addWidget(QtGui.QLabel("clust"))
            dcBox2.addWidget(self.highlightSelector)
        if self.fileList != None:
            dcBox1.addWidget(QtGui.QLabel("file"))
            dcBox2.addWidget(self.fileSelector)

        hbox1.addLayout(dcBox1)
        hbox1.addLayout(dcBox2)

        ## gating layout
        if self.enableGating == True:
            gateBox1 = QtGui.QVBoxLayout()
            gateBox1.setAlignment(QtCore.Qt.AlignLeft)
            gateBox2 = QtGui.QVBoxLayout()
            gateBox2.setAlignment(QtCore.Qt.AlignLeft)

            hbox3a.addWidget(QtGui.QLabel('Gate Controls'))
            gateBox1.addWidget(QtGui.QLabel("gate"))
            gateBox2.addWidget(self.gateSelector)
            hbox3.addLayout(gateBox1)
            hbox3.addLayout(gateBox2)
            hbox3_1.addWidget(self.vertSliderLabel)
            hbox3_1.addWidget(self.vertSlider)
            hbox3_2.addWidget(self.gate_set)
            hbox3_2.addWidget(self.gate_clear)
            hbox3_3.addWidget(self.gate_save)
       
        ## plot controls layout
        hbox5.addWidget(QtGui.QLabel('Plot Controls'))
        plotOptionBox1 = QtGui.QVBoxLayout()
        plotOptionBox1.setAlignment(QtCore.Qt.AlignLeft)
        plotOptionBox2 = QtGui.QVBoxLayout()
        plotOptionBox2.setAlignment(QtCore.Qt.AlignLeft)
        plotOptionBox1.addWidget(self.grid_cb)
        plotOptionBox1.addWidget(self.scale_cb)
        plotOptionBox2.addWidget(self.axLab_cb)
        plotOptionBox2.addWidget(self.title_cb)

        #hbox6.addWidget(self.markerSliderLabel)
        #hbox6.addWidget(self.markerSlider)
        hbox6a.addLayout(plotOptionBox1)
        hbox6a.addLayout(plotOptionBox2)
 
        ## figure draw layout
        hbox7.addWidget(QtGui.QLabel('Plot Draw'))
        hbox8.addWidget(self.vizSelector)
        hbox9.addWidget(self.fig_save) 

        ## finalize layout
        if self.compactMode == False:
            vbox1.addLayout(hbox1a)
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        if self.compactMode == False:
            vbox1.addLayout(hbox3a)
        vbox1.addLayout(hbox3)
        vbox1.addLayout(hbox3_1)
        vbox1.addLayout(hbox3_2)
        vbox1.addLayout(hbox3_3)
        vbox1.addLayout(hbox4)
        if self.compactMode == False:
            vbox2.addLayout(hbox5)
        vbox2.addLayout(hbox6a) 
        vbox2.addLayout(hbox6) 
        if self.compactMode == False:
            vbox3.addLayout(hbox7)
        vbox3.addLayout(hbox8)
        vbox3.addLayout(hbox9)
       
        vboxLeft.addLayout(vbox1)
        vboxLeft.addLayout(vbox2)
        vboxLeft.addLayout(vbox3)

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
    
        ## set layout
        vboxRight.addWidget(self.canvas)
        masterBox.addLayout(vboxLeft)
        masterBox.addLayout(vboxRight)
        self.setLayout(masterBox)

    def force_scale_callback(self,index=None):
        if self.forceScale == False and self.xAxLimit == None:
            msg = 'Function not available for single plots'
            QtGui.QMessageBox.information(self, "Info", msg)
            self.forceScale == False
            self.force_cb.setChecked(False)

    def channel1_selector_callback(self,selectedInd):
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
        self.init_labels_events(self.selectedFileName,self.modelRunID)
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

    def gate_select_callback(self,ind):

        currentGateInd = int(self.gateSelector.currentIndex())
        self.currentGate= str(self.gateSelector.currentText())
        self.gate_clear_callback()

        mid1 = 0.5 * self.events[:,self.selectedChannel1].max()
        mid2 = 0.5 * self.events[:,self.selectedChannel2].max()
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
            self.gateInteractor = DrawGateInteractor(self.ax, self.canvas, self.events, self.selectedChannel1, self.selectedChannel2)
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

    #def marker_slider_callback(self, value):
    #    self.markerSliderLabel.setText(str(value))
    #    self.markerSize = int(value)
    #    self.draw()
        
    def gate_set_callback(self):

        self.gate_clear_callback()
        gate =  self.gateInteractor.gate

        gx = np.array([g[0] for g in gate])
        gy = np.array([g[1] for g in gate])
        self.line = Line2D(gx,gy,linewidth=3.0,alpha=0.8)
        self.ax.add_line(self.line)
        self.canvas.draw()

    def title_set_callback(self,cb):
        if self.title_cb.isChecked() == True and self.plotTitle != None:
            self.ax.set_title(self.plotTitle,fontname=self.fontName,fontsize=self.fontSize,visible=True)
        else:
            self.ax.set_title(self.plotTitle,fontname=self.fontName,fontsize=self.fontSize,visible=False)
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
        
        print 'saving', gateToSave.keys()

        if gateFilePath == None or gateFilePath == '':
            return 
        tmp1 = open(gateFilePath,'w')
        cPickle.dump(gateToSave,tmp1)

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

    # how to use CytostreamPlotter with fcm
    import fcm

    ## check that unittests were run and necessary data is present
    baseDir = os.getcwd()
    #selectedFile = "3FITC_4PE_004"
    #filePath = os.path.join(baseDir,"..","example_data",selectedFile+".fcs")
    #channelDict = {'fsc-h':0,'ssc-h':1}
    selectedFile = "J6901HJ1-06_CMV_CD8"
    filePath = os.path.join("/","home","clemmys","research","manuscripts","PositivityThresholding","scripts","data","eqapol11C",selectedFile+".fcs")
    channelDict = {'fsc-a':0, 'fsc-h':1, 'fsc-w':2, 'ssc-a':3, 'ssc-h':4, 'ssc-w':5, 'time':6}

    fcsData = fcm.loadFCS(filePath,auto_comp=False)
    fcsData.logicle(scale_max=262144)
    events = fcsData[:,:].copy()

    ## declare the necessary variables
    fileNameList = [selectedFile]
    eventsList = [events]
    fileChannels = fcsData.channels

    ## create plot
    app = QtGui.QApplication(sys.argv)
    cp = CytostreamPlotter(fileNameList,
                           eventsList,
                           fileChannels,
                           channelDict,
                           drawState='heat',
                           parent=None,
                           background=True,
                           selectedChannel1=6,
                           selectedChannel2=3,
                           mainWindow=None,
                           uniqueLabels=None,
                           enableGating=False,
                           homeDir=None,
                           compactMode=False,
                           labelList=None,
                           minNumEvents=3,
                           showNoise=False,
                           axesLabels=None,
                           plotTitle="example plot title",
                           dpi=100,
                           subsample = 'original',
                           transform='logicle'
                           )

    cp.draw(selectedFile=selectedFile)

    ## show it
    cp.show()
    sys.exit(app.exec_())
