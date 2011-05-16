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
from cytostream import Model, Logger 
from cytostream.tools import fetch_plotting_events, get_all_colors, PlotDataOrganizer, draw_scatter
from cytostream.tools import DrawGateInteractor, PolyGateInteractor
from cytostream.qtlib import RadioBtnWidget


class CytostreamPlotter(QtGui.QWidget):
    '''
    
    '''

    def __init__(self,fileChannels,drawState='scatter',parent=None,background=False,modelType='components',xAxLimit=None,yAxLimit=None,
                 fileList=None, selectedChannel1=0,selectedChannel2=1,mainWindow=None,uniqueLabels=None,enableGating=False,homeDir=None):

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
        self.fileList = fileList
        self.selectedChannel1 = selectedChannel1
        self.selectedChannel2 = selectedChannel2
        self.mainWindow = mainWindow
        self.uniqueLabels = uniqueLabels
        self.enableGating = enableGating
        self.homeDir = homeDir

        ## gates
        self.gateInteractor = None
        self.currentGate = 'None'

        ## variables to be used when class is called for drawing
        self.events=None
        self.dataSetName=None
        self.subsample=None
        self.line=None
        self.vizList = ['scatter','contour','scatter heatmap']

        ## create figure widget
        self.create_figure_widget()

    def _draw(self):
        self.ax.clear()
        self.gate_clear_callback()
        if self.drawState == 'scatter':
            draw_scatter(self)
        elif self.drawState == 'contour':
            ##mat = self.events[:,[self.selectedChannel1,self.selectedChannel2]]
            msg = 'Function still under development'
            QtGui.QMessageBox.information(self, "Info", msg)
            self.drawState = 'scatter'
            self._draw()
            self.vizSelector.btns[self.drawState].setChecked(True)
            self.vizSelector.selectedItem = self.drawState

            #x = self.events[:,self.selectedChannel1]
            #y = self.events[:,self.selectedChannel2]
            #z = x*np.exp(-x**2-y**2)
            #buff = 0.02
            #bufferX = buff * (x.max() - x.min())
            #bufferY = buff * (y.max() - y.min())
            #
            ### define the grid
            #xMin, xMax = x.min()-bufferX,x.max()+bufferX
            #yMin, yMax = y.min()-bufferY,y.max()+bufferY
            #xi = np.linspace(xMin,xMax,100)
            #yi = np.linspace(yMin,yMax,100)

            ### grid the data
            #zi = griddata(x,y,z,xi,yi,interp='nn')
            #mat = self.events[:,[self.selectedChannel1,self.selectedChannel2]]
            #CS = self.ax.contour(xi,yi,zi)
            #CS = self.ax.contour(xi,yi,zilinewidths=0.5,colors='k')
            #CS = self.ax.contourf(xi,yi,zi)#cmap=self.fig.cm.jet)

            ### adjust axes 
            #self.ax.set_xlim([xMin,xMax])
            #self.ax.set_ylim([yMin,yMax])
            #
            #self.canvas.draw()
            #npts = 200
            #x = uniform(-2,2,npts)
            #y = uniform(-2,2,npts)
            #z = x*np.exp(-x**2-y**2)
            # define grid.
            #xi = np.linspace(-2.1,2.1,100)
            #yi = np.linspace(-2.1,2.1,200)
            # grid the data.
            #zi = griddata(x,y,z,xi,yi,interp='linear')
            # contour the gridded data, plotting dots at the nonuniform data points.
            #CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
            #CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
            #plt.colorbar() # draw colorbar
            # plot data points.
            #plt.scatter(x,y,marker='o',c='b',s=5,zorder=10)
            #plt.xlim(-2,2)
            #plt.ylim(-2,2)
            #plt.title('griddata test (%d points)' % npts)
            #plt.show()
            #im = self.ax.imshow(mat, interpolation='bilinear', cmap=cm.gray)
                                #origin='lower', extent=[-3,3,-3,3])
       
        elif self.drawState == 'scatter heatmap':
            msg = 'Function still under development'
            QtGui.QMessageBox.information(self, "Info", msg)
            self.drawState = 'scatter'
            self._draw()
            self.vizSelector.btns[self.drawState].setChecked(True)
            self.vizSelector.selectedItem = self.drawState
        else:
            print "ERROR: only scatter is implemented"

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()

        self.dpi = 110
        self.fig = Figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.figureWidget)
        self.ax = self.fig.add_subplot(111)

        ## prepare layout
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
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
        hbox6 = QtGui.QHBoxLayout()
        hbox6.setAlignment(QtCore.Qt.AlignCenter)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignTop)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignTop)
        vbox3 = QtGui.QVBoxLayout()
        vbox3.setAlignment(QtCore.Qt.AlignTop)
        vbox4 = QtGui.QVBoxLayout()
        vbox4.setAlignment(QtCore.Qt.AlignTop)
        vbox5 = QtGui.QVBoxLayout()
        vbox5.setAlignment(QtCore.Qt.AlignTop)
        vbox6 = QtGui.QVBoxLayout()
        vbox6.setAlignment(QtCore.Qt.AlignBottom)

        vboxLeft = QtGui.QVBoxLayout()
        vboxRight = QtGui.QVBoxLayout()
        masterBox = QtGui.QHBoxLayout()

        ## upper controls
        channelsLabel = QtGui.QLabel('Channels')
        hbox1a.addWidget(channelsLabel)                                                                                                               
        self.channel1Selector = QtGui.QComboBox(self)
        for channel in self.fileChannels:
            self.channel1Selector.addItem(channel)

        self.channel1Selector.setCurrentIndex(self.selectedChannel1)
        self.connect(self.channel1Selector, QtCore.SIGNAL('activated(int)'),self.channel1_selector_callback)        
        hbox1.addWidget(self.channel1Selector)

        self.channel2Selector = QtGui.QComboBox(self)
        for channel in self.fileChannels:
            self.channel2Selector.addItem(channel)

        self.channel2Selector.setCurrentIndex(self.selectedChannel2)
        self.connect(self.channel2Selector, QtCore.SIGNAL('activated(int)'),self.channel2_selector_callback)        
        hbox1.addWidget(self.channel2Selector)

        if self.fileList != None or self.uniqueLabels != None:
            additionalSelectorLabel = QtGui.QLabel('Additional Selectors')
            hbox2a.addWidget(additionalSelectorLabel)

        if self.fileList != None:                                  
            self.fileSelector = QtGui.QComboBox(self)
            for f in self.fileList:
                self.fileSelector.addItem(f)
                
            self.fileSelector.setCurrentIndex(self.fileList.index(self.dataSetName))
            self.connect(self.fileSelector, QtCore.SIGNAL('activated(int)'),self.file_selector_callback)
            hbox2.addWidget(self.fileSelector)

        if self.uniqueLabels != None:                                                                         
            self.highlightSelector = QtGui.QComboBox(self)
            for hl in ["None"] + self.uniqueLabels:
                self.highlightSelector.addItem(str(hl))

            self.highlightSelector.setCurrentIndex(0)
            self.connect(self.highlightSelector, QtCore.SIGNAL('activated(int)'),self.highlight_selector_callback)
            hbox2.addWidget(self.highlightSelector)

        ## lower controls 
        if self.enableGating == True:
            gatingLabel = QtGui.QLabel('Gate Controls')
            hbox3a.addWidget(gatingLabel)
            self.gateSelector = QtGui.QComboBox(self)
            for gt in ["None","Draw","Polygon", "Rectangle", "Square"]:
                self.gateSelector.addItem(gt)

            self.gateSelector.setCurrentIndex(0)
            self.connect(self.gateSelector, QtCore.SIGNAL('activated(int)'),self.gate_select_callback)

            self.gate_set = QtGui.QPushButton("Set")
            self.connect(self.gate_set, QtCore.SIGNAL('clicked()'), self.gate_set_callback)
            self.gate_set.setEnabled(False)

            self.gate_clear = QtGui.QPushButton("Clear")
            self.connect(self.gate_clear, QtCore.SIGNAL('clicked()'), self.gate_clear_callback)
            self.gate_clear.setEnabled(False)

            self.gate_save = QtGui.QPushButton("Save Gate")
            self.connect(self.gate_save, QtCore.SIGNAL('clicked()'), self.gate_save_callback)
            self.gate_save.setEnabled(False)

            defaultVert = 6
            self.vertSliderLabel = QtGui.QLabel(str(defaultVert))
            self.vertSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.vertSlider.setRange(3,8)
            self.vertSlider.setValue(defaultVert)
            self.vertSlider.setTracking(True)
            self.vertSlider.setTickPosition(QtGui.QSlider.TicksBothSides)
            self.connect(self.vertSlider, QtCore.SIGNAL('valueChanged(int)'), self.gate_vert_selector_callback)
            self.vertSlider.setEnabled(False)

            hbox3_1.addWidget(self.gateSelector)
            hbox3_1.addWidget(self.vertSlider)
            hbox3_1.addWidget(self.vertSliderLabel)
            hbox3_2.addWidget(self.gate_set)
            hbox3_2.addWidget(self.gate_clear)
            hbox3_3.addWidget(self.gate_save)

        figControlsLabel = QtGui.QLabel('Figure Controls')
        hbox4a.addWidget(figControlsLabel)
        self.grid_cb = QtGui.QCheckBox("Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb,QtCore.SIGNAL('stateChanged(int)'), self._draw)
        hbox4.addWidget(self.grid_cb)

        self.force_cb = QtGui.QCheckBox("Scale")
        self.force_cb.setChecked(self.forceScale)
        self.connect(self.force_cb,QtCore.SIGNAL('stateChanged(int)'), self.force_scale_callback)
        hbox4.addWidget(self.force_cb)

        self.vizSelector = RadioBtnWidget(self.vizList,parent=self,callbackFn=self.plot_viz_callback)
        hbox5.addWidget(self.vizSelector)
        defaultViz = 'scatter'
        self.vizSelector.btns[defaultViz].setChecked(True)
        self.vizSelector.selectedItem = defaultViz

        self.fig_save = QtGui.QPushButton("Save Figure")
        self.connect(self.fig_save, QtCore.SIGNAL('clicked()'), self.figure_save)
        hbox6.addWidget(self.fig_save)

        # finalize layout
        vbox1.addLayout(hbox1a)
        vbox1.addLayout(hbox1)
        vbox2.addLayout(hbox2a)
        vbox2.addLayout(hbox2)
        vbox3.addLayout(hbox3a)
        vbox3.addLayout(hbox3_1)
        vbox3.addLayout(hbox3_2)
        vbox3.addLayout(hbox3_3)
        vbox4.addLayout(hbox4a)
        vbox4.addLayout(hbox4)
        vbox5.addLayout(hbox5)
        vbox6.addLayout(hbox6)
        vboxLeft.addLayout(vbox1)
        vboxLeft.addLayout(vbox2)
        vboxLeft.addLayout(vbox3)
        vboxLeft.addLayout(vbox4)
        vboxLeft.addLayout(vbox5)
        vboxLeft.addLayout(vbox6)
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
        self._draw()

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
        self._draw()

        if self.mainWindow != None:
            origTuple = self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex]
            newTuple = (int(origTuple[0]),self.channelList.index(selectedTxt))
            self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex] = newTuple
            self.mainWindow.controller.save()

    def file_selector_callback(self,selectedInd):
        selectedTxt = str(self.fileSelector.currentText())
        self.dataSetName=selectedTxt
        self._draw()

        if self.mainWindow != None:
            fileNames = get_fcs_file_names(self.mainWindow.controller.homeDir)
            selectedIndex = fileNames.index(selectedTxt)
            self.mainWindow.log.log['plots_to_view_files'][self.subplotIndex] = selectedIndex
            self.mainWindow.controller.save()

    def highlight_selector_callback(self,selectedInd):
        selectedTxt = str(self.highlightSelector.currentText())
        self.highlight = selectedTxt
        self._draw()

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

        mid1 = 0.5 * self.events[self.selectedChannel1].max()
        mid2 = 0.5 * self.events[self.selectedChannel2].max()
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

    def gate_set_callback(self):

        self.gate_clear_callback()
        gate =  self.gateInteractor.gate

        gx = np.array([g[0] for g in gate])
        gy = np.array([g[1] for g in gate])
        self.line = Line2D(gx,gy,linewidth=2.0,alpha=0.8)
        self.ax.add_line(self.line)
        self.canvas.draw()

    def gate_clear_callback(self):
        if self.gateInteractor != None:
            self.gateInteractor.clean()

        if self.line != None:
            self.line.set_visible(False)

        self.gateSelector.setCurrentIndex(0)
        self.canvas.draw()
        
    def gate_save_callback(self):
        currentGateInd = int(self.gateSelector.currentIndex())
        currentGate= str(self.gateSelector.currentText())
        print currentGate, self.currentGate
        print self.gateInteractor.gate

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
                      'fileName':self.dataSetName}
        
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
        print 'plot viz callback', item
        if item in self.vizList:
            self.drawState = item
            self._draw()

    def generic_callback(self):
        print 'this is a generic callback'


if __name__ == '__main__':

    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004"
    modelName = 'run1'
    channel1 = 0 
    channel2 = 3
    modelType = 'modes'
    subsample = 1000
    homeDir = os.path.join(baseDir,'..','projects','utest')

    ## check that model is present
    modelChk = os.path.join(baseDir,'..','projects','utest','models','%s_%s.log'%(selectedFile,modelName)) 
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
    if modelName != None:
        statModel,statModelClasses = model.load_model_results_pickle(selectedFile,modelName,modelType=modelType)
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
    sp = CytostreamPlotter(fileChannels,background=True,modelType=modelType,enableGating=True,uniqueLabels=uniqueLabels,homeDir=homeDir)
    draw_scatter(sp,events,selectedFile,channel1,channel2,subsample,labels=labels,highlight=None,modelName=modelName)

    ## show it
    sp.show()
    sys.exit(app.exec_())
