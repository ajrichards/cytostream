'''
functions that are used to align files
'''

import sys,re,os,csv,cPickle
import numpy as np
from multiprocessing import Pool, cpu_count
from scipy.cluster.vq import whiten
from scipy.spatial.distance import pdist
from cytostream.stats import DistanceCalculator, EmpiricalCDF, BootstrapHypoTest, GaussianDistn, kullback_leibler,  run_kmeans_with_sv
import matplotlib.pyplot as plt
from fcm.statistics import mixnormpdf

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
            ## determine distances
            clusterEvents = fileData[np.where(fileLabels==int(clusterID))[0],:]
            if len(clusterEvents) < fa.minNumEvents:
                withinThresholds[fileName][str(int(clusterID))] = None
                continue

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
                    distances = whiten(distances)
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

def get_modes(fa,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters, phi, isPhi2=False):
        
    results = nonNoiseResults[phiIndices]
    resultsFiles = nonNoiseFiles[phiIndices]
    resultsClusters = nonNoiseClusters[phiIndices]

    newLabels = [np.array([-1 * int(label) for label in fa.get_labels(fn)]) for fn in fa.expListNames]
    for fileName in fa.expListNames:
        fileIndex = fa.expListNames.index(fileName)
        fileLabels = fa.get_labels(fileName)
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
  
                ## remember the noise clusters
                if isPhi2 == False:
                    if fa.noiseClusters.has_key(fileName) and int(c) in fa.noiseClusters[fileName]:
                        if fa.modeNoiseClusters[str(phi)].has_key(fileName):
                            fa.modeNoiseClusters[str(phi)][fileName].append(str(clusterCount))
                        else:
                            fa.modeNoiseClusters[str(phi)][fileName] = [str(clusterCount)]
                else:
                    if fa.noiseClusters.has_key(fileName) and int(c) in fa.noiseClusters[fileName]:
                        if fa.phi2NoiseClusters.has_key(fileName):
                            fa.phi2NoiseClustes[fileName].append(clusterCount)
                        else:
                            fa.phi2NoiseClusters[fileName] = [clusterCount]

                ## call the clusters that have less than the min num required events as noise
                if isPhi2 == False:
                    if len(np.where(fileLabels == c)[0]) < fa.minNumEvents:
                        if fa.modeNoiseClusters[str(phi)].has_key(fileName):
                            fa.modeNoiseClusters[str(phi)][fileName].append(clusterCount)
                        else:
                            fa.modeNoiseClusters[str(phi)][fileName] = [clusterCount]
                else:
                    if len(np.where(fileLabels == c)[0]) < fa.minNumEvents:
                        if fa.phi2NoiseClusters.has_key(fileName):
                            fa.phi2NoiseClustes[fileName].append(clusterCount)
                        else:
                            fa.phi2NoiseClusters[fileName] = [clusterCount]
                
                if clustersLeft.__contains__(c):
                    clustersLeft.remove(int(c))

        #print fileName, clustersLeft, np.unique(newLabels[fileIndex])
        ## change the labels of unmatched clusters
        for c in clustersLeft:
            clusterCount += 1
            newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * c)[0]] = clusterCount
            
            if isPhi2 == False:
                if fa.noiseClusters.has_key(fileName) and c in fa.noiseClusters[fileName]:
                    if fa.modeNoiseClusters[str(phi)].has_key(fileName):
                        fa.modeNoiseClusters[str(phi)][fileName].append(clusterCount)
                    else:
                        fa.modeNoiseClusters[str(phi)][fileName] = [clusterCount]
            else:
                if fa.noiseClusters.has_key(fileName) and c in fa.noiseClusters[fileName]:
                    if fa.phi2NoiseClusters.has_key(fileName):
                        fa.phi2NoiseClusters[fileName].append(clusterCount)
                    else:
                        fa.phi2NoiseClusters[fileName] = [clusterCount]

    return newLabels

def bootstrap_compare(eventsI,eventsJ):
    n,m = len(eventsI),len(eventsJ)

    if n == 0 or m == 0:
        print "ERROR in bootstrap_compare -- cluster had 0 elements"
        return None
                                                                             
    bootstrapDataLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])
    bootstrapData = np.vstack([eventsI,eventsJ])
    bstpr = BootstrapHypoTest(bootstrapData, bootstrapDataLabels, nrep=50)
    bresults = bstpr.get_results()  

    return bresults

