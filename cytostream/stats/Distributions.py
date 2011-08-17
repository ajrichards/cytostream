#!/usr/local/bin/env python

import re
import numpy as np


class GaussianDistn:
    '''
    A simple class representation of a Gaussian distribution
      mu - is the mean 
      sigma - is the standard deviation

    '''

    def __init__(self, mu, sigma):
        '''                                                                                                                                                   
        constructor                                                                                                                                           
                                                                                                                                                              
        '''
        ## ensure we are working with arrays and floats
        if type(mu) == type([]):
            mu = np.array(mu)
        if type(sigma) == type([]):
            sigma = np.array(sigma)
        if type(mu) == type(0):
            mu = float(mu)
        if type(sigma) == type(0):
            sigma = float(sigma)

        #self._input_error_check(mu,sigma)

        ## save the parameters
        self.mu = mu
        self.sigma = sigma

    def _input_error_check(self, mu,sigma):

        if type(sigma) == type(0.0):
            d = 1
        elif len(sigma.shape) == 1:
            d = 1
        elif len(sigma.shape) == 2:
            x,d = sigma.shape

        if type(mu) == type(0.0) and type(sigma) != type(0.0):
            raise TypeError, "In GaussianDist mismatched inputs"
        elif type(sigma) == type(0.0) and type(mu) != type(0.0):
            raise TypeError, "In GaussianDist mismatched inputs"
        elif mu.size[0] != x or mu.size[1] != d:
            raise TypeError, "In GaussianDist arg dim mismatch\n\tmu:%s\n\tn:%s\n\td:%s"%(len(mu),x,d)

        self.d = d

    def get_type(self):
        return self.__class__.__name__

    def generate(self,n):
        return np.random.normal(self.mu,self.sigma,n) 

class BetaDistn:
    '''
    A simple class representation of a Beta distribution
      mu - is the mean 
      sigma - is the standard deviation

    '''

    def __init__(self, a, b):
        '''                                                                                                                                                   
        constructor                                                                                                                                           
                                                                                                                                                              
        '''
        
        ## error checking
        self._input_error_check(a,b)

        ## save the parameters
        self.a = a
        self.b = b

    def _input_error_check(self, a,b):
        '''
        error check the inputs 
        '''

        if a <= 0:
            raise TypeError, "In BetaDist invalid arg 'a'" 
            return False

        if a <= 0:
            raise TypeError, "In BetaDist invalid arg 'b'" 
            return False

        return True

 

    def get_type(self):
        return self.__class__.__name__

