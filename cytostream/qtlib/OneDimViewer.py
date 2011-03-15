#!/usr/bin/python
'''
Cytostream
OneDimViewer
A widget that handles the visualization of single channels as a smoothed
multiple files may be viewed on the same plot

'''

__author__ = "A Richards"


import sys,os,re
from PyQt4 import QtGui,QtCore
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from scipy.stats import gaussian_kde
from cytostream import get_fcs_file_names, Logger, Model
from cytostream.tools import fetch_plotting_events
from matplotlib.widgets import CheckButtons

class OneDimViewer(QtGui.QWidget):
    '''
    wrapper for the OneDimDrawClass

    '''

    def __init__(self, homeDir, subset='original', parent=None, channelDefault=None, callBack=None,background=True):
        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "ERROR: specified homedir is not a directory:", homeDir
            return False

        ## declare variables
        self.setWindowTitle('1-D Viewer')
        self.subset = subset
        self.background = background
        self.callBack = callBack
        self.homeDir = homeDir
        self.colors = ['b','orange','k','g','r','c','m','y']

        ## initialize model
        projectID = os.path.split(homeDir)[-1]
        log = Logger()
        log.initialize(homeDir,load=True)
        model = Model()
        model.initialize(homeDir)

        ## additional class-wide variables
        self.fcsFileList = get_fcs_file_names(homeDir)
        self.masterChannelList = model.get_master_channel_list() 

        ## setup layouts
        hl = QtGui.QHBoxLayout()
        hl.setAlignment(QtCore.Qt.AlignCenter)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignCenter)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.setAlignment(QtCore.Qt.AlignCenter)

        ## create checkboxes for each file
        self.chkBoxes = {}
        first = True
        count = -1
        #lab = QtGui.QLabel("blah", self)
        #print dir(lab)

        for fcsFileName in self.fcsFileList:
            count+=1
            fcsFileName = re.sub(".\fcs","",fcsFileName)
            color = count % len(self.colors)
            self.chkBoxes[fcsFileName] = QtGui.QCheckBox(fcsFileName, self)
            self.chkBoxes[fcsFileName].setFocusPolicy(QtCore.Qt.NoFocus)

            if first == True:
                self.chkBoxes[fcsFileName].toggle()
                first = False

            vbox1.addWidget(self.chkBoxes[fcsFileName])
            self.connect(self.chkBoxes[fcsFileName], QtCore.SIGNAL('clicked()'),lambda x=fcsFileName: self.fcs_file_callback(fcsFileName=x))

        ## channel selector
        self.channelSelector = QtGui.QComboBox(self)
        self.channelSelector.setMaximumWidth(180)
        self.channelSelector.setMinimumWidth(180)

        for channel in self.masterChannelList:
            self.channelSelector.addItem(channel)

        hbox2.addWidget(self.channelSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        if channelDefault != None:
            if self.masterChannelL.__contains__(channelDefault):
                self.channelSelector.setCurrentIndex(self.modelsRun.index(modelDefault))
            else:
                print "ERROR: in OneDimViewerDoc - bad specified channelDefault"

        #if callBack == None:
        #    self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.generic_callback)
        #else:
        self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.channel_callback)

        ## create the drawer
        self.odv = OneDimDraw(self.fcsFileList,self.masterChannelList,model,log,subset=subset,background=True,parent=self)
        hbox3.addWidget(self.odv)

        ## add a mpl navigation toolbar
        ntb = NavigationToolbar(self.odv,self)
        hbox4.addWidget(ntb)

        ## finalize layout
        vbox1.addLayout(hbox1)
        vbox2.addLayout(hbox2)
        vbox2.addLayout(hbox3)
        vbox2.addLayout(hbox4)
        hl.addLayout(vbox1)
        hl.addLayout(vbox2)
        self.setLayout(hl)

    def generic_callback(self):
        print 'callback does not do anything'

    def channel_callback(self):
        cInd = self.channelSelector.currentIndex()
        c = str(self.channelSelector.currentText())
        self.odv.paint(channel=c)
        
    def fcs_file_callback(self,fcsFileName=None):
        if fcsFileName != None:
            fcsIndices = [0 for i in range(len(self.fcsFileList))]

            for fcsFileName in self.fcsFileList:
                if self.chkBoxes[fcsFileName].isChecked() == True:
                    fcsIndices[self.fcsFileList.index(fcsFileName)] = 1

            channel = self.channelSelector.currentText()
            self.odv.paint(channel=channel,fcsIndices=fcsIndices)


    def get_results_mode(self):
        return self.resultsMode

    def disable_all(self):
        self.channelSelector.setEnabled(False)

        for key in self.chkBoxes.keys():
            self.chkBoxes[key].setEnabled(False)

    def enable_all(self):
        self.channelSelector.setEnabled(True)

        for key in self.chkBoxes.keys():
            self.chkBoxes[key].setEnabled(True)

