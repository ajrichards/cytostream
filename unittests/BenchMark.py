#!/usr/bin/env python


import sys,os,unittest,time,re,time

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import NoGuiAnalysis

## test class for the main window function
class BenchMarkTest(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd


        try:
            import gpustats
        except:
            print "ERROR: gpu not available not running benchmark"
            return

        ## declare variables
        projectID = 'utest'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        channelDict = {'FSCH':0,'SSCH':1,'FL1H':2,'FL2H':3}
        
        ## run the initial model for all files
        self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.set('subsample_qa', 1000)
        self.nga.set('subsample_analysis', 1000)
        self.nga.set('model_to_run','dpmm-mcmc')
        self.nga.set('dpmm_niters',100)
        self.nga.set('dpmm_burnin',900)
        
    def testRunModel(self):
        timeBegin = time.time()        
        self.nga.run_model()
        timeEnd = time.time()
        runTime = timeEnd - timeBegin
        print "Runtime", runTime

### Run the tests
if __name__ == '__main__':
    unittest.main()
