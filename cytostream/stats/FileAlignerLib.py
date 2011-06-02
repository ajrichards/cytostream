#!/usr/bin/python


'''
library for file aligner related functions

'''
from __future__ import division
import sys,os,re,cPickle,time
import numpy as np
import scipy.stats as stats
from scipy.cluster.vq import whiten

from cytostream import NoGuiAnalysis
from scipy.spatial.distance import pdist, squareform
from cytostream.stats import SilValueGenerator, DistanceCalculator
from cytostream.stats import Bootstrapper, EmpiricalCDF,BootstrapHypoTest,GaussianDistn, kullback_leibler
from fcm.statistics.distributions import mvnormpdf


from FALib import _calculate_within_thresholds, event_count_compare, get_modes, relabel_template

class FileAlignerII():

    '''
    (1) calculate and save sample statistics
    (2) calculate and save silhouette values
    (3) determine noise
    (4) self alignment
    (5) create a template file
    (6) scan all files with template file

    '''

    def __init__(self,expListNames=[],expListData=[],expListLabels=None,phiRange=None,homeDir='.',
                 refFile=None,verbose=False,excludedChannels=[],isProject=False,noiseSubset=600,
                 modelRunID=None,distanceMetric='mahalanobis',medianTransform=True):

        ## declare variables
        self.expListNames = [expName for expName in expListNames]
        self.expListData = expListData
        self.phiRange = phiRange
        self.matchResults = None
        self.homeDir = homeDir
        self.verbose = verbose
        self.modelRunID = modelRunID
        self.isProject = isProject
        self.noiseSubset = noiseSubset

        ## control variables 
        self.medianTransform = medianTransform
        self.silValueEstimateSample = 500
        self.distanceMetric = distanceMetric
        self.globalScoreDict = {}
        self.newLabelsAll = {}
        self.modelType = 'components'
        self.noiseClusters = {}
        self.referenceOverlap = 1e7
        self.modeLabels = {}

        self.overlapMetric = 'eventcount'
        if self.overlapMetric not in ['kldivergence','eventcount']:
            print "ERROR: bad overlapMetric in FileAligner"

        if self.verbose == True:
            print "Initializing file aligner"

        ## handle labels
        if expListLabels != None:
            self.expListLabels = [np.array([int(label) for label in labelList]) for labelList in expListLabels]
        else:
            self.expListLabels = None

        ## error check
        if self.expListLabels == None and modelRunID == None:
            print "ERROR: if expListLabels are not specified then modelRunID must be specified"
            return None

        ## making dir tree
        if os.path.isdir(self.homeDir) == False:
            print "INPUT ERROR: FileAligner.py -- baseDir does not exist"
            return None

        self.make_dir_tree()

        ## handle exp data
        if type(expListData) != type([]):
            print "ERROR: FileAligner: expListData must be of type list"
            return None
        elif len(expListData) == 0 and self.homeDir == None:
            print "ERROR: without expListData a homDir must be specified"
            return None
        elif len(expListData) == 0 and self.modelRunID == None:
            print "ERROR: without expListData a modelRunID must be specified"
            return None
        elif self.homeDir != None:
            self._init_project()
        else:
            self.expListData = [expData[:,:].copy() for expData in expListData]

        ## handle exluded channels
        modelLog = self.nga.get_model_log(self.expListNames[0],self.modelRunID)

        if modelLog != None:
            subsample = modelLog['subsample']
            events = self.nga.get_events(self.expListNames[0],subsample)
        else:
            events = self.expListData[0]

        self.numChannels = np.shape(events)[1]
        if excludedChannels != None:
            self.includedChannels = list(set(range(self.numChannels)).difference(set(excludedChannels)))
        else:
            self.includedChannels = range(self.numChannels)

        ## handle phi range
        if self.phiRange == None:
            self.phiRange = np.array([0.4,0.8])
        if type(self.phiRange) == type([]):
            self.phiRange = np.array(self.phiRange)
        if type(self.phiRange) != type(np.array([])):
            print "INPUT ERROR: phi range is not a list or np.array", type(self.phiRange)
            return None

    def run(self,filterNoise=True):
        ## get sample statistics
        if self.verbose == True:
            print "...getting sample statistics"
        self.sampleStats = self.get_sample_statistics()

        ## get sil values
        if self.verbose == True:
            print "...getting silhouette values"
        self.silValues = self.get_silhouette_values(subsample=self.noiseSubset)

        if filterNoise == True:
            ## use bootstrap to determine noise clusters
            if self.verbose == True:
                print "...bootstrapping to find noise clusters\n"

            clustersList = []
            clustersIDList = []
            for key, item in self.silValues.iteritems():
                for cluster, value in item.iteritems():
                    clustersList.append(float(value))
                    clustersIDList.append(key+"#"+cluster)

            clustersList = np.array(clustersList)
            boots = Bootstrapper(clustersList)
            bootResults = boots.get_results()
        
            ## collect noise clusters
            self.noiseClusters = {}
            lowerLimit = bootResults['meanCI'][0]
            for c in range(len(clustersList)):
                if lowerLimit > clustersList[c]:
                    fname,cname = re.split("#",clustersIDList[c])
                    if self.noiseClusters.has_key(fname) == True:
                        self.noiseClusters[fname].append(cname)
                    else:
                        self.noiseClusters[fname] = [cname]

        ## get overlap thresholds
        if self.verbose == True:
            print "\n...calculating within thresholds"
        self.withinThresholds = _calculate_within_thresholds(self)

        ## self alignment
        if self.verbose == True:
            print "\n...performing self alignment"
        self.selfAlignment = self.run_self_alignment()

        ## finish template file according to phi
               
        ### loop through each phi ###
        phi = self.phiRange[0]
        if self.verbose == True:
            print "...getting modes %s phi"%(phi)
       
        nonNoiseIndices = np.where(self.selfAlignment['results'] > 0)[0]
        nonNoiseResults = self.selfAlignment['results'][nonNoiseIndices]
        nonNoiseFiles = self.selfAlignment['files'][nonNoiseIndices]
        nonNoiseClusters = self.selfAlignment['clusters'][nonNoiseIndices]
        phiIndices = np.where(nonNoiseResults >= phi)[0]
        newLabels = get_modes(self,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters)
        self.modeLabels[str(phi)] = newLabels

        if self.verbose == True:
            print "...getting sample statistics again"

        sampleStatsPhi = self.get_sample_statistics(allLabels=self.modeLabels[str(phi)])

        ## get overlap thresholds
        if self.verbose == True:
            print "\n...calculating within thresholds"
        withinThresholdsPhi = _calculate_within_thresholds(self,allLabels=self.modeLabels[str(phi)])
        
        ## getting template file
        if self.verbose == True:
            print "...creating template file"
            
        templateAlignment = self.create_template_file(phi,thresholds=withinThresholdsPhi,sampleStats=sampleStatsPhi)
        print templateAlignment['results']
        nonNoiseIndices = np.where(templateAlignment['results'] > 0)[0]
        nonNoiseResults = templateAlignment['results'][nonNoiseIndices]
        nonNoiseFiles = templateAlignment['files'][nonNoiseIndices]
        nonNoiseClusters = templateAlignment['clusters'][nonNoiseIndices]
        phiIndices = np.where(nonNoiseResults >= phi)[0]
        #templateLabels = relabel_template(self,phiIndices,nonNoiseResults,nonNoiseFiles,nonNoiseClusters)
        
    def _init_project(self):
        self.nga = NoGuiAnalysis(self.homeDir,loadExisting=True)
        self.nga.set("results_mode",self.modelType)
        if self.expListNames == None:
            self.expListNames = self.nga.get_file_names()
        self.fileChannels = self.nga.get('alternate_channel_labels')

    def make_dir_tree(self):
        if self.verbose == True and os.path.isdir(os.path.join(self.homeDir,'alignfigs')) == True:
            print "INFO: deleting old files for file aligner"

        dirs = ['results','alignfigs']
        for diry in dirs:
            if os.path.isdir(os.path.join(self.homeDir,diry)) == False:
                os.mkdir(os.path.join(self.homeDir,diry))
            
        if os.path.isdir(os.path.join(self.homeDir,'alignfigs')) == True:
            ## clean out figures dir
            for item1 in os.listdir(os.path.join(self.homeDir,'alignfigs')):
                if os.path.isdir(os.path.join(self.homeDir,'alignfigs',item1)) == True:
                    for item2 in os.listdir(os.path.join(self.homeDir,'alignfigs',item1)):
                        os.remove(os.path.join(self.homeDir,'alignfigs',item1,item2))
                else:
                    os.remove(os.path.join(self.homeDir,'alignfigs',item1))
            
            ## clean out relevant results
            if os.path.isdir(os.path.join(self.homeDir,'results','alignments')) == True:
                for item1 in os.listdir(os.path.join(self.homeDir,'results','alignments')):
                    os.remove(os.path.join(self.homeDir,'results','alignments',item1))
                
            ## remove old log files 
            if os.path.isfile(os.path.join(self.homeDir,"results","_FileMerge.log")) == True:
                os.remove(os.path.join(self.homeDir,"results","_FileMerge.log"))
            if os.path.isfile(os.path.join(self.homeDir,"results","_FileMerge.log")) == True:
                os.remove(os.path.join(self.homeDir,"results","_FileMerge.log"))
            if os.path.isfile(os.path.join(self.homeDir,"results","alignments.log")) == True:
                os.remove(os.path.join(self.homeDir,"results","alignments.log"))

        ## ensure directories are present
        if os.path.isdir(os.path.join(self.homeDir,"results")) == False:
            os.mkdir(os.path.join(self.homeDir,"results"))            
        if os.path.isdir(os.path.join(self.homeDir,"results","alignments")) == False:
            os.mkdir(os.path.join(self.homeDir,"results","alignments"))
        if os.path.isdir(os.path.join(self.homeDir,"alignfigs")) == False:
            os.mkdir(os.path.join(self.homeDir,"alignfigs"))

    def get_labels(self,selectedFile):

        if selectedFile not in self.expListNames:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return

        if self.expListLabels == None:
            statModel, labels = self.nga.get_model_results(selectedFile,self.modelRunID,self.modelType)
            return labels
        else:
            fileInd = self.expListNames.index(selectedFile)
            return self.expListLabels[fileInd]

    def get_events(self,selectedFile):

        if selectedFile not in self.expListNames:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return

        modelLog = self.nga.get_model_log(selectedFile,self.modelRunID)

        if modelLog != None:
            subsample = modelLog['subsample']
            events = self.nga.get_events(selectedFile,subsample)
            return events[:,self.includedChannels]
        else:
            fileInd = self.expListNames.index(selectedFile)
            return self.expListData[fileInd][:,self.includedChannels]

    def get_sample_statistics(self,allLabels=None):
        centroids, variances, numClusts, numDataPoints = {},{},{},{}
        centroidList = {}
        centroidListIDs = {}
        clusterDists = {}
        
        for expInd in range(len(self.expListNames)):
            expName = self.expListNames[expInd]
            centroids[expName] = {}
            variances[expName] = {}
            numClusts[expName] = None
            numDataPoints[expName] = {}
            centroidList[expName] = None
            centroidListIDs[expName] = []
            clusterDists[expName] = {}

        for expInd in range(len(self.expListNames)):
            expName = self.expListNames[expInd]
            expData = self.get_events(expName)
            if allLabels == None:
                expLabels = self.get_labels(expName)
            else:
                expLabels = allLabels[expInd]

            if self.verbose == True:
                print "\r\t%s/%s files"%(expInd+1, len(self.expListNames)),

            for cluster in np.sort(np.unique(expLabels)):
                clusterInds =np.where(expLabels==cluster)[0]
                centroid = expData[clusterInds,:].mean(axis=0)
                centroids[expName][str(cluster)] = centroid
                #print 'debug', np.shape(expData[clusterInds,:]), np.cov(expData[clusterInds,:].T).shape, expData[clusterInds,:].var(axis=0).shape
                variances[expName][str(cluster)] = np.cov(expData[clusterInds,:].T)
                numDataPoints[expName][str(cluster)] = len(clusterInds)
                if centroidList[expName] == None:
                    centroidList[expName] = np.array([centroid])
                else:
                    centroidList[expName] = np.vstack([centroidList[expName],centroid])
        
                centroidListIDs[expName].append(cluster)

            numClusts[expName] = len(np.unique(expLabels))

            ## save the threshold distance for comparisons based on mean euclidean distance
            clustDists = pdist(centroidList[expName],'euclidean')
            clustDists = squareform(clustDists)
            means = clustDists.mean(axis=0)
            stds  = clustDists.std(axis=0)

            for cid in range(len(centroidListIDs[expName])):
                cID = centroidListIDs[expName][cid]
                threshold = stats.norm.ppf(0.6,loc=means[cid],scale=stds[cid])
                clusterDists[expName][str(cID)] = threshold
                #print expName, cID, means[cid], stds[cid], threshold

        if self.verbose == True:
            print "\n"

        return {'mus':centroids,'sigmas':variances,'k':numClusts,'n':numDataPoints,'dists':clusterDists}

    def get_silhouette_values(self,subsample=None):
        silValues = {}
        silValuesElements = {}
        for expName in self.expListNames:
            silValues[expName] = {}

        ## create subset if data for large data sets 
        subsetExpData = []
        subsetExpLabels = []

        if subsample != None:
            for expInd in range(len(self.expListNames)):
                expName = self.expListNames[expInd]
                expData =  self.get_events(expName)
                expLabels = self.get_labels(expName)
                newIndices = []

                totalInds = 0
                for cluster in np.sort(np.unique(expLabels)):
                    clusterInds = np.where(expLabels==cluster)[0]
                    totalInds += len(clusterInds)

                    if len(clusterInds) > subsample:
                        percentTotal = float(len(clusterInds)) / float(len(expLabels)) 
                        randSelected = clusterInds[np.random.randint(0,len(clusterInds),subsample)]
                        newIndices += randSelected.tolist()
                    else:
                        newIndices += clusterInds.tolist()

                ## save indices and data
                subsetExpData.append(expData[newIndices,:])
                subsetExpLabels.append(expLabels[newIndices])

        ## calculate the silvalues for each file and the subsampled clusters
        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            
            if subsample != None:
                fileData = subsetExpData[c]
                fileLabels = subsetExpLabels[c]
            else:
                fileData = self.get_events(expName)
                fileLabels = self.get_labels(expName)

            fileClusters = np.sort(np.unique(fileLabels))    
    
            if self.verbose == True:
                print "\r\t%s/%s files"%(c+1, len(self.expListNames)),
            silValuesElements[expName] = self._get_silhouette_values(fileData,fileLabels)
        
            ## save only sil values for each cluster
            for clusterID in fileClusters:
                clusterElementInds = np.where(fileLabels == clusterID)[0]
                clusterSilValue = silValuesElements[expName][clusterElementInds].mean()
                silValues[expName][str(clusterID)] = clusterSilValue
                del clusterElementInds

        if self.verbose == True:
            print "\n"

        return silValues

    def _get_silhouette_values(self,mat,labels):
        svg = SilValueGenerator(mat,labels)
        return svg.silValues

    def create_log_file(self):
        ''' 
        create a log file to document cluster changes
        each log is specific to a give phi
        '''

        if self.covariateID == None:
            self.logFile = csv.writer(open(os.path.join(self.baseDir,"results","_FileMerge.log"),'wa'))
        else:
            self.logFile = csv.writer(open(os.path.join(self.baseDir,"results","_FileMerge_%s.log"%(self.covariateID)),'wa'))
        self.logFile.writerow(["expListNames",re.sub(",",";",re.sub("\[|\]|'","",str(self.expListNames)))])
        self.logFile.writerow(["refFile",self.refFile])
        self.logFile.writerow(["silThresh",self.minMergeSilValue])
        self.logFile.writerow(['phi','algorithmStep','fileSource','OldLabel','fileTarget','newLabel','numEventsChanged','percentoverlap','silValue']) 

    def run_self_alignment(self):
        totalClusters = np.array([(float(n)*(float(n)-1.0)) / 2.0 for n in self.sampleStats['k'].itervalues()]).sum()
        alignResults = np.zeros((totalClusters),) -1
        alignResultsFiles = np.zeros((totalClusters),) -1
        alignResultsClusters = np.array(['None'],dtype='|S7').repeat(totalClusters)

        clustCount = -1
        fileCount = 0

        for fileName in self.expListNames:
            fileCount += 1
            fileLabels = self.get_labels(fileName)
            fileClusters = np.sort(np.unique(fileLabels))
            fileData = self.get_events(fileName)
            
            if self.verbose == True:
                print "\r\t%s/%s files"%(fileCount,len(self.expListNames)),
          
            for ci in range(len(fileClusters)):
                clusterI = fileClusters[ci]
                clusterEventsI = fileData[np.where(fileLabels==clusterI)[0],:]
                clusterMuI = self.sampleStats['mus'][fileName][str(clusterI)] 

                for cj in range(len(fileClusters)):
                    clusterJ = fileClusters[cj]
                    ## do not compare cluster to itself
                    if ci <= cj:
                        continue
                    clustCount+=1

                    ## check for noise label
                    if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterI)):
                        continue
                    if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterJ)):
                        continue

                    ## check that the centroids are at least a reasonable distance apart                    
                    clusterMuJ = self.sampleStats['mus'][fileName][str(clusterJ)] 
                    eDist = pdist([clusterMuI,clusterMuJ],'euclidean')[0]
                    threshold1 = self.sampleStats['dists'][fileName][str(clusterI)]
                    threshold2 = self.sampleStats['dists'][fileName][str(clusterJ)]

                    #print fileName, clusterI, clusterJ, eDist, threshold1, threshold2
                    if eDist > threshold1 or eDist > threshold2:
                        continue
                    
                    clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]
                    overlap1 = event_count_compare(self,clusterEventsI,clusterEventsJ,fileName,clusterJ)
                    overlap2 = event_count_compare(self,clusterEventsJ,clusterEventsI,fileName,clusterI)
                    overlap = np.max([overlap1, overlap2])
                    alignResults[clustCount] = overlap

                    #if overlap > 0:
                    #    print fileName, clusterI, clusterJ, klDist.sum(),overlap

                    ## save results
                    alignResultsFiles[clustCount] = self.expListNames.index(fileName)
                    alignResultsClusters[clustCount] = "%s#%s"%(clusterI,clusterJ)
            
        if self.verbose == True:
            print "\n"

        ## integrity check
        if int(totalClusters) != int(clustCount + 1):
            print "ERROR: FileAlingerLib failed integrity check clustCount",totalClusters, clustCount

        return {'results':alignResults,'files':alignResultsFiles,'clusters':alignResultsClusters}

    def create_template_file(self,phi,thresholds=None,sampleStats=None):
   
        ## find file with fewest non-noise clusters
        fileWithMinNumClusters = None
        minClusts = np.inf

        if sampleStats == None:
            sampleStats = self.sampleStats

        if thresholds == None:
            thresholds = self.withinThresholds

        for fileIndex in range(len(self.expListNames)):
            fileName = self.expListNames[fileIndex]
            noiseClusters = 0
        
            ## check for the number of noise clusters
            if self.noiseClusters.has_key(fileName):
                noiseClusters = len(self.noiseClusters[fileName])

            fileLabels = self.modeLabels[str(phi)][fileIndex]
            fileClusters = np.sort(np.unique(fileLabels))
            fileClusterNumber = len(fileClusters) - noiseClusters

            if fileClusterNumber < minClusts:
                minClusts = fileClusterNumber
                fileWithMinNumClusters = fileName

        ## create a copy of file to start template
        fileWithMinNumClustersInd = self.expListNames.index(fileWithMinNumClusters)
        templateData = self.get_events(fileWithMinNumClusters)
        templateLabels = self.modeLabels[str(phi)][fileWithMinNumClustersInd]

        ## remove noise clusters from file
        if self.noiseClusters.has_key(fileWithMinNumClusters):
            noiseInds = np.array([])
            for cid in self.noiseClusters[fileWithMinNumClusters]:
                noiseInds = np.hstack([noiseInds, np.where(templateLabels==int(cid))[0]])
            nonNoiseInds = list(set(range(len(templateLabels))).difference(set(noiseInds)))
            templateData = templateData[nonNoiseInds,:]
            templateLabels = templateLabels[nonNoiseInds,:]

        ## setup save variables
        templateClusters = np.sort(np.unique(templateLabels))
        totalClusters = np.array([(float(n)*(float(n)-1.0)) / 2.0 for n in self.sampleStats['k'].itervalues()]).sum()
        totalClusters = totalClusters + (len(templateClusters)*(len(templateClusters) - 1.0)) / 2.0 
        alignResults = np.zeros((totalClusters),) -1
        alignResultsFiles = np.zeros((totalClusters),) -1
        alignResultsClusters = np.array(['None'],dtype='|S7').repeat(totalClusters)

        ## more variables
        fileCount = 0
        clustCount = -1
        newClusterCount = 0
        newClusterData = None
        newClusterLabels = None
        appearedTwice = []

        ## align template to all other files
        for fileInd in range(len(self.expListNames)):
            fileName = self.expListNames[fileInd]
            fileCount += 1
            fileLabels = self.modeLabels[str(phi)][fileInd]
            fileClusters = np.sort(np.unique(fileLabels))
            fileData = self.get_events(fileName)

            if self.verbose == True:
                print "\r\t%s/%s files"%(fileCount,len(self.expListNames)),
                      
            for ci in range(len(templateClusters)):
                clusterI = templateClusters[ci]
                templateEvents = templateData[np.where(templateLabels==clusterI)[0],:]
                clusterMuI = templateEvents.mean(axis=0)

                for cj in range(len(fileClusters)):
                    clusterJ = fileClusters[cj]
                    ## check for noise label
                    if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterJ)):
                        continue

                    if ci <= cj:
                        continue

                    clustCount += 1

                    ## check that the centroids are at least a reasonable distance apart                    
                    #clusterMuJ = sampleStats['mus'][fileName][str(clusterJ)] 
                    #eDist = pdist([clusterMuI,clusterMuJ],'euclidean')[0]
                    #threshold2 = sampleStats['dists'][fileName][str(clusterJ)]

                    #if eDist > threshold2:
                    #    continue
                    
                    clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]
                    overlap = event_count_compare(self,templateEvents,clusterEventsJ,fileName,clusterJ,thresholds=thresholds)

                    if overlap > phi:
                        continue

                    ## scan against the other soon to be new clusters
                    isNew = True
                    if newClusterLabels != None:
                        newIDs = np.sort*np.unique(newClusterLabels))
                        for nid in newIDs:
                            savedEvents = newClusterData[np.where(newClusterLabel) == nid][0]
                            overlap = event_count_compare(self,savedEvents,clusterEventsJ,fileName,clusterJ,thresholds=thresholds)
                            if overlap < phi:
                                appearedTwice.append(nid)
                                ifNew = False
                    
                    if isNew == False:
                        continue

                    ## add to newClusters
                    newClusterCount += 1
                    if newClusterData == None:
                        newClusterData = clusterEventsJ
                        newClusterLabels = np.array([newClusterCount]).repeat(clusterEventsJ.shape[0])
                    else:
                        newClusterData = np.vstack([newClusterData,clusterEventsJ])
                        newClusterLabels = np.hstack([newClusterLabels, np.array([newClusterCount]).repeat(clusterEventsJ.shape[0])])
                    print newClusterData.shape, newClusterLabels.shape


                    #alignResults[clustCount] = overlap
                    ## save results
                    #alignResultsFiles[clustCount] = self.expListNames.index(fileName)
                    #alignResultsClusters[clustCount] = "%s#%s"%(clusterI,clusterJ)

        self.templateData = templateData
        self.templateLabels = templateLabels
        return {'results':alignResults,'files':alignResultsFiles,'clusters':alignResultsClusters}
