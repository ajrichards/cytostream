import sys,os,unittest,time,re
import numpy as np
from SimulatedData2 import case1, case2, case3
from SimulatedData2 import case1Labels, case2Labels, case3Labels
import matplotlib.pyplot as plt
from fcm.statistics import mixnormpdf
from cytostream.stats import run_kmeans_with_sv

BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class MultivarTestPDF(unittest.TestCase):

    _initialized = False

    def setUp(self):
        if self._initialized == False:
            self._initialize()        

    def _initialize(self):
        self.__class__._initialized = True

    def doNotTestPlot(self):
        print 'create plot'
        self.assertTrue(self._initialized)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(case1[:,0],case1[:,1],'o',linewidth=0)
        plt.show()

    def testThatItWorks(self):
        self.assertTrue(self._initialized)
        
        ## use kmeans to fit the data and get labels
        kmeanResults = run_kmeans_with_sv(case1)
        kmeanCentroids =  kmeanResults['centroids']
        kmeanLabels = kmeanResults['labels']
        k = kmeanResults['k'] 
        avgSilVal = kmeanResults['avgSilVal']

        ## ensure good kmean results
        self.assertEqual(int(k),2)
        self.assertEqual(len(kmeanCentroids),int(k))
        self.assertEqual(len(kmeanLabels),int(case1.shape[0]))

        ## use sample stats to parameterize the mixnormpdf
        mu = np.array([case1[np.where(kmeanLabels == i)[0],:].mean(axis=0) for i in [0,1]])
        sigma = np.array([np.cov(case1[np.where(kmeanLabels == i)[0],:].T) for i in [0,1]])
        pi = np.array([float(len(np.where(kmeanLabels == i)[0])) / float(len(kmeanLabels)) for i in [0,1]])

        x = np.array([[8,20],[10,12]])
        mnpdf = mixnormpdf(x,pi,mu,sigma)
        
        ## make sure the point the is far away has a smaller probability
        self.assertTrue(mnpdf[1] > mnpdf[0])
        
        ## ensure we have proper probabilities
        self.assertEqual(len(np.where(mnpdf < 1.0)[0]),2)
        self.assertEqual(len(np.where(mnpdf > 0.0)[0]),2)


### Run the tests 
if __name__ == '__main__':
    unittest.main()

    