def pool_compare_bootstrap(args):
    eventsI = args[0]
    eventsJ = args[1]
    identifier = args[2]

    print '...bootstrapping', identifier

    n,m = len(eventsI),len(eventsJ)

    if n == 0 or m == 0:
        print "ERROR in bootstrap_compare -- cluster had 0 elements"
        return None
                                                                             
    bootstrapDataLabels = np.hstack([np.array([0]).repeat(n),np.array([1]).repeat(m)])
    bootstrapData = np.vstack([eventsI,eventsJ])
    bstpr = BootstrapHypoTest(bootstrapData, bootstrapDataLabels, nrep=50)
    bresults = bstpr.get_results()  

    return bresults


def get_alignment_labels(fa,alignment,phi,evaluator='rank'):
    '''
    gets alignment labels
    
    to debug 
      (1) comment out the 'normalize the labels' block
      (2) uncommend the 'debug' print line 

    '''

    if evaluator not in ['rank','bootstrap','kldivergence','variance','mixpdf']:
        print "ERROR: in get_alignment_labels evaluator not valid"

    results = alignment['results']
    resultsFiles = alignment['files']
    resultsClusters = alignment['clusters']
    
    newLabels = [np.array([-1 * int(label) for label in fa.get_labels(fn)]) for fn in fa.expListNames]
    clusterCount = 10000
    noiseClustCount = 0
    templateData = fa.get_template_data()

    for fileName in fa.expListNames:
        fileIndex = fa.expListNames.index(fileName)
        fileLabels = fa.get_labels(fileName)
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
            if int(clusterID) in fa.noiseClusters[fileName]:
                continue
            
            if len(templateMatches) < 1:
                continue

            if len(np.where(fileLabels == clusterID)[0]) < fa.minNumEvents:
                continue
             
            ## debug
            #print 'In file %s cluster %s will be changed to %s due to a overlap of %s'%(fileName,clusterID,templateMatches,matchSignif)
            if evaluator == 'rank' or len(matchSignif) == 1:
                rankedInds = np.argsort(matchSignif)[::-1]
            elif evaluator == 'variance':
                varResults = []
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                covarJ = np.cov(eventsJ.T)
                for tm in templateMatches:
                   eventsI = templateData[np.where(fa.templateLabels==tm)[0],:]
                   covarI = np.cov(eventsJ.T)
                   varResults.append(np.abs(covarI - covarJ).sum())
                rankedInds = np.argsort(varResults)
                
            elif evaluator == 'mixpdf':

                mixpdfResults = []

                ## fit the template cluster
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                kmeanResults = run_kmeans_with_sv(eventsJ,subsample=2000)
                kmeanLabels = kmeanResults['labels']
                uniqueLabels = np.unique(kmeanLabels)
                k = kmeanResults['k']

                mu = np.array([eventsJ[np.where(kmeanLabels == i)[0],:].mean(axis=0) for i in uniqueLabels])
                sigma = np.array([np.cov(eventsJ[np.where(kmeanLabels == i)[0],:].T) for i in uniqueLabels])
                pi = np.array([float(len(np.where(kmeanLabels == i)[0])) / float(len(kmeanLabels)) for i in uniqueLabels])

                for tm in templateMatches:
                   eventsI = templateData[np.where(fa.templateLabels==tm)[0],:]
                   mnpdf = mixnormpdf(eventsI,pi,mu,sigma)                                   
                   mixpdfResults.append(mnpdf.mean())
                   
                rankedInds = np.argsort(mixpdfResults)

            elif evaluator == 'bootstrap':
                bootstrapResults = []
                #print "\t...bootstrapping for ", fileName, clusterID
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                for tm in templateMatches:
                    eventsI = templateData[np.where(fa.templateLabels==tm)[0],:]
                    bsResults = bootstrap_compare(eventsI, eventsJ)
                    bootstrapResults.append(bsResults['delta1'])
                rankedInds = np.argsort(bootstrapResults)
            
                #print evaluator,bootstrapResults[rankedInds[0]],bootstrapResults[rankedInds[1]]
    
                #allEventsI = []
                #for tm in templateMatches:
                #    allEventsI.append(templateData[np.where(fa.templateLabels==tm)[0],:])
                #eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                #pool = Pool(processes=cpu_count()-1,masktasksperchild=1)
                #args = zip(allEventsI,
                #           [eventsJ]*len(templateMatches),
                #           ["%s-%s"%(fileName,clusterID)]*len(templateMatches))
                #_bootstrapResults = pool.map(pool_compare_bootstrap,args)
                #bootstrapResults = []
                #
                #for tm in range(len(templateMatches)):
                #    matchResults = _bootstrapResults[tm]
                #    bootstrapResults+=matchResults
                #rankedInds = np.argsort(bootstrapResults)

            elif evaluator == 'kldivergence':
                klResults = []
                eventsJ = fileData[np.where(fileLabels==clusterID)[0],:]
                gd1 = GaussianDistn(eventsJ.mean(axis=0), np.cov(eventsJ.T))

                ## things to try use max of both kldists 
                for tm in templateMatches:
                    eventsI = templateData[np.where(fa.templateLabels==tm)[0],:]
                    #print "kld", eventsJ.shape, eventsI.shape
                    gd2 = GaussianDistn(eventsI.mean(axis=0), np.cov(eventsI.T))
                    klDist1 = kullback_leibler(gd1,gd2)
                    klDist2 = kullback_leibler(gd2,gd1)
                    klList = [klDist1.sum(),klDist2.sum()]
                    klDist = klList[np.argmax([klDist1.sum(),klDist2.sum()])] 
                    klResults.append(klDist)
                    #print "...",tm,klList
                #print klResults
                rankedInds = np.argsort(klResults)
            
            ## if multiple matches handle
            newLabels[fileIndex][np.where(newLabels[fileIndex] == -1 * clusterID)[0]] = templateMatches[rankedInds[0]]

        ## change the labels of unmatched clusters
        clustersLeft = np.unique(newLabels[fileIndex][np.where(newLabels[fileIndex] < 0)])

        for c in clustersLeft:
            if int(-1.0*c) in fa.noiseClusters[fileName]:
                noiseClustCount -= 1
                newLabels[fileIndex][np.where(newLabels[fileIndex] ==  c)[0]] = noiseClustCount
            else:
                clusterCount += 1
                newLabels[fileIndex][np.where(newLabels[fileIndex] ==  c)[0]] = clusterCount

        ## handle special labeling of noise clusters
        ## TODO

    ## normalize the labels
    allLabs = set([])
    newLabelsCopy = [nl.copy() for nl in newLabels]
    for fileInd in range(len(newLabels)):
        fileLabels = newLabelsCopy[fileInd]
        allLabs.update(np.sort(np.unique(fileLabels)).tolist())
    allLabs = np.sort(list(allLabs))
    nextLab = 0
    for ulab in allLabs:
        if ulab < 0:
            continue
        nextLab+=1
        for fileInd in range(len(newLabels)):
            labInds = np.where(newLabelsCopy[fileInd] == ulab)[0]
            if len(labInds) == 0:
                continue
            
            newLabels[fileInd][labInds] = nextLab
    
    return newLabels
    
