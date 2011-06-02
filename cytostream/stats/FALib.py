'''
functions that are used to align files
'''

import sys,re
import numpy as np
from cytostream.stats import DistanceCalculator, EmpiricalCDF

def _calculate_within_thresholds(fa,allLabels=None):

    withinThresholds = {}
         
    for fileIndex in range(len(fa.expListNames)):
        fileName = fa.expListNames[fileIndex]
        if allLabels == None:
            fileLabels = fa.get_labels(fileName)
        else:
            fileLabels = allLabels[fileIndex]
        fileData = fa.get_events(fileName)
        fileClusters = np.sort(np.unique(fileLabels))
            
        if withinThresholds.has_key(fileName) == False:
            withinThresholds[fileName] = {}

        for clusterID in fileClusters:
            ## check for noise label
            if fa.noiseClusters.has_key(fileName) and fa.noiseClusters[fileName].__contains__(str(clusterID)):
                continue

            ## determine distances
            clusterEvents = fileData[np.where(fileLabels==int(clusterID))[0],:]
            clusterMean = clusterEvents.mean(axis=0)
            dc = DistanceCalculator(distType=fa.distanceMetric)
            if fa.distanceMetric == 'mahalanobis':
                inverseCov = dc.get_inverse_covariance(clusterEvents)
                if inverseCov != None:
                    dc.calculate(clusterEvents,matrixMeans=clusterMean,inverseCov=inverseCov)
                    distances = dc.get_distances()
                else:
                    dc.calculate(clusterEvents,matrixMeans=clusterMean)
                    distances = dc.get_distances()
                    distances = whiten(btnDistances)
            else:
                dc.calculate(clusterEvents,matrixMeans=clusterMean)
                distances = dc.get_distances()

            ## use the inverse normal to get a one-sided critical value
            #threshold = stats.norm.ppf(0.975,loc=withinDistancesJ.mean(),scale=withinDistancesJ.std())
            #print withinDistancesJ.mean(),withinDistancesJ.std(),threshold

            ## use the eCDF to find a threshold
            eCDF = EmpiricalCDF(distances)        
            thresholdLow = eCDF.get_value(0.025)
            thresholdHigh = eCDF.get_value(0.975)
            withinThresholds[fileName][str(int(clusterID))] = {'ci':(thresholdLow, thresholdHigh)}

    return withinThresholds

def get_modes(fa,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters):
        
    results = nonNoiseResults[phiIndices]
    resultsFiles = nonNoiseFiles[phiIndices]
    resultsClusters = nonNoiseClusters[phiIndices]

    newLabels = [np.array([-1 * int(label) for label in fa.get_labels(fn)]) for fn in fa.expListNames]
    for fileName in fa.expListNames:
        fileIndex = fa.expListNames.index(fileName)
        fileLabels = fa.get_labels(fileName)
        #fileLabels = newLabels[fileIndex]
        fileClusters = np.sort(np.unique(fileLabels))
        fileInds = np.where(resultsFiles == fileIndex)[0]
        fileSpecificResults = results[fileInds]
        fileSpecificClusters = resultsClusters[fileInds]
        fileSpecificClusters1 = np.zeros(len(fileSpecificClusters),dtype=int)
        fileSpecificClusters2 = np.zeros(len(fileSpecificClusters),dtype=int)

        for fsc in range(len(fileSpecificClusters)):
            c1,c2 = re.split("#", fileSpecificClusters[fsc])
            fileSpecificClusters1[fsc] = int(c1)
            fileSpecificClusters2[fsc] = int(c2)

        ## determine the matches that have multiple matches 
        bestMatchesCluster = []
        bestMatches = []
        bestMatchSig = []
       
        for clusterID in fileClusters:
            matches1Inds = np.where(fileSpecificClusters1 == clusterID)[0]
            matches2Inds = np.where(fileSpecificClusters2 == clusterID)[0]
            matches1 = fileSpecificClusters2[matches1Inds]
            matches2 = fileSpecificClusters1[matches2Inds]
            allMatchInds = np.hstack([matches1Inds,matches2Inds])
            allMatches = np.hstack([matches1,matches2])
            allMatchResults = fileSpecificResults[allMatchInds]

            if len(allMatches) == 0:
                continue

            ## at this point another type of significance may be used
            bestMatches.append(allMatches.tolist() + [clusterID])
            bestMatchSig.append(allMatchResults.mean())
        
        ## order from least significant to most
        clusterCount = 0
        clustersLeft = [int(cl) for cl in fileClusters] 
        orderedInds = np.argsort(bestMatchSig)        
        for oi in orderedInds:
            clustersToChange = bestMatches[oi]
            clusterCount += 1
            for c in clustersToChange:
                newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * c)[0]] = clusterCount
            
                if clustersLeft.__contains__(c):
                    clustersLeft.remove(int(c))

        #print fileName, clustersLeft, np.unique(newLabels[fileIndex])


        ## change the labels of unmatched clusters
        for c in clustersLeft:
            clusterCount += 1
            newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * c)[0]] = clusterCount

    return newLabels


