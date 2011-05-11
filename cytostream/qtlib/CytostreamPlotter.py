import sys,os,re
from PyQt4 import QtCore, QtGui

import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from cytostream import Model, Logger 
from cytostream.tools import fetch_plotting_events, get_all_colors, PlotDataOrganizer


class CytostreamPlotter(QtGui.QWidget):
    '''
    
    '''

    def __init__(self,fileChannels,drawState='scatter',parent=None,background=False,modelType='components',xAxLimit=None,yAxLimit=None,
                 fileList=None, selectedChannel1=0,selectedChannel2=1,mainWindow=None,uniqueLabels=None,enableGating=False):

        ## initialize
        QtGui.QWidget.__init__(self,parent)
        
        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

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

        ## variables to be used when class is called for drawing
        self.events=None
        self.dataSetName=None
        self.subsample=None

        ## create figure widget
        self.create_figure_widget()

    def _draw(self):
        if self.drawState == 'scatter':
            self.draw_scatter()
        else:
            print "ERROR: only scatter is implemented"

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()

        self.dpi = 100
        self.fig = Figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.figureWidget)
        self.ax = self.fig.add_subplot(111)
        #self.canvas.mpl_connect('pick_event', self.generic_callback)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.figureWidget)

        ## prepare layout
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()

        ## upper controls                                                                                                                                      
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

        if self.fileList != None:                                                                                                         
            self.fileSelector = QtGui.QComboBox(self)
            for f in self.fileList:
                self.fileSelector.addItem(f)
                
            self.fileSelector.setCurrentIndex(self.fileList.index(self.dataSetName))
            self.connect(self.fileSelector, QtCore.SIGNAL('activated(int)'),self.file_selector_callback)
            hbox1.addWidget(self.fileSelector)

        if self.uniqueLabels != None:                                                                         
            self.highlightSelector = QtGui.QComboBox(self)
            for hl in ["None"] + self.uniqueLabels:
                self.highlightSelector.addItem(str(hl))

            self.highlightSelector.setCurrentIndex(0)
            self.connect(self.highlightSelector, QtCore.SIGNAL('activated(int)'),self.highlight_selector_callback)
            hbox1.addWidget(self.highlightSelector)


        ## lower controls 
        hbox2.addWidget(self.mpl_toolbar)

        if self.enableGating == True:
            self.gate_save = QtGui.QPushButton("Save Gate")
            self.connect(self.gate_save, QtCore.SIGNAL('clicked()'), self.generic_callback)
            self.gate_clear = QtGui.QPushButton("Clear Gate")
            self.connect(self.gate_clear, QtCore.SIGNAL('clicked()'), self.generic_callback)
            hbox2.addWidget(self.gate_clear)
            hbox2.addWidget(self.gate_save)

        self.grid_cb = QtGui.QCheckBox("Show Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb,QtCore.SIGNAL('stateChanged(int)'), self._draw)
        hbox2.addWidget(self.grid_cb)

        self.force_cb = QtGui.QCheckBox("Force Scale")
        self.force_cb.setChecked(self.forceScale)
        self.connect(self.force_cb,QtCore.SIGNAL('stateChanged(int)'), self.force_scale_callback)
        hbox2.addWidget(self.force_cb)

        # finalize layout
        vbox.addLayout(hbox1)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

    def draw_scatter(self,events=None,dataSetName=None,channel1Ind=None,
                     channel2Ind=None,subsample=None,labels=None, modelName='run1',highlight=None,log=None):

        buff = 0.02
        centroids = None
        if channel1Ind != None:
            self.selectedChannel1=channel1Ind
            self.channel1Selector.setCurrentIndex(self.selectedChannel1)
        if channel2Ind != None:
            self.selectedChannel2=channel2Ind
            self.channel2Selector.setCurrentIndex(self.selectedChannel2)

        if events != None:
            self.events=events
            self.dataSetName=dataSetName
            self.subsample=subsample
            self.labels=labels
            self.modelName = modelName
            self.highlight=highlight
            self.log=log

        if self.highlight == "None":
            self.highlight = None

        ## clear axis
        self.ax.clear()
        self.ax.grid(self.grid_cb.isChecked())

        ## declare variables
        if self.log == None:
            fontName = 'Arial'
            markerSize = 1
            fontSize = 10
            plotType = 'png'
            filterInFocus = None
        else:
            fontName = self.log.log['font_name']
            markerSize = int(self.log.log['scatter_marker_size'])
            fontSize = int(self.log.log['font_size'])
            plotType = self.log.log['plot_type']
            filterInFocus = self.log.log['filter_in_focus']

        ## specify channels
        index1 = int(self.selectedChannel1)
        index2 = int(self.selectedChannel2)
        channel1 = self.fileChannels[index1]
        channel2 = self.fileChannels[index2]

        ## get centroids
        if self.labels != None:
            plotID, channelsID = self.pdo.get_ids(self.dataSetName,self.subsample,self.modelName,index1,index2)
            centroids = self.pdo.get_centroids(self.events,self.labels,plotID,channelsID)

        ## error check
        if self.labels != None:
            n,d = self.events.shape
            if n != self.labels.size:
                print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
                return None

        ## make plot
        totalPoints = 0
        if self.labels == None:
            dataX,dataY = (self.events[:,index1],self.events[:,index2])
            self.ax.scatter([dataX],[dataY],color='blue',s=markerSize)
        else:
            if type(np.array([])) != type(self.labels):
                self.labels = np.array(self.labels)

            numLabels = np.unique(self.labels).size
            maxLabel = np.max(self.labels)

            for l in np.sort(np.unique(self.labels)):
                clusterColor = self.colors[l]
                markerSize = int(markerSize)

                ## handle highlighted clusters      
                if self.highlight != None and str(int(self.highlight)) == str(int(l)):
                    alphaVal = 0.8
                    markerSize =  markerSize+4
                elif self.highlight !=None and str(int(self.highlight)) != str(int(l)):
                    alphaVal = 0.5
                    clusterColor = "#CCCCCC"
                else:
                    alphaVal=0.8

                ## check to see if centorids are already available
                dataX = self.events[:,index1][np.where(self.labels==l)[0]]
                dataY = self.events[:,index2][np.where(self.labels==l)[0]]
            
                totalPoints+=dataX.size

                if dataX.size == 0:
                    continue
                self.ax.scatter(dataX,dataY,color=clusterColor,s=markerSize)

                ## handle centroids if present     
                prefix = ''

                if centroids != None:
                    if centroids[str(int(l))].size != self.events.shape[1]:
                        print "ERROR: ScatterPlotter.py -- centroids not same shape as events" 
                    
                    xPos = centroids[str(int(l))][index1]
                    yPos = centroids[str(int(l))][index2]

                    if xPos < 0 or yPos <0:
                        continue

                    if clusterColor in ['#FFFFAA','y','#33FF77','#CCFFAA']:
                        self.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                     )
                    else:
                        self.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                     )

        ## handle data edge buffers
        bufferX = buff * (self.events[:,index1].max() - self.events[:,index1].min())
        bufferY = buff * (self.events[:,index2].max() - self.events[:,index2].min())
        self.ax.set_xlim([self.events[:,index1].min()-bufferX,self.events[:,index1].max()+bufferX])
        self.ax.set_ylim([self.events[:,index2].min()-bufferY,self.events[:,index2].max()+bufferY])
       
        ## force square axes
        self.ax.set_aspect(1./self.ax.get_data_ratio())

        ## save file
        self.ax.set_title("%s_%s_%s"%(channel1,channel2,self.dataSetName),fontname=fontName,fontsize=fontSize)
        self.ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        self.ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
        for t in self.ax.get_xticklabels():
            t.set_fontsize(fontSize)
            t.set_fontname(fontName)
    
        for t in self.ax.get_yticklabels():
            t.set_fontsize(fontSize)
            t.set_fontname(fontName)
    
        if self.forceScale == True:
            ax.set_xlim(self.xAxLimit)
            ax.set_ylim(self.yAxLimit)

        self.canvas.draw()

    def force_scale_callback(self,index=None):
        if self.forceScale == False and self.xAxLimit == None:
            msg = 'Function not available for single plots'
            QtGui.QMessageBox.information(self, "Info", msg)
            self.forceScale == False
            self.force_cb.setChecked(False)

    def channel1_selector_callback(self,selectedInd):
        selectedTxt = str(self.channel1Selector.currentText())
        self.selectedChannel1 = selectedInd
        self._draw()

        if self.mainWindow != None:
            origTuple = self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex]
            newTuple = (self.channelList.index(selectedTxt),int(origTuple[1]))
            self.mainWindow.log.log['plots_to_view_channels'][self.subplotIndex] = newTuple
            self.mainWindow.controller.save()

    def channel2_selector_callback(self,selectedInd):
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
    sp = CytostreamPlotter(fileChannels,background=True,modelType=modelType,enableGating=True,uniqueLabels=uniqueLabels)
    sp.draw_scatter(events,selectedFile,channel1,channel2,subsample,labels=labels,highlight=None,modelName=modelName)

    ## show it
    sp.show()
    sys.exit(app.exec_())