def event_count_compare(clusterEventsI,clusterEventsJ,clusterJ,threshold):
    '''
    model the sink (j) then determine number of events in source (i) that overlap
    '''
    
    distanceMetric = 'mahalanobis'
    clusterMeanJ = clusterEventsJ.mean(axis=0)

    dc = DistanceCalculator(distType=distanceMetric)
    if distanceMetric == 'mahalanobis':
        inverseCov = dc.get_inverse_covariance(clusterEventsJ)
        if inverseCov != None:
            dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ,inverseCov=inverseCov)
            distances = dc.get_distances()
        else:
            dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ)
            distances = dc.get_distances()
            distances = whiten(distances)
    else:
        dc.calculate(clusterEventsI,matrixMeans=clusterMeanJ)
        distances = dc.get_distances()

    ## calculate % overlap
    overlappedInds1 = np.where(distances > threshold[0])[0]
    overlappedInds2 = np.where(distances < threshold[1])[0]
    overlappedInds = list(set(overlappedInds1).intersection(set(overlappedInds2)))
    
    if len(overlappedInds) == 0:
        return 0
 
    if len(distances) == 0:
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
            #if compareCount > 10:
            #    continue

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


def calculate_intercluster_score(fa,expListNames,expListLabels,templateLabels,returnMagDictOnly=False):
    '''
    calculate a global file alignment score
    '''

    ## get unique labels for each file
    uniqueList = []
    maxLength = 0
    for fileInd in range(len(expListNames)):
        fileName = expListNames[fileInd]
        fileLabels = expListLabels[fileInd]
        uniqueLabels = np.unique(fileLabels)
        if uniqueLabels.size > maxLength:
            maxLength = uniqueLabels.size
        uniqueList.append(uniqueLabels)
        
    ## buffer each list with 0 and create a matrix
    mat = np.zeros((maxLength,len(expListNames)),)
    for i in range(len(uniqueList)):
        uls = uniqueList[i]
        mat[:len(uls),i] = np.array(uls)
        
    ## get magnitudes for each cluster
    uniqueTemplateLabs = np.unique(templateLabels)
    magnitudeDict = {}
    for cluster in uniqueTemplateLabs:
        magnitudeDict[str(cluster)] = np.where(mat==cluster)[0].size - 1

    if returnMagDictOnly == True:
        return magnitudeDict

    ## calculate a score
    goodnessScore = 0
    
    ## get number of data points in each cluster
    numEvents = {}
    for fileInd in range(len(expListLabels)):
        fileName = expListNames[fileInd]
        numEvents[fileName] = {}
        fileData = fa.get_events(fileName)
        fileLabels = expListLabels[fileInd]

        for cluster in np.unique(fileLabels):
            clusterInds = np.where(fileLabels==cluster)[0]
            numEvents[fileName][str(cluster)] = len(clusterInds)

    for cluster in uniqueTemplateLabs:

        ## skip noise
        if cluster < 0:
            continue

        totalEventsAcrossFiles = 0
        for fileInd in range(len(expListNames)):
            fileName = expListNames[fileInd]
            if numEvents[fileName].has_key(str(cluster)):
                totalEventsAcrossFiles+=numEvents[fileName][str(cluster)]

        if magnitudeDict[str(cluster)] <= 0:
            continue

        goodnessScore += (magnitudeDict[str(cluster)] * float(totalEventsAcrossFiles))
    
    return goodnessScore, magnitudeDict

