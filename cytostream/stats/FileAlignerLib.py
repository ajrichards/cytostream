#!/usr/bin/python


'''
library for file aligner related functions

'''

import sys,os,re
import numpy as np
import scipy.stats as stats
from scipy.cluster.vq import whiten

from cytostream import NoGuiAnalysis
from cytostream.stats import SilValueGenerator, DistanceCalculator
from cytostream.stats import Bootstrapper, EmpiricalCDF

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
                 refFile=None,verbose=False,excludedChannels=[],isProject=False,
                 modelRunID=None,distanceMetric='mahalanobis',medianTransform=True):

        ## declare variables
        self.expListNames = [expName for expName in expListNames]
        self.expListLabels = [np.array([int(label) for label in labelList]) for labelList in expListLabels]
        self.expListData = expListData
        self.phiRange = phiRange
        self.matchResults = None
        self.homeDir = homeDir
        self.verbose = verbose
        self.modelRunID = modelRunID
        self.isProject = isProject

        ## control variables 
        self.medianTransform = medianTransform
        self.silValueEstimateSample = 500
        self.distanceMetric = distanceMetric
        self.globalScoreDict = {}
        self.newLabelsAll = {}
        self.modelType = 'components'
        
        if self.verbose == True:
            print "Initializing file aligner"

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
        events = self.get_events(self.expListNames[0])
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

    def run(self):
        ## median transform data
        print "DEBUG -- need to do median transform"

        ## get sample statistics
        if self.verbose == True:
            print "...getting sample statistics"
        self.sampleStats = self.get_sample_statistics(self.expListLabels)

        ## get sil values
        if self.verbose == True:
            print "...getting silhouette values"
        self.silValues = self.get_silhouette_values(self.expListLabels)

        ## use bootstrap to determine noise clusters
        if self.verbose == True:
            print "...bootstrapping to find noise clusters"

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
        if self.verbose == True:
            print "...Noise Clusters:"
            for key,item in self.noiseClusters.iteritems():
                print "\t", key, item

        ## calculate all within distances
        self._calculate_all_within_thresholds()
        print self.withinThresholds

        ## self alignment
        self.selfAlignment = self._self_alignment()
        print self.selfAlignment

        ## create a template file
        
    def _init_project(self):
        self.nga = NoGuiAnalysis(self.homeDir,loadExisting=True)
        self.nga.set("results_mode",self.modelType)
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
            events = nga.get_events(selectedFile,subsample)
            return events
        else:
            fileInd = self.expListNames.index(selectedFile)
            return self.expListData[fileInd]

    def get_sample_statistics(self,expListLabels):
        centroids, variances, numClusts, numDataPoints = {},{},{},{}
        for expInd in range(len(expListLabels)):
            expName = self.expListNames[expInd]
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
        #subsetExpData = []
        #subsetExpLabels = []

        #for c in range(len(self.expListNames)):
        #    expName = self.expListNames[c]
        #    expData = self.expListData[c]
        #    expLabels = expListLabels[c]
        #    fileClusters = np.sort(np.unique(expLabels))

            #newIndices = []
            #for clusterInd in fileClusters:
            #    clusterElementInds = np.where(expLabels == clusterInd)[0]
            #    if clusterElementInds.size > self.silValueEstimateSample:
            #        randSelectedInds = clusterElementInds[np.random.randint(0,clusterElementInds.size ,self.silValueEstimateSample)]
            #        #print len(expLabels),clusterElementInds.size, clusterElementInds.shape, clusterElements
            #        newIndices = newIndices + randSelectedInds.tolist()
            #    else:
            #        newIndices = newIndices + clusterElementInds.tolist() 
            #
            #if len(expLabels) == 0:
            #    print "ERROR there is a problem with the labels for %s "%expName
            #    sys.exit()

            #subsetExpData.append(expData[newIndices,:])
            #subsetExpLabels.append(np.array(expLabels)[newIndices])

        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            expData = self.get_events(expName)
            expLabels = self.get_labels(expName)
            fileClusters = np.sort(np.unique(expLabels))

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
           
        #return silValuesElements
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


    def _calculate_all_within_thresholds(self):

        self.withinThresholds = {}

        for fileName in self.expListNames:
            fileLabels = self.get_labels(fileName)
            fileData = self.get_events(fileName)
            fileClusters = np.sort(np.unique(fileLabels))
            
            if self.withinThresholds.has_key(fileName) == False:
                self.withinThresholds[fileName] = {}
            
            print 'fileName', fileClusters
            for clusterID in fileClusters:

                ## check for noise label
                if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterID)):
                    print 'skipping in calculate_all_within_thresholds', fileName, clusterID
                    continue

                ## determine distances
                clusterEvents = fileData[np.where(fileLabels==int(clusterID))[0],:]
                clusterMean = clusterEvents.mean(axis=0)
                dc = DistanceCalculator(distType=self.distanceMetric)
                if self.distanceMetric == 'mahalanobis':
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
                threshold = eCDF.get_value(0.975)
                self.withinThresholds[fileName][str(int(clusterID))] = threshold

    def _self_alignment(self):
        totalClusters = np.array([(float(n)*(float(n)-1.0)) / 2.0 for n in self.sampleStats['k'].itervalues()]).sum()
        overlapList = np.zeros((totalClusters),) -1
        overlapListFiles = np.zeros((totalClusters),) -1
        overlapListClusters = np.array(['None'],dtype='|S7').repeat(totalClusters)

        clustCount = -1
        for fileName in self.expListNames:
            fileLabels = self.get_labels(fileName)
            fileClusters = np.sort(np.unique(fileLabels))
            
            for clusterI in fileClusters:
                for clusterJ in fileClusters:
                    
                    ## do not compare cluster to itself
                    if clusterI <= clusterJ:
                        continue

                    clustCount+=1
                    
                    ## check for noise label
                    if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterI)):
                        print 'skipping in _self_alignment', fileName, clusterI
                        continue

                    if self.noiseClusters.has_key(fileName) and self.noiseClusters[fileName].__contains__(str(clusterJ)):
                        print 'skipping in _self_alignment', fileName, clusterJ
                        continue

                    ## get and store overlap
                    overlap1 = self._compare_source_sink(fileName,fileName,clusterI, clusterJ)
                    overlap2 = self._compare_source_sink(fileName,fileName,clusterJ, clusterI)
                    overlap = np.max([overlap1,overlap2])

                    overlapList[clustCount] = overlap
                    overlapListFiles[clustCount] = self.expListNames.index(fileName)
                    y,z = np.sort([int(clusterI),int(clusterJ)]) 
                    overlapListClusters[clustCount] = str(y)+"-"+str(z)

        ## integrity check
        if int(totalClusters) != int(clustCount + 1):
            print "ERROR: FileAlingerLib failed integrity check clustCount",totalClusters, clustCount

        return {'overlap':overlapList,'file_names':overlapListFiles,'cluster_ids':overlapListClusters}


    def _compare_source_sink(self,fileI, fileJ, clusterI, clusterJ):
        '''
        model the sink (j) then determine number of events in source (i) that overlap
        '''

        ## get distances of cluster i's events to cluster j's centroid
        clusterI, clusterJ =  int(clusterI), int(clusterJ)
        labelsI = self.get_labels(fileI)
        dataI = self.get_events(fileI)
        clusterEventsI = dataI[np.where(labelsI==clusterI)[0],:]
          
        clusterMeanJ = self.sampleStats['mus'][fileJ][str(clusterJ)]
        dc = DistanceCalculator(distType=self.distanceMetric)
        if self.distanceMetric == 'mahalanobis':
            inverseCov = dc.get_inverse_covariance(clusterEventsI)
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
        threshold = self.withinThresholds[fileJ][str(clusterJ)]
        overlappedInds = np.where(distances < threshold)[0]

        if len(overlappedInds) == 0:
            return 0
 
        return float(len(overlappedInds)) / float(len(distances))

    def create_template_file(self):
        print 'creating template file'
        ## find file with fewest clusters
        

        ## scan all non-noise clusters 
