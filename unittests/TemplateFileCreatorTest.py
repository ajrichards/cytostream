import sys,os,unittest,time,re

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

import numpy as np
from SimulatedData3 import case1, case2, case3
from SimulatedData3 import case1Labels, case2Labels, case3Labels
from cytostream.stats import TemplateFileCreator

BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class TemplateFileCreatorTest(unittest.TestCase):


    def testForCorrectTemplateFileCreation(self):
        fileList = [case1,case2,case3]
        fileLabelList = [case1Labels,case2Labels,case3Labels]
        tfc = TemplateFileCreator(fileList,fileLabelList)

        ## check that template contains correct num labels
        self.assertEqual(len(np.unique(tfc.templateLabels)),27)
        
        ## check that case 1 is used to create the template file
        self.assertEqual(tfc.templateSeedInd,0)

        ## ensure that we have the correct num. of thresholds
        self.assertEqual(len(tfc.thresholds),len(fileList))
        self.assertEqual(len(tfc.templateThresholds.keys()),27)

        ## ensure best labeling is 3 clusters
        firstBest = tfc.bestModeLabels[0]
        self.assertEqual(len(np.unique(firstBest)),3)

        ## ensure that the second best has 9 clusters
        secondBest = tfc.bestModeLabels[1]
        self.assertEqual(len(np.unique(secondBest)),9)

        ## draw stuff
        tfc.draw_templates()
        #tfc.draw_dendragram()
        
    def testForCorrectNumClustersAdded(self):
        fileList = [case1,case2,case3]
        fileLabelList = [case1Labels,case2Labels,case3Labels]
        tfc = TemplateFileCreator(fileList,fileLabelList,templateSeedInd=2)

        ## check that template contains correct num labels
        self.assertEqual(len(np.unique(tfc.templateLabels)),26)


### Run the tests 
if __name__ == '__main__':
    unittest.main()