def pool_compare_self(args):

    ## input variables
    fileName = args[0]
    fileData = args[1]
    fileLabels = args[2]
    fileClusters = args[3]
    sampleStats = args[4]
    noiseClusters = args[5]
    thresholds = args[6]
    minNumEvents = args[7]

    ## additional variables
    alignResults = []
    alignResultsFiles = []
    alignResultsClusters = []

    for ci in range(len(fileClusters)):
        clusterI = fileClusters[ci]
        clusterEventsI = fileData[np.where(fileLabels==clusterI)[0],:]
        clusterMuI = sampleStats['mus'][fileName][str(clusterI)]
        clustersToCompare = []
        clusterCtList = []

        for cj in range(len(fileClusters)):
            clusterJ = fileClusters[cj]
            
            ## do not compare cluster to itself
            if ci <= cj:
                continue

            ## check for noise label
            if noiseClusters.has_key(fileName) and noiseClusters[fileName].__contains__(clusterI):
                continue
            if noiseClusters.has_key(fileName) and noiseClusters[fileName].__contains__(clusterJ):
                continue

            ## get events
            clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]

            ## ensure cluster is at least of mininum size
            if len(clusterEventsI) < minNumEvents or len(clusterEventsJ) < minNumEvents:
                continue

            ## check that the centroids are at least a reasonable distance apart                    
            clusterMuJ = sampleStats['mus'][fileName][str(clusterJ)] 
            eDist = pdist([clusterMuI,clusterMuJ],'euclidean')[0]
            threshold1 = sampleStats['dists'][fileName][str(clusterI)]
            threshold2 = sampleStats['dists'][fileName][str(clusterJ)]
            
            #print fileName, clusterI, clusterJ, eDist, threshold1, threshold2
            if eDist > threshold1 or eDist > threshold2:
                continue
                    
            overlap1 = event_count_compare(clusterEventsI,clusterEventsJ,clusterJ,thresholds[fileName][str(clusterJ)]['ci'])
            overlap2 = event_count_compare(clusterEventsJ,clusterEventsI,clusterI,thresholds[fileName][str(clusterI)]['ci'])
            overlap = np.max([overlap1, overlap2])

            ## save results
            alignResults.append(overlap)
            alignResultsFiles.append(fileName)
            alignResultsClusters.append("%s#%s"%(clusterI,clusterJ))
            
    return [alignResults,alignResultsFiles,alignResultsClusters]

