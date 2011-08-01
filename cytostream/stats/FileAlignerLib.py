#!/usr/bin/python


'''
library for file aligner related functions

'''
from __future__ import division
import sys,os,re,cPickle,time,csv,datetime
import numpy as np
import scipy.stats as stats
from scipy.cluster.vq import whiten
from multiprocessing import Pool, cpu_count

from cytostream import NoGuiAnalysis
from scipy.spatial.distance import pdist, squareform
from cytostream.stats import DistanceCalculator
from cytostream.stats import Bootstrapper, EmpiricalCDF,BootstrapHypoTest,GaussianDistn, kullback_leibler
from cytostream.tools import get_all_colors,get_master_label_list
from fcm.statistics.distributions import mvnormpdf
import matplotlib.pyplot as plt
from cytostream.stats import _calculate_within_thresholds, event_count_compare, get_modes, get_alignment_labels
from cytostream.stats import calculate_intercluster_score, pool_compare_scan, pool_compare_self
from cytostream.stats import get_alignment_scores,get_silhouette_values
from cytostream.stats import scale, find_noise

class FileAligner():

    '''
    (1) calculate and save sample statistics
    (2) calculate and save silhouette values
    (3) determine noise
    (4) self alignment
    (5) create a template file
    (6) scan all files with template file

    '''

    def __init__(self,templateFile,expListNames,expListLabels,expListData=[],phiRange=[0.2,0.6],homeDir='.',alignmentDir='alignment',
                 refFile=None,verbose=False,excludedChannels=[],isProject=False,dirClean=True,noiseSample=2000,
                 modelRunID=None,distanceMetric='mahalanobis',medianTransform=False,useSavedNoise=True):

        ## declare variables
        self.expListNames = [expName for expName in expListNames]
        self.expListData = expListData
        self.phiRange = phiRange
        self.phi2 = 0.95
        self.matchResults = None
        self.homeDir = homeDir
        self.verbose = verbose
        self.modelRunID = modelRunID
        self.isProject = isProject
        self.noiseSample = noiseSample
        self.alignmentDir = alignmentDir
        self.dirClean = dirClean
        self.templateData,self.templateLabels = templateFile 

        ## control variables 
        self.medianTransform = medianTransform
        self.distanceMetric = distanceMetric
        self.globalScoreDict = {}
        self.newLabelsAll = {}
        self.modelType = 'components'
        self.noiseClusters = {}
        self.modeNoiseClusters = {}
        self.modeLabels = {}
        self.alignLabels = {}
        self.minNumEvents = 3

        if self.verbose == True:
            print "Initializing file aligner"

        ## handle saved noise
        if useSavedNoise == True:
            if os.path.exists(os.path.join(self.homeDir,'results','noiseClusters.pickle')) == False:
                print "WARNING: FileAligner trying to used saved noise clusters when they do not exist"
                self.savedNoise = None
            tmp = open(os.path.join(self.homeDir,'results','noiseClusters.pickle'),'r')
            self.savedNoise = cPickle.load(tmp)
            tmp.close()
        else:
            self.savedNoise = None

        ## begin time count
        self.timeBegin = time.time()

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

        ## prepare for logging and results storage
        self.make_dir_tree()
        self.create_log_files()

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

    def run(self,evaluator='rank'):
        ## get sample statistics
        if self.verbose == True:
            print "...getting sample statistics"
        self.sampleStats = self.get_sample_statistics()

        ## get sil values
        if self.savedNoise != None:
            if self.verbose == True:
                print "...getting silhouette values"
            allEvents = [self.get_events(expName) for expName in self.expListNames]
            allLabels = [self.get_labels(expName) for expName in self.expListNames]
            self.silValues = get_silhouette_values(allEvents,allLabels,subsample=self.noiseSample,
                                                   minNumEvents=self.minNumEvents)
        ## filter the noise
        if self.verbose == True:
            print "...getting noise clusters"
        self.noiseClusters = {}
        
        if self.savedNoise == None:
            for fileInd in range(len(self.expListNames)):
                expName = self.expListNames[fileInd]
                mat = self.get_events(expName)
                labels = self.get_labels(expName)
                noiseClusters = find_noise(mat,labels,silValues=self.silValues[str(fileInd)],minNumEvents=self.minNumEvents)
                self.noiseClusters[expName] = noiseClusters
        else:
            for fileInd in range(len(self.expListNames)):
                expName = self.expListNames[fileInd]
                self.noiseClusters[expName] = self.savedNoise[fileInd]
            
        ## get overlap thresholds
        if self.verbose == True:
            print "\n...calculating within thresholds"
        self.withinThresholds = _calculate_within_thresholds(self)

        print "noise", self.noiseClusters

        ### loop through each phi ###
        for phi in self.phiRange:
            ## scan files with template
            if self.verbose == True:
                print "...scanning files with template"

            alignment = self.scan_files_with_template(phi,thresholds=self.withinThresholds,sampleStats=self.sampleStats)
            aLabels = get_alignment_labels(self,alignment,phi,evaluator=evaluator)
            self.alignLabels[str(phi)] = aLabels
    
            ## save labels
            tmp =  open(os.path.join(self.homeDir,self.alignmentDir,"alignLabels_%s.pickle"%(phi)),'w')
            cPickle.dump(aLabels,tmp)
            tmp.close()

            ## calculate and save global alignment score
            if self.verbose == True:
                print "...calculating scores"

            allEvents = [self.get_events(expName) for expName in self.expListNames]
            silValuesPhi = get_silhouette_values(allEvents,aLabels,subsample=self.noiseSample,
                                                 minNumEvents=self.minNumEvents)

            numTemplateClusters = len(np.unique(self.templateLabels))

            ## calculate silhouette value for product score
            alignedSampleStatsPhi = self.get_sample_statistics(allLabels=self.alignLabels[str(phi)])
            fileMeans = []
            productScore = 0
            masterLabelList = get_master_label_list(aLabels)

            for fileInd in range(len(self.expListNames)):
                fileName = self.expListNames[fileInd]
                fileSilVals = []
                fileInd = self.expListNames.index(fileName)
                            
                for cid in masterLabelList:
                    if cid < 0:
                        continue

                    if silValuesPhi[str(fileInd)].has_key(str(cid)) == False or alignedSampleStatsPhi['n'][fileName].has_key(str(cid)) == False:
                        continue
                    fileSilVals += [silValuesPhi[str(fileInd)][str(cid)]] * alignedSampleStatsPhi['n'][fileName][str(cid)]
                    
                _fileMean = np.array(fileSilVals).mean()
                fileMeans.append(_fileMean)

            ## get matches for product score                
            totalPossibleMatches = (float(len(self.expListNames)) * float(len(masterLabelList))) - float(len(masterLabelList)) 

            totalMatches = 0
            for cid in masterLabelList:
                clusterMagScore = -1
                for fileInd in range(len(self.expListNames)):
                    uniqueLabs = np.unique(aLabels[fileInd])

                    if cid in uniqueLabs:
                        clusterMagScore+=1

                if clusterMagScore < 1:
                    continue

                totalMatches+=clusterMagScore

            normalizedMatchScore = totalMatches / totalPossibleMatches
            silValue = scale(np.array(fileMeans).mean(),(-1,1),(0,1))
            productScore = normalizedMatchScore * silValue

            print evaluator, phi, normalizedMatchScore, silValue, productScore
            self.alignmentScores.writerow([phi,numTemplateClusters,silValue,normalizedMatchScore,productScore])
            
            ## save a copy of the template file
            if os.path.isdir(os.path.join(self.homeDir,'figs','templates')) == False:
                os.mkdir(os.path.join(self.homeDir,'figs','templates'))
            self.globalScoreDict[str(phi)] = productScore
            figName = os.path.join(self.homeDir,'figs','templates','template_figure_%s_%s.png'%(evaluator,re.sub("\.","",str(phi))))

        self.timeEnd = time.time()
        timeTaken = str(datetime.timedelta(seconds=round(self.timeEnd-self.timeBegin,6)))
        self.alignmentLog.writerow(['time_taken',timeTaken])
        print 'runTime (hh:mm:ss)',timeTaken

    def _init_project(self):
        self.nga = NoGuiAnalysis(self.homeDir,loadExisting=True)
        self.nga.set("results_mode",self.modelType)
        if self.expListNames == None:
            self.expListNames = self.nga.get_file_names()
        self.fileChannels = self.nga.get('alternate_channel_labels')

        #print "using %s files"%len(self.expListNames)

    def make_dir_tree(self):
        if self.verbose == True and os.path.isdir(os.path.join(self.homeDir,'alignfigs')) == True:
            print "INFO: deleting old files for file aligner"

        dirs = ['results',self.alignmentDir,os.path.join('figs',self.alignmentDir)]
        for diry in dirs:
            if os.path.isdir(os.path.join(self.homeDir,diry)) == False:
                os.mkdir(os.path.join(self.homeDir,diry))
            
        if os.path.isdir(os.path.join(self.homeDir,self.alignmentDir)) == True and self.dirClean == True:
            ## clean out figures dir
            for item1 in os.listdir(os.path.join(self.homeDir,self.alignmentDir)):
                if os.path.isdir(os.path.join(self.homeDir,self.alignmentDir,item1)) == True:
                    for item2 in os.listdir(os.path.join(self.homeDir,self.alignmentDir,item1)):
                        os.remove(os.path.join(self.homeDir,self.alignmentDir,item1,item2))
                else:
                    os.remove(os.path.join(self.homeDir,self.alignmentDir,item1))
            
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

    def get_template_data(self):

        events = self.templateData[:,self.includedChannels]

        if self.medianTransform == True:
            events = events - np.median(events,axis=0) + 5000

        return events

    def get_events(self,selectedFile):

        if selectedFile not in self.expListNames:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return

        modelLog = self.nga.get_model_log(selectedFile,self.modelRunID)

        if modelLog != None:
            subsample = modelLog['subsample']
            events = self.nga.get_events(selectedFile,subsample)
            events = events[:,self.includedChannels]
        else:
            fileInd = self.expListNames.index(selectedFile)
            events = self.expListData[fileInd][:,self.includedChannels]

        if self.medianTransform == True:
            events = events - np.median(events,axis=0) + 5000

        return events

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
            expData = self.get_events(expName)
            if allLabels == None:
                expLabels = self.get_labels(expName)
            else:
                expLabels = allLabels[expInd]

            for cluster in np.sort(np.unique(expLabels)):
                clusterInds =np.where(expLabels==cluster)[0]

                if len(clusterInds) < self.minNumEvents:
                    centroids[expName][str(cluster)] = None
                    variances[expName][str(cluster)] = None
                    continue

                centroid = expData[clusterInds,:].mean(axis=0)
                centroids[expName][str(cluster)] = centroid
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

        return {'mus':centroids,'sigmas':variances,'k':numClusts,'n':numDataPoints,'dists':clusterDists}

    def create_log_files(self):
        ''' 
        create a log file to document cluster changes
        each log is specific to a give phi
        '''

        ## set up the log files
        self.alignmentScores = csv.writer(open(os.path.join(self.homeDir,self.alignmentDir,"AlignmentScores.log"),'w'))
        self.alignmentScores.writerow(["phi","num_template_clusters","silhouette_val,normalized_matches,product_score"])
        self.alignmentLog = csv.writer(open(os.path.join(self.homeDir,self.alignmentDir,"Alignment.log"),'w'))
        
    def run_self_alignment(self):
        pool = Pool(processes=cpu_count(),maxtasksperchild=1)
        fileDataList = []
        fileLabelsList = []
        fileClusterList = []

        for fileName in self.expListNames:
            fileDataList.append(self.get_events(fileName))
            fileLabelsList.append(self.get_labels(fileName))
            fileClustersList = [np.sort(np.unique(fl)) for fl in fileLabelsList]
            
        n = len(self.expListNames)
        args = zip(self.expListNames,
                   fileDataList,
                   fileLabelsList,
                   fileClustersList,
                   [self.sampleStats]*n,
                   [self.noiseClusters]*n,
                   [self.withinThresholds]*n,
                   [self.minNumEvents]*n)

        results = pool.map(pool_compare_self,args)
        
        ## reformat the results
        alignResults = []
        alignResultsFiles = []
        alignResultsClusters = []

        for fileInd in range(len(self.expListNames)):
            fileName = self.expListNames[fileInd]
            fileResults = results[fileInd]
            if len(fileResults[0]) == 0:
                continue

            alignResults += fileResults[0]
            alignResultsFiles += [self.expListNames.index(fr) for fr in fileResults[1]]
            alignResultsClusters += fileResults[2]

        return {'results':alignResults,'files':alignResultsFiles,'clusters':alignResultsClusters}

    def scan_files_with_template(self,phi,thresholds=None,sampleStats=None):

        pool = Pool(processes=cpu_count(),maxtasksperchild=1)
   
        ## find file with fewest non-noise clusters
        fileWithMinNumClusters = None
        minClusts = np.inf

        if sampleStats == None:
            sampleStats = self.sampleStats

        if thresholds == None:
            thresholds = self.withinThresholds

        ## setup save variables
        templateClusters = np.unique(self.templateLabels)
        alignResults = []
        alignResultsFiles = []
        alignResultsClusters =[]

        ## more variables
        fileCount = 0
        clustCount = -1
        newClusterCount = 0
        newClusterData = None
        newClusterLabels = None
        appearedTwice = set([])
        templateThresholds = {}
        templateData = self.get_template_data()

        ## calculate within thresholds for template
        for clusterID in templateClusters:

            ## skip clusters that do not have enough events
            templateEvents = templateData[np.where(self.templateLabels==int(clusterID))[0],:]
            if len(templateEvents) < self.minNumEvents:
                continue

            ## determine distances
            templateMean = templateEvents.mean(axis=0)
            dc = DistanceCalculator(distType=self.distanceMetric)
            if self.distanceMetric == 'mahalanobis':
                inverseCov = dc.get_inverse_covariance(templateEvents)
                if inverseCov != None:
                    dc.calculate(templateEvents,matrixMeans=templateMean,inverseCov=inverseCov)
                    distances = dc.get_distances()
                else:
                    dc.calculate(templateEvents,matrixMeans=templateMean)
                    distances = dc.get_distances()
                    distances = whiten(distances)
            else:
                dc.calculate(templateEvents,matrixMeans=templateMean)
                distances = dc.get_distances()

            ## use the eCDF to find a threshold
            eCDF = EmpiricalCDF(distances)
            thresholdLow = eCDF.get_value(0.025)
            thresholdHigh = eCDF.get_value(0.975)
            templateThresholds[str(int(clusterID))] = {'ci':(thresholdLow, thresholdHigh)}

        ## scan through the files
        fileDataList = []
        fileLabelsList = []
        fileClusterList = []
        fileLabelsList = allLabels = [self.get_labels(expName) for expName in self.expListNames] #self.phi2Labels

        fileInd = -1
        for fileName in self.expListNames:
            fileInd += 1
            fileDataList.append(self.get_events(fileName))
            fileClustersList = [np.sort(np.unique(fl)) for fl in fileLabelsList]
            
        n = len(self.expListNames)
        args = zip(self.expListNames,
                   fileDataList,
                   fileLabelsList,
                   fileClustersList,
                   [sampleStats]*n,       # [self.sampleStatsPhi2]*2
                   [thresholds]*n,  # [self.withinThresholdsPhi2]*n,
                   [templateData]*n,
                   [self.templateLabels]*n,
                   [templateClusters]*n,
                   [templateThresholds]*n,
                   [phi]*n,
                   [self.minNumEvents]*n,
                   [self.noiseClusters]*n)

        results = pool.map(pool_compare_scan,args)
        
        ## reformat the results
        alignResults = []
        alignResultsFiles = []
        alignResultsClusters = []

        for fileInd in range(len(self.expListNames)):
            fileName = self.expListNames[fileInd]
            fileResults = results[fileInd]
            
            if len(fileResults[0]) == 0:
                continue

            alignResults += fileResults[0]
            alignResultsFiles += [self.expListNames.index(fr) for fr in fileResults[1]]
            alignResultsClusters += fileResults[2]
                    
        if self.verbose == True:
            print "\n"

        return {'results':np.array(alignResults),'files':np.array(alignResultsFiles),'clusters':np.array(alignResultsClusters)}

    def get_best_match(self):
        result = (None, None)
        maxScore = 0

        for phi,score in self.globalScoreDict.iteritems():
            if score > maxScore:
                maxScore = score
                result = (float(phi),float(score))

        return result
