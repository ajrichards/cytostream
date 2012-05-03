import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

from cytostream import get_fcs_file_names
from cytostream.qtlib import CytostreamPlotter

class NWayViewer(QtGui.QWidget):

    def __init__(self,controller,channels,files,runs,highlights,numSubplots,figMode='qa',parent=None,
                 background=False,modelType=None,mainWindow=None,useScaled=False):

        QtGui.QWidget.__init__(self,parent)
        if parent == None:
            self.parent = self
        else:
            self.parent = parent

        ## input variables
        self.setWindowTitle('N Way Plotter')
        self.controller = controller
        self.homeDir = self.controller.homeDir
        self.channels = channels
        self.files = files
        self.runs = runs
        self.highlights = highlights
        self.numSubplots = int(numSubplots)
        self.figMode = figMode
        self.background = background
        self.modelType = modelType
        self.mainWindow = mainWindow
        self.plots = {}
 
        ## ensure valid input
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
        
        if self.figMode == "qa":
            subsample=self.controller.log.log['subsample_qa']
            modelType,modelName=None,None
        elif self.figMode == 'model results':
            subsample=self.controller.log.log['subsample_analysis']
            modelType=self.controller.log.log['results_mode']
        else:
            print "ERROR: NWayViewer invalid results mode"

        if self.numSubplots > 1:
            compactMode = True
        else:
            compactMode = False

        for i in range(self.numSubplots):
            cp = CytostreamPlotter(self.controller.fileNameList,
                                   self.controller.eventsList,
                                   self.controller.fileChannels,
                                   self.controller.channelDict,
                                   drawState='heat',
                                   modelRunID=self.runs[i],
                                   parent=self.parent,
                                   background=True,
                                   selectedChannel1=self.channels[i][0],
                                   selectedChannel2=self.channels[i][1],
                                   mainWindow=self.mainWindow,
                                   uniqueLabels=None,
                                   enableGating=False,
                                   homeDir=self.controller.homeDir,
                                   compactMode=compactMode,
                                   labelList=None,
                                   minNumEvents=3,
                                   showNoise=False,
                                   axesLabels=True,
                                   useScaled=useScaled,
                                   plotTitle="default",
                                   dpi=100,
                                   subsample = subsample,
                                   transform=self.controller.log.log['plots_transform'],
                                   subplotNum=i+1
                                   )

            cp.draw(selectedFile=self.controller.fileNameList[self.files[i]])

            ## store widget for editing
            self.plots[str(i+1)] = cp

            ## widget layout
            if self.numSubplots in [1,2,3]:
                self.hbl1.addWidget(cp)
            elif self.numSubplots in [4]:
                if i in [0,1]:
                    self.hbl1.addWidget(cp)
                else:
                    self.hbl2.addWidget(cp)
            elif self.numSubplots in [5,6]:
                if i in [0,1,2]:
                    self.hbl1.addWidget(cp)
                else:
                    self.hbl2.addWidget(cp)
            elif self.numSubplots in [7,8,9]:
                if i in [0,1,2]:
                    self.hbl1.addWidget(cp)
                elif i in [3,4,5]:
                    self.hbl2.addWidget(cp)
                else:
                    self.hbl3.addWidget(cp)
            elif self.numSubplots in [10,11,12]:
                if i in [0,1,2,3]:
                    self.hbl1.addWidget(cp)
                elif i in [4,5,6,7]:
                    self.hbl2.addWidget(cp)
                else:
                    self.hbl3.addWidget(cp)

        ## finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        self.vbl.addLayout(self.hbl3)
        self.setLayout(self.vbl)

### Run the tests 
if __name__ == '__main__':

    from cytostream import NoGuiAnalysis
    app = QtGui.QApplication(sys.argv)

    ## check that unittests were run and necessary data is present
    baseDir = os.getcwd()
    selectedFile = "3FITC_4PE_004"
    filePath = os.path.join(baseDir,"..","example_data",selectedFile+".fcs")
    channelDict = {'FSCH':0,'SSCH':1}
    subsample = 100000

    ## setup class to run model
    homeDir = os.path.join(baseDir,"..","projects","utest")
    nga = NoGuiAnalysis(homeDir,channelDict,[filePath],useSubsample=True,makeQaFigs=False,record=False,transform='logicle')
    nga.set('num_iters_mcmc', 1200)
    nga.set('subsample_qa', 2000)
    nga.set('subsample_analysis', subsample)
    nga.set('dpmm_k',96)
    nga.set('thumbnail_results_default','components')
    
    figMode = 'qa'
    plotsToViewChannels   = [(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,0),(2,1),(2,3),(0,0),(2,2),(3,3)]
    plotsToViewFiles      = [0,0,0,0,0,0,0,0,0,0,0,0]
    plotsToViewRuns       = ['run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1']
    plotsToViewHighlights = [None,None,None,None,None,None,None,None,None,None,None,None]
    numSubplots = 1

    nwv = NWayViewer(nga.controller,plotsToViewChannels,plotsToViewFiles,plotsToViewRuns,plotsToViewHighlights,
                     numSubplots,figMode=figMode,background=True,modelType='components',useScaled=True)

    nwv.show()
    sys.exit(app.exec_())    
