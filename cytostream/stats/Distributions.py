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
        ## error checking
        if type(mu) == type([]):
            mu = np.array(mu)
        if type(sigma) == type([]):
            sigma = np.array(sigma)
        self._input_error_check(mu,sigma)

        if type(mu) == type(0):
            mu = float(mu)
        if type(sigma) == type(0):
            sigma = float(sigma)

        ## save the parameters
        self.mu = mu
        self.sigma = sigma

    def _input_error_check(self, mu,sigma):
        
        if type(mu) != type([]) and type(mu) != type(np.array([])):
            if re.search("a-z|A-Z",str(mu)):
                raise TypeError, "In GaussianDist arg 'mu' must be numeric"
            if re.search("a-z|A-Z",str(sigma)):
                raise TypeError, "In GaussianDist arg 'sigma' must be numeric"
        else:

            if len(mu) == 2: 
                n = sigma.shape[0]
                if len(mu) != n:
                    raise TypeError, "In GaussianDist arg dim mismatch\n\tmu:%s\n\tn:%s"%(len(mu),n)
            else:
                n,d = sigma.shape
                if len(mu) != n or len(mu) != d:
                    raise TypeError, "In GaussianDist arg dim mismatch\n\tmu:%s\n\tn:%s\n\td:%s"%(len(mu),n,d)