def relabel_template(fa,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters):
        
    fileSpecificresults = nonNoiseResults[phiIndices]
    fileSpecificFiles = nonNoiseFiles[phiIndices]
    fileSpecificClusters = nonNoiseClusters[phiIndices]
    newLabels = [-1 * int(label) for label in fa.templateLabels]

    #for fileName in fa.expListNames:
    #    fileIndex = fa.expListNames.index(fileName)
    #    fileLabels = fa.get_labels(fileName)
    #    fileClusters = np.sort(np.unique(fileLabels))
    #    fileInds = np.where(resultsFiles == fileIndex)[0]
    #    fileSpecificResults = results[fileInds]
    #    fileSpecificClusters = resultsClusters[fileInds]
    #    fileSpecificClusters1 = np.zeros(len(fileSpecificClusters),dtype=int)
    #    fileSpecificClusters2 = np.zeros(len(fileSpecificClusters),dtype=int)

    for fsc in range(len(fileSpecificClusters)):
        c1,c2 = re.split("#", fileSpecificClusters[fsc])
        fileSpecificClusters1[fsc] = int(c1)
        fileSpecificClusters2[fsc] = int(c2)
        print c1,c2

    sys.exit()
    ## determine the matches that have multiple matches 
    bestMatchesCluster = []
    bestMatches = []
    bestMatchSig = []
       
    for clusterID in fileClusters:
        matches1Inds = np.where(fileSpecificClusters1 == clusterID)[0]
        matches2Inds = np.where(fileSpecificClusters2 == clusterID)[0]
        matches1 = fileSpecificClusters2[matches1Inds]
        matches2 = fileSpecificClusters1[matches2Inds]
        allMatchInds = np.hstack([matches1Inds,matches2Inds])
        allMatches = np.hstack([matches1,matches2])
        allMatchResults = fileSpecificResults[allMatchInds]

        ## ignore all single matches
        if len(allMatches) <= 1:
            continue

        ## at this point another type of significance may be used
        bestMatches.append(allMatches.tolist() + [clusterID])
        bestMatchSig.append(allMatchResults.mean())
        
    ## order from least significant to most
    clusterCount = 0
    clustersLeft = [int(cl) for cl in fileClusters] 
    orderedInds = np.argsort(bestMatchSig)        
    for oi in orderedInds:
        clustersToChange = bestMatches[oi]
        clusterCount += 1
        for c in clustersToChange:
            newLabels[np.where(newLabels == -1 * c)[0]] = clusterCount
            
            if clustersLeft.__contains__(c):
                clustersLeft.remove(int(c))

    ## change the labels of unmatched clusters
    for c in clustersLeft:
        clusterCount += 1
        newLabels[np.where(newLabels == -1 * c)[0]] = clusterCount

    return newLabels


    '''
    bootMatches = []
    bootMatchesLabels = []
    fileCount = 0
    for fileName in fa.expListNames:
        fileCount += 1
        fileLabels = fa.get_labels(fileName)
        fileClusters = np.sort(np.unique(fileLabels))
        fileData = fa.get_events(fileName)

        for m in range(len(results)):
            fname = fa.expListNames[int(resultsFiles[m])]
            if fileName != fname:
                continue
            clusterI, clusterJ = [int(ci) for ci in re.split("#", resultsClusters[m])]
            eventsI = fileData[np.where(fileLabels==int(clusterI))[0],:]
            eventsJ = fileData[np.where(fileLabels==int(clusterJ))[0],:]
            n,m = len(eventsI),len(eventsJ)
            bootstrapDataLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])
            bootstrapData = np.vstack([eventsI,eventsJ])
            bstpr = BootstrapHypoTest(bootstrapData, bootstrapDataLabels, nrep=1000)
            bresults = bstpr.get_results()
                
            #print "matching", fname, clusterI, clusterJ, bresults
            
            if bresults['delta1'] > 3.0:
                continue
                
            bootMatches.append(bresults['delta1'])
            bootMatchsLabels.append("%s#%s#%s"%(fname,clusterI,clusterJ))

        if len(bootMatches) == 0:
            return

    ## relabel
    sortedInds = np.argsort(bootMatches)
    bootMatches = np.array(bootMatches)[sortedInds]
    bootMatchesLabels = np.array(bootMatchesLabels)[sortedInds]
    '''
    
