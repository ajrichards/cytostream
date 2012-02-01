import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

from cytostream import get_fcs_file_names
from cytostream.qtlib import CytostreamPlotter

class NWayViewer(QtGui.QWidget):

    def __init__(self,nga,channels,files,runs,highlights,subsample,numSubplots,figMode='qa',parent=None,
                 background=False,modelType=None,mainWindow=None):

        QtGui.QWidget.__init__(self,parent)

        ## input variables
        self.setWindowTitle('N Way Plotter')
        self.nga = nga
        self.homeDir = self.nga.homeDir
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

        print len(self.nga.eventsList)
        sys.exit()


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
            cp = CytostreamPlotter(self.files,
                                   self.nga.eventsList,
                                   channelList,
                                   channelDict,
                                   drawState='heat',
                                   parent=self.parent,
                                   background=True,
                                   selectedChannel1=self.channels[i][0],
                                   selectedChannel2=self.channels[i][0],
                                   mainWindow=None,
                                   uniqueLabels=None,
                                   enableGating=False,
                                   homeDir=None,
                                   compactMode=False,
                                   labelList=None,
                                   minNumEvents=3,
                                   showNoise=False,
                                   axesLabels=True,
                                   useScaled=False,
                                   plotTitle="default",
                                   dpi=100,
                                   subsample = 'original',
                                   transform='logicle'
                                   )

            #cp = CytostreamPlotter(selectedChannel1=self.channels[i][0],selectedChannel2=self.channels[i][1],enableGating=False,
            #                       homeDir=self.homeDir,isProject=True,compactMode=True)
            #cp.init_labels_events(self.files[i],self.runs[i],modelType=self.modelType)
            #cp.draw()
    
            cp.draw(selectedFile=fileNameList[0])

            if self.numSubplots in [2]:
                self.hbl1.addWidget(cp)
            elif self.numSubplots in [3]:
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
        channelDict = {'fsc-h':0,'ssc-h':1}
        filePathList = [os.path.join(os.getcwd(),"cytostream","example_data", "3FITC_4PE_004.fcs")]
        print "WARNING: Model not present - (Re)running unit test"
        self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.set('subsample_qa', 1000)
        self.nga.set('subsample_analysis', 1000)
        self.nga.run_model()
    else:
        ## connect to a cytostream project
        nga = NoGuiAnalysis(homeDir,loadExisting=True)
        app = QtGui.QApplication(sys.argv)
    
    figMode = 'qa'
    plotsToViewChannels =   [(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,0),(2,1),(2,3),(0,0),(2,2),(3,3)]
    plotsToViewFiles =      [0,0,0,0,0,0,0,0,0,0,0,0]
    plotsToViewRuns =       ['run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1']
    plotsToViewHighlights = [None,None,None,None,None,None,None,None,None,None,None,None]
    numSubplots = 2

    nwv = NWayViewer(nga,plotsToViewChannels,plotsToViewFiles,plotsToViewRuns,plotsToViewHighlights,
                     subsample,numSubplots,figMode=figMode,background=True,modelType=modelType)

    nwv.show()
    sys.exit(app.exec_())    
