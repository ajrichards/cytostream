#!/usr/bin/env python

import os,sys,time,unittest,getopt,re
import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')
from cytostream.tools import calculate_intercluster_score,PieChartCreator,DotPlotCreator
from cytostream.stats import FileAligner
from cytostream import NoGuiAnalysis,SaveSubplots
from SimulatedData1 import case1, case2, case3, case4, case5, case6
from SimulatedData1 import case1Labels, case2Labels, case3Labels, case4Labels, case5Labels, case6Labels

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
        arrayList = [case1,case2,case3,case4,case5,case6]
        channelList = ['channel1','channel2']
        projectID = 'falign'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)

        ## setup class to run model
        self.nga = NoGuiAnalysis(homeDir,arrayList,useSubsample=True,makeQaFigs=False,record=False,dType='array',inputChannels=channelList)
        self.nga.set("subsample_analysis", "original")
        self.nga.set("thumbnail_results_default","components")        
        self.nga.run_model()
        
        ## create all pairwise figs for all files
        #fileNameList = self.nga.get_file_names()
        #for fileName in fileNameList:
        #    self.nga.make_results_figures(fileName,'run1')
 
        ## gather required data for file alignment
        #expListLabels = [case1Labels,case2Labels,case3Labels,case4Labels,case5Labels,case6Labels]
        expListNames = ['case1','case2','case3','case4','case5','case6']
        expListLabels = []
        modelName = 'dpmm'
        phiRange = [0.2,0.8]

        ## get labels from dpmm model run (array is default if no file name is given)
        for fileName in ['array1', 'array2', 'array3','array4','array5','array6']:
            statModel, statModelClasses = self.nga.get_model_results(fileName,'run1','components')
            expListLabels.append(statModelClasses)


        ## run file alignment 
        print "Running file alignment.........."
        timeBegin = time.time()
        self.fa = FileAligner(expListNames,arrayList,expListLabels,modelName,phiRange=phiRange,refFile=None,excludedChannels=[],verbose=VERBOSE,
                              distanceMetric='mahalanobis',baseDir=homeDir)
        timeEnd = time.time()
        print "time taken for alignment: ", timeEnd - timeBegin
        
        ## save the plots 
        print 'making figures...'
        plotsToViewChannels = [(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)]
        self.nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewFiles = [0,1,2,3,4,5,0,0,0,0,0,0]
        self.nga.set("plots_to_view_files",plotsToViewFiles)
        plotsToViewRuns = ['run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1']
        self.nga.set('plots_to_view_files',plotsToViewFiles)
        alignDir = os.path.join(homeDir,'alignfigs','test')
        os.mkdir(alignDir)

        numSubplots = 6
        figMode = 'qa'
        figName = os.path.join(alignDir,'subplots_orig_qa.png')
        figTitle = "unittest fa1 - unaligned qa"
        ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)

        figMode = 'analysis'
        figName = os.path.join(alignDir,'subplots_orig_dpmm.png')
        figTitle = "unittest fa1 - unaligned dpmm"
        plotsToViewRuns = self.nga.controller.log.log['plots_to_view_runs']
        ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)

        bestPhi, bestScore = self.fa.get_best_match()
        bestLabels = self.fa.newLabelsAll[str(bestPhi)]
        figName = os.path.join(alignDir,'subplots_aligned.png')
        ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True,inputLabels=bestLabels)

    def test_model_run(self):

        ## tests 
        self.failIf(self.fa.globalScoreDict['0.2'] < 85000.0)
        bestPhi, bestScore = self.fa.get_best_match()
        self.assertEqual(bestPhi,str(0.2))
        print 'testing complete'

### Run the tests 
if __name__ == '__main__':
    unittest.main()
