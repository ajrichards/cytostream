#!/usr/bin/env python

## make imports 
#from __future__ import division
import sys,time
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import scipy.stats as stats
from fcm.statistics.distributions import mvnormpdf
from cytostream.stats import EmpiricalCDF

class TwoComponentGaussEM():

    def __init__(self, y, numIters, numRuns,verbose=False,initialGuesses=None,subset="cd3"):
        
        ## variables
        self.y = y.copy()
        self.verbose = verbose
        self.subset = subset


        # ignore zero and very small 
        self.y = self.y[np.where(self.y > 0.0)[0]]
        eCDF = EmpiricalCDF(self.y)
        thresholdLow = eCDF.get_value(0.05)
        self.y = self.y[np.where(self.y > thresholdLow)[0]]

        #print "\tdata", y.shape, y.mean(), np.median(y), y.var()

        ## error check
        self.initialGuesses = initialGuesses
        if self.initialGuesses != None and self.initialGuesses['n'] == None:
            self.initialGuesses['n'] = len(y)

        ## run it
        self.maxLike, self.bestEst = self.run_em_algorithm(numIters, numRuns)
        

    def get_results(self):
        return self.maxLike, self.bestEst

    ### make definations for initial guessing, expectation, and maximization
    def get_init_guesses(self,y):
        ## make intial guesses for the parameters (mu1, sig1, mu2, sig2 and pi)
        n    = len(self.y)
        sortedVals = y.copy()
        sortedVals.sort()
        yMed = np.median(y)

        if self.subset in ['cd3','cd4','ssc','fsc']:
            mu1 = np.random.uniform(0.1 * yMed,0.9*yMed) ## 200, 500
            mu2 = np.random.uniform(1.5 * yMed,3.9 *yMed) ## 550,750
            sig1 = np.random.uniform(1.0*yMed,1.0*yMed)  ## 
            sig2 = np.random.uniform(1.0*yMed,1.0*yMed)
            pi   = np.random.uniform(0.1,0.9)
        if self.subset in ['cd8']:
            mu1 = np.random.uniform(0.1*yMed,0.9*yMed)   ## 200, 500
            mu2 = np.random.uniform(1.5 * yMed,3.9*yMed) ## 550,750
            sig1 = np.random.uniform(0.1*yMed,1.0*yMed)  ## 
            sig2 = np.random.uniform(0.1*yMed,1.0*yMed)
            pi   = np.random.uniform(0.1,0.9)
      
        return {'n':n, 'mu1':mu1, 'mu2':mu2, 'sig1':sig1, 'sig2':sig2, 'pi':pi}

    def perform_expectation(self, y, parms):
        gammaHat = np.zeros((parms['n']),'float')
        phiTheta1 = stats.norm.pdf(y,loc=parms['mu1'],scale=np.sqrt(parms['sig1']))
        phiTheta2 = stats.norm.pdf(y,loc=parms['mu2'],scale=np.sqrt(parms['sig2']))
        numer = parms['pi'] * phiTheta2
        #numer = numer[np.where(np.isnan(numer)==False)]
        denom = ((1.0 - parms['pi']) * phiTheta1) + (parms['pi'] * phiTheta2)
        #denom = denom[np.where(np.isnan(denom)==False)]

        denom[np.where(denom == 0.0)[0]] = np.finfo(float).eps
        gammaHat = numer / denom 
        
        return gammaHat

    def perform_maximization(self,y,parms,gammaHat):
        ## use weighted maximum likelihood fits to get updated parameter estimates
        numerMuHat1 = 0
        denomHat1 = 0
        numerSigHat1 = 0
        numerMuHat2 = 0
        denomHat2 = 0
        numerSigHat2 = 0
        piHat = 0
        
        ## get numerators and denomanators for updating of parameter estimates
        numerMuHat1 = ( (1.0 - gammaHat) * y )
        numerMuHat1 = numerMuHat1[np.where(np.isnan(numerMuHat1)==False)].sum()
        numerSigHat1 = ( (1.0 - gammaHat) * ( y - parms['mu1'] )**2 )
        numerSigHat1 = numerSigHat1[np.where(np.isnan(numerSigHat1)==False)].sum()
        denomHat1 = (1.0 - gammaHat)
        denomHat1 = denomHat1[np.where(np.isnan(denomHat1)==False)].sum()
        
        numerMuHat2 = (gammaHat * y)
        numerMuHat2 = numerMuHat2[np.where(np.isnan(numerMuHat2)==False)].sum()
        numerSigHat2 = (gammaHat * ( y - parms['mu2'] )**2)
        numerSigHat2 = numerSigHat2[np.where(np.isnan(numerSigHat2)==False)].sum() 
        denomHat2 = gammaHat
        denomHat2 = denomHat2[np.where(np.isnan(denomHat2)==False)].sum()
        piHat = (gammaHat / parms['n'])
        piHat = piHat[np.where(np.isnan(piHat)==False)].sum()
    
        ## ensure we are not dividing by 0
        if denomHat1 == 0.0:
            denomHat1 =  np.finfo(float).eps
            #print 'changing denomhat1', np.finfo(float).eps
        if denomHat2 == 0.0:
            denomHat2 =  np.finfo(float).eps
            #print 'changing denomhat2', np.finfo(float).eps

        ## calculate estimates
        muHat1 = numerMuHat1 / denomHat1
        sigHat1 = numerSigHat1 / denomHat1
        muHat2 = numerMuHat2 / denomHat2
        sigHat2 = numerSigHat2 / denomHat2

        return {'mu1':muHat1, 'mu2':muHat2, 'sig1': sigHat1, 'sig2':sigHat2, 'pi':piHat, 'n':parms['n']}

    def get_likelihood(self,y,parms,gammaHat):
        phiTheta1 = stats.norm.pdf(y,loc=parms['mu1'],scale=np.sqrt(parms['sig1'])) 
        phiTheta2 = stats.norm.pdf(y,loc=parms['mu2'],scale=np.sqrt(parms['sig2']))
       
        
        phiTheta1[np.where(phiTheta1 == 0.0)[0]] = np.finfo(float).eps
        phiTheta2[np.where(phiTheta2 == 0.0)[0]] = np.finfo(float).eps
        
        part1 = (1.0 - gammaHat) * np.log(phiTheta1) + gammaHat * np.log(phiTheta2)
        part2 = (1.0 - gammaHat) * np.log(parms['pi']) + gammaHat * np.log(1.0 - parms['pi'])
        
        ## remove nans
        part1 = part1[np.where(np.isnan(part1)==False)]
        part2 = part2[np.where(np.isnan(part2)==False)]

        return part1.sum() + part2.sum() 


    def run_em_algorithm(self, numIters, numRuns, verbose = True):
        '''
        main algorithm functions
        '''

        maxLike = -np.inf
        bestEstimates = None

        for j in range(numRuns):

            iterCount = 0
            if self.initialGuesses == None:
                parms = self.get_init_guesses(self.y)
            else:
                parms = self.initialGuesses

            ## iterate between E-step and M-step
            while iterCount < numIters:
                iterCount += 1
    
                ## check for valid variance estimates
                if parms['sig1'] <= 0.0 or parms['sig2'] <= 0.0:
                    iterCount += 1
                    if self.initialGuesses == None:
                        parms = self.get_init_guesses(self.y)
                    else:
                        parms = self.initialGuesses
    
                ## E-step
                gammaHat = self.perform_expectation(self.y,parms)
                logLike = self.get_likelihood(self.y,parms,gammaHat)

                ## check again for valid variance estimates
                if parms['sig1'] <= 0.0 or parms['sig2'] <= 0.0:
                    iterCount += 1
                    if self.initialGuesses == None:
                        parms = self.get_init_guesses(self.y)
                    else:
                        parms = self.initialGuesses

                #if self.verbose == True:
                #    print 'iteration',iterCount,'mu1',round(parms['mu1'],2),'mu2',round(parms['mu2'],2),'sig1',round(parms['sig1'],2),
                #    print 'sig2',round(parms['sig2'],2),'pi',round(parms['pi'],2),'obs.data likelihood', round(logLike,4)

                ## M-step
                parms = self.perform_maximization(self.y,parms,gammaHat)
    
            if logLike > maxLike:
                maxLike = logLike
                bestEstimates = parms.copy()
                bestEstimates['likelihood'] = maxLike

            #if self.verbose == True:
            #    print 'runNum: ',j + 1,'mu1: ',round(parms['mu1'],2),'mu2: ',round(parms['mu2'],2),'sig1: ',round(parms['sig1'],2),
            #    print 'sig2: ',round(parms['sig2'],2),'pi: ',round(parms['pi'],2),'obs.data likelihood: ', round(logLike,4)

        return maxLike, bestEstimates
 