def pool_compare_scan(args):

    ## input variables
    fileName = args[0]
    fileData = args[1]
    fileLabels = args[2]
    fileClusters = args[3]
    sampleStats = args[4]
    thresholds = args[5]
    templateData= args[6]
    templateLabels = args[7]
    templateClusters = args[8]
    templateThresholds = args[9]
    phi = args[10]
    minNumEvents = args[11]
    noiseClusters = args[12]

    ## additional variables
    alignResults = []
    alignResultsFiles = []
    alignResultsClusters = []

    for ci in range(len(templateClusters)):
        clusterI = int(templateClusters[ci])
        templateEvents = templateData[np.where(templateLabels==clusterI)[0],:]
        clusterMuI = templateEvents.mean(axis=0)

        for cj in range(len(fileClusters)):         
            clusterJ = int(fileClusters[cj])
            clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]

            if len(templateEvents) < minNumEvents or len(clusterEventsJ) < minNumEvents:
                continue
            
            #print fileName, len(templateEvents), len(clusterEventsJ),sampleStats['mus'][fileName].has_key(clusterJ)
        
            ## check for noise label
            if noiseClusters.has_key(fileName) and noiseClusters[fileName].__contains__(int(clusterJ)):
                continue

            ## check that the centroids are at least a reasonable distance apart                    
            clusterMuJ = clusterEventsJ.mean(axis=0)#sampleStats['mus'][fileName][str(clusterJ)]
            eDist = pdist([clusterMuI,clusterMuJ],'euclidean')[0]
            threshold = sampleStats['dists'][fileName][str(clusterJ)]
                    
            if eDist > threshold:
                continue
            
            overlap1 = event_count_compare(templateEvents,clusterEventsJ,clusterJ,thresholds[fileName][str(clusterJ)]['ci'])
            overlap2 = event_count_compare(clusterEventsJ,templateEvents,clusterI,templateThresholds[str(clusterI)]['ci'])
            overlap = np.max([overlap1, overlap2])

            if overlap < phi:
                continue

            ## save results
            alignResults.append(overlap)
            alignResultsFiles.append(fileName)
            alignResultsClusters.append("%s#%s"%(clusterI,clusterJ))
     
    return [alignResults,alignResultsFiles,alignResultsClusters]

def get_alignment_scores(homeDir,alignmentDir='alignment',makeFig=True):
    alignScores = {'phi':[],'num_template_clusters':[],'sil_val':[],'normalized_matches':[],'product_score':[]}
    alignScoreFilePath = os.path.join(homeDir,alignmentDir,'AlignmentScores.log')
    
    if os.path.exists(alignScoreFilePath) == False:
        print "ERROR: get_alignment_scores -- alignment file does not exist"
        return None

    reader = csv.reader(open(alignScoreFilePath,'r'))
    header = reader.next()
    
    for linja in reader:
        alignScores['phi'].append(float(linja[0]))
        alignScores['num_template_clusters'].append(float(linja[1])) 
        alignScores['sil_val'].append(float(linja[2]))
        alignScores['normalized_matches'].append(float(linja[3]))
        alignScores['product_score'].append(float(linja[4]))

    if makeFig == True:
        bestInd = np.argmax(alignScores['product_score'])
        bestPhi = alignScores['phi'][bestInd]
        projectID = os.path.split(homeDir)[-1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        p1 = ax.plot(alignScores['phi'], alignScores['sil_val'], color='b',linewidth=2.0)
        p2 = ax.plot(alignScores['phi'], alignScores['normalized_matches'], color='orange',linewidth=2.0)
        p3 = ax.plot(np.array(bestPhi).repeat(10),np.linspace(0,1,10),'k--',linewidth=2.0)
        ax.set_xlim(0,1)
        ax.set_ylim(0,1)
        ax.legend((p1[0],p2[0],p3[0]),("sil val", "matches",r"best $\phi$"))
        ax.set_title(projectID)
        figName = os.path.join(homeDir,'figs',alignmentDir,'AlignScores.png')
        plt.savefig(figName)

    return alignScores

def get_saved_template(homeDir='.',savePath=None):
    '''
    return a tuple of template events and templatelabels

    '''
    
    if savePath == None:
        savePath = os.path.join(homeDir,'results')

    ## get the data
    tmp =  open(os.path.join(savePath,"templateData.pickle"),'r')
    if os.path.exists(os.path.join(savePath,"templateData.pickle")) == False:
        print "ERROR: template data does not exist ", os.path.join(savePath,"templateData.pickle")
        return [],[],[]

    templateData = cPickle.load(tmp)
    tmp.close()

    ## get the components
    tmp =  open(os.path.join(savePath,"templateComponents.pickle"),'r')
    if os.path.exists(os.path.join(savePath,"templateComponents.pickle")) == False:
        print "ERROR: template data does not exist ", os.path.join(savePath,"templateComponents.pickle")
        return [],[],[]

    templateComponents = cPickle.load(tmp)
    tmp.close()

    ## get the modes
    tmp =  open(os.path.join(savePath,"templateModes.pickle"),'r')
    if os.path.exists(os.path.join(savePath,"templateModes.pickle")) == False:
        print "ERROR: template data does not exist ", os.path.join(savePath,"templateModes.pickle")
        return [],[],[]

    templateModes = cPickle.load(tmp)
    tmp.close()

    return templateData,templateComponents,templateModes
