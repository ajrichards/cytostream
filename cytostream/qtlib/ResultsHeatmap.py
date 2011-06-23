import sys,os,re
from PyQt4 import QtGui
import numpy as np

import matplotlib
from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from scipy import interpolate
from cytostream import Model,get_fcs_file_names,get_models_run


class ResultsHeatmap(FigureCanvas):
    '''
    class to carry out the creation of a matplotlib figure embedded into the cytostream application.
    The interactive matplotlib figure displays a summary of the modeling results as a heatmap.

    selectedFile - The currently selected file associated with the project -- see FileSelector class
    homeDir - home directory of the project i.e. '/.../cytostream/projects/foo'
    modelName - The currently selected model -- see FileSelector class
    parent (optional) - A QtGui.QWidget() instance
    background (optional) - for saving the figure a backgound should be rendered during plot generation
    
    Testing: this function may be tested by running: 
    $ python ResultsHeatmap.py

    '''

    def __init__(self, homeDir, modelName, parent=None, modelType='modes',altDir=None, background=False):

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        ## prepare plot environment
        self.fig = Figure()
        self.fig.set_frameon(background)

        ## initialize model
        projectID = os.path.split(homeDir)[-1]
        model = Model()
        model.initialize(projectID,homeDir)

        ## additional class-wide variables
        self.fcsFileList = get_fcs_file_names(homeDir)
        self.modelsRunList = get_models_run(homeDir)
        self.fcsFileLabels = [re.sub("\.fcs","",f) for f in self.fcsFileList]
        self.masterChannelList = model.get_master_channel_list() 
        self.modelName = modelName
        self.modelType = modelType

        ## create the plot
        pltCount = 0

        for fileName in self.fcsFileList:
            pltCount +=1
            self.ax = self.fig.add_subplot(pltCount,1,pltCount)
            self.make_heatmap(homeDir,model,fileName)

        ## initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        ## notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def make_heatmap(self,homeDir,model,fileName,colorBar=False):

        statModel,statModelClasses = model.load_model_results_pickle(self.modelName,self.modelType)
        statModelClasses = statModelClasses + 0.5
        #print statModelClasses[:50]

        print np.unique(statModelClasses) 
        sortedInds = np.argsort(statModelClasses)
        statModelClasses = np.array([statModelClasses[sortedInds]])
        maxLabel = statModelClasses.max()
        #maxLabel = np.unique(statModelClasses).size + 1.0
        mycmap = self.cmap_discretize(plt.cm.jet,maxLabel+1.0)
        cbTicks = np.arange(0, maxLabel) + 0.49
        im = self.ax.imshow(statModelClasses,aspect='auto',interpolation='nearest',cmap=mycmap)
        self.fig.colorbar(im,ticks=[],format='%.0f',spacing='uniform') # ticks=cbTicks
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        print statModelClasses
        print cbTicks
        #print maxLabel, len(cbTicks+ 0.5)
        #print np.arange(maxLabel)
        #print statModelClasses.max(), len(np.unique(statModelClasses))

    def cmap_discretize(self,cmap, N):
        """Return a discrete colormap from the continuous colormap cmap.
        
            cmap: colormap instance, eg. cm.jet. 
            N: Number of colors.
        
        Example
            x = resize(arange(100), (5,100))
            djet = cmap_discretize(cm.jet, 5)
            imshow(x, cmap=djet)
        """
   
        cdict = cmap._segmentdata.copy()
        # N colors
        colors_i = np.linspace(0,1.,N)
        # N+1 indices
        indices = np.linspace(0,1.,N+1)
        for key in ('red','green','blue'):
            # Find the N colors
            D = np.array(cdict[key])
            I = interpolate.interp1d(D[:,0], D[:,1])
            colors = I(colors_i)
            # Place these colors at the correct indices.
            A = np.zeros((N+1,3), float)
            A[:,0] = indices
            A[1:,1] = colors
            A[:-1,2] = colors

            # Create a tuple for the dictionary.
            L = []
            for l in A:
                L.append(tuple(l))
            cdict[key] = tuple(L)
       
        # Return colormap object
        return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


if __name__ == '__main__':

    ## prepare args
    baseDir = os.path.dirname(__file__)
    homeDir = os.path.join(baseDir,'..','projects','utest')
    modelName = '3FITC_4PE_004_sub1000_dpmm-cpu'
    modelType = 'modes'

    ## use qt to display widget
    app = QtGui.QApplication(sys.argv)
    rh = ResultsHeatmap(homeDir,modelName,background=True)

    rh.show()
    sys.exit(app.exec_())
