import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

from cytostream import get_fcs_file_names
from cytostream.qtlib import MultiplePlotter

class NWayViewer(QtGui.QWidget):

    def __init__(self,homeDir,channels,files,runs,highlights,subsample,numSubplots,figMode='qa',parent=None,
                 background=False,modelType=None,mainWindow=None):

        QtGui.QWidget.__init__(self,parent)

        ## input variables
        self.setWindowTitle('N Way Plotter')
        self.homeDir = homeDir
        self.channels = channels
        self.files = files
        self.runs = runs
        self.highlights = highlights
        self.subsample = subsample
        self.numSubplots = numSubplots
        self.figMode = figMode
        self.parent = parent
        self.background = background
        self.modelType = modelType
        self.mainWindow = mainWindow

        ## modify variables
        fileNames = get_fcs_file_names(self.homeDir)
        self.files = [fileNames[i] for i in files]

        if self.figMode == 'qa':
            self.runs = [None for i in self.runs]
            self.modelType = None

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl3 = QtGui.QHBoxLayout()
        self.hbl3.setAlignment(QtCore.Qt.AlignCenter)

        for i in range(numSubplots):
            mp = MultiplePlotter(self.homeDir,self.files[i],self.channels[i][0],self.channels[i][1],self.subsample,background=self.background,
                                 modelName=self.runs[i],modelType=self.modelType,mode=self.figMode,parent=self,
                                 showNavBar=False,mainWindow=self.mainWindow,subplotIndex=i)
            
            if self.numSubplots in [2]:
                self.hbl1.addWidget(mp)
            elif self.numSubplots in [3]:
                self.hbl1.addWidget(mp)
            elif self.numSubplots in [4]:
                if i in [0,1]:
                    self.hbl1.addWidget(mp)
                else:
                    self.hbl2.addWidget(mp)
            elif self.numSubplots in [5,6]:
                if i in [0,1,2]:
                    self.hbl1.addWidget(mp)
                else:
                    self.hbl2.addWidget(mp)
            elif self.numSubplots in [7,8,9]:
                if i in [0,1,2]:
                    self.hbl1.addWidget(mp)
                elif i in [3,4,5]:
                    self.hbl2.addWidget(mp)
                else:
                    self.hbl3.addWidget(mp)
            elif self.numSubplots in [10,11,12]:
                if i in [0,1,2,3]:
                    self.hbl1.addWidget(mp)
                elif i in [4,5,6,7]:
                    self.hbl2.addWidget(mp)
                else:
                    self.hbl3.addWidget(mp)

        ## finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        self.vbl.addLayout(self.hbl3)
        self.setLayout(self.vbl)

### Run the tests 
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
        sys.exit()

    app = QtGui.QApplication(sys.argv)

    
    figMode = 'qa'
    plotsToViewChannels =   [(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,0),(2,1),(2,3),(0,0),(2,2),(3,3)]
    plotsToViewFiles =      [0,0,0,0,0,0,0,0,0,0,0,0]
    plotsToViewRuns =       ['run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1']
    plotsToViewHighlights = [None,None,None,None,None,None,None,None,None,None,None,None]
    numSubplots = 6

    nwv = NWayViewer(homeDir,plotsToViewChannels,plotsToViewFiles,plotsToViewRuns,plotsToViewHighlights,
                     subsample,numSubplots,figMode=figMode,background=True,modelType=modelType)

    nwv.show()
    sys.exit(app.exec_())    
