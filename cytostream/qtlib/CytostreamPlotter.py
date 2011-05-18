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
from cytostream.tools import fetch_plotting_events, get_all_colors, PlotDataOrganizer, draw_scatter,draw_heat_scatter
from cytostream.tools import DrawGateInteractor, PolyGateInteractor
from cytostream.qtlib import RadioBtnWidget

class CytostreamPlotter(QtGui.QWidget):
    '''
    
    '''

    def __init__(self,fileChannels=None,drawState='Heat',parent=None,background=True,xAxLimit=None,yAxLimit=None,
                 selectedChannel1=0,selectedChannel2=1,mainWindow=None,uniqueLabels=None,enableGating=False,homeDir=None,
                 compactMode=False,isProject=False):

        ## initialize
        QtGui.QWidget.__init__(self,parent)
        
        ## plotting variables
        self.fileChannels = fileChannels
        self.pdo = PlotDataOrganizer()
        self.colors = get_all_colors()
        self.drawState = drawState
        self.xAxLimit = xAxLimit
        self.yAxLimit = yAxLimit
        self.forceScale = False
        self.selectedChannel1 = selectedChannel1
        self.selectedChannel2 = selectedChannel2
        self.mainWindow = mainWindow
        self.uniqueLabels = uniqueLabels
        self.enableGating = enableGating
        self.homeDir = homeDir
        self.compactMode = compactMode
        self.isProject = isProject

        ## addition variables
        self.gateInteractor = None
        self.currentGate = 'None'
        self.gateSelector = None
        self.fileList = None
        self.log = None
        self.model = None
        self.markerSize = 1

        if self.isProject == True:
            self._init_project()

        ## error check
        if self.isProject == False and self.fileChannels == None:
            print "ERROR CytostreamPlotter -- if not project specified must specify fileChannels"
            return

        ## variables to be used when class is called for drawing
        self.events=None
        self.selectedFileName=None
        self.subsample=None
        self.line=None
        self.labels = None
        self.highlight = None
        self.vizList = ['Heat','Scatter','Contour']

        ## create figure widget
        self.create_figure_widget()

    def _init_project(self):
        ## model, logger
        self.log = Logger()
        self.log.initialize(self.homeDir,load=True)
        self.model = Model()
        self.model.initialize(self.homeDir)
        self.fileChannels = self.log.log['alternate_channel_labels'] 
        self.fileList = get_fcs_file_names(self.homeDir)

    def init_labels_events(self,selectedFile,modelRunID=None,modelType='components'):

        if selectedFile not in self.fileList:
            print "ERROR CytostreamPlotter _init_labels_events -- bad fileList"
            return

        self.modelRunID = modelRunID

        ## handle analysis mode variables
        if self.modelRunID != None:
            statModel,statModelClasses = self.model.load_model_results_pickle(selectedFile,self.modelRunID,modelType=modelType)
            labels = statModelClasses
        else:
            statModel,statModelClasses = None, None
            centroids,labels = None,None

        if self.modelRunID != None:
            modelLog = self.model.load_model_results_log(selectedFile,self.modelRunID)
            subsample = modelLog['subsample']
            if subsample != 'original': subsample = int(float(subsample))
        else:
            subsample = self.log.log['subsample_qa']

        self.events,self.labels = fetch_plotting_events(selectedFile,self.model,self.log,subsample,labels=labels)
        
        if self.modelRunID != None:
            self.uniqueLabels = np.sort(np.unique(labels)).tolist()
        else:
            self.uniqueLabels = None

    def draw(self):
        self.ax.clear()
        self.gate_clear_callback()
        if self.drawState == 'Scatter':
            draw_scatter(self)
        elif self.drawState == 'Heat':
            draw_heat_scatter(self)
        elif self.drawState == 'Contour':
            msg = 'Function still under development'
            QtGui.QMessageBox.information(self, "Info", msg)
            self.vizSelector.btns['Heat'].setChecked(True)
            #self.draw()
            self.vizSelector.selectedItem = self.drawState
        else:
            print "ERROR: only scatter is implemented"

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()
        self.dpi = 100
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
            gatingLabel = QtGui.QLabel('Gate Controls')
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

        figControlsLabel = QtGui.QLabel('Figure Controls')
        self.grid_cb = QtGui.QCheckBox("Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)

        self.labels_cb = QtGui.QCheckBox("Label")
        self.labels_cb.setChecked(True)
        self.connect(self.labels_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)
        
        self.axLab_cb = QtGui.QCheckBox("Axes")
        self.axLab_cb.setChecked(True)
        self.connect(self.axLab_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)

        self.title_cb = QtGui.QCheckBox("Title")
        self.title_cb.setChecked(True)
        self.connect(self.title_cb,QtCore.SIGNAL('stateChanged(int)'), self.draw)

        defaultMS = 1
        self.markerSliderLabel = QtGui.QLabel(str(defaultMS))
        self.markerSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.markerSlider.setRange(1,10)
        self.markerSlider.setValue(defaultMS)
        self.markerSlider.setTracking(True)
        self.markerSlider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.connect(self.markerSlider, QtCore.SIGNAL('valueChanged(int)'), self.marker_slider_callback)
        self.markerSlider.setEnabled(True)
    
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
        hbox5.setAlignment(QtCore.Qt.AlignLeft)
        hbox6a = QtGui.QHBoxLayout()
        hbox6a.setAlignment(QtCore.Qt.AlignCenter)
        hbox6 = QtGui.QHBoxLayout()
        hbox6.setAlignment(QtCore.Qt.AlignCenter)
        hbox7 = QtGui.QHBoxLayout()
        hbox7.setAlignment(QtCore.Qt.AlignLeft)
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
        plotOptionBox1.addWidget(self.labels_cb)
        plotOptionBox2.addWidget(self.axLab_cb)
        plotOptionBox2.addWidget(self.title_cb)

        hbox6.addWidget(self.markerSliderLabel)
        hbox6.addWidget(self.markerSlider)
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
        self.highlight = selectedTxt
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

    def marker_slider_callback(self, value):
        self.markerSliderLabel.setText(str(value))
        self.markerSize = int(value)
        self.draw()
        
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

    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004"
    modelRunID = 'run1'
    channel1 = 0 
    channel2 = 3
    modelType = 'modes'
    subsample = 1000
    homeDir = os.path.join(baseDir,'..','projects','utest')

    ## check that model is present
    modelChk = os.path.join(baseDir,'..','projects','utest','models','%s_%s.log'%(selectedFile,modelRunID)) 
    if os.path.isfile(modelChk) == False:
        print "ERROR: Model not present - (Re)run unit tests"
        print modelChk
        sys.exit()

    ## plotting vars
    projectID = os.path.split(homeDir)[-1]
    log = Logger()
    log.initialize(homeDir,load=True)
    model = Model()
    model.initialize(homeDir)

    ## handle analysis mode variables
    if modelRunID != None:
        statModel,statModelClasses = model.load_model_results_pickle(selectedFile,modelRunID,modelType=modelType)
        labels = statModelClasses
    else:
        statModel,statModelClasses = None, None
        centroids,labels = None,None

    ## get the events
    events,labels = fetch_plotting_events(selectedFile,model,log,subsample,labels=labels)
    fileChannels = log.log['alternate_channel_labels'] 
    uniqueLabels = np.sort(np.unique(labels)).tolist()

    ## create plot
    app = QtGui.QApplication(sys.argv)
    sp = CytostreamPlotter(fileChannels=fileChannels,enableGating=True,uniqueLabels=uniqueLabels,homeDir=homeDir,
                           compactMode=True)
    draw_heat_scatter(sp,events,selectedFile,channel1,channel2,subsample,labels=labels,highlight=None,modelRunID=modelRunID)

    ## show it
    sp.show()
    sys.exit(app.exec_())
