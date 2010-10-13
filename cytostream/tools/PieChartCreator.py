#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

class PieChartCreator():

    def __init__(self,newLabelsLists,expListNames,saveas=None):
        self.newLabelsLists = newLabelsLists
        self.expListNames = expListNames
        self.saveas = saveas
        self.colors = ['b','g','r','c','m','y','k','orange','#AAAAAA','#FF6600',
                  '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',
                  '#FA58AC', '#8A0808','#D8D8D8','#336666','#996633']
        self.masterLabelList = self.get_master_index_list()
        self.allClusterFractions = self.get_cluster_fractions()
        self.create_plot()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelsLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def get_cluster_fractions(self):
        allClusterFractions = []
        for fileInd in range(len(self.newLabelsLists)):

            labelList = self.newLabelsLists[fileInd]
            clusterFractions = []

            for clusterID in self.masterLabelList:
                eventCount =  np.where(np.array(labelList) == clusterID)[0].size
                clusterFractions.append(eventCount / float(len(labelList)))

            allClusterFractions.append(clusterFractions)

        return allClusterFractions

    def create_plot(self):
        fig = plt.figure(3,figsize=(6.0,9))
        subplotCount = 0
        for fileInd in range(len(self.allClusterFractions)):
            subplotCount+=1
            ax = fig.add_subplot(3,2,subplotCount)

            labels = ['%s'%l for l in self.masterLabelList]
            fracs = self.allClusterFractions[fileInd]
            nonZeroInds = np.where(np.array(fracs) != 0.0)[0]
            labels = np.array(labels)[nonZeroInds]
            fracs = np.array(fracs)[nonZeroInds]
            colorList = [self.colors[int(l)] for l in labels]
            explode = [0 for l in labels]
            ax.pie(fracs, explode=explode, labels=None, colors=colorList, shadow=True) #  autopct='%1.1f%%'
            ax.set_title(self.expListNames[fileInd], bbox={'facecolor':'0.8', 'pad':5})  

        if self.saveas != None:
            fig.savefig(self.saveas+".pdf")
