#!/usr/local/bin/python


'''
class that creates a template file for file alignment
The smaller the value for fixed overlap the more difficult it is to add new clusters to the template

'''
import os,sys
from multiprocessing import Pool, cpu_count
import numpy as np
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist
from scipy.cluster.vq import whiten
import matplotlib.pyplot as plt
from cytostream.stats import DistanceCalculator, EmpiricalCDF, event_count_compare, get_silhouette_values, find_noise
from cytostream.tools import get_all_colors

## global vars
FIXED_OVERLAP = 0.4

def pool_compare_template(args):

    ## input variables
    fileInd = args[0]
    fileData = args[1]
    fileLabels = args[2]
    fileClusters = args[3]
    templateData = args[4]
    templateLabels = args[5]
    templateClusters = args[6]
    noiseClusters = args[7]
    thresholds = args[8]
    templateThresholds = args[9]

    ## additional variables     
    clustersMatched = []
    newClusterData = None
    newClusterLabels = None
    newClusterCount = 0
    appearedTwice = set([])

    for ci in range(len(templateClusters)):
        clusterI = templateClusters[ci]
        if templateThresholds.has_key(str(int(clusterI))) == False:
            print 'in template skipping', fileInd,clusterI
            continue

        templateEvents = templateData[np.where(templateLabels==clusterI)[0],:]
        clusterMuI = templateEvents.mean(axis=0)

        for cj in range(len(fileClusters)):
            clusterJ = fileClusters[cj]

            ## debug
            #print 'compare', fileInd, clusterI, clusterJ
            
            ## check to see if matched
            if clusterJ in clustersMatched:
                continue

            ## check for noise label                                                                                                                                            
            if noiseClusters[fileInd].__contains__(int(clusterJ)):
                clustersMatched.append(clusterJ)
                continue

            ## determine overlap
            clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]
            overlap1 = event_count_compare(templateEvents,clusterEventsJ,clusterJ,thresholds[fileInd][str(clusterJ)]['ci'])
            overlap2 = event_count_compare(clusterEventsJ,templateEvents,clusterI,templateThresholds[str(clusterI)]['ci'])
            overlap = np.max([overlap1,overlap2])

            ## everything with at least 20% overlap is a match
            if overlap >= FIXED_OVERLAP:
                clustersMatched.append(clusterJ)
                continue

        nonMatches = list(set(fileClusters).difference(set(clustersMatched)))

    return nonMatches

