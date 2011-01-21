import os,sys,unittest,getopt,time
import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')

from cytostream.stats import FileAligner
from cytostream.tools import make_plots_as_subplots,calculate_intercluster_score,PieChartCreator
from SimulatedData2 import case1, case2, case3
from SimulatedData2 import case1Labels, case2Labels, case3Labels

## check for verbose flag
VERBOSE=False
optlist, args = getopt.getopt(sys.argv[1:], 'v')
for o, a in optlist:
    if o == '-v':
        VERBOSE = True

class FileAlignerTest2(unittest.TestCase):
    '''      
    test class for 3 different simulated cases
                     
    '''
    def test_file_aligner_data_2(self):
        ## declare variables 
        modelName = 'cdp'
        mkPlots = True
        showCentroids = True
        expListNames = ['case1','case2','case3']
        expListData = [case1,case2,case3]
        expListLabels = [case1Labels,case2Labels,case3Labels]
        phiRange = [0.2,0.8] 

        ## determine location                             
        cwd = os.getcwd()

        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = cwd
        else:
            BASEDIR = os.path.join(os.path.split(cwd)[0],'unittests')

        ## run it
        timeBegin = time.time()
        fa = FileAligner(expListNames,expListData,expListLabels,modelName,phiRange=phiRange,refFile=None,excludedChannels=[],verbose=VERBOSE,distanceMetric='mahalanobis',baseDir=BASEDIR)
        timeEnd = time.time()

        if VERBOSE == True:
            print "time taken for alignment: ", timeEnd - timeBegin
            print 'creating figures'

        ## make plots
        beforeStats = fa.get_sample_statistics(expListLabels)
        beforeFig = os.path.join(BASEDIR,"alignfigs","unaligned","TestCase2Before.png")
        make_plots_as_subplots(expListNames,expListData,expListLabels,centroids=beforeStats['mus'],showCentroids=True,
                               figTitle='Before File Alignment',saveas=beforeFig,refFile=fa.refFile,subplotRows=1,subplotCols=3,asData=True)

        for phi in phiRange:
            afterStats = fa.get_sample_statistics(fa.newLabelsAll[str(round(phi,4))])
            pieChartSave = os.path.join(BASEDIR,"alignfigs","pies","piefigs_testcase2_%s.png"%(phi))
            pcc = PieChartCreator(fa.newLabelsAll[str(round(phi,4))],expListNames,saveas=pieChartSave,subplotRows=1,subplotCols=3)
            afterFig = os.path.join(BASEDIR,"alignfigs",str(phi),"TestCase2After.png")
            make_plots_as_subplots(fa.expListNames,fa.expListData,fa.newLabelsAll[str(round(phi,4))],centroids=afterStats['mus'],showCentroids=True,
                                   figTitle='After File Alignment',saveas=afterFig,refFile=fa.refFile,subplotRows=1,subplotCols=3,asData=True)

        bestPhi, bestScore = fa.get_best_match()
        print 'bestphi,bestscore',bestPhi, bestScore
        print fa.globalScoreDict

        ## tests                               
        self.assertEqual(fa.globalScoreDict['0.2'], 6400.0)
        self.assertEqual(fa.globalScoreDict['0.8'], 2200.0)

### Run the tests                            
if __name__ == '__main__':
    unittest.main()
