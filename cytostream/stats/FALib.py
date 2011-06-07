'''
functions that are used to align files
'''

import sys,re
import numpy as np
from cytostream.stats import DistanceCalculator, EmpiricalCDF, BootstrapHypoTest, GaussianDistn, kullback_leibler

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
            #if fa.noiseClusters.has_key(fileName) and fa.noiseClusters[fileName].__contains__(str(clusterID)):
            #    continue

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

def get_modes(fa,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters, phi):
        
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
                if fa.noiseClusters.has_key(fileName) and str(c) in fa.noiseClusters[fileName]:
                    if fa.modeNoiseClusters[str(phi)].has_key(fileName):
                        fa.modeNoiseClusters[str(phi)][fileName].append(str(clusterCount))
                    else:
                        fa.modeNoiseClusters[str(phi)][fileName] = [str(clusterCount)]

                if clustersLeft.__contains__(c):
                    clustersLeft.remove(int(c))

        #print fileName, clustersLeft, np.unique(newLabels[fileIndex])
        ## change the labels of unmatched clusters
        for c in clustersLeft:
            clusterCount += 1
            newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * c)[0]] = clusterCount
            if fa.noiseClusters.has_key(fileName) and str(c) in fa.noiseClusters[fileName]:
                if fa.modeNoiseClusters[str(phi)].has_key(fileName):
                    fa.modeNoiseClusters[str(phi)][fileName].append(str(clusterCount))
                else:
                    fa.modeNoiseClusters[str(phi)][fileName] = [str(clusterCount)]

    return newLabels

def bootstrap_compare(eventsI,eventsJ):
    n,m = len(eventsI),len(eventsJ)

    if n == 0 or m == 0:
        print "ERROR in bootstrap_compare -- cluster had 0 elements"
        return None
                                                                             
    bootstrapDataLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])                                                               
    bootstrapData = np.vstack([eventsI,eventsJ])                                                                                                     
    bstpr = BootstrapHypoTest(bootstrapData, bootstrapDataLabels, nrep=500)
    bresults = bstpr.get_results()  

    return bresults


