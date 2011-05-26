#!/usr/bin/python


'''
library for file aligner related functions

'''

import sys,os,re
import numpy as np
from cytostream import NoGuiAnalysis
from cytostream.stats import SilValueGenerator
from cytostream.stats import Bootstrapper

class FileAlignerII():

    '''
    (1) calculate and save sample statistics
    (2) calculate and save silhouette values
    (3) determine noise
    (4) self alignment
    (5) create a template file
    (6) scan all files with template file

    '''


    def __init__(self,expListNames=[],expListData=[],expListLabels=None,phiRange=None,homeDir=None,
                 refFile=None,verbose=False,excludedChannels=[],baseDir=".",
                 modelRunID=None,distanceMetric='mahalanobis',medianTransform=True):

        ## declare variables
        self.expListNames = [expName for expName in expListNames]
        self.expListLabels = [[label for label in labelList] for labelList in expListLabels]
        self.phiRange = phiRange
        self.matchResults = None
        self.baseDir = baseDir
        self.homeDir = homeDir
        self.verbose = verbose
        self.isProject = False
        self.modelRunID = modelRunID

        ## control variables 
        self.medianTransform = medianTransform
        self.silValueEstimateSample = 500
        self.distanceMetric = distanceMetric
        self.globalScoreDict = {}
        self.newLabelsAll = {}
        self.modelType = 'components'
        
        if self.verbose == True:
            print "Initializing file aligner"

        ## making dir tree
        if os.path.isdir(self.baseDir) == False:
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
            self.isProject = True
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

        ## self alignment
        print 'suppose do do self alignment'

        ## create a template file
        

    def _init_project(self):
        self.nga = NoGuiAnalysis(homeDir,loadExisting=True)
        self.nga.set("results_mode",self.modelType)
        self.expListNames = self.nga.get_file_names()
        self.fileChannels = self.nga.get_file_channels()


    def make_dir_tree(self):
        if self.verbose == True and os.path.isdir(os.path.join(self.baseDir,'alignfigs')) == True:
            print "INFO: deleting old files for file aligner"

        dirs = ['results','alignfigs']
        for diry in dirs:
            if os.path.isdir(os.path.join(self.baseDir,diry)) == False:
                os.mkdir(os.path.join(self.baseDir,diry))
            
        if os.path.isdir(os.path.join(self.baseDir,'alignfigs')) == True:
            ## clean out figures dir
            for item1 in os.listdir(os.path.join(self.baseDir,'alignfigs')):
                if os.path.isdir(os.path.join(self.baseDir,'alignfigs',item1)) == True:
                    for item2 in os.listdir(os.path.join(self.baseDir,'alignfigs',item1)):
                        os.remove(os.path.join(self.baseDir,'alignfigs',item1,item2))
                else:
                    os.remove(os.path.join(self.baseDir,'alignfigs',item1))
            
            ## clean out relevant results
            if os.path.isdir(os.path.join(self.baseDir,'results','alignments')) == True:
                for item1 in os.listdir(os.path.join(self.baseDir,'results','alignments')):
                    os.remove(os.path.join(self.baseDir,'results','alignments',item1))
                
            ## remove old log files 
            if os.path.isfile(os.path.join(self.baseDir,"results","_FileMerge.log")) == True:
                os.remove(os.path.join(self.baseDir,"results","_FileMerge.log"))
            if os.path.isfile(os.path.join(self.baseDir,"results","_FileMerge.log")) == True:
                os.remove(os.path.join(self.baseDir,"results","_FileMerge.log"))
            if os.path.isfile(os.path.join(self.baseDir,"results","alignments.log")) == True:
                os.remove(os.path.join(self.baseDir,"results","alignments.log"))

        ## ensure directories are present
        if os.path.isdir(os.path.join(self.baseDir,"results")) == False:
            os.mkdir(os.path.join(self.baseDir,"results"))            
        if os.path.isdir(os.path.join(self.baseDir,"results","alignments")) == False:
            os.mkdir(os.path.join(self.baseDir,"results","alignments"))
        if os.path.isdir(os.path.join(self.baseDir,"alignfigs")) == False:
            os.mkdir(os.path.join(self.baseDir,"alignfigs"))


    def get_labels(self,selectedFile):

        if selectedFile not in self.fileList:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return
    
        if self.isProject == True:
            statModel, labels = self.nga.get_model_results(selectedFile,self.modelRunID,self.modelType)
            return labels
        else:
            fileInd = self.expListNames.index(selectedFile)
            return self.expListLabels[fileInd]

    def get_events(self,selectedFile):

        if selectedFile not in self.expListNames:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return

        if self.isProject == True:
            modelLog = self.nga.get_model_results_log(selectedFile,self.modelRunID)
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
            #expName = self.expListNames[c]
            #expData = subsetExpData[c]
            #expLabels = subsetExpLabels[c]

            expName = self.expListNames[c]
            expData = self.expListData[c]
            expLabels = expListLabels[c]
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


    
    def create_template_file(self):
        print 'creating template file'
        ## find file with fewest clusters
        

        ## scan all non-noise clusters 
