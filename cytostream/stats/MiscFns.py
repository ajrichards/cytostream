from __future__ import division
import numpy as np
import scipy.stats as stats
from cytostream.stats import TwoComponentGaussEM

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

def two_component_em(clustEvents,verbose=False,emGuesses=None):
    '''
    given a 1D np.array of events and the labels associated with those events
    return a two component gaussian object and the cutpoint
    '''

    ## declare variables
    subsampleSize = 5000     # subsample size
    numIters = 25            # num em iters
    numRuns = 1              # within em runs
    numReps = 2              # num times to draw sample

    resultsDict = {'maxLike':-np.inf,'params':None}


    if clustEvents.size > subsampleSize:
        #print 'getting subset for ', clustEvents.size

        for rep in range(numReps):
            clustInds = np.arange(0,clustEvents.size,subsampleSize)
            np.random.shuffle(clustInds)
            events = clustEvents.copy()[clustInds]

            ## run em
            tcg = TwoComponentGaussEM(events, numIters, numRuns,verbose=True,initialGuesses=emGuesses)
            if tcg.maxLike > resultsDict['maxLike']:
                resultsDict['maxLike'] = tcg.maxLike.copy() 
                resultsDict['params'] = tcg.bestEst.copy()                
    else:
        ## run em
        tcg = TwoComponentGaussEM(clustEvents, numIters, numRuns,verbose=True,initialGuesses=emGuesses)
        resultsDict['maxLike'] = tcg.maxLike.copy() 
        resultsDict['params'] = tcg.bestEst.copy()
    
    ## get cut point
    cutpoint = stats.norm.ppf(0.025,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))

    return resultsDict,cutpoint
