#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault, SaveSubplots

'''
description - Shows the user how to run a simple model then several subplots are generated to 
              illustrate plot generation.

A. Richards
'''


class TestCase4(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## run the no gui analysis
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]

        projectID = 'utest'
        self.homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        self.baseDir = BASEDIR

        ## run the initial model for all files
        configDict = configDictDefault.copy()
        configDict['num_iters_mcmc'] = 1200

        self.nga = NoGuiAnalysis(self.homeDir,filePathList,configDict=configDict,useSubsample=True,makeQaFigs=False,record=False)
        fileNameList = self.nga.get_file_names()
    
        ## create all pairwise figs for within cytostream visualization
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')
    
    def test_plot_generation(self):

        numSubplots = 12

        ## test basic quality assurance plots
        figMode = 'qa'
        figName = os.path.join(self.baseDir,'unittests','subplots_test_qa.png')
        figTitle = "testing qualitiy assurance plots"
        ss = SaveSubplots(self.homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)
        print 'plot saved as ', figName

        ## change several subplots indices
        plotsToViewChannels = [(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)]
        self.nga.set('plots_to_view_channels',plotsToViewChannels)

        ## note that which files appear in a subplot or which model can be changed using the following
        plotsToViewFiles = [0,0,0,0,0,0,0,0,0,0,0,0]
        plotsToViewRuns = ['run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1','run1']
        self.nga.set('plots_to_view_files',plotsToViewFiles)
        self.nga.set('plots_to_view_runs', plotsToViewRuns)

        ## plot run1
        figMode = 'analysis'
        figName = os.path.join(self.baseDir,'unittests','subplots_test_run1a.png')
        figTitle = "testing run1 plots"
        ss = SaveSubplots(self.homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)
        print 'plot saved as ', figName

        ## show use of highlighting and how to change the number of subplots
        plotsToViewHighlights = [0,1,2,3,None,None,None,None,None,None,None,None]
        self.nga.set('plots_to_view_highlights', plotsToViewHighlights)
        numSubplots = 4
        figName = os.path.join(self.baseDir,'unittests','subplots_test_run1b.png')
        figTitle = "testing run1 plots highlighting"
        ss = SaveSubplots(self.homeDir,figName,numSubplots,figMode=figMode,figTitle=figTitle,forceScale=True)
        print 'plot saved as ', figName


### Run the tests 
if __name__ == '__main__':
    unittest.main()
