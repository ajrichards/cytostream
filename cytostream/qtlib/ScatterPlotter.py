import sys,os,re
from PyQt4 import QtGui
import numpy as np
import matplotlib as mpl

if mpl.get_backend() == 'MacOSX':
    mpl.use('Agg')

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from cytostream import Model, Logger 
from cytostream.tools import fetch_plotting_events, get_all_colors, get_file_sample_stats

class ScatterPlotter(FigureCanvas):
    '''
    class to carry out the creation of a matplotlib figure embedded into the cytostream application
    selectedFile - The currently selected file associated with the project -- see FileSelector class
    channel1 - File specific channel ind to be plotted on the x-axis
    channel2 - File specific channel ind to be plotted on the y-axis
    homeDir - home directory of the project i.e. '/.../cytostream/projects/foo'
    parent (optional) - A QtGui.QWidget() instance
    subset (optional) - Specifies the number of samples in a subset
    modelName (optional) - The currently selected model -- see FileSelector class
    modelType (optional) - The mode or type associated with a model (i.e. components, modes)
    background (optional) - for saving the figure a backgound should be rendered during plot generation
    
    Testing: this function may be tested by first running the unit tests provided with cytostream then moving into
    the directory containing ScatterPlotter and running 'python ScatterPlotter'.

    '''

    def __init__(self,homeDir,selectedFile,channel1,channel2,subset,modelName=None,parent=None,
                 background=False,modelType=None):

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        if modelName != None and modelType == None:
            print "ERROR: if model name specified must specify model type as well"
            print 'modelName', modelName, 'modelType', modelType
            return False

        if modelType != None and modelName == None:
            print "ERROR: if model type specified must specify model name as well"
            return False

        ## prepare plot environment
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.set_frameon(background)
        self.plotDict = {}
        self.modelType = modelType
        self.colors = get_all_colors()

        ## prepare model
        projectID = os.path.split(homeDir)[-1]        
        self.log = Logger()
        self.log.initialize(homeDir,load=True)
        self.model = Model()
        self.model.initialize(homeDir)

        ## create initial scatter plot
        self.make_scatter_plot(selectedFile,channel1,channel2,subset,modelName=modelName)
        
        ## initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def make_scatter_plot(self,selectedFile,channel1Ind,channel2Ind,subsample,buff=0.02,modelName=None,highlight=None):

        if highlight == "None":
            highlight = None

        if highlight != None and modelName==None:
            print "ERROR: ScatterPlotter.py -- if highlight is specified then modelName must also be true"
            highlight = None

        ## clear axis
        self.ax.clear()

        ## declare variables
        fontName = self.log.log['font_name']
        markerSize = int(self.log.log['scatter_marker_size'])
        fontSize = int(self.log.log['font_size'])
        plotType = self.log.log['plot_type']
        filterInFocus = self.log.log['filter_in_focus']

        ## specify channels
        fileChannels = self.log.log['alternate_channel_labels']
        index1 = int(channel1Ind)
        index2 = int(channel2Ind)
        channel1 = fileChannels[index1]
        channel2 = fileChannels[index2]

        ## handle analysis mode variables
        plotID, channelsID = self.get_plot_channel_id(selectedFile,subsample,modelName,index1,index2)
        if modelName != None:
            statModel,statModelClasses = self.model.load_model_results_pickle(selectedFile,modelName,modelType=self.modelType)
            labels = statModelClasses
        else:
            statModel,statModelClasses = None, None
            centroids,labels = None,None

        ## get events
        events,labels = fetch_plotting_events(selectedFile,self.model,self.log,subsample,labels=labels)

        ## handle sample stats
        if labels != None and self.plotDict[plotID][channelsID].has_key('centroids') == False:
            centroids,variances,sizes = get_file_sample_stats(events,labels)    
            self.plotDict[plotID][channelsID]['centroids'] = centroids
            self.plotDict[plotID][channelsID]['variances'] = variances
            self.plotDict[plotID][channelsID]['sizes'] = sizes
        elif labels != None and self.plotDict[plotID][channelsID].has_key('centroids') == True:
            centroids = self.plotDict[plotID][channelsID]['centroids']

        if labels != None:
            n,d = events.shape
            if n != labels.size:
                print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
                return None

        ## make plot
        totalPoints = 0
        if labels == None:

            ## check to see if data are already available
            if self.plotDict[plotID][channelsID].has_key('qa') == False:
                self.plotDict[plotID][channelsID]['qa'] = (events[:,index1],events[:,index2])
            
            ## make the plot
            dataX,dataY = self.plotDict[plotID][channelsID]['qa']
            self.ax.scatter([dataX],[dataY],color='blue',s=markerSize)
        else:
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)

            for l in np.sort(np.unique(labels)):
                clusterColor = self.colors[l]
                markerSize = int(self.log.log['scatter_marker_size'])

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
        fileName = selectedFile
        self.ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
        self.ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        self.ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)


    def get_plot_channel_id(self,selectedFile,subsample,modelName,index1,index2):
        if modelName == None:
            plotID = "%s_%s"%(selectedFile,subsample)
        else:
            plotID = "%s_%s_%s"%(selectedFile,subsample,modelName)

        channelsID = "%s-%s"%(index1,index2)

        if self.plotDict.has_key(plotID) == False:
            self.plotDict[plotID] = {}
        if self.plotDict[plotID].has_key(channelsID) == False:
            self.plotDict[plotID][channelsID] = {}

        return plotID, channelsID


if __name__ == '__main__':

    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004"
    selectedModel = 'run1'
    channel1 = 0 
    channel2 = 3
    modelType = 'modes'
    subsample = 1000
    homeDir = os.path.join(baseDir,'..','projects','utest')

    ## check that model is present
    modelChk = os.path.join(baseDir,'..','projects','utest','models','%s_%s.log'%(selectedFile,selectedModel)) 
    if os.path.isfile(modelChk) == False:
        print "ERROR: Model not present - (Re)run unit tests"
        print modelChk
        sys.exit()

    app = QtGui.QApplication(sys.argv)
    parent =  QtGui.QWidget()

    if mode == 'qa':
        sp = ScatterPlotter(homeDir,selectedFile,channel1,channel2,subsample,background=True)
    if mode == 'results':
        sp = ScatterPlotter(homeDir,selectedFile,channel1,channel2,subsample,background=True,
                            modelName=selectedModel,modelType=modelType)
    sp.show()
    sys.exit(app.exec_())
