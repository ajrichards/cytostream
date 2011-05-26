#!/usr/bin/python

'''

an example of how to do a bootstrap estimate of variance
as a validation we set the data to the following and we
know the exact bootstrap variance of the median is 36.01483.

data = array([1,2,7,16,19])  


A. Richards 
'''

### make imports 
from numpy import array,zeros,random,median,power,var,sqrt
import scipy.stats as stats

class Bootstrapper():
    


    def __init__(self,data, nrep=4000, confidenceLevel=0.05):
        nrep             = nrep                       # this is B
        n                = len(data)
        sampleMean       = data.mean()
        sampleMedian     = median(data)
        bootstrapMedians = zeros((nrep,),'float')              
        bootstrapMeans   = zeros((nrep,),'float')
        confidenceLevel  = 0.05

        ### sample with replacement
        for b in range(0,nrep):
            randIndices = random.randint(0,len(data),(len(data),))
            bootstrapSample = data.take(randIndices)
            bootstrapMedians[b] = median(bootstrapSample)
            bootstrapMeans[b] = bootstrapSample.mean()

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
        
    def get_results(self):
        return self.results

### Run the tests 
if __name__ == '__main__':

    data = array([274, 28.5, 1.7, 20.8, 871, 363, 1311, 1661, 236, 828,
                  458, 290, 54.9, 175, 1787, 970, 0.75, 1278, 776, 126],'float')


    boots = Bootstrapper(data)
    bootResults = boots.get_results()

    for key,item in bootResults.iteritems():
        print key,item
