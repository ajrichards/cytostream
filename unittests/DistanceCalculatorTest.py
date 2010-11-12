#!/usr/bin/env python

import sys,os,unittest,time,re
from scipy.spatial.distance import cdist, pdist, squareform

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

from cytostream.stats import DistanceCalculator
import numpy as np
BASEDIR = os.path.dirname(__file__)

 
class DistanceCalculatorTest(unittest.TestCase):

     def testEuclideanDistance(self):         
         ## debug
         a = np.array([1,2,3,4,5])
         b = np.array([1,1,1,1,1])
         mat = np.vstack((a,b)).T
                  
         ## get distances
         dc = DistanceCalculator(mat,distType='euclidean')
         distances = dc.get_distances()

         ## check against known answer
         answer = np.array([ 2,  1,  0,  1,  2])
         print distances.shape
         for element in range(distances.shape[0]):
             self.assertEqual(answer[element],distances[element])

     def testMahalanobis(self):         
         ## create an elipse that is wide in the x dimension
         largeN = 15
         a = np.random.normal(10,1.5,largeN)
         b = np.random.normal(10,0.5,largeN)
         mat = np.vstack((a,b)).T

         ## get distances
         dc = DistanceCalculator(mat,distType='mahalanobis')
         distances = dc.get_distances()

### Run the tests                                                                                                                                                                    
if __name__ == '__main__':
    unittest.main()
