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
    if subset in ['cd3']:
        subsampleSize = 2000
    elif subset in ['cd4']:
        subsampleSize = 3000    
    elif subset in ['cd8']:
        subsampleSize = 3000
    elif subset in ['ssc']:
        subsampleSize = 2000
    elif subset in ['fsc']:
        subsampleSize = 3000
    else:
        print "ERROR in two_component_em -- invalid subset specified"

    numIters = 25             # num em iters
    if emGuesses == None:
        numRuns = 50
    else:
        numRuns = 1
    numReps = 6               # num times to draw sample
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
    #if resultsDict['params']['pi'] <= 0.5:
    if resultsDict['params']['sig1'] < resultsDict['params']['sig2']:
        if subset in ['fsc']:
            #cutpoint = stats.norm.ppf(0.999,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
            cutpoint = resultsDict['params']['mu1'] + (6.0 * np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['ssc']:
            cutpoint = resultsDict['params']['mu1'] + (6,0 * np.sqrt(resultsDict['params']['sig1']))
            #cutpoint = stats.norm.ppf(0.9999,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
    else:
        if subset in ['fsc']:
            #cutpoint = stats.norm.ppf(0.999,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
            cutpoint = resultsDict['params']['mu2'] + (6.0 * np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['ssc']:
            cutpoint = resultsDict['params']['mu2'] + (6.0 * np.sqrt(resultsDict['params']['sig2']))
            #cutpoint = stats.norm.ppf(0.9999,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
        
    if resultsDict['params']['mu2'] > resultsDict['params']['mu1']:
        if subset in ['cd8']:
            cutpoint = stats.norm.ppf(0.975,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['cd3']:
            cutpoint = stats.norm.ppf(0.001,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['cd4']:
            cutpoint = stats.norm.ppf(0.9999,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1'])) - (0.0001 * np.sqrt(resultsDict['params']['sig1'])) 
    else:
        if subset in ['cd8']:
            cutpoint = stats.norm.ppf(0.975,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2']))
        elif subset in ['cd3']:
            cutpoint = stats.norm.ppf(0.001,loc=resultsDict['params']['mu1'],scale=np.sqrt(resultsDict['params']['sig1']))
        elif subset in ['cd4']:
            cutpoint = stats.norm.ppf(0.9999,loc=resultsDict['params']['mu2'],scale=np.sqrt(resultsDict['params']['sig2'])) - (0.0001 * np.sqrt(resultsDict['params']['sig2'])) 

    return resultsDict,cutpoint

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]


