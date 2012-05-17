#!/usr/bin/env python


import sys,os,unittest,time,re,time,subprocess

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import NoGuiAnalysis

## python path 
if sys.platform == 'win32':
    pythonPath = os.path.join("C:\Python27\python")
elif sys.platform == 'darwin':
    pythonPath = os.path.join("/","usr","local","bin","python")
else:
    pythonPath = os.path.join(os.path.sep,"usr","bin","python")

## test class for the main window function
class BenchMarkTest(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            self.baseDir = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            self.baseDir = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## declare variables
        #projectID = 'utest'
        #self.homeDir =  os.path.join(self.baseDir,"cytostream","projects", projectID)
        #filePathList = [os.path.join(self.baseDir,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        #channelDict = {'FSCH':0,'SSCH':1,'FL1H':2,'FL2H':3}

        ##################################################################
        projectID = 'eqapol-test'
        self.homeDir =  os.path.join(self.baseDir,"cytostream","projects", projectID)
        filePathList = [os.path.join(os.getenv("HOME"),"research","eqapol","sendout1","Site_Data","002","FCS_Files","002_11Aug11_A03.fcs")]
        channelDict = {'FSCA':0,'SSCA':1,'CD4':2,'CD3':3,'IFNG+IL2':4,'CD8':5,'Time':6}
        ##################################################################

        ## run the initial model for all files
        self.nga = NoGuiAnalysis(self.homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.set('subsample_qa', 2000)
        self.nga.set('subsample_analysis', 'original') ## 
        self.nga.set('model_to_run','dpmm-mcmc')
        self.nga.set('dpmm_niter',1)
        self.nga.set('dpmm_burnin',999)
        self.nga.set('dpmm_k',96)
        self.fileName = self.nga.get_file_names()[0]

    def testRunModel(self):
        try:
            import gpustats
        except:
            print "ERROR: gpu not available not running benchmark"
            return

        timeBegin = time.time()
        #self.nga.run_model()
        gpuDevice = 2
        script = os.path.join(self.baseDir,'cytostream',"RunModelDPMM.py")
        cmd = "%s %s -h %s -g %s -f %s"%(pythonPath,script,self.homeDir,gpuDevice,self.fileName)
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)

        while True:
            next_line = proc.stdout.readline()
            if next_line == '' and proc.poll() != None:
                break
            sys.stdout.write(next_line)
            sys.stdout.flush()

        timeEnd = time.time()
        runTime = timeEnd - timeBegin
        print "Runtime", runTime

### Run the tests
if __name__ == '__main__':
    unittest.main()
