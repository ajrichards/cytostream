#!/usr/bin/env python

import numpy as np
from scipy.spatial.distance import cdist, squareform


class DistanceCalculator():
    def __init__(self,mat,matrixMeans=None,distType='euclidean'):
        
        '''
        this class calculates the distance from a set of vectors (features) and another set of means
        
        '''

        ## variables
        self.distType = distType

        ## error checking
        if type(np.array([])) != type(mat):
            raise RuntimeError("ERROR in distance calculator - input matrix must be of type np.array()")
            return None
        
        validMetrics = ['euclidean','mahalanobis']
        if self.distType not in validMetrics:
            raise RuntimeError("ERROR in distance calculator - input distance type is invalid \nmust be in %s"%validMetrics)
            return None
    
        if matrixMeans != None:
            if matrixMeans.shape[0] != n or matrixMeans.shape[1] != d:
                raise RuntimeError("ERROR in distance calculator - calculation of matrix means had a dimension error")

        ## gather dimensions of the input matrix
        dims = mat.shape
        if len(dims) == 1:
            n = dims[0]
            d = 1
        elif len(dims) == 2:
            n,d = dims
        else:
            raise RuntimeError("ERROR in distance calculator - input matrix does not have reasonable dimensions - %s"%dims)

        ## find matrix means
        if matrixMeans == None:
            matrixMeans = self.get_means_as_matrix(mat)

        print 'mean', mat.mean(axis=0)

        ## get distances using scipy 
        matrixMeans = mat.mean(axis=0)
        matrixMeans = np.tile(matrixMeans,[n,1])

        if self.distType == 'euclidean':
            self.dists = cdist(mat,matrixMeans,self.distType)
        elif self.distType == 'mahalanobis':
            self.dists = cdist(mat,matrixMeans,self.distType, VI=None)

        self.dists = self.dists[:,0]

    def get_means_as_matrix(self,mat):
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
        matrixMeans = np.tile(matrixMeans,[n,1])

        return matrixMeans

    def get_distances(self):
        return self.dists
