#!/usr/bin/env python

import os,sys,time,unittest,getopt,re
import matplotlib
import numpy as np
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')
from cytostream.tools import PieChartCreator,DotPlotCreator
from cytostream.stats import FileAligner
from cytostream import NoGuiAnalysis,SaveSubplots
from SimulatedData1 import case1, case2, case3, case4, case5, case6
from SimulatedData1 import case1Labels, case2Labels, case3Labels, case4Labels, case5Labels, case6Labels


## debugging the low num events
case1 = np.vstack([case1,np.array([15,6])])
case1Labels = np.hstack([case1Labels,np.array([99])])

## check for verbose flag
VERBOSE=False
optlist, args = getopt.getopt(sys.argv[1:], 'v')
for o, a in optlist:
    if o == '-v':
        VERBOSE = True

class FileAlignerTest1(unittest.TestCase):
    '''
    test class for 6 different simulated cases

    '''

    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## run the no gui analysis
        expListData = [case1,case2,case3,case4,case5,case6]
        channelList = ['channel1','channel2']
        projectID = 'falign'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        expListNames = ['case1','case2','case3','case4','case5','case6']
        expListLabels = []
        modelName = 'dpmm'
        phiRange = [0.1,0.6,0.9]
        useDPMM = False
        
        ## setup class to run model        
        self.nga = NoGuiAnalysis(homeDir,expListData,useSubsample=True,makeQaFigs=False,record=False,dType='array',inputChannels=channelList)
        self.nga.set("subsample_analysis", "original")
        self.nga.set("thumbnail_results_default","components")

        if useDPMM == True:    
            self.nga.run_model()
            
            for fileName in ['array1', 'array2', 'array3','array4','array5','array6']:
                statModel, statModelClasses = self.nga.get_model_results(fileName,'run1','components')
                expListLabels.append(statModelClasses)
        else:
            expListLabels = [case1Labels,case2Labels,case3Labels,case4Labels,case5Labels,case6Labels]
         
        ## run file alignment
        expListNames = ['array1', 'array2', 'array3','array4','array5','array6']
        print "Running file alignment.........."
        self.fa = FileAligner(expListNames,expListData,expListLabels,phiRange,verbose=VERBOSE,homeDir=homeDir)
        self.fa.run(evaluator='rank',filterNoise=True)
                
        ## save the plots 
        print 'making figures...'
        self.nga.set("subsample_analysis", "original")
        plotsToViewChannels = [(0,1) for i in range(16)]
        self.nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewFiles = range(16)
        self.nga.set("plots_to_view_files",plotsToViewFiles)
        
        figsDir = os.path.join(homeDir,'figs','alignment')
        numSubplots = 6
        figMode = 'qa'
        figName = os.path.join(figsDir,'subplots_orig_qa.png')
        figTitle = "unittest fa1 - unaligned qa"
        ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True,drawState='heat')

        figMode = 'analysis'
        figName = os.path.join(figsDir,'subplots_orig_dpmm.png')
        if useDPMM == True:
            figTitle = "unittest fa1 - unaligned dpmm"
        else:
            figTitle = "Clustered labels"
        plotsToViewRuns = self.nga.controller.log.log['plots_to_view_runs']
        if useDPMM == False:
            ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True,inputLabels=expListLabels)
        else:
            ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)

        ## saves a plot of the modes
        modeLabels = self.fa.phi2Labels
        figName = os.path.join(figsDir,'modes_phi2.png')
        figTitle = "Unaligned Modes Phi2"
        ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True,inputLabels=modeLabels)

        for phi in phiRange:
            ## saves a plot of the aligned modes
            alignLabels = self.fa.alignLabels[str(phi)]
            figName = os.path.join(figsDir,'aligned_%s.png'%phi)
            figTitle = "Aligned Modes %s"%phi
            ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True,inputLabels=alignLabels)

    def test_model_run(self):
        ## test that we picked up the noise cluster
        self.failIf(len(self.fa.noiseClusters['array6']) != 1) 
        ### tests 
        bestPhi, bestScore = self.fa.get_best_match()
        print 'bestScore',bestScore,self.fa.globalScoreDict['0.1']


### Run the tests 
if __name__ == '__main__':
    unittest.main()
