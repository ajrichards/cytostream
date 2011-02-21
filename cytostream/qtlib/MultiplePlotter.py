import sys,os,re
from PyQt4 import QtGui, QtCore
import numpy as np

from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from cytostream.qtlib import ScatterPlotter
from cytostream import Model, Logger, get_fcs_file_names

class MultiplePlotter(QtGui.QWidget):
    def __init__(self,homeDir,selectedFile,channel1,channel2,subsample,modelName=None,parent=None,
                 background=False,modelType=None,mode='qa',showNavBar=True):

        #super(MultiplePlotter, self).__init__()
        QtGui.QWidget.__init__(self,parent)

        ## input variables
        self.setWindowTitle('Multiple Plotter')
        self.homeDir = homeDir
        self.subsample = subsample
        self.parent = parent
        self.background = background
        self.modelType = modelType
        self.mode = mode

        ## class variables
        self.selectedChannel1 = int(channel1)
        self.selectedChannel2 = int(channel2)
        self.selectedFile = selectedFile
        self.selectedModelName = modelName
        self.selectedHighlight = "None"
        self.fileList = get_fcs_file_names(self.homeDir)
        
        ## layout variables
        self.vbl = QtGui.QVBoxLayout()                       # overall layout
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()                      # layout for comboboxes
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()                      # layout for plot
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)        
        self.hbl3 = QtGui.QHBoxLayout()                      # layout for toolbar
        self.hbl3.setAlignment(QtCore.Qt.AlignCenter) 

        ## get file channels
        projectID = os.path.split(self.homeDir)[-1]
        log = Logger()
        log.initialize(projectID,self.homeDir,load=True)
        model = Model()
        model.initialize(projectID,self.homeDir)
        channelView = log.log['channel_view']
        self.channelList = model.get_file_channel_list(selectedFile)
        
        ## initialize widgets
        self.initChannel1()
        self.hbl1.addLayout(self.chan1Layout)
        self.initChannel2()
        self.hbl1.addLayout(self.chan2Layout)
        self.initFileSelector()
        self.hbl1.addLayout(self.filesLayout)

        if self.selectedModelName != None:
            statModel,statModelClasses = model.load_model_results_pickle(self.selectedFile,self.selectedModelName,modelType=self.modelType)
            uniqueLabels = np.sort(np.unique(statModelClasses)).tolist()
            self.initHighlight(uniqueLabels)
            self.hbl1.addLayout(self.highlightLayout)

        ## create the first plot
        self.create_plot()
        self.hbl2.addWidget(self.plot)

        ## add the navigation toolbar
        if showNavBar == True:
            self.ntb = NavigationToolbar(self.plot, self)
            self.hbl3.addWidget(self.ntb)

        ## finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        if showNavBar == True:
            self.vbl.addLayout(self.hbl3)
        self.setLayout(self.vbl)

    def initChannel1(self):
        ## setup layouts
        self.chan1LayoutA = QtGui.QHBoxLayout()
        self.chan1LayoutA.setAlignment(QtCore.Qt.AlignCenter)
        self.chan1LayoutB = QtGui.QHBoxLayout()
        self.chan1LayoutB.setAlignment(QtCore.Qt.AlignCenter)
        self.chan1Layout = QtGui.QVBoxLayout()
        self.chan1Layout.setAlignment(QtCore.Qt.AlignCenter)
        
        ## create label
        #self.labelChan1 = QtGui.QLabel("x-axis", self)
        #self.chan1LayoutA.addWidget(self.labelChan1)

        ## create combobox
        self.channel1Selector = QtGui.QComboBox(self)
        for channel in self.channelList:
            self.channel1Selector.addItem(channel)

        ## set default
        self.channel1Selector.setCurrentIndex(self.selectedChannel1)
        self.connect(self.channel1Selector, QtCore.SIGNAL('activated(int)'),self.channel1_selector_callback)
        self.chan1LayoutB.addWidget(self.channel1Selector)

        ## finalize layout
        #self.chan1Layout.addLayout(self.chan1LayoutA)
        self.chan1Layout.addLayout(self.chan1LayoutB)

    def initChannel2(self):
        ## setup layouts
        self.chan2LayoutA = QtGui.QHBoxLayout()
        self.chan2LayoutA.setAlignment(QtCore.Qt.AlignCenter)
        self.chan2LayoutB = QtGui.QHBoxLayout()
        self.chan2LayoutB.setAlignment(QtCore.Qt.AlignCenter)
        self.chan2Layout = QtGui.QVBoxLayout()
        self.chan2Layout.setAlignment(QtCore.Qt.AlignCenter)
        
        ## create label
        #self.labelChan2 = QtGui.QLabel("y-axis", self)
        #self.chan2LayoutA.addWidget(self.labelChan2)

        ## create combobox
        self.channel2Selector = QtGui.QComboBox(self)
        for channel in self.channelList:
            self.channel2Selector.addItem(channel)

        ## set default
        self.channel2Selector.setCurrentIndex(self.selectedChannel2)
        self.connect(self.channel2Selector, QtCore.SIGNAL('activated(int)'),self.channel2_selector_callback)
        self.chan2LayoutB.addWidget(self.channel2Selector)

        ## finalize layout
        #self.chan2Layout.addLayout(self.chan2LayoutA)
        self.chan2Layout.addLayout(self.chan2LayoutB)
 
    def initFileSelector(self):
        ## setup layouts
        self.filesLayoutA = QtGui.QHBoxLayout()
        self.filesLayoutA.setAlignment(QtCore.Qt.AlignCenter)
        self.filesLayoutB = QtGui.QHBoxLayout()
        self.filesLayoutB.setAlignment(QtCore.Qt.AlignCenter)
        self.filesLayout = QtGui.QVBoxLayout()
        self.filesLayout.setAlignment(QtCore.Qt.AlignCenter)
        
        ## create label
        #self.labelFiles = QtGui.QLabel("file selector", self)
        #self.filesLayoutA.addWidget(self.labelFiles)

        ## create combobox
        self.fileSelector = QtGui.QComboBox(self)
        for f in self.fileList:
            self.fileSelector.addItem(f)

        ## set default
        self.fileSelector.setCurrentIndex(self.fileList.index(self.selectedFile))
        self.connect(self.fileSelector, QtCore.SIGNAL('activated(int)'),self.file_selector_callback)
        self.filesLayoutB.addWidget(self.fileSelector)

        ## finalize layout
        #self.filesLayout.addLayout(self.filesLayoutA)
        self.filesLayout.addLayout(self.filesLayoutB)
    
    def initHighlight(self,uniqueLabels):
        ## setup layouts
        self.highlightLayoutA = QtGui.QHBoxLayout()
        self.highlightLayoutA.setAlignment(QtCore.Qt.AlignCenter)
        self.highlightLayoutB = QtGui.QHBoxLayout()
        self.highlightLayoutB.setAlignment(QtCore.Qt.AlignCenter)
        self.highlightLayout = QtGui.QVBoxLayout()
        self.highlightLayout.setAlignment(QtCore.Qt.AlignCenter)
        
        ## create label
        self.labelHighlight = QtGui.QLabel("highlight", self)
        self.highlightLayoutA.addWidget(self.labelHighlight)

        ## create combobox
        self.highlightSelector = QtGui.QComboBox(self)
        for hl in ["None"] + uniqueLabels:
            self.highlightSelector.addItem(str(hl))

        ## set default
        self.highlightSelector.setCurrentIndex(0)
        self.connect(self.highlightSelector, QtCore.SIGNAL('activated(int)'),self.highlight_selector_callback)
        self.highlightLayoutB.addWidget(self.highlightSelector)

        ## finalize layout
        self.highlightLayout.addLayout(self.highlightLayoutA)
        self.highlightLayout.addLayout(self.highlightLayoutB)

    def create_plot(self):
        self.plot = ScatterPlotter(self.homeDir,self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType, parent=self.parent)
        
    def channel1_selector_callback(self,selectedInd):
        selectedTxt = str(self.channel1Selector.currentText())
        self.selectedChannel1 = selectedInd
        self.plot.make_scatter_plot(self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,
                                    modelName=self.selectedModelName,highlight=self.selectedHighlight)
        self.plot.draw()

    def channel2_selector_callback(self,selectedInd):
        selectedTxt = str(self.channel2Selector.currentText())
        self.selectedChannel2 = selectedInd
        self.plot.make_scatter_plot(self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,
                                    modelName=self.selectedModelName,highlight=self.selectedHighlight)
        self.plot.draw()

    def file_selector_callback(self,selectedInd):
        selectedTxt = str(self.fileSelector.currentText())
        self.selectedFile = selectedTxt
        self.plot.make_scatter_plot(self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,
                                    modelName=self.selectedModelName,highlight=self.selectedHighlight)
        self.plot.draw()
        
    def highlight_selector_callback(self,selectedInd):
        selectedTxt = str(self.highlightSelector.currentText())
        self.selectedHighlight = selectedTxt
        self.plot.make_scatter_plot(self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,
                                    modelName=self.selectedModelName,highlight=self.selectedHighlight)
        self.plot.draw()

    def get_selected(self,selectorID):
        if selectorID == 'channel1':
            selectedInd = self.channelSelector1.currentIndex()
            selectedTxt = str(self.channelSelector1.currentText())

        return selectedTxt, selectedInd


### Run the tests 
if __name__ == '__main__':
    
    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'qa'#'results'
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004"
    modelName = None #'run1'
    channel1 = 0
    channel2 = 3
    modelType = 'modes'
    subsample = 1000
    homeDir = os.path.join(baseDir,'..','projects','utest')

    ## check that model is present
    modelChk = os.path.join(baseDir,'..','projects','utest','models','%s_%s.log'%(selectedFile,modelName))
    if mode == 'results' and os.path.isfile(modelChk) == False:
        print "ERROR: Model not present - (Re)run unit tests"
        print modelChk
        sys.exit()

    app = QtGui.QApplication(sys.argv)

    if mode == 'qa':
        modelType,modelName = None, None
        
    mp = MultiplePlotter(homeDir,selectedFile,channel1,channel2,subsample,background=True,
                         modelName=modelName,modelType=modelType,mode=mode)

    mp.show()
    sys.exit(app.exec_())


