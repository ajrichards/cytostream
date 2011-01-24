import sys,os,re
from PyQt4 import QtGui
import numpy as np

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from cytostream import Model, Logger

class ScatterPlotter(FigureCanvas):
    '''
    class to carry out the creation of a matplotlib figure embedded into the cytostream application
    selectedFile - The currently selected file associated with the project -- see FileSelector class
    channel1 - File specific channel ind to be plotted on the x-axis
    channel2 - File specific channel ind to be plotted on the y-axis
    homeDir - home directory of the project i.e. '/.../cytostream/projects/foo'
    parent (optional) - A QtGui.QWidget() instance
    subset (optional) - Specifies the number of samples in a subset
    altDir (optional) - Used when data should be saved in a non-default directory
    modelName (optional) - The currently selected model -- see FileSelector class
    modelType (optional) - The mode or type associated with a model (i.e. components, modes)
    background (optional) - for saving the figure a backgound should be rendered during plot generation
    
    Testing: this function may be tested by first running the unit tests provided with cytostream then moving into
    the directory containing ScatterPlotter and running 'python ScatterPlotter'.

    '''

    def __init__(self,homeDir,selectedFile,channel1,channel2,subset,modelName=None,parent=None,
                 altDir=None,background=False,modelType=None):

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        if modelName != None and modelType == None:
            print "ERROR: if model name specified must specify model type as well"
            return False

        if modelType != None and modelName == None:
            print "ERROR: if model type specified must specify model name as well"
            return False

        ## prepare plot environment
        self.fig = Figure()
        ax = self.fig.add_subplot(111)
        self.fig.set_frameon(background)
        
        ## prepare model
        projectID = os.path.split(homeDir)[-1]        
        log = Logger()
        log.initialize(projectID,homeDir,load=True)
        model = Model()
        model.initialize(projectID,homeDir)

        if modelName != None:
            statModel,statModelClasses = model.load_model_results_pickle(modelName,modelType)
        
            if modelType == 'components':
                centroids = statModel.mus()
            elif modelType == 'modes':
                centroids = statModel.modes()
        else:
            statModel,statModelClasses = None, None
            centroids = None

        self.make_scatter_plot(ax,log,model,selectedFile,channel1,channel2,subset,labels=statModelClasses,
                               centroids=centroids,statModel=statModel,modelType=modelType)
        
        # initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def make_scatter_plot(self,ax,log,model,selectedFile,channel1Ind,channel2Ind,subsample,labels=None,buff=0.02,
                          altDir=None,centroids=None,statModel=None,modelType=None):

        ## declare variables
        fontName = log.log['font_name']
        markerSize = int(log.log['scatter_marker_size'])
        fontSize = log.log['font_size']
        plotType = log.log['plot_type']
        filterInFocus = log.log['filter_in_focus']

        ## specify channels
        fileChannels = model.get_file_channel_list(selectedFile)
        index1 = int(channel1Ind)
        index2 = int(channel2Ind)
        channel1 = fileChannels[index1]
        channel2 = fileChannels[index2]

        ## get events          
        if re.search('filter',str(subsample)):
            pass
        elif subsample != 'original':
            subsample = str(int(float(subsample)))

        ## ensure the proper events are being loaded
        if re.search('original',str(subsample)) and re.search('filter',str(subsample)):
            events = model.get_events(selectedFile,subsample=subsample)
            subsample = self.log.log['setting_max_scatter_display']
            subsampleIndices = model.get_subsample_indices(subsample)
            events = events[subsampleIndices,:]
        elif filterInFocus != None and filterInFocus != 'None' and re.search('filter',filterInFocus):
            events = model.get_events(selectedFile,subsample=filterInFocus)
        elif re.search('original',str(subsample)):
            subsample = self.log.log['setting_max_scatter_display']
            subsampleIndices = model.get_subsample_indices(subsample)
            if labels != None:
                labels = labels[subsampleIndices]

            events = model.get_events(selectedFile,subsample=subsample)
        else:
            events = model.get_events(selectedFile,subsample=subsample)

        if labels != None:
            n,d = events.shape
            if n != labels.size:
                print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
                return None
        ###############################
        print "........................."
        print "debuggin."
        print events.shape
        print "........................."
        ###############################

        ## make plot
        totalPoints = 0
        if labels == None:
            ax.scatter([events[:,index1]],[events[:,index2]],color='blue',s=markerSize)
        else:
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            cmp = model.get_n_color_colorbar(maxLabel+1)

            for l in np.sort(np.unique(labels)):
                rgbVal = tuple([val * 256 for val in cmp[l,:3]])
                hexColor = model.rgb_to_hex(rgbVal)[:7]

                x = events[:,index1][np.where(labels==l)[0]]
                y = events[:,index2][np.where(labels==l)[0]]

                totalPoints+=x.size

                if x.size == 0:
                    continue
                ax.scatter(x,y,color=hexColor,s=markerSize)

        ## handle data edge buffers
        bufferX = buff * (events[:,index1].max() - events[:,index1].min())
        bufferY = buff * (events[:,index2].max() - events[:,index2].min())
        ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
        ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

        ## save file
        fileName = selectedFile
        ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
        ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

if __name__ == '__main__':

    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'qa'
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
