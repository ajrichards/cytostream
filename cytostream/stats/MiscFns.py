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

def two_component_em(clustEvents,verbose=False,emGuesses=None,subset="cd3"):
    '''
    given a 1D np.array of events and the labels associated with those events
    return a two component gaussian object and the cutpoint
    '''

    subset = subset.lower()

    ## declare variables
    if subset in ['cd3','cd4']:
        subsampleSize = 40000    
    elif subset in ['cd8']:
        subsampleSize = 80000    
    elif subset in ['ssc','fsc']:
        subsampleSize = 30000    
    else:
        print "ERROR in two_component_em -- invalid subset specified"

    numIters = 25             # num em iters
    if emGuesses == None:
        numRuns = 3
    else:
        numRuns = 1
    numReps = 3               # num times to draw sample
    eps = np.finfo(float).eps

    resultsDict = {'maxLike':-np.inf,'params':None}

    if clustEvents.size > subsampleSize:
        #print 'getting subset for ', clustEvents.size

        for rep in range(numReps):
            clustInds = np.arange(0,clustEvents.size)
            np.random.shuffle(clustInds)
            events = clustEvents.copy()[clustInds[:subsampleSize]]

            ## run em
            tcg = TwoComponentGaussEM(events, numIters, numRuns,verbose=True,initialGuesses=emGuesses,subset=subset)
            maxLike, bestEst = tcg.get_results()

            if maxLike > resultsDict['maxLike'] :
                resultsDict['maxLike'] = maxLike
                resultsDict['params'] = bestEst.copy()
    else:
        ## run em
        tcg = TwoComponentGaussEM(clustEvents,numIters, numRuns,verbose=True,initialGuesses=emGuesses)
        resultsDict['maxLike'] = tcg.maxLike.copy() 
        resultsDict['params'] = tcg.bestEst.copy()
    
    ## get cut point 0.025
    if resultsDict['params']['pi'] <= 0.5:
        if subset in ['fsc']:
            #cutpoint = stats.norm.ppf(0.999,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
            cutpoint = resultsDict['params']['mu1'] + (3.0 * np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['ssc']:
            #cutpoint = stats.norm.ppf(0.999,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
            cutpoint = resultsDict['params']['mu1'] + (3.0 * np.sqrt(resultsDict['params']['sig1']))
    else:
        if subset in ['fsc']:
            #cutpoint = stats.norm.ppf(0.999,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
            cutpoint = resultsDict['params']['mu2'] + (3.0 * np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['ssc']:
            #cutpoint = stats.norm.ppf(0.975,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
            cutpoint = resultsDict['params']['mu2'] + (3.0 * np.sqrt(resultsDict['params']['sig2']))
        
    if resultsDict['params']['mu2'] > resultsDict['params']['mu1']:
        if subset in ['cd8']:
            cutpoint = stats.norm.ppf(0.975,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['cd3']:
            cutpoint = stats.norm.ppf(0.01,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['cd4']:
            cutpoint = stats.norm.ppf(0.01,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
    else:
        if subset in ['cd8']:
            cutpoint = stats.norm.ppf(0.975,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['cd3']:
            cutpoint = stats.norm.ppf(0.01,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['cd4']:
            cutpoint = stats.norm.ppf(0.01,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))

    return resultsDict,cutpoint

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
