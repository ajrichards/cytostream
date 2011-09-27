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
        #self.assertEqual(len(tfc.thresholds),len(fileList))
        #self.assertEqual(len(tfc.templateThresholds.keys()),27)

        ## sil value ranking 
        print 'mode sil values', tfc.modeSilValues
        print 'cluster sil values', tfc.clusterSilValues
        print 'mode sizes', tfc.modeSizes
        print 'best mode sizes  by sv', tfc.modeSizes[np.argsort(tfc.modeSilValues)[::-1]]#tfc.modeSizes[np.argsort(tfc.modeSilValues)]


        ## ensure best labeling is 3 clusters
        firstBest = tfc.bestModeLabels[0]
        self.assertEqual(len(np.unique(firstBest)),3)

        ## ensure that the second best has 9 clusters
        secondBest = tfc.bestModeLabels[1]
        self.assertEqual(len(np.unique(secondBest)),9)

        ## draw stuff
        tfc.draw_templates()
        #tfc.draw_dendragram()
        
    #def testForCorrectNumClustersAdded(self):
    #    fileList = [case1,case2,case3]
    #    fileLabelList = [case1Labels,case2Labels,case3Labels]
    #    tfc = TemplateFileCreator(fileList,fileLabelList,templateSeedInd=2)
    #    
    #    print np.sort(np.unique(tfc.templateLabels))
    #
    #    ## check that template contains correct num labels
    #    self.assertEqual(len(np.unique(tfc.templateLabels)),26)

    def tearDown(self):
        for fileName in ['Template.log','templateData.pickle','templateComponents.pickle','templateModes.pickle',
                         'noiseClusters.pickle']:
            if os.path.exists(fileName):
                os.remove(fileName)
            #if os.path.exists('templates.png'):
            #    os.remove('templates.png')


### Run the tests 
if __name__ == '__main__':
    unittest.main()