class OneDimDraw(FigureCanvas):
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

    def __init__(self,fcsFileList,masterChannelList,model,log,subset="original",parent=None,altDir=None, modelName=None, background=False, modelType=None):

        ## prepare plot environment
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.set_frameon(background)
        self.selectedChannelInd = 0
        self.selectedFileIndices = [0]
        self.colors = ['b','orange','k','g','r','c','m','y']
        self.lines = ['-','.','--','-.','o','d','s','^']

        ## declare variables
        self.fcsFileList = fcsFileList
        self.masterChannelList = masterChannelList
        self.subset = subset

        ## create the plot
        self.make_plot(model,log,subset)

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

    def make_plot(self,model,log,subset,buff=0.02):
        
        ## make all the line plots (dict key order : [fileInd][channelInd]
        self.plotDict = {}
        self.tagDict = {}
        
        ## determine max val for each channel
        self.maxVal = 0
        for fcsFileInd in range(len(self.fcsFileList)):
            fcsFileName = re.sub("\.fcs|\.pickle|\.csv","",self.fcsFileList[fcsFileInd])
            for channelInd in range(len(self.masterChannelList)):
                data,labels = fetch_plotting_events(fcsFileName,model,log,self.subset)
                events = [float(d) for d in data[:, channelInd]]
                newMax = np.max(events)
                if newMax > self.maxVal:
                    self.maxVal = newMax

        for fcsFileInd in range(len(self.fcsFileList)):
            for channelInd in range(len(self.masterChannelList)):
                if fcsFileInd == 0 and channelInd == 0:
                    visible = True
                else:
                    visible = False

                self.make_line_plot(subset,model,log,fcsFileInd,channelInd,visible=visible)

    def make_line_plot(self,subset,model,log,fcsFileInd,channelInd,visible=False):

        fcsFileName = re.sub("\.fcs|\.pickle|\.csv","",self.fcsFileList[fcsFileInd])
        fileChannelList = model.get_file_channel_list(fcsFileName)

        ## determine subset of events
        data,labels = fetch_plotting_events(fcsFileName,model,log,self.subset)
        events = [float(d) for d in data[:, channelInd]]
        fileChannelList = model.get_file_channel_list(fcsFileName)

        ## the histogram of the data
        #n, bins, patches = self.ax.hist(events, 50, normed=True,facecolor='blue', alpha=0.75)

        ## find the kernel density function
        self.pdfX = np.linspace(-200, self.maxVal,300) #np.min(events)
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
            currentLabs.append(self.fcsFileList[fcsIndex])

        #if len(self.selectedFileIndices) > 0:
        #    self.fig.legend( currentPlts, currentLabs, 'upper right', shadow=True)
        
        self.draw()
        
if __name__ == '__main__':

    ## prepare args
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    homeDir = os.path.join(baseDir,'..','projects','utest')
    subsample = '1e3'

    ## use qt to display widget
    app = QtGui.QApplication(sys.argv)
    odv = OneDimViewer(homeDir,subset=subsample,background=True)

    odv.show()
    sys.exit(app.exec_())
