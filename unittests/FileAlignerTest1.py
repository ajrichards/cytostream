import os,sys,time,unittest,getopt,re
import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')
from cytostream.tools import calculate_intercluster_score,PieChartCreator,DotPlotCreator
from cytostream.stats import FileAligner
from cytostream import NoGuiAnalysis
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
        #filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        arrayList = [case1,case2,case3,case4,case5,case6]
        channelList = ['channel1','channel2']
        projectID = 'falign'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)

        ## setup class to run model
        self.nga = NoGuiAnalysis(homeDir,arrayList,useSubsample=True,makeQaFigs=False,record=False,dType='array',inputChannels=channelList)
        self.nga.run_model()
        fileNameList = self.nga.get_file_names()
    
        ## create all pairwise figs for all files
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')
        
        ## run the model again this time for only one file while using more of the config file functionality
        #fileName = "3FITC_4PE_004"
        #configDict['imput_data_type'] = 'array'
        #self.nga.set('excluded_channels_analysis',[1])
        #self.nga.set('thumbnails_to_view', [(0,2),(0,3)])
        #self.nga.set('file_in_focus',fileName)
        #self.nga.run_model()
        #self.nga.make_results_figures(fileName,'run2')
        
        ## if file_in_focus is changed return it to the original state
        #self.nga.set('file_in_focus','all')                

    def test_model_run(self):
        print 'testing complete'

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
        projectID = 'utest'
        self.homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        self.baseDir = BASEDIR

    def test_file_aligner_data_1(self):
        ## declare variables 
        modelName = 'cdp'
        mkPlots = True
        showCentroids = True
        expListNames = ['case1','case2','case3','case4','case5','case6']
        expListData = [case1,case2,case3,case4,case5,case6]
        expListLabels = [case1Labels,case2Labels,case3Labels,case4Labels,case5Labels,case6Labels]
        phiRange = [0.2,0.4] 

        ## determine location
        cwd = os.getcwd()

        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = cwd
        else:
            BASEDIR = os.path.join(os.path.split(cwd)[0],'unittests')

        ## run it
        timeBegin = time.time()
        fa = FileAligner(expListNames,expListData,expListLabels,modelName,phiRange=phiRange,refFile=None,excludedChannels=[],
                         verbose=VERBOSE,distanceMetric='mahalanobis',baseDir=BASEDIR)
        timeEnd = time.time()

        if VERBOSE == True:
            print "time taken for alignment: ", timeEnd - timeBegin 
            print 'creating figures'

        figMode = 'analysis'
        figName = os.path.join(self.baseDir,'unittests','before_alignment_fa_test1.png')
        figTitle = "before fa test1"
        ss = SaveSubplots(self.homeDir,figName,6,figMode=figMode,figTitle=figTitle,forceScale=True)
        os.remove(figName)

        #print dir(fa)
        #print 'mus', fa.sampleStats['mus']
        #print 'sigmas', fa.sampleStats['sigmas']
        #sys.exit()

        ## make plots
        #beforeStats = fa.get_sample_statistics(expListLabels)
        #beforeFig = os.path.join(BASEDIR,"alignfigs","unaligned","TestCase1Before.png")
        #make_plots_as_subplots(expListNames,expListData,expListLabels,centroids=beforeStats['mus'],showCentroids=True,
        #                       figTitle='Before File Alignment',saveas=beforeFig,refFile=fa.refFile,subplotRows=2,subplotCols=3,asData=True)

        #for phi in phiRange:
        #    afterStats = fa.get_sample_statistics(fa.newLabelsAll[str(round(phi,4))])
        #    pieChartSave = os.path.join(BASEDIR,"alignfigs","pies","piefigs_testcase1_%s.png"%(phi))
        #    pcc = PieChartCreator(fa.newLabelsAll[str(round(phi,4))],expListNames,saveas=pieChartSave,subplotRows=2,subplotCols=3)
        #    dotPlotSave = os.path.join(BASEDIR,"alignfigs","pies","dotfigs_%s.png"%(phi))
        #    dpc = DotPlotCreator(fa.newLabelsAll[str(round(phi,4))],[re.sub("ACS-T-Pt_", "", name) for name in expListNames],saveas=dotPlotSave)        
        #    afterFig = os.path.join(BASEDIR,"alignfigs",str(phi),"TestCase1After.png")
        #    make_plots_as_subplots(fa.expListNames,fa.expListData,fa.newLabelsAll[str(round(phi,4))],centroids=afterStats['mus'],showCentroids=True,
        #                           figTitle='After File Alignment',saveas=afterFig,refFile=fa.refFile,subplotRows=2,subplotCols=3,asData=True)
        
        #bestPhi, bestScore = fa.get_best_match()
        #print 'bestphi,bestscore',bestPhi, bestScore



        ## tests
        #self.assertEqual(bestScore,85600.0)
        #scatterFilePath = os.path.join(BASEDIR,"alignfigs",str(bestPhi),"TestCase1After.png")
        #self.assertTrue(os.path.isfile(scatterFilePath))
        #self.assertTrue(os.path.isfile(dotPlotSave))
        #self.assertTrue(os.path.isfile(pieChartSave))
    ''' 

### Run the tests 
if __name__ == '__main__':
    unittest.main()
