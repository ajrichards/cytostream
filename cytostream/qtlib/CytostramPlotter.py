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

    def __init__(self,fileChannels,parent=None,background=False,modelType='components'):

        ## initialize
        QtGui.QWidget.__init__(self,parent)
        self.create_figure_widget()

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        ## prepare plot environment
        #self.fig = Figure()
        #self.ax = self.fig.add_subplot(111)
        #self.fig.set_frameon(background)
        #self.modelType = modelType
        #self.colors = get_all_colors()
        #self.fileChannels = fileChannels

        ## plotting variables
        self.events = events
        self.labels = labels
        self.pdo = PlotDataOrganizer()

        ## create figure widget
        self.create_figure_widget()

        ## initialization of the canvas 
        #FigureCanvas.__init__(self, self.fig)
        #self.setParent(parent)
        #FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        # notify the system of updated policy
        #FigureCanvas.updateGeometry(self)

    def create_figure_widget(self):
        self.figureWidget = QtGui.QWidget()

        self.dpi = 100
        self.fig = Figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.figureWidget)
        self.ax = self.fig.add_subplot(111)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.figureWidget)

        # Other GUI controls                                                                                 
        self.textbox = QtGui.QLineEdit()
        self.textbox.setMinimumWidth(200)
        #self.connect(self.textbox, QtCore.SIGNAL('editingFinished ()'), self.on_draw)

        self.draw_button = QtGui.QPushButton("&Draw")
        #self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), self.on_draw)

        slider_label = QtGui.QLabel('Bar width (%):')
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        #self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.on_draw)

        # finalize layout                               
        hbox = QtGui.QHBoxLayout()

        for w in [self.textbox, self.draw_button, self.grid_cb,
                  slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, QtCore.Qt.AlignVCenter)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def draw_scatter_plot(self,events,dataSetName,channel1Ind,channel2Ind,subsample,labels=None, highlight=None):

        buff = 0.02

        if highlight == "None":
            highlight = None

        ## clear axis
        self.ax.clear()

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
        index1 = int(channel1Ind)
        index2 = int(channel2Ind)
        channel1 = self.fileChannels[index1]
        channel2 = self.fileChannels[index2]

        ## get centroids
        if labels != None:
            plotID, channelsID = self.pdo.get_ids(self.dataSetName,self.subsample,self.modelName,index1,index2)
            self.pdo.get_centroids(events,labels,plotID,ChannelsID)

        ## error check
        if labels != None:
            n,d = events.shape
            if n != labels.size:
                print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
                return None

        ## make plot
        totalPoints = 0
        if labels == None:
            self.pdo.add_data(plotID,channelsID)
            dataX,dataY = (events[:,index1],events[:,index2])
            self.ax.scatter([dataX],[dataY],color='blue',s=markerSize)
        else:
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)

            for l in np.sort(np.unique(labels)):
                clusterColor = self.colors[l]
                markerSize = int(markerSize)

                ## handle highlighted clusters      
                if highlight != None and str(int(highlight)) == str(int(l)):
                    alphaVal = 0.8
                    markerSize =  markerSize+4
                elif highlight !=None and str(int(highlight)) != str(int(l)):
                    alphaVal = 0.5
                    clusterColor = "#CCCCCC"
                else:
                    alphaVal=0.8

                ## check to see if centorids are already available
                dataX = events[:,index1][np.where(labels==l)[0]]
                dataY = events[:,index2][np.where(labels==l)[0]]
            
                totalPoints+=dataX.size

                if dataX.size == 0:
                    continue
                self.ax.scatter(dataX,dataY,color=clusterColor,s=markerSize)

                ## handle centroids if present     
                prefix = ''

                if centroids != None:
                    if centroids[str(int(l))].size != events.shape[1]:
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
        bufferX = buff * (events[:,index1].max() - events[:,index1].min())
        bufferY = buff * (events[:,index2].max() - events[:,index2].min())
        self.ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
        self.ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])
        #self.ax.set_xticklabels(fontsize=fontSize-1,fontname=fontName)
        #self.ax.set_yticklabels(fontsize=fontSize-1,fontname=fontName)

        ## force square axes
        self.ax.set_aspect(1./self.ax.get_data_ratio())

        ## save file
        self.ax.set_title("%s_%s_%s"%(channel1,channel2,dataSetName),fontname=fontName,fontsize=fontSize)
        self.ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        self.ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

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

    ## create plot
    sp = CytostreamPlotter(fileChannels,background=True,modelType=modelType)
    sp.draw_scatter_plot(self,events,dataSetName,channel1Ind,channel2Ind,subsample,labels=labels, highlight=None)

    ## show it
    app = QtGui.QApplication(sys.argv)
    sp.show()
    sys.exit(app.exec_())
