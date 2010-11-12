#!/usr/bin/python
'''
file indices begin with 0
cluster indices are forced to begin with 1

'''

import os,csv,re,sys,cPickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.ticker import MaxNLocator
from scipy.spatial.distance import pdist,cdist,squareform
from scipy.cluster.vq import whiten
import scipy.stats as stats
from cytostream.tools import calculate_intercluster_score 
from cytostream.stats import SilValueGenerator

class FileAligner():
    '''
    expListNames   - a list of the individual experiemnts
    expListData    - a list of np.arrays containing the (n x d) data for each experiment data set
    expListLabels  - a list of lists or np.arrays containing the labels for each data set 
    phi            - percent overlap for between cluster comparison before align call

    '''

    def __init__(self,expListNames,expListData,expListLabels,modelName,phiRange=[0.4],minSilValue=0.3,
                 mkPlots=True,refFile=None,verbose=False,excludedChannels=[],basedir="."):
        self.expListNames = [expName for expName in expListNames]
        #self.expListData = [whiten(expData[:,:].copy()) for expData in expListData]
        self.expListData = [expData[:,:].copy() for expData in expListData]
        self.expListLabels = [[label for label in labelList] for labelList in expListLabels]
        self.phiRange = phiRange
        self.matchResults = None
        self.modelName = modelName
        self.mkPlots = mkPlots
        self.minMergeSilValue = minSilValue
        self.basedir = basedir
        self.verbose = verbose
        self.silValueEstimateSample = 500
        numChannels = np.shape(self.expListData[0])[1]
        self.newLabelsAll = {}

        ## error checking 
        if type(self.phiRange) != type([]) and type(self.phiRange) != type(np.array([])):
            print "INPUT ERROR: phi range is not a list or np.array"

        ## handle excluded channels
        if excludedChannels != None:
            self.includedChannels = list(set(range(numChannels)).difference(set(excludedChannels)))
        else:
            self.includedChannels = range(numChannels)

        ## use data only from included channels
        self.expListData = [expData[:,self.includedChannels] for expData in self.expListData]

        ## preprocessing of data
        if self.verbose == True:
            print "transforming labels"
        self.transform_labels()
        if self.verbose == True:
            print "getting sample statistics"
        self.sampleStats = self.get_sample_statistics(self.expListLabels)

        ## determine reference file
        if self.verbose == True:
            print "Determining reference file"
        if refFile != None and self.expListNames.__contains__(refFile) == False:
            print "INPUT ERROR: invalid reference file name"
        elif refFile != None and self.expListNames.__contains__(refFile) == True:
            if self.verbose == True:
                print "\tusing input reference file name"
            self.refFile = refFile
        else:
            if self.verbose == True:
                print "\tusing generated reference file name"
            self.refFile = self.get_reference_file()

        ## prepare log file
        self.create_log_file()
        self.create_alignments_file()

        ## create a copy of the reference file
        refFileInd = self.expListNames.index(self.refFile)
        refFileLabels = [lab for lab in self.expListLabels[refFileInd]]
        originalRefFileLabels = [lab for lab in refFileLabels]
        refFileData = self.expListData[refFileInd].copy()
        self.expListNames.append("copied_ref_file")
        self.expListLabels.append(refFileLabels)
        self.expListData.append(refFileData)

        if self.verbose == True:
            print "getting sample statistics"
        self.sampleStats = self.get_sample_statistics(self.expListLabels)
        if self.verbose == True:
            print "getting silhouette values"
        self.silValues = self.get_silhouette_values(self.expListLabels)

        ## make overlap comparisons
        if self.verbose == True:
            print "making overlap comparisons"
        
        ## align files
        for phi in self.phiRange:
            if self.verbose == True:
                print "performing file alignment -- ", phi
        
            ## ensure ref file labels are originals
            self.expListLabels[refFileInd] = [lab for lab in originalRefFileLabels]
            
            ## merge clusters in reference
            self._merge_clusters_in_reference(self.refFile,phi)

            ## find overlaps
            self.matchResults = self.make_overlap_comparisons(self.refFile)        
            
            ## carry out file alignment
            self.perform_file_alignment(self.refFile,self.matchResults,phi)
            self._save_clusters(phi)
            
            ## write data to alignments file
            interClusterDistance = calculate_intercluster_score(self.expListNames,self.expListData,self.newLabelsAll[str(round(phi,4))])
            
            allMeanSilValues = []
            for en in range(len(self.expListNames)):
                expName = self.expListNames[en]
                if expName == refFile:
                    continue

                data =  self.expListData[en]
                labels =  self.newLabelsAll[str(round(phi,4))][en]
                svg = SilValueGenerator(data,labels)
                silvalues = svg.silValues
                allMeanSilValues.append(silvalues.mean())
            
            self.alignmentFile.writerow([phi,interClusterDistance,np.array(allMeanSilValues).mean()])

        ## move the copied reference file labels to the reference labels
        for phi in self.phiRange:
            self.newLabelsAll[str(round(phi,4))][self.expListNames.index(self.refFile)] = [lab for lab in self.newLabelsAll[str(round(phi,4))][-1]]
            self.newLabelsAll[str(round(phi,4))].pop()

        self.expListNames.pop()
        self.expListData.pop()
        self.expListLabels.pop()

    def create_log_file(self):
        ''' 
        create a log file to document cluster changes
        each log is specific to a give phi
        '''
        if os.path.isdir(os.path.join(self.basedir,"results")) == False:
            os.mkdir(os.path.join(self.basedir,"results"))

        self.logFile = csv.writer(open(os.path.join(self.basedir,"results","_FileMerge.log"),'wa'))
        self.logFile.writerow(["expListNames",re.sub(",",";",re.sub("\[|\]|'","",str(self.expListNames)))])
        self.logFile.writerow(["refFile",self.refFile])
        self.logFile.writerow(["silThresh",self.minMergeSilValue])
        self.logFile.writerow(['phi','algorithmStep','fileSource','OldLabel','fileTarget','newLabel','numEventsChanged','percentoverlap','silValue']) 


    def create_alignments_file(self):
        ''' 
        create a log file to document  the alignments

        '''
        if os.path.isdir(os.path.join(self.basedir,"results")) == False:
            os.mkdir(os.path.join(self.basedir,"results"))

        self.alignmentFile = csv.writer(open(os.path.join(self.basedir,"results","alignments.log"),'wa'))
        self.alignmentFile.writerow(["phi","alignment-score","average-silvalue"])


    def transform_labels(self):
        ## ensure that labels begin at 1 and not 0
        newExpListLabels = []
        for labels in self.expListLabels:
            labels = 1 + np.array(labels)
            newExpListLabels.append(labels.tolist())

        self.expListLabels = newExpListLabels

    def get_sample_statistics(self,expListLabels):

        centroids, variances, numClusts, numDataPoints = {},{},{},{}
        for expInd in range(len(expListLabels)):
            expName = self.expListNames[expInd]
            #for expName in self.expListNames:
            centroids[expName] = {}
            variances[expName] = {}
            numClusts[expName] = None
            numDataPoints[expName] = {}

        for expInd in range(len(expListLabels)):
            expName = self.expListNames[expInd]
            expData = self.expListData[expInd]
            expLabels = expListLabels[expInd]

            for cluster in np.sort(np.unique(expLabels)):
                centroids[expName][str(cluster)] = expData[np.where(expLabels==cluster)[0],:].mean(axis=0)
                variances[expName][str(cluster)] = expData[np.where(expLabels==cluster)[0],:].var(axis=0)
                numDataPoints[expName][str(cluster)] = len(np.where(expLabels==cluster)[0])

            numClusts[expName] = len(np.unique(expLabels))

        return {'mus':centroids,'sigmas':variances,'k':numClusts,'n':numDataPoints}

    def get_silhouette_values(self,expListLabels):
        silValues = {}
        silValuesElements = {}
        for expName in self.expListNames:
            silValues[expName] = {}

        ## create subset if data for large data sets 
        subsetExpData = []
        subsetExpLabels = []

        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            expData = self.expListData[c]
            expLabels = expListLabels[c]
            fileClusters = np.sort(np.unique(expLabels))

            newIndices = []
            for clusterInd in fileClusters:
                clusterElementInds = np.where(expLabels == clusterInd)[0]
                if clusterElementInds.size > self.silValueEstimateSample:
                    randSelectedInds = clusterElementInds[np.random.randint(0,clusterElementInds.size,self.silValueEstimateSample)]
                    newIndices = newIndices + randSelectedInds.tolist()
                else:
                    newIndices = newIndices + clusterElementInds.tolist() 

            subsetExpData.append(expData[newIndices,:])
            subsetExpLabels.append(np.array(expLabels)[newIndices])

        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            expData = subsetExpData[c]
            expLabels = subsetExpLabels[c]

            if self.verbose == True:
                print '\tgetting silhouette values %s/%s'%(c+1,len(self.expListNames))
            silValuesElements[expName] = self._get_silhouette_values(expData,expLabels)
            fileClusters = np.sort(np.unique(expLabels))

            ## save only sil values for each cluster
            for clusterID in fileClusters:
                clusterElementInds = np.where(expLabels == clusterID)[0]
                clusterSilValue = silValuesElements[expName][clusterElementInds].mean()
                silValues[expName][str(clusterID)] = clusterSilValue
                del clusterElementInds
           
        return silValues

    def _get_silhouette_values(self,mat,labels):        
        svg = SilValueGenerator(mat,labels)
        return svg.silValues

    def get_reference_file(self,method='minimum'):
        '''
        get a reference data file or patient
        '''
        if method not in ['minimum', 'median']:
            print "ERROR: could not get reference file in get_reference_file -- bad method input"
            return None

        modeClusters = int(stats.mode(np.array(self.sampleStats['k'].values()))[0][0])
        medianClusters = np.median(np.array(self.sampleStats['k'].values()))
        minNumClusters = np.min(np.array(self.sampleStats['k'].values()))
        maxNumClusters = np.max(np.array(self.sampleStats['k'].values()))
        
        ## choose a cluster with the median for the number of clusters 
        refFile = None
        
        if method == 'median':
            minScore = 100
            for c in range(len(self.expListNames)):
                expName = self.expListNames[c]
                k = self.sampleStats['k'][expName]
                if k <= medianClusters:
                    score = medianClusters - k
                if k > medianClusters:
                    score = k - medianClusters

                if score < minScore:
                    minScore = score
                    refFile = expName
        elif method == 'minimum':
            for c in range(len(self.expListNames)):
                expName = self.expListNames[c]
                k = self.sampleStats['k'][expName]
                
                if int(k) == minNumClusters and refFile == None:
                    refFile = expName

        return refFile

    def make_overlap_comparisons(self,refFile):
        '''
        compare all pairwise clusters
        
        '''
        matchResults = None
        totalCompares = int((float(len(self.expListNames)) * float(len(self.expListNames))-1.0)/2.0)
        compareCount = 0
        self.clustersAligned = {}
        shortVersion = False
        refFileInd = self.expListNames.index(self.refFile)

        if self.matchResults != None:
            shortVersion = True
            numRows, numCols = np.shape(self.matchResults)
            totalCompares = len(self.expListNames) - 1

            for row in range(numRows):
                previousResult = self.matchResults[row,:]
            
                if int(previousResult[0]) == int(refFileInd) or int(previousResult[1]) == int(refFileInd):
                    continue

                if matchResults == None:
                    matchResults = previousResult
                else:
                    matchResults = np.vstack((matchResults, previousResult))

        for pIndex1 in range(len(self.expListNames)):
            for pIndex2 in range(len(self.expListNames)):
                if pIndex2 >= pIndex1:
                    continue

                ## if short version recalculate only ref file compares
                if shortVersion == True and int(refFileInd) not in [int(pIndex1),int(pIndex2)]:
                    continue

                compareCount+=1
                if self.verbose == True:
                    print "\tcomparing %s and %s (%s/%s)"%(pIndex1,pIndex2,compareCount,totalCompares)

                ## potential speedup step here -- avoid distant comparisions
                patient1 = self.expListNames[pIndex1]
                patient2 = self.expListNames[pIndex2]
                dataPatient1 = self.expListData[pIndex1]
                dataPatient2 = self.expListData[pIndex2]
                labelsPatient1 = self.expListLabels[pIndex1]
                labelsPatient2 = self.expListLabels[pIndex2]
                
                ## order the clusters such that the ones with the greatest number of elements are first
                sortedLabelsPatient1 = np.sort(np.unique(labelsPatient1))
                sortedLabelsPatient2 = np.sort(np.unique(labelsPatient2))

                sizesPatient1 = []
                for clusterID in sortedLabelsPatient1:
                    sizesPatient1.append(np.where(labelsPatient1 == clusterID)[0].size)
                sizeOrderedLabelsPatient1 = sortedLabelsPatient1[np.argsort(sizesPatient1)]
                sizeOrderedLabelsPatient1 = sizeOrderedLabelsPatient1[::-1]

                sizesPatient2 = []
                for clusterID in sortedLabelsPatient2:
                    sizesPatient2.append(np.where(labelsPatient2 == clusterID)[0].size)
                sizeOrderedLabelsPatient2 = sortedLabelsPatient2[np.argsort(sizesPatient2)]
                sizeOrderedLabelsPatient1 = sizeOrderedLabelsPatient1[::-1]

                for cluster1 in sizeOrderedLabelsPatient1:
                    for cluster2 in sizeOrderedLabelsPatient2:
         
                        ## take events in the clusters and find their euclidean distance from their centers
                        eventsPatient1 = dataPatient1[np.where(labelsPatient1==cluster1)[0],:]
                        eventsPatient2 = dataPatient2[np.where(labelsPatient2==cluster2)[0],:]

                        ## calculate within cluster distances
                        euclidDist1 = (eventsPatient1 - eventsPatient1.mean(axis=0))**2.0
                        euclidDist1 = np.sqrt(euclidDist1.sum(axis=1))
                        euclidDist2 = (eventsPatient2 - eventsPatient2.mean(axis=0))**2.0
                        euclidDist2 = np.sqrt(euclidDist2.sum(axis=1))

                        ## determine the number of events that overlap
                        overlap1 = (eventsPatient1 - eventsPatient2.mean(axis=0))**2.0
                        overlap1 = np.sqrt(overlap1.sum(axis=1))
                        overlap2 = (eventsPatient2 - eventsPatient1.mean(axis=0))**2.0
                        overlap2 = np.sqrt(overlap2.sum(axis=1))

                        threshold1 = stats.norm.ppf(0.975,loc=euclidDist1.mean(),scale=euclidDist1.std())
                        threshold2 = stats.norm.ppf(0.975,loc=euclidDist2.mean(),scale=euclidDist2.std())

                        overlappingInds1 = np.where(overlap1<threshold2)[0]
                        overlappingInds2 = np.where(overlap2<threshold1)[0]
                        percentOverlap1 = float(len(overlappingInds1)) / float(np.shape(eventsPatient1)[0])
                        percentOverlap2 = float(len(overlappingInds2)) / float(np.shape(eventsPatient2)[0])
                        percentOverlap = np.max([percentOverlap1, percentOverlap2])

                        if percentOverlap > 1.0:
                            print "ERROR: in calculation of percent overlap", percentOverlap

                        ## discard results with withouth percent overlap
                        if  percentOverlap < 1e-16:
                            continue

                        ## save the results
                        #print patient1,patient2,pIndex1,pIndex2, cluster1,cluster2,(percentOverlap1,percentOverlap2),percentOverlap

                        results = np.array(([pIndex1, pIndex2, cluster1,cluster2, percentOverlap]))
                        if matchResults == None:
                            matchResults = results
                        else:
                            matchResults = np.vstack((matchResults, results))

        return matchResults


    def perform_file_alignment(self,refFile,matchResults,phi):
        ## check that we have results
        if matchResults == None:
            print "WARNING: matchResults contains no results"
            return None

        ## filter results by using only best matches and accounting for sil value and overlap thresholds
        filteredResults = self._filter_comparison_results(matchResults,refFile,phi,refComparison=True)

        ## create variables for newLabels
        self.newLabelsAll[str(round(phi,4))] = []      
        for labInd in range(len(self.expListLabels)):
            labels = self.expListLabels[labInd]
            self.newLabelsAll[str(round(phi,4))].append(-1.0 * np.array(labels).copy())

        ## make reference file comparisons
        self._make_reference_comparisons(refFile,filteredResults,phi)
        
        ## make a collection of clusters without matches to ref file
        filteredResults = self._filter_comparison_results(matchResults,refFile,phi,refComparison=False)
        
        try:
            frows, fcols = np.shape(filteredResults)
        except:
            frows = 0

        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
        clustersYetToLabel = []
        for altInd in range(len(self.newLabelsAll[str(round(phi,4))])):
            if int(altInd) == int(refFileInd):
                continue
            labels = self.newLabelsAll[str(round(phi,4))][altInd] 
            uniqueLabels = np.sort(np.unique(labels))
            negClusters = uniqueLabels[np.where(uniqueLabels < 0)[0]]
            for negInd in negClusters:
                clustersYetToLabel.append((int(altInd),int(negInd)))

        ## label clusters that do not match a label
        clustersLeft = [clust for clust in clustersYetToLabel]
        nextLabel =  np.max(refFileLabels) + 1

        ## check for remaining matching cluster
        for negCluster in clustersYetToLabel:
            fileInd = negCluster[0]
            clusterInd = negCluster[1]

            bestMatchList = []
            for rowNum in range(frows):
                results = filteredResults[rowNum,:]
                if results[0] == fileInd and int(results[2]) == int(-1.0 * clusterInd):
                    bestMatch = (results[1],results[3],results[4])
                    bestMatchList.append(bestMatch)
                elif results[1] == fileInd and int(results[3]) == int(-1.0 * clusterInd):
                    bestMatch = (results[0],results[2],results[4])
                    bestMatchList.append(bestMatch)

            if len(bestMatchList) > 0:
                if clustersLeft.__contains__((fileInd,clusterInd)) == True:
                    indicesToChange = np.where((self.newLabelsAll[str(round(phi,4))][fileInd]) == clusterInd)[0]
                    self.newLabelsAll[str(round(phi,4))][fileInd][indicesToChange] = nextLabel
                    clustersLeft.remove((fileInd,clusterInd))
                 
                for bestMatch in bestMatchList:
                    if clustersLeft.__contains__((bestMatch[0],-1*bestMatch[1])) == True:
                        indicesToChange = np.where((self.newLabelsAll[str(round(phi,4))][int(bestMatch[0])]) == -1*bestMatch[1])[0]

                        ## make sure match is over sil value threshold
                        uniqueLabels = np.sort(np.unique(self.expListLabels[int(bestMatch[0])])).tolist()
                        clusterInd = uniqueLabels.index(bestMatch[1])
                        clusterSilValue = self.silValues[self.expListNames[int(bestMatch[0])]][str(int(bestMatch[1]))]

                        if clusterSilValue < self.minMergeSilValue:
                            if self.verbose == True:
                                print "INFO: Skipping merge in nonref-match -- silhouette values" 
                            continue

                        self.newLabelsAll[str(round(phi,4))][int(bestMatch[0])][indicesToChange] = nextLabel
                        self.logFile.writerow([phi,'nonref-match',self.expListNames[int(bestMatch[0])], int(-1.0*bestMatch[1]),'NA',nextLabel,indicesToChange.size,"NA",clusterSilValue])
                        clustersLeft.remove((bestMatch[0],-1*bestMatch[1]))                
                        
                nextLabel += 1
        
        ## label clusters that had no match at all
        for negCluster in clustersLeft:
            fileInd = negCluster[0]
            clusterInd = negCluster[1]
            indicesToChange = np.where((self.newLabelsAll[str(round(phi,4))][fileInd]) == clusterInd)[0]

            ## log change
            clusterSilValue = self.silValues[self.expListNames[int(fileInd)]][str(int(-1.0*clusterInd))]
            self.logFile.writerow([phi,'no-match',self.expListNames[fileInd], int(-1.0*clusterInd-1.0),'NA',nextLabel,indicesToChange.size,"NA",clusterSilValue])

            self.newLabelsAll[str(round(phi,4))][fileInd][indicesToChange] = nextLabel
            nextLabel += 1

        ## change back to positive the ref labels and ensure labels are ints
        self.newLabelsAll[str(round(phi,4))][refFileInd] = -1 * self.newLabelsAll[str(round(phi,4))][refFileInd]
        self.newLabelsAll[str(round(phi,4))] = [[int(l) for l in labels] for labels in self.newLabelsAll[str(round(phi,4))]]

        ## normalize labels starting at 1
        allLabels = []
        for labels in self.newLabelsAll[str(round(phi,4))]:
            allLabels+=labels
        uniqueLabels = np.sort(np.unique(allLabels)).tolist()
        normalizedLabels = range(1,len(uniqueLabels)+1)
    
        if len(uniqueLabels) != len(normalizedLabels):
            print "ERROR: normalization could not complete"

        self.newLabelsAll[str(round(phi,4))] = [np.array(newLabels) for newLabels in self.newLabelsAll[str(round(phi,4))]]
        for fileInd in range(len(self.expListNames)):
            expName = self.expListNames[fileInd]
            for clusterInd in np.sort(np.unique(self.newLabelsAll[str(round(phi,4))][fileInd])):
                newLabel = normalizedLabels[uniqueLabels.index(clusterInd)]
                indicesToChange = np.where((self.newLabelsAll[str(round(phi,4))][fileInd]) == clusterInd)[0]
                self.newLabelsAll[str(round(phi,4))][fileInd][indicesToChange] = newLabel

        ## finalize labels and log file
        self.newLabelsAll[str(round(phi,4))] = [newLabels.tolist() for newLabels in self.newLabelsAll[str(round(phi,4))]]
        self._recreate_log_file(uniqueLabels,normalizedLabels)

    def _recreate_log_file(self,uniqueLabels,normalizedLabels):
        newLogFile = csv.writer(open(os.path.join(self.basedir,"results","FileMerge.log"),'w'))
        reader = csv.reader(open(os.path.join(self.basedir,"results","_FileMerge.log"),'r'))

        for linja in reader:
            if len(linja) > 6:
                newLabel = linja[5]
                if uniqueLabels.__contains__(newLabel):
                    normalizedLabel = normalizedLabels[uniqueLabels.index(newLabel)]
                    linja[5] = normalizedLabel
            newLogFile.writerow(linja)

    def _save_clusters(self,phi):
        '''
        save the aligned clusters to csv files 
        one for each file at each specified phi

        '''

        if os.path.isdir(os.path.join(self.basedir,'results')) == False:
            os.mkdir(os.path.join(self.basedir,'results'))
        if os.path.isdir(os.path.join(self.basedir,'results','alignments')) == False:
            os.mkdir(os.path.join(self.basedir,'results','alignments'))

        for fileName in self.expListNames:
            if re.search("copied_ref_file",fileName):
                  labelsFile = os.path.join(self.basedir,'results','alignments',"%s_%s.csv"%(self.refFile,re.sub("\.","",str(phi))))
            else:
                labelsFile = os.path.join(self.basedir,'results','alignments',"%s_%s.csv"%(fileName,re.sub("\.","",str(phi))))
            labelsWriter = csv.writer(open(labelsFile,'w'))
        
            fileInd = self.expListNames.index(fileName)
            labels = self.newLabelsAll[str(round(phi,4))][fileInd]
            for lab in labels:
                labelsWriter.writerow([lab])

    def _merge_clusters_in_reference(self,refFile,phi0):
        ## order the clusters such that the ones with the greatest number of elements are first
        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
        refFileData = self.expListData[refFileInd]
        sortedLabels = np.sort(np.unique(refFileLabels))

        sizesRefFile = []
        for clusterID in sortedLabels:
            sizesRefFile.append(np.where(refFileLabels == clusterID)[0].size)
        sizeOrderedLabels = sortedLabels[np.argsort(sizesRefFile)]
        sizeOrderedLabels = sizeOrderedLabels[::-1]

        matchResults = None

        alreadyRenamed = []
        for cluster1 in sizeOrderedLabels:
            for cluster2 in sizeOrderedLabels:

                if cluster1 == cluster2:
                    continue

                ## take events in the clusters and find their euclidean distance from their centers
                eventsRefFile1 = refFileData[np.where(refFileLabels==cluster1)[0],:]
                eventsRefFile2 = refFileData[np.where(refFileLabels==cluster2)[0],:]

                euclidDist1 = (eventsRefFile1 - eventsRefFile1.mean(axis=0))**2.0
                euclidDist1 = np.sqrt(euclidDist1.sum(axis=1))

                euclidDist2 = (eventsRefFile2 - eventsRefFile2.mean(axis=0))**2.0
                euclidDist2 = np.sqrt(euclidDist2.sum(axis=1))

                ## determine the number of events that overlap
                overlap1 = (eventsRefFile1 - eventsRefFile2.mean(axis=0))**2.0
                overlap1 = np.sqrt(overlap1.sum(axis=1))

                overlap2 = (eventsRefFile2 - eventsRefFile1.mean(axis=0))**2.0
                overlap2 = np.sqrt(overlap2.sum(axis=1))
                
                threshold1 = stats.norm.ppf(0.975,loc=euclidDist1.mean(),scale=euclidDist1.std())
                threshold2 = stats.norm.ppf(0.975,loc=euclidDist2.mean(),scale=euclidDist2.std())

                overlappingInds1 = np.where(overlap1<threshold2)[0]
                overlappingInds2 = np.where(overlap2<threshold1)[0]
                percentOverlap1 = float(len(overlappingInds1)) / float(np.shape(eventsRefFile1)[0])
                percentOverlap2 = float(len(overlappingInds2)) / float(np.shape(eventsRefFile2)[0])
                percentOverlap = np.max([percentOverlap1, percentOverlap2])

                ## minimum percent overlap testing for merge
                if phi0 >= percentOverlap:
                    continue

                ## handle clusters with multiple matches
                if alreadyRenamed.__contains__(str(cluster1)):
                    continue

                alreadyRenamed.append(str(cluster1))
                
                ## save the results
                results = np.array(([cluster1,cluster2, percentOverlap]))

                ## silvalue testing for merge
                clusterSilValue1 = self.silValues[self.expListNames[refFileInd]][str(cluster1)]
                clusterSilValue2 = self.silValues[self.expListNames[refFileInd]][str(cluster2)]

                if clusterSilValue1 < self.minMergeSilValue or clusterSilValue2 < self.minMergeSilValue:
                    if self.verbose == True:
                        print "INFO: skipping merge in reference -- silvalue" 
                    continue
 
                if matchResults == None:
                    matchResults = np.array(((results),))
                else:
                    matchResults = np.vstack((matchResults, results))
            
        ## merge the specified clusters
        if matchResults == None:
            return

        ## create a dict that contains a list of all percent overlaps for each cluster
        filteringDict = {}
        redundent = []
        mRows, mCols = np.shape(matchResults)
        for row in range(mRows):
            fResult = matchResults[row,:]

            # save results into dict
            cluster1 = int(fResult[0])
            cluster2 = int(fResult[1])
            silVal1 = self.silValues[self.expListNames[refFileInd]][str(cluster1)]
            silVal2 = self.silValues[self.expListNames[refFileInd]][str(cluster2)]
            pOverlap = fResult[2]

            orderedClusters = np.sort(np.array([cluster1,cluster2]))

            if redundent.__contains__((orderedClusters[0],orderedClusters[1])) == True:
                continue

            redundent.append((orderedClusters[0],orderedClusters[1]))

            if silVal1 < self.minMergeSilValue:
                pass
            elif filteringDict.has_key(cluster1):
                filteringDict[cluster1].append(pOverlap)
            else:
                filteringDict[cluster1] = [pOverlap]

            if silVal2 < self.minMergeSilValue:
                pass
            elif filteringDict.has_key(cluster2):
                filteringDict[cluster2].append(pOverlap)
            else:
                filteringDict[cluster2] = [pOverlap]

        ## loop through all labels    
        beenMatched = []
        for label in sortedLabels:
            matches = []

            ## find all clusters whose minimal overlap correspond to label
            for row in range(mRows):
                rowElements = matchResults[row,:]
                cluster1 = rowElements[0]
                cluster2 = rowElements[1]
                pOverlap = rowElements[2]

                if cluster1 != int(label) and cluster2 != int(label):
                    continue

                if cluster1 == int(label) and np.array(filteringDict[cluster1]).min() == pOverlap:
                    matches.append(cluster2)
                    
                if cluster2 == int(label) and np.array(filteringDict[cluster2]).min() == pOverlap:
                    matches.append(cluster1)

            for clustToChange in matches:
                indicesToChange = np.where((self.expListLabels[refFileInd]) == clustToChange)[0]
                if indicesToChange.size == 0:
                    continue
                if clustToChange < label:
                    continue

                if self.verbose == True:
                    print 'ref file changing %s to %s with %s elements and %s overlap'%(clustToChange,label,indicesToChange.size,rowElements[2])
                
                self.logFile.writerow([phi0,'within-ref',self.refFile,clustToChange,self.refFile,label,indicesToChange.size,rowElements[2],"NA"])
                self.expListLabels[refFileInd] = np.array(self.expListLabels[refFileInd])
                self.expListLabels[refFileInd][indicesToChange] = label
                self.expListLabels[refFileInd] = self.expListLabels[refFileInd].tolist()

    def _make_reference_comparisons(self,refFile,filteredResults,phi):
        ## given a reference cluster figure out which clusters match
        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
        refFileData = self.expListData[refFileInd]
        refLabels = np.sort(np.unique(refFileLabels))
  
      
        if filteredResults == None:
            print "INFO: no files merged in reference comparisions"
            return None

        try:
            frows, fcols = np.shape(filteredResults)
        except:
            frows = 0

        clusterCompares = {}
            
        for rowNum in range(frows):
            results = filteredResults[rowNum,:]

            if results[0] != refFileInd and results[1] != refFileInd:
                continue
    
            if results[0] == refFileInd:
                refCluster = results[2]
                altCluster = results[3]
                altFile = results[1]
                
            elif results[1] == refFileInd:
                refCluster = results[3]
                altCluster = results[2]
                altFile = results[0]

            if clusterCompares.has_key(refCluster) == False:
                clusterCompares[refCluster] = {'values': [results[4]],'file-cluster':[(int(altFile),int(altCluster))]}
            else:
                clusterCompares[refCluster]['values'].append(results[4])
                clusterCompares[refCluster]['file-cluster'].append((int(altFile),int(altCluster)))

        ## make decisions about merging for reference comparisons
        alreadyRenamed = []
        for key, item in clusterCompares.iteritems():
            key = int(key)

            count = -1
            for fileCluster in item['file-cluster']:
                count += 1
                altFile = fileCluster[0]
                altFileName =  self.expListNames[altFile]
                altFileLabels = self.expListLabels[altFile]
                altCluster = -1 * fileCluster[1]
                percentOverlap = item['values'][count]
                altFileClusters = np.sort(np.unique(altFileLabels)).tolist()
                altClusterInd = altFileClusters.index(fileCluster[1])

                ## make index changes based on minimum perscribed percent overlap
                if phi >= percentOverlap:
                    continue

                indicesToChange = np.where((self.newLabelsAll[str(round(phi,4))][altFile]) == altCluster)[0]
                
                ## before merging a cluster ensure the clusters silhouette value is > the minimum threshold
                clusterSilValue = self.silValues[altFileName][str(fileCluster[1])]  #altClusterInd
                
                if clusterSilValue < self.minMergeSilValue:
                    if self.verbose == True:
                        print '\t\tnot merging - cluster sil value < sil value threshold'
                    continue

                ## handle clusters with multiple matches
                fileClust = altFileName+"-"+str(altCluster)
                if alreadyRenamed.__contains__(fileClust):
                    continue

                alreadyRenamed.append(fileClust)
                
                ## log the comparisons to the reference file
                self.logFile.writerow([phi,'between-ref',altFileName,int(-1.0*altCluster-1.0),self.refFile,key,indicesToChange.size,percentOverlap,clusterSilValue])

                if self.verbose == True:
                    print '\tchanging %s to %s in file %s'%(altCluster,key,altFile), percentOverlap,clusterSilValue

                self.newLabelsAll[str(round(phi,4))][altFile][indicesToChange] = key

    def _filter_comparison_results(self,matchResults,refFile,phi,refComparison=True):
        ## go through the results and keep only the results that have values >0
        if matchResults == None:
            print "WARNING: skipping results filter -- matchResults empty"
            return None

        ## declare variables
        numRows, numCols = np.shape(matchResults)
        filteredResults = None
        totalNumClusters = 0
        matchDict = {}
        uniqueClusters = []

        ## preprae data for reference file comparisons
        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
       
        ## create a dict that contains a list of all percent overlaps for each cluster
        filteringDict = {}
        for row in range(numRows):
            fResult = matchResults[row,:]
            
            # only keep the comparisons with the reference file
            if refComparison == True and refFileInd not in [int(fResult[0]),int(fResult[1])]:
                continue
            if refComparison == False and refFileInd in [int(fResult[0]),int(fResult[1])]:
                continue

            # save results into dict
            key1 = "%s-%s"%(int(fResult[0]),int(fResult[2]))
            key2 = "%s-%s"%(int(fResult[1]),int(fResult[3]))
            silVal1 = self.silValues[self.expListNames[int(fResult[0])]][str(int(fResult[2]))]
            silVal2 = self.silValues[self.expListNames[int(fResult[1])]][str(int(fResult[3]))]
            pOverlap = fResult[4]

            ##if non-ref compare keep percent overlap
            if refComparison == False:
                if pOverlap < phi:
                    pass
                elif  silVal1 < self.minMergeSilValue:
                    pass
                elif filteringDict.has_key(key1):
                    filteringDict[key1].append(pOverlap)
                else:
                    filteringDict[key1] = [pOverlap]
                
                if pOverlap < phi:
                    pass
                elif silVal2 < self.minMergeSilValue:
                    pass
                elif filteringDict.has_key(key2):
                    filteringDict[key2].append(pOverlap)
                else:
                    filteringDict[key2] = [pOverlap]

            if refComparison == True:
                file1ClusterSize = self.sampleStats['n'][self.expListNames[int(fResult[0])]][str(int(fResult[2]))]
                file2ClusterSize = self.sampleStats['n'][self.expListNames[int(fResult[1])]][str(int(fResult[3]))]
                sizeSimilarity = np.abs(float(file1ClusterSize) - float(file2ClusterSize))

                if pOverlap < phi:
                    pass
                elif  silVal1 < self.minMergeSilValue:
                    pass
                elif filteringDict.has_key(key1):
                    filteringDict[key1].append(sizeSimilarity)
                else:
                    filteringDict[key1] = [sizeSimilarity]
            
                if pOverlap < phi:
                    pass
                elif silVal2 < self.minMergeSilValue:
                    pass
                elif filteringDict.has_key(key2):
                    filteringDict[key2].append(sizeSimilarity)
                else:
                    filteringDict[key2] = [sizeSimilarity]
            
        ## use filtering dictionary and threshold percent overlap to filter results    
        filteredResults = None
        for rowNum in range(numRows):
            result = matchResults[rowNum,:]

            # only keep the comparisons with the reference file
            if refComparison == True and refFileInd not in [int(result[0]),int(result[1])]:
                continue
            if refComparison == False and refFileInd in [int(result[0]),int(result[1])]:
                continue
          
            # find the cluster that is being compared to the reference
            if refComparison == True:
                if int(result[0]) == refFileInd:
                    key = "%s-%s"%(int(result[1]),int(result[3]))
                    silVal = self.silValues[self.expListNames[int(result[1])]][str(int(result[3]))]
                elif int(result[1]) == refFileInd:
                    key = "%s-%s"%(int(result[0]),int(result[2]))
                    silVal = self.silValues[self.expListNames[int(result[0])]][str(int(result[2]))]

                # discard if sil value fails
                if  silVal < self.minMergeSilValue:
                    continue            

                # discard results not above percent overlap
                pOverlap = result[4]
                if pOverlap < phi:
                    continue
            
                # discard results not equal to mminimum overlap
                #mimimalOverlap = np.array(filteringDict[key]).min()
                #if pOverlap != mimimalOverlap:
                #    continue
            
                file1ClusterSize = self.sampleStats['n'][self.expListNames[int(result[0])]][str(int(result[2]))]
                file2ClusterSize = self.sampleStats['n'][self.expListNames[int(result[1])]][str(int(result[3]))]
                sizeSimilarity = np.abs(float(file1ClusterSize) - float(file2ClusterSize))

                if sizeSimilarity != np.array(filteringDict[key]).min():
                    continue
                
            else:
                # discard results not above percent overlap
                pOverlap = result[4]
                if pOverlap < phi:
                    continue

            # save non discarded results
            if filteredResults == None:
                filteredResults = result
            else:
                filteredResults = np.vstack((filteredResults,result))

        return filteredResults


    def makePlotsSameAxis(self,expListNames,expListData,expListLabels,colors,centroids,showCentroids=True):
        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot(111)
        plotCount = -1
        plotMarkers = ["o","+","^","s"]
        plotDict = {}

        for c in range(len(expListNames)):
            plotCount += 1
            expData = expListData[c]
            labels = expListLabels[c]
            expName = expListNames[c]

            if plotCount == 0:
                visible = True
            else:
                visible = False

            x = expData[:,0]
            y = expData[:,1]

            plotDict[plotCount] = ax.scatter(x,y,color=colors[plotCount],s=self.markerSize,visible=visible)
            #ax.set_title("Case %s"%subplotCount)
            ax.set_xlim([0,14])
            ax.set_ylim([0,14])

        rax = plt.axes([0.15, 0.12, 0.15, 0.15])
        check = CheckButtons(rax, ('Case1', 'Case2', 'Case3','Case4'), (True, False, False, False))

        def func(label):
            if label == 'Case1': plotDict[0].set_visible(not plotDict[0].get_visible())
            elif label == 'Case2': plotDict[1].set_visible(not plotDict[1].get_visible())
            elif label == 'Case3': plotDict[2].set_visible(not plotDict[2].get_visible())
            elif label == 'Case4': plotDict[3].set_visible(not plotDict[3].get_visible())
            plt.draw()
        check.on_clicked(func)


    def show_plots(self):
        plt.show()
