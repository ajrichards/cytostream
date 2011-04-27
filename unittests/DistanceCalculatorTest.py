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
                  
         ## calculate distances
         dc = DistanceCalculator(distType='euclidean')
         dc.calculate(mat)

         ## fetch distances
         distances = dc.get_distances()
         
         ## calculate the known answer
         answer = (mat - mat.mean(axis=0))**2.0   
         answer = np.sqrt(answer.sum(axis=1))

         ## check against known answer
         for element in range(distances.shape[0]):
             self.assertEqual(answer[element],distances[element])

     def testMahalanobis(self):         
         ## create an elipse that is wide in the x dimension
         largeN = 15
         a = np.random.normal(10,1.5,largeN)
         b = np.random.normal(10,0.5,largeN)
         mat = np.vstack((a,b)).T

         ## test that the input mean gives no input syntax 
         dc1 = DistanceCalculator(distType='mahalanobis')
         matrixMeans1 = dc1.get_mean(mat)
         dc1.calculate(mat)
         distances1 = dc1.get_distances()

         dc2 = DistanceCalculator(distType='mahalanobis')
         matrixMeans2 = dc2.get_mean(mat)
         dc2.calculate(mat,matrixMeans=matrixMeans2)
         distances2 = dc2.get_distances()

         ## check distances
         for d in range(len(distances1)):
             self.assertEqual(distances1[d],distances2[d])
         
         ## test that input inv covar provides same results as well
         dc3 = DistanceCalculator(distType='mahalanobis')
         matrixMeans3 = dc3.get_mean(mat)
         inverseCov = dc2.get_inverse_covariance(mat)
         dc3.calculate(mat,matrixMeans=matrixMeans3,inverseCov=inverseCov)
         distances3 = dc2.get_distances()

         ## check distances
         for d in range(len(distances1)):
             self.assertEqual(distances1[d],distances3[d])

### Run the tests                                                                                                                                                                    
if __name__ == '__main__':
    unittest.main()