def event_count_compare(fa,clusterEventsI,clusterEventsJ,fileJ,clusterJ,thresholds=None):
    '''
    model the sink (j) then determine number of events in source (i) that overlap
    '''
          
    if thresholds == None:
        thresholds = fa.withinThresholds

    clusterMeanJ = clusterEventsJ.mean(axis=0)

    dc = DistanceCalculator(distType=fa.distanceMetric)
    if fa.distanceMetric == 'mahalanobis':
        inverseCov = dc.get_inverse_covariance(clusterEventsJ)
        if inverseCov != None:
            dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ,inverseCov=inverseCov)
            distances = dc.get_distances()
        else:
            dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ)
            distances = dc.get_distances()
            distances = whiten(btnDistances)
    else:
        dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ)
        distances = dc.get_distances()

    ## calculate % overlap
    threshold = thresholds[fileJ][str(clusterJ)]['ci']
    #print distances.shape, distances.mean(), threshold
    overlappedInds1 = np.where(distances > threshold[0])[0] #threshold[0]
    overlappedInds2 = np.where(distances < threshold[1])[0]
    overlappedInds = list(set(overlappedInds1).intersection(set(overlappedInds2)))
    #print overlappedInds1.shape,overlappedInds2.shape,overlappedInds.shape
    
    if len(overlappedInds) == 0:
        return 0
 
    return float(len(overlappedInds)) / float(len(distances))


def make_bootstrap_comparision(fa):
        
    ## make bootstrap comparisons
    templateClusters = np.sort(np.unique(templateLabels))
    comparisons = []
    totalComparisons = (float(len(templateClusters)) * (float(len(templateClusters)) - 1.0)) / 2.0
    print 'bootstrapping hypo test'
    compareCount = 0
    for ci in range(len(templateClusters)):
        clusterI = templateClusters[ci]
        eventsI = templateData[np.where(templateLabels==int(clusterI))[0],:]
        for cj in range(len(templateClusters)):
            
            if ci >= cj:
                continue

            ## debug 
            if compareCount > 10:
                continue

            compareCount += 1
            clusterJ = templateClusters[cj]
            eventsJ = templateData[np.where(templateLabels==int(clusterJ))[0],:]
            n,m = len(eventsI),len(eventsJ)
            bootstrapDataLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])
            bootstrapData = np.vstack([eventsI,eventsJ])
            bstpr = BootstrapHypoTest(bootstrapData, bootstrapDataLabels, nrep=500)
            bresults = bstpr.get_results()
                
            if bresults['delta1'] < 0.1:
                comparisons.append([clusterI,clusterJ,bresults['delta1']])
            print clusterI, clusterJ, bresults['delta1'],"%s/%s"%(compareCount,totalComparisons)  
         
    print 'template', fileWithMinNumClusters


#if self.overlapMetric == 'kldivergence':
#    eCDF = EmpiricalCDF(nonNoiseResults)
#    thresholdLow = eCDF.get_value(phi)
#    phiIndices = np.where(nonNoiseResults < thresholdLow)[0]
#    print thresholdLow
#    print "out of %s cluster comparisons we need to consider %s"%(len(nonNoiseResults),len(phiIndices))
#    print "phi", phi
#    print 'not complete'
#if len(phiIndices) > 0:
#    self._get_modes(phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters)

#if self.overlapMetric == 'kldivergence':
#    ## assume normal distributions
#gd1 = GaussianDistn(clusterEventsJ.mean(axis=0), np.cov(clusterEventsJ.T))
#gd2 = GaussianDistn(clusterEventsI.mean(axis=0), np.cov(clusterEventsI.T))
#klDist1 = kullback_leibler(gd1,gd2)
#klDist2 = kullback_leibler(gd2,gd1)
#klList = [klDist1,klDist2]
#klDist = klList[np.argmin([klDist1.sum(),klDist2.sum()])]
#alignResults[clustCount] = klDist.sum()
#if klDist > 20000:
#    continue 
