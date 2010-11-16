#!/usr/bin/env python

import time
import numpy as np
from scipy.spatial.distance import cdist, squareform
from scipy.linalg import inv

class DistanceCalculator():
    def __init__(self,matrixMeans=None,distType='euclidean'):
        
        '''
        this class calculates the distance from a set of vectors (features) and another set of means
        
        '''

        ## variables
        self.distType = distType

        ## error checking
        validMetrics = ['euclidean','mahalanobis']
        if self.distType not in validMetrics:
            raise RuntimeError("ERROR in distance calculator - input distance type is invalid \nmust be in %s"%validMetrics)
            return None
    
    def calculate_dev(self,mat,matrixMeans=None,inverseCov=None):
        ## error checking
        if type(np.array([])) != type(mat):
            raise RuntimeError("ERROR in distance calculator - input matrix must be of type np.array()")
            return None
        
        ## gather dimensions of the input matrix
        dims = mat.shape
        
        if len(dims) == 1:
            n = dims[0]
            d = 1
        elif len(dims) == 2:
            n,d = dims
        else:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)

        if matrixMeans != None:
            if matrixMeans.size != d:
                raise RuntimeError("ERROR in distance calculator - badly formated matrix means - %s")
        else:
            matrixMeans = mat.mean(axis=0)

        if self.distType == 'euclidean':
            dists = (mat - matrixMeans)**2.0
            dists = np.sqrt(dists.sum(axis=1))
        
        self.dists = dists


    def calculate(self,mat,matrixMeans=None,inverseCov=None):
        ## error checking
        if type(np.array([])) != type(mat):
            raise RuntimeError("ERROR in distance calculator - input matrix must be of type np.array()")
            return None
        
        ## gather dimensions of the input matrix
        dims = mat.shape
        
        if len(dims) == 1:
            n = dims[0]
            d = 1
        elif len(dims) == 2:
            n,d = dims
        else:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)

        if matrixMeans != None:
            if matrixMeans.size != d:
                raise RuntimeError("ERROR in distance calculator - badly formated matrix means - %s")

        ## find matrix means
        if matrixMeans == None:
            matrixMeans = self.get_mean(mat)

        ## get distances using scipy 
        matrixMeans = matrixMeans.reshape((1,d))

        if self.distType == 'euclidean':
            self.dists = cdist(mat,matrixMeans,self.distType)
        elif self.distType == 'mahalanobis':
            self.dists = cdist(mat,matrixMeans,self.distType, VI=None)

        self.dists = self.dists[:,0]

    def get_mean(self,mat):
        ## get distances using scipy 
        dims = mat.shape
        if len(dims) == 1:
            n = dims[0]
            d = 1
        elif len(dims) == 2:
            n,d = dims
        else:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)
        
        matrixMeans = mat.mean(axis=0)

        return matrixMeans

    def get_inverse_covariance(self,mat):

        ## get distances using scipy 

        dims = mat.shape
        if len(dims) == 1:
            n = dims[0]
            d = 1
        elif len(dims) == 2:
            n,d = dims
        else:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)
        
        a = mat.T

        ## get the covariance matrix and its inverse
        cov = np.cov(a)
        invCov = np.linalg.inv(cov)

        if invCov.shape[0] != d and invCov.shape[1] != d:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)

    def get_distances(self):
        return self.dists
