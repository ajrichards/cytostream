import sys,os,re
from PyQt4 import QtGui
import numpy as np

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from cytostream import Model

class ScatterPlotter(FigureCanvas):
    '''
    class to carry out the creation of a matplotlib figure embedded into the cytostream application
    selectedFile - The currently selected file associated with the project -- see FileSelector class
    channel1 - File specific channel name to be plotted on the x-axis
    channel2 - File specific channel name to be plotted on the y-axis
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

    def __init__(self,homeDir,selectedFile,channel1,channel2,parent=None,subset="All Data",altDir=None,modelName=None,background=False,modelType=None):

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
        model = Model()
        model.initialize(projectID,homeDir)
        
        if modelName != None:
            statModel,statModelClasses = model.load_model_results_pickle(modelName,modelType)
        
            if modelType == 'components':
                centroids = statModel.mus()
            elif modelType == 'modes':
                #centroids = {}
                #n,d = np.shape(statModel.modes())
                #for i in range(n):
                #    centroids[i] = statModel.modes()[statModel.cmap[i]][:]
                
                centroids = statModel.modes()
        else:
            statModel,statModelClasses = None, None
            centroids = None

        self.make_scatter_plot(ax,model,selectedFile,channel1,channel2,subset,labels=statModelClasses,centroids=centroids,statModel=statModel,modelType=modelType)
        
        # initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def make_scatter_plot(self,ax,model,selectedFile,channel1,channel2,subset,labels=None,buff=0.02,altDir=None,centroids=None,statModel=None,modelType=None):
        if subset == 'All Data':
            markerSize = 4
        elif float(subset) < 1e4:
            markerSize = 5
        else:
            markerSize = 4
        fontName = 'arial'
        fontSize = 12
        plotType = 'png'

        fileChannels = model.get_file_channel_list(selectedFile)
        index1 = fileChannels.index(channel1)
        index2 = fileChannels.index(channel2)
        data = model.pyfcm_load_fcs_file(selectedFile)

        ## subset give an numpy array of indices 
        if subset != "All Data":
            subsampleIndices = model.get_subsample_indices(subset)
            data = data[subsampleIndices,:]

        ## make plot 
        totalPoints = 0
        if labels == None:
            ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
        else:    
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            cmp = model.get_n_color_colorbar(maxLabel+1)
            
            #for l in np.sort(np.unique(labels)):
            for labInd in np.argsort(np.unique(labels)):
                l = np.unique(labels)[labInd]

                rgbVal = tuple([val * 256 for val in cmp[l,:3]])
                hexColor = model.rgb_to_hex(rgbVal)[:7]

                x = data[:,index1][np.where(labels==l)[0]]
                y = data[:,index2][np.where(labels==l)[0]]
            
                totalPoints+=x.size

                if x.size == 0:
                    continue
    
                ax.scatter([x],[y],color=hexColor,s=markerSize)
                
                ## add means if specified
                #print l, rgbVal,centroids[labInd]
                if modelType == 'modes':
                    #print labInd
                    #labInd = statModel.cmap[labInd][0]
                    #print labInd, np.shape(centroids)
                    prefix = ''
                    hexColor = 'black'
                else:
                    prefix = ''

                xPos = centroids[labInd][index1]
                yPos = centroids[labInd][index2]
                ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white',
                        ha="center", va="center",
                        bbox = dict(boxstyle="round",facecolor=hexColor)
                        )
                #ax.text(xPos, yPos, 'c%s'%l, color='black',
                #        ha="center", va="center",
                #        bbox = dict(boxstyle="round",facecolor=hexColor)
                #        )

        ## handle data edge buffers 
        bufferX = buff * (data[:,index1].max() - data[:,index1].min())
        bufferY = buff * (data[:,index2].max() - data[:,index2].min())
        ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
        ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

        ### save file 
        fileName = selectedFile
        ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
        ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

if __name__ == '__main__':
    # check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    modelType = 'modes'
    modelChk = os.path.join(baseDir,'..','projects','utest','models','3FITC_4PE_004_sub1000_dpmm%s.pickle'%modelType) 
    if os.path.isfile(modelChk) == False:
        print "ERROR: Model not present - (Re)run unit tests"
        print modelChk
        sys.exit()

    mode = 'results'
    homeDir = os.path.join(baseDir,'..','projects','utest')
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004.fcs"
    selectedModel = 'sub1000_dpmm'
    subsample = 'All Data' #'1e3'
    channel1 = 'FL1-H' 
    channel2 = 'FL2-H'

    app = QtGui.QApplication(sys.argv)
    parent =  QtGui.QWidget()

    if mode == 'qa':
        sp = ScatterPlotter(homeDir,selectedFile,channel1,channel2,subset=subsample,background=True)
    if mode == 'results':
        sp = ScatterPlotter(homeDir,selectedFile,channel1,channel2,subset=subsample,background=True,
                            modelName=re.sub("\.pickle|\.fcs","",selectedFile) + "_" + selectedModel, modelType='modes')
    sp.show()
    sys.exit(app.exec_())