def get_alignment_labels(fa,alignment,phi,evaluator='rank'):
        
    if evaluator not in ['rank','bootstrap','kldivergence']:
        print "ERROR: in get_alignment_labels evaluator not valid"


    results = alignment['results']
    resultsFiles = alignment['files']
    resultsClusters = alignment['clusters']
    newLabels = [np.array([-1 * int(label) for label in fa.modeLabels[str(phi)][fn]]) for fn in range(len(fa.expListNames))]

    for fileName in fa.expListNames:
        fileIndex = fa.expListNames.index(fileName)
        fileLabels = fa.modeLabels[str(phi)][fileIndex]
        fileData = fa.get_events(fileName)
        fileClusters = np.sort(np.unique(fileLabels))
        fileInds = np.where(resultsFiles == fileIndex)[0]
        fileSpecificResults = results[fileInds]
        fileSpecificClustersAll = resultsClusters[fileInds]
        templateSpecificClusters = np.zeros(len(fileSpecificClustersAll),dtype=int)
        fileSpecificClusters = np.zeros(len(fileSpecificClustersAll),dtype=int)

        ## prepare the labels
        for fsc in range(len(fileSpecificClustersAll)):
            c1,c2 = re.split("#", fileSpecificClustersAll[fsc])
            templateSpecificClusters[fsc] = int(c1)
            fileSpecificClusters[fsc] = int(c2)

        ## determine if there are multiple matches, handle it, then assign labels
        for clusterID in fileClusters:
            matchInds = np.where(fileSpecificClusters == clusterID)[0]
            templateMatches = templateSpecificClusters[matchInds]
            matchSignif = fileSpecificResults[matchInds]

            ## skip noise 
            if fa.modeNoiseClusters[str(phi)].has_key(fileName) and str(clusterID) in fa.modeNoiseClusters[str(phi)][fileName]:
                continue

            #print 'In file %s cluster %s will be changed to %s due to a overlap of %s'%(fileName,clusterID,templateMatches,matchSignif)

            if evaluator == 'rank' or len(matchSignif) == 1:
                rankedInds = np.argsort(matchSignif)[::-1]
                #print "\t...using rank"
            elif evaluator == 'bootstrap':
                bootstrapResults = []
                print "\t...bootstrapping for ", fileName, clusterID
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                for tm in templateMatches:
                    eventsI = fa.templateData[np.where(fa.templateLabels==tm)[0],:]
                    bsResults = bootstrap_compare(eventsI, eventsJ)
                    bootstrapResults.append(bsResults['delta1'])
                rankedInds = np.argsort(bootstrapResults)
            elif evaluator == 'kldivergence':
                klResults = []
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                gd1 = GaussianDistn(eventsJ.mean(axis=0), np.cov(eventsJ.T))
                print "\t...using kl for ", fileName, clusterID

                ## things to try use max of both kldists 
                for tm in templateMatches:
                    eventsI = fa.templateData[np.where(fa.templateLabels==tm)[0],:]
                    gd2 = GaussianDistn(eventsI.mean(axis=0), np.cov(eventsI.T))
                    klDist1 = kullback_leibler(gd1,gd2)
                    klDist2 = kullback_leibler(gd2,gd1)
                    klList = [klDist1,klDist2]
                    klDist = klList[np.argmin([klDist1.sum(),klDist2.sum()])] 
                    klResults.append(klDist)
                rankedInds = np.argsort(klResults)

            if len(templateMatches) < 1:
                continue
                
            ## if multiple matches handle
            newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * clusterID)[0]] = templateMatches[rankedInds[0]]

        ## change the labels of unmatched clusters
        clustersLeft = np.unique(newLabels[fileIndex][np.where(newLabels[fileIndex] < 0)])
        clusterCount = np.max(fa.templateLabels)

        for c in clustersLeft:
            if fa.modeNoiseClusters[str(phi)].has_key(fileName) and str(int(-1.0*c)) in fa.modeNoiseClusters[str(phi)][fileName]:
                newLabels[fileIndex][np.where(newLabels[fileIndex] ==  c)[0]] = -1
            else:
                clusterCount += 1
                newLabels[fileIndex][np.where(newLabels[fileIndex] ==  c)[0]] = clusterCount

        ## handle special labeling of noise clusters
        ## TODO

    return newLabels
    
def event_count_compare(fa,clusterEventsI,clusterEventsJ,fileJ,clusterJ,thresholds=None,inputThreshold=None):
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
    if inputThreshold != None:
        threshold = inputThreshold
    else:
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

def get_master_label_list(expListLabels):
    labelMasterList = set([])
    for labelList in expListLabels:
        fileLabels = np.sort(np.unique(labelList))
        labelMasterList.update(fileLabels)

    masterLabelList = np.sort(np.unique(labelMasterList))

    return masterLabelList

def calculate_intercluster_score(fa,expListNames,expListLabels):
    '''
    calculate a global file alignment score
    '''

    masterLabelList = get_master_label_list(expListLabels)

    ## get a dict of magnitudes
    magnitudeDict = {}
    for cluster in masterLabelList:
        magnitude = -1
        for fileInd in range(len(expListNames)):
            fileName = expListNames[fileInd]
            fileLabels = expListLabels[fileInd]
            uniqueLabels = np.sort(np.unique(fileLabels)).tolist()
            if uniqueLabels.__contains__(cluster):
                magnitude+=1

        magnitudeDict[cluster] = magnitude

    ## calculate a score 
    goodnessScore = 0
    for cluster in masterLabelList:
        totalEventsAcrossFiles = 0
        for fileInd in range(len(expListNames)):
            fileName = expListNames[fileInd]
            fileLabels = expListLabels[fileInd]
            fileData = fa.get_events(fileName)
            clusterEvents = fileData[np.where(fileLabels==cluster)[0],:]
            n,k = np.shape(clusterEvents)
            totalEventsAcrossFiles+=n

        goodnessScore += (magnitudeDict[cluster] * float(totalEventsAcrossFiles))

    return goodnessScore




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
