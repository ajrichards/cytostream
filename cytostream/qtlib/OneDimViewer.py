import sys,os,re
from PyQt4 import QtGui
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from scipy.stats import gaussian_kde
from cytostream import Model,get_fcs_file_names
from matplotlib.widgets import CheckButtons


class OneDimViewer(FigureCanvas):
    '''
    class to carry out the creation of a matplotlib figure embedded into the cytostream application.
    The interactive matplotlib figure allowed the user to select channels and toggle samples within
    each channel.

    selectedFile - The currently selected file associated with the project -- see FileSelector class
    homeDir - home directory of the project i.e. '/.../cytostream/projects/foo'
    parent (optional) - A QtGui.QWidget() instance
    subset (optional) - Specifies the number of samples in a subset
    modelName (optional) - The currently selected model -- see FileSelector class
    modelType (optional) - The mode or type associated with a model (i.e. components, modes)
    background (optional) - for saving the figure a backgound should be rendered during plot generation
    
    Testing: this function may be tested by running: 
    $ python OneDimViewer.py

    '''

    def __init__(self, homeDir, parent=None, subset="All Data",altDir=None, modelName=None, background=False, modelType=None):

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        ## prepare plot environment
        #self.fig = Figure()
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.set_frameon(background)
        self.selectedChannelInd = 0
        self.selectedFileIndices = [0]
        self.colors = ['b','orange','k','g','r','c','m','y']
        self.lines = ['-','.','--','-.','o','d','s','^']

        ## initialize model
        projectID = os.path.split(homeDir)[-1]
        model = Model()
        model.initialize(projectID,homeDir)

        ## additional class-wide variables
        self.fcsFileList = get_fcs_file_names(homeDir)
        self.fcsFileLabels = [re.sub("\.fcs","",f) for f in self.fcsFileList]
        self.masterChannelList = model.get_master_channel_list() 

        ## create the plot
        self.make_plot(model,subset)

        ## initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        ## notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def get_line_attrs(self,fcsFileInd):
        line = int(np.floor(float(fcsFileInd) / float(len(self.colors))))
        color = fcsFileInd % len(self.colors)

        return self.colors[color],self.lines[line]

    def make_plot(self,model,subset,buff=0.02):
        
        ## specify variables 
        if subset == 'All Data':
            markerSize = 4
        elif float(subset) < 1e4:
            markerSize = 5
        else:
            markerSize = 4

        fontName = 'arial'
        fontSize = 12
        plotType = 'png'

        ## make all the line plots (dict key order : [fileInd][channelInd]
        self.plotDict = {}
        self.tagDict = {}
        
        for fcsFileInd in range(len(self.fcsFileList)):
            for channelInd in range(len(self.masterChannelList)):
                if fcsFileInd == 0 and channelInd == 0:
                    visible = True
                else:
                    visible = False

                self.make_line_plot(subset,model,fcsFileInd,channelInd,visible=visible)

    def make_line_plot(self,subset,model,fcsFileInd,channelInd,visible=False):

        fcsFileName = self.fcsFileList[fcsFileInd]
        fileChannelList = model.get_file_channel_list(fcsFileName)

        ## determine subset of events
        data = model.pyfcm_load_fcs_file(fcsFileName)

        if subset != 'All Data':
            indices = model.get_subsample_indices(subset)
            events = [float(d) for d in data[indices,channelInd]]
        else:             
            events = [float(d) for d in data[:, channelInd]]

        fileChannelList = model.get_file_channel_list(fcsFileName)

        ## the histogram of the data
        #n, bins, patches = self.ax.hist(events, 50, normed=True,facecolor='blue', alpha=0.75)

        ## find the kernel density function
        self.pdfX = np.linspace(-200, np.max(events),300) #np.min(events)
        approxPdf = gaussian_kde(events)
        if self.plotDict.has_key(str(fcsFileInd)) == False:
            self.plotDict[str(fcsFileInd)] = {}

        self.plotDict[str(fcsFileInd)][str(channelInd)] = approxPdf

        if visible == True:
            color,lineStyle  = self.get_line_attrs(fcsFileInd)
            self.ax.plot(self.pdfX,approxPdf(self.pdfX),color=color,linestyle=lineStyle,linewidth=2.0,alpha=0.90)
            

            #self.draw()
        
    def paint(self,channel=None,fcsIndices=None):
        if channel != None:
            if self.masterChannelList.__contains__(channel) == False:
                print 'ERROR: master channel list does not contain', channel
    
            self.selectedChannelInd = self.masterChannelList.index(channel)

        if fcsIndices != None:
            self.selectedFileIndices = np.where(np.array(fcsIndices) == 1)[0]

        self.ax.clear()
        currentPlts = []
        currentLabs = []
        for fcsIndex in self.selectedFileIndices:
            approxPdf = self.plotDict[str(fcsIndex)][str(self.selectedChannelInd)]
            color,lineStyle  = self.get_line_attrs(fcsIndex)
            pt = self.ax.plot(self.pdfX,approxPdf(self.pdfX),color=color,linestyle=lineStyle,linewidth=2.0,alpha=0.90)
            currentPlts.append(pt)
            currentLabs.append(self.fcsFileLabels[fcsIndex])
            
        self.fig.legend( currentPlts, currentLabs, 'upper right', shadow=True)
        self.draw()
        

if __name__ == '__main__':

    ## prepare args
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    homeDir = os.path.join(baseDir,'..','projects','utest')
    subsample = 'All Data' #'1e3'

    ## use qt to display widget
    app = QtGui.QApplication(sys.argv)
    #parent =  QtGui.QWidget()
    odv = OneDimViewer(homeDir,subset=subsample,background=True)

    odv.show()
    sys.exit(app.exec_())