if __name__ == '__main__':

    y1 = np.array([-0.39,0.12,0.94,1.67,1.76,2.44,3.72,4.28,4.92,5.53])
    y2 = np.array([ 0.06,0.48,1.01,1.68,1.80,3.25,4.12,4.60,5.28,6.22])
    y  = np.hstack((y1,y2))

    numIters = 25
    numRuns = 2
    verbose = True
    makePlots = True
    beginTime = time.time()
    tcg = TwoComponentGaussEM(y, numIters, numRuns,verbose=verbose)
    endTime = time.time()
    print 'time taken', endTime-beginTime

    print 'maxLike', tcg.maxLike
    print 'bestEstimates', tcg.bestEst

    if makePlots == True:
        n, bins, patches = plt.hist(y,15,normed=1,facecolor='gray',alpha=0.75)
    
        ## add a 'best fit' line (book results)
        mu1 = 4.62
        mu2 = 1.06
        sig1 = 0.87
        sig2 = 0.77

        p1 = mlab.normpdf( bins, mu1, np.sqrt(sig1))
        p2 = mlab.normpdf( bins, mu2, np.sqrt(sig2))
        l1 = plt.plot(bins, p1, 'r--', linewidth=1)
        l2 = plt.plot(bins, p2, 'r--', linewidth=1)

        ## add a 'best fit' line (results from here)
        p3 = mlab.normpdf( bins, tcg.bestEst['mu1'], np.sqrt(tcg.bestEst['sig1']))
        p4 = mlab.normpdf( bins, tcg.bestEst['mu2'], np.sqrt(tcg.bestEst['sig2']))
        l3 = plt.plot(bins, p3, 'k-', linewidth=1)
        l4 = plt.plot(bins, p4, 'k-', linewidth=1)

        plt.xlabel('y')
        plt.ylabel('freq')
        plt.ylim([0,0.8])
    
        plt.legend( (l1[0], l3[0]), ('Book Estimate', 'My Estimate') )

        plt.savefig('../TwoComponentGauss.png')
        plt.show()
