import sys,os,unittest,time,re

BASEDIR = os.path.dirname(__file__)

from cytostream.stats import GaussianDistn, kullback_leibler
import numpy as np

## test class for the main window function
class KullbackLeiblerTest(unittest.TestCase):


    def testUnivariateCase(self):
        gd1 = GaussianDistn(2,2)
        gd2 = GaussianDistn(2.0,2.0)
        klDist = kullback_leibler(gd1,gd2)
        self.assertEqual(int(klDist.sum()),0)
        
    def testBivariateCase(self):
        gd1 = GaussianDistn([5,2],np.array([2.0,1.0]))
        gd2 = GaussianDistn([5,2],np.array([2.0,1.0]))
        klDist = kullback_leibler(gd1,gd2)
        self.assertEqual(int(klDist.sum()),0)
        
    def testMultivariateCase(self):
        #cov = np.array([[1,2,3],[2,1,2],[3,2,1]])
        cov = np.array([[1,0,0],[0,1,0],[0,0,1]])
        gd1 = GaussianDistn([5,2,3],cov)
        gd2 = GaussianDistn([5,2,3],cov)
        klDist = kullback_leibler(gd1,gd2)
        self.assertEqual(int(klDist.sum()),0)
    

### Run the tests 
if __name__ == '__main__':
    unittest.main()
