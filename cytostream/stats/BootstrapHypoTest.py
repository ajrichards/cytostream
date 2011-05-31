#!/usr/bin/python

'''

an example of how to do a bootstrap estimate of variance
as a validation we set the data to the following and we
know the exact bootstrap variance of the median is 36.01483.

data = array([1,2,7,16,19])  


A. Richards 
'''

### make imports
import numpy as np 
from numpy import array,zeros,random,median,power,var,sqrt
import scipy.stats as stats

class BootstrapHypoTest():
    '''
    (1) draw B samples of size n + m, call the first n observation z* and the remaining y*
    (2) evaluate t(x) and each sample
    (3) Approximate ASL = #{t(x*^b} >= t_obs} / B where t_obs is the observed value of t(x)

    delta1 tests the difference in means
    delta2 tests the difference in variances

    '''

    def __init__(self,data, dataLabels, nrep=4000, confidenceLevel=0.05):
        
        '''
        data are a mixture of z and y
        data labels specify z (0) and y (1)
        '''

        ## ensure data is in matri form
        if len(data.shape) == 1:
            data = np.array([data]).T



        ## variables
        numObs, numDims  = data.shape
        self.nrep        = nrep # this is B
        dataZ            = data[np.where(dataLabels == 1)[0],:]
        dataY            = data[np.where(dataLabels == 0)[0],:]
        n                = len(dataZ)
        m                = len(dataY)
        bootstrapMeans   = zeros((self.nrep,numDims),'float')
        zstarMean        = zeros((self.nrep,numDims),'float') 
        ystarMean        = zeros((self.nrep,numDims),'float')
        tx               = zeros((self.nrep,numDims),'float')
        confidenceLevel  = 0.05

        ## error check
        if m + n != data.shape[0]:
            print "ERROR failed intgrity chk -- BootstrapHypotest" 

        ## sample data with replacement
        for b in range(0,self.nrep):
            randIndices = np.random.randint(0,m+n,m+n)
            bootstrapSample = data[randIndices,:]
            bootstrapLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])
            zstarMean[b] = bootstrapSample[:n,:].mean(axis=0)
            ystarMean[b] = bootstrapSample[-m:,:].mean(axis=0)
            
            # evaluate t(x) on each sample
            tx[b] = self.get_studentized_test_stat(bootstrapSample,bootstrapLabels)
           

        ##### delta 1 #####
        ## if using simple diff
        #delta1Obs = dataZ.mean(axis=0) - dataY.mean(axis=0)
        #asl = float(len(np.where(zstarMean - ystarMean > delta1Obs)[0])) / float(nrep)
        
        ## if using studentized test statistic
        delta1Obs = self.get_studentized_test_stat(data,dataLabels)
        asl1 = float(len(np.where(tx > delta1Obs)[0])) / float(self.nrep)
        
        ##### delta 2 #####
        #zstarSE = self.get_standard_error_estimate(zstarMean)
        #ystarSE = self.get_standard_error_estimate(ystarMean)
        #delta2Obs = dataZ.std() - dataY.std()
        #print zstarSE, ystarSE, delta2Obs

        ## save results
        self.results ={'delta1': asl1}


    def get_standard_error_estimate(self,bootstrapMeans):
        xBar       = bootstrapMeans.mean()
        varHatMean  = (1.0 / (self.nrep - 1.0)) * (np.power((bootstrapMeans - xBar),2).sum())
        return varHatMean

        '''
        ### calculate bootstrap estimates of variance
        meanMedians  = bootstrapMedians.mean()
        varHatMedian = (1.0 / (nrep - 1.0)) * (power((bootstrapMedians - meanMedians),2).sum())  
        meanMeans    = bootstrapMeans.mean()
        varHatMean   = (1.0 / (nrep - 1.0)) * (power((bootstrapMeans - meanMeans),2).sum())

        ### find the critical value (where ppf is the percent point function) we assume a two sided hypothesis
        criticalValue = stats.norm.ppf(1.0 - (confidenceLevel / 2.0))

        ### find confidence intervals
        medianCI = (sampleMedian - (criticalValue * sqrt(varHatMedian)),sampleMedian + (criticalValue * sqrt(varHatMedian)))
        meanCI   = (sampleMean - (criticalValue * sqrt(varHatMean)),sampleMean + (criticalValue * sqrt(varHatMean)))
        
        self.results = {'confidenceLevel':confidenceLevel,'criticalValue':criticalValue,'sampleMean':sampleMean,'sampleMedian':sampleMedian,
                        'sampleVar':var(data),'varHatMedian':varHatMedian,'medianCI':medianCI,'varHatMean':varHatMean,'meanCI':meanCI}
        
        '''

    def get_studentized_test_stat(self, data,dataLabels):
        dataZ = data[np.where(dataLabels == 1)[0],:]
        dataY = data[np.where(dataLabels == 0)[0],:]
        #if self.dims == 1:
        #    n,m = float(len(dataZ)),float(len(dataY))
        #else:  
        n,m = dataZ.shape[0],dataY.shape[0]
 
        ssDiff = np.power(dataZ - dataZ.mean(axis=0),2).sum() + np.power(dataY - dataY.mean(axis=0),2).sum() 
        sigmaBar = np.sqrt(ssDiff / (n + m-2.0))
        return (dataZ.mean(axis=0) - dataY.mean(axis=0)) / (sigmaBar * np.sqrt( (1.0 / n) + (1.0 / m)))

    def get_results(self):
        return self.results

### Run the tests 
if __name__ == '__main__':

    #data = array([274, 28.5, 1.7, 20.8, 871, 363, 1311, 1661, 236, 828,
     #             458, 290, 54.9, 175, 1787, 970, 0.75, 1278, 776, 126],'float')

    data = np.array([10,16,23,27,31,38,40,46,50,52,94,99,104,141,146,197])
    dataLabels = np.array([0,1,1,0,0,1,0,0,0,0,1,1,0,1,0,1])

    boots = BootstrapHypoTest(data,dataLabels,nrep=1000)
    print "bootstrap result  ", boots.results['delta1']
    print "permutation result", 0.152
    #bootResults = boots.get_results()

    #or key,item in bootResults.iteritems():
     #   print key,item
