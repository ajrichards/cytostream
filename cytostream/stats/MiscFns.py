from __future__ import division
import numpy as np


def kullback_leibler(d1,d2):
    '''
    The KL divegence is a measures distance between two probability distributions
    It is not a true distance metric because
      -symmetry constraint
      -triangle inequality
    
    This function takes as input two GaussianDistn class objects.  They may be 
    univariate or multivariate.  See the unittest TestKullbackLeibler.py
 
    '''

    dist = ( (0.5 * np.log(d2.sigma**2/d1.sigma**2)) - 0.5 + d1.sigma**2/(2*d2.sigma**2)
             + (abs(d2.mu-d1.mu)**2)/(2*d2.sigma**2) )

    return dist