class TemplateFileCreator():
    '''
    class that creates a template file for the FileAligner class
    using hierarchical clustering of centroids 

    '''

    def __init__(self,matList,matLabelList,linkageMethod='average',templateSeedInd=None,excludedChannels=[]):
        '''
        constructor
        
        mat - np.array (nxd) of events
        labels - list or np.array of labels of size n
        linkageMethod - ['average','centroid','single','complete','weighted'] 
                     for more see scipy.cluster.hierarchy.linkage

        '''

        ## declare variables
        self.matList = matList
        self.matLabelList = matLabelList
        self.numFiles = len(self.matList)
        self.noiseClusters = []
        self.thresholds = []
        self.distanceMetric = 'mahalanobis'
        self.excludedChannels = excludedChannels
        self.minNumEvents = 4
        self.noiseSample = 2000

        ## error checking 
        if len(self.matList) != len(self.matLabelList):
            raise RuntimeError("TemplateFileCreator: Invalid input -- dim mismatch")
        
        for f in range(self.numFiles):
            self._error_check_input(self.matList[f], self.matLabelList[f])

        if templateSeedInd != None and templateSeedInd not in range(self.numFiles):
            raise RuntimeError("TemplateFileCreator: Invalid templateSeedInd -- dim mismatch")

        ## handle excluded channels
        if len(self.matList[0].shape) == 1:
            self.numChannels = 1
        else:
            self.numChannels = self.matList[0].shape[1]

        if len(self.excludedChannels) > 0:
            self.includedChannels = np.array(list(set(range(self.numChannels)).difference(set(excludedChannels))))
        else:
            self.includedChannels = np.arange(self.numChannels)

        ## get sil values
        allEvents = [self.get_events(fid) for fid in range(self.numFiles)]
        allLabels = [self.get_labels(fid) for fid in range(self.numFiles)]
        self.silValues = get_silhouette_values(allEvents,allLabels,subsample=self.noiseSample,
                                               minNumEvents=self.minNumEvents)
        ## find noise clusters
        for fileInd in range(self.numFiles):
            labels = self.get_labels(fileInd)
            mat = self.get_events(fileInd)
            self.noiseClusters.append(self._find_noise(fileInd,mat,labels))

        print self.noiseClusters

        ## handle template seed
        if templateSeedInd != None:
            self.templateSeedInd = templateSeedInd
        else:
            self.templateSeedInd = self._select_mat_for_seed()

        ## create the initial template from one of the files in the list
        self.templateMat = self.get_events(self.templateSeedInd).copy()
        self.templateLabels = self.get_labels(self.templateSeedInd).copy()
        self.templateClusters = np.unique(self.templateLabels)
        
        ## remove noise clusters from consideration as part of template
        self._clean_template()

        ## calculate within thresholds for all files
        for fileInd in range(self.numFiles):
            th = self._get_within_thresholds(fileInd,fileNoiseClusters=self.noiseClusters[fileInd])
            self.thresholds.append(th)
        
        self.templateThresholds = self.thresholds[self.templateSeedInd]

        ## add components to template that are represented in at least 2 non-template files
        self._add_nonseed_clusters_to_template()

        ## run hier clustering
        self._run_hier_clust_on_centroids(method=linkageMethod)

    def get_events(self,fileInd):
        '''
        convenience function to return a np.array of observations

        '''

        if fileInd not in range(self.numFiles):
            print "ERROR: TemplateFileCreator.get_events -- invalid fileInd specified"
            return
        
        return self.matList[fileInd][:,self.includedChannels]

    def get_labels(self,fileInd):
        '''
        convenience function to return a np.array of labels

        '''

        if fileInd not in range(self.numFiles):
            print "ERROR: TemplateFileCreator.get_labels -- invalid fileInd specified"
            return

        return self.matLabelList[fileInd]

    def _find_noise(self,fileInd,mat,labels,useSilVals=True):
        '''
        for a given set of labels and observations find the noise clusters
        '''

        if useSilVals == True:
            noiseClusters = find_noise(mat,labels,silValues=self.silValues[str(fileInd)],minNumEvents=self.minNumEvents)
        else:
            noiseClusters = find_noise(mat,labels,minNumEvents=self.minNumEvents)

        return noiseClusters
                    
    def _add_nonseed_clusters_to_template(self):

        ## align template to all other files
        pool = Pool(processes=cpu_count(),maxtasksperchild=1)
        fileDataList = []
        fileLabelsList = []
        fileClusterList = []
        fileIndList = []
        
        for fileInd in range(self.numFiles):
            
            ## skip the file used to make the template
            if fileInd == self.templateSeedInd:
                continue

            fileIndList.append(fileInd)
            fileDataList.append(self.get_events(fileInd))
            fileLabelsList.append(self.get_labels(fileInd))
        
        fileClustersList = [np.sort(np.unique(fl)) for fl in fileLabelsList]

        ## set up variables to pass to pool 
        n = self.numFiles
        args = zip(fileIndList,
                   fileDataList,
                   fileLabelsList,
                   fileClustersList,
                   [self.templateMat]*n,
                   [self.templateLabels]*n,
                   [self.templateClusters]*n,
                   [self.noiseClusters]*n,
                   [self.thresholds]*n,
                   [self.templateThresholds]*n)

        #self.alignmentLog.writerow(['start_file',"%s-%s"%(phi,fileWithMinNumClusters)])

        ## scan through all of the files to find nonmatches
        results = pool.map(pool_compare_template,args)
        pool.close()
        newClusterData = None
        newClusterLabels = None
        appearedTwice = set([])
        newClusterCount=0

        ## determine which clusters to add to template file 
        for fi in range(len(fileIndList)):
            fileInd = fileIndList[fi]
            fileData = self.get_events(fileInd)
            fileLabels = self.get_labels(fileInd)
            nonMatches = results[fi]
        
            for clusterJ in nonMatches:
                clusterEventsJ = fileData[np.where(fileLabels==clusterJ)[0],:]

                ## scan against the other soon to be new clusters 
                isNew = True
                if newClusterLabels != None:
                    newIDs = np.sort(np.unique(newClusterLabels))
                    for nid in newIDs:
                        if isNew == False:
                            continue

                        savedEvents = newClusterData[np.where(newClusterLabels==nid)[0],:]
                        overlap = event_count_compare(savedEvents,clusterEventsJ,clusterJ,self.thresholds[fileInd][str(clusterJ)]['ci'])
                        
                        ## use a constant value for phi when creating the template file
                        if overlap >= FIXED_OVERLAP:
                            appearedTwice.update([nid])
                            isNew = False

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

        ## add the clusters to the template file
        if newClusterLabels != None:
            newClusterLabels = newClusterLabels + np.max(self.templateLabels)
            appearedTwice = np.array(list(appearedTwice)) + np.max(self.templateLabels)
            print "...Adding %s clusters to template seed"%len(appearedTwice)

            for cid in appearedTwice:
                ncEvents = newClusterData[np.where(newClusterLabels == cid)[0],:]
                ncLabels = np.array([cid]).repeat(ncEvents.shape[0])
                self.templateMat = np.vstack([self.templateMat,ncEvents])
                self.templateLabels = np.hstack([self.templateLabels, ncLabels])

    def _get_within_thresholds(self,fileInd,fileData=None,fileLabels=None,fileNoiseClusters=[]): 
        '''
        calculate within thresholds
        input either a fileInd or both the fileData and fileLabels
        
        '''

        fileThresholds = {}
        if fileData != None and fileLabels != None:
            pass
        else:
            fileLabels = self.get_labels(fileInd)
            fileData = self.get_events(fileInd)
        
        fileClusters = np.sort(np.unique(fileLabels))
        fileMean = fileData.mean(axis=0)
        for clusterID in fileClusters:
            clusterID = int(clusterID)
            
            if clusterID in fileNoiseClusters:
                continue

            fileClusterEvents = fileData[np.where(fileLabels==clusterID)[0],:]
            fileClusterMean = fileClusterEvents.mean(axis=0)

            ## determine distances
            dc = DistanceCalculator(distType=self.distanceMetric)
            if self.distanceMetric == 'mahalanobis':
                inverseCov = dc.get_inverse_covariance(fileClusterEvents)
                if inverseCov != None:
                    dc.calculate(fileClusterEvents,matrixMeans=fileClusterMean,inverseCov=inverseCov)
                    distances = dc.get_distances()
                else:
                    dc.calculate(fileClusterEvents,matrixMeans=fileClusterMean)
                    distances = dc.get_distances()
                    distances = whiten(distances)
            else:
                dc.calculate(fileClusterEvents,matrixMeans=fileClusterMean)
                distances = dc.get_distances()

            #nanCount = len(np.where(np.isnan(distances) == True)[0])
            #if nanCount > 0:
            #    print nanCount, len(distances),len(fileClusterEvents)
            #    print "TemplateFileCreator encountered NaNs",maxVal
                
            ## use the eCDF to find a threshold
            eCDF = EmpiricalCDF(distances)
            thresholdLow = eCDF.get_value(0.025)
            thresholdHigh = eCDF.get_value(0.975)
            fileThresholds[str(clusterID)] = {'ci':(thresholdLow, thresholdHigh)}

        return fileThresholds


    def _clean_template(self):
        '''
        remove noise clusters from templae file
        '''

        fileSpecificNoiseClusters = self.noiseClusters[self.templateSeedInd]
        noiseInds = np.array([])

        for cid in fileSpecificNoiseClusters:
            print type(self.templateLabels)
            noiseInds = np.hstack([noiseInds,np.where(self.templateLabels==int(cid))[0]])

        nonNoiseInds = list(set(range(len(self.templateLabels))).difference(set(noiseInds)))
        self.templateMat = self.templateMat[nonNoiseInds,:]
        self.templateLabels = self.templateLabels[nonNoiseInds,:]

    def _select_mat_for_seed(self):
        
        '''
        select the file with the most clusters for a seed file

        '''

        matWithMinNumClusters = None
        matWithMaxNumClusters = None
        minClusts = np.inf
        maxClusts = -np.inf

        for fileInd in range(self.numFiles):
            noiseClusters = 0
            
            ## check for the number of noise clusters 
            if len(self.noiseClusters[fileInd]) > 0:
                noiseClusters = len(self.noiseClusters[fileInd])

            matLabels = self.matLabelList[fileInd]
            matClusters = np.sort(np.unique(matLabels))
            matClusterNumber = len(matClusters) - noiseClusters

            if matClusterNumber < minClusts:
                minClusts = matClusterNumber
                matWithMinNumClusters = fileInd
            if matClusterNumber > maxClusts:
                maxClusts = matClusterNumber
                matWithMaxNumClusters = fileInd

        return matWithMaxNumClusters

    def _run_hier_clust_on_centroids(self,method='average'):
        '''
        runs hierarchical clustering based on the centroids of the data per scipy's methods

        '''

        uniqueLabels = np.sort(np.unique(self.templateLabels))
        centroids = np.array([self.templateMat[np.where(self.templateLabels == i)[0],:].mean(axis=0) for i in uniqueLabels])
               
        self.y = pdist(centroids)
        self.z = hierarchy.linkage(self.y,method)
        r2 = hierarchy.inconsistent(self.z,2)

        ## rank the average of linkage hieghts by standard deviation the report the averages
        meanHeights = r2[:,0]
        stdHeights = r2[:,1]
        rankedInds = np.argsort(stdHeights)[::-1]
        bestCutPoints = meanHeights[rankedInds]

        ## save centroid labels for all cuts of the dentragram
        allCentroidLabels = {}
        rankedK = []
        for cp in bestCutPoints:
            centroidLabels = hierarchy.fcluster(self.z,t=cp,criterion='distance')
            k = len(np.unique(centroidLabels))
            if allCentroidLabels.has_key(str(k)) == True:
                continue
            
            allCentroidLabels[str(k)] = centroidLabels 
            rankedK.append(k)
        
        centroidLabels = allCentroidLabels[str(rankedK[0])]
    
        ## save the top 3 modes 
        self.bestModeLabels = []
        for rk in rankedK[:3]:
            centroidLabels = allCentroidLabels[str(rk)]
            self.bestModeLabels.append(self._get_mode_labels(self.templateLabels,centroidLabels,uniqueLabels))
   
    def _get_mode_labels(self,labels,centroidLabels,uniqueLabels):
        '''
        internal method to convert centroid labels to modes

        '''

        modeLabels = np.zeros((labels.size,))
        for c in range(len(uniqueLabels)):
            uid = uniqueLabels[c]
            newLab = centroidLabels[c]
            inds = np.where(labels == uid)[0]
            modeLabels[inds] = newLab

        return modeLabels

    def _error_check_input(self,mat,labels):
        
        ## input error checking 
        if type(mat) != type(np.array([])):
            raise RuntimeError("TemplateFileCreator: Invalid input type (mat)")
        if type(labels) == type(np.array([])):
            labels = labels
        elif type(labels) == type([]):
            labels = np.array(labels)
        else:
            raise RuntimeError("TemplateFileCreator: Invalid input type (labels)")
        
        if len(mat.shape) == 1:
            n = mat.shape[0]
            d = 1
        else:
            n,d = mat.shape

        if n != labels.size:
            raise RuntimeError("TemplateFileCreator: data mismatch in matrix and labels")

    def draw_dendragram(self):
        fig = plt.figure()
        dg = hierarchy.dendrogram(self.z)
        plt.savefig("dendragram.png")

    def draw_templates(self,dim1=0,dim2=1,saveas='templates.png'):
        colorList = get_all_colors()
        fig = plt.figure()
        ax = fig.add_subplot(131)
        colorsToPlot = [colorList[l] for l in self.templateLabels]
        ax.scatter(self.templateMat[:,dim1], self.templateMat[:,dim2],marker='o',edgecolor='none',s=2,c=colorsToPlot)
        ax.set_title("Template")
        ax.set_aspect(1./ax.get_data_ratio())

        ax = fig.add_subplot(132)
        colorsToPlot = [colorList[l] for l in self.bestModeLabels[0]]
        ax.scatter(self.templateMat[:,dim1], self.templateMat[:,dim2],marker='o',edgecolor='none',s=2,c=colorsToPlot)
        ax.set_title("Best Mode")
        ax.set_aspect(1./ax.get_data_ratio())

        ax = fig.add_subplot(133)
        colorsToPlot = [colorList[l] for l in self.bestModeLabels[1]]
        ax.scatter(self.templateMat[:,dim1], self.templateMat[:,dim2],marker='o',edgecolor='none',s=2,c=colorsToPlot)
        ax.set_title("Second Best Mode")
        ax.set_aspect(1./ax.get_data_ratio())

        plt.savefig(saveas)
        
