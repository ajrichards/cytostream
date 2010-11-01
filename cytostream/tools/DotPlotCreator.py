#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from cytostream.tools import get_all_colors
from matplotlib.ticker import MaxNLocator

class DotPlotCreator():

    def __init__(self,newLabelLists,expListNames,saveas=None):

        self.newLabelLists = newLabelLists
        self.expListNames = expListNames
        self.saveas = saveas
        #self.subplotRows = subplotRows
        #self.subplotCols = subplotCols
        self.fontSize = 10
        self.fontName = 'arial'
        self.colors = get_all_colors()

        self.masterLabelList = self.get_master_index_list()
        #self.allClusterFractions = self.get_cluster_fractions()
        self.create_plot()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def create_plot(self):

        fig = plt.figure(figsize=(10,6.5))
        ax = fig.add_subplot(111)
        ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                      alpha=0.5)

        for i in range(len(self.newLabelLists)):
            labels = self.newLabelLists[i]
            totalElements = len(labels)
            colToPlot = [] 
            for lab in self.masterLabelList:
                indices = np.where(labels == lab)[0]
                if len(indices) > 0:
                    colToPlot.append(float(indices.size) / float(totalElements))
                else:
                    colToPlot.append(0)
            
            colToPlot = np.array(colToPlot) * 400
            ax.scatter(np.array([i+1]).repeat(len(self.masterLabelList)),range(1,len(self.masterLabelList)+1),marker='o',s=colToPlot,alpha=0.7)

        ax.set_ylim([0,len(self.masterLabelList) + 1])
        ax.set_xlim([0,len(self.newLabelLists) + 1])
        xticklabels = plt.getp(plt.gca(), 'xticklabels')
        plt.setp(xticklabels, fontsize=self.fontSize-1, fontname=self.fontName)
        yticklabels = plt.getp(plt.gca(), 'yticklabels')
        plt.setp(yticklabels, fontsize=self.fontSize-1, fontname=self.fontName)
       

        #ax.xaxis.set_major_locator(MaxNLocator(len(self.masterLabelList)+1))
        #ax.yaxis.set_major_locator(MaxNLocator(len(self.newLabelLists)+1))
         #
        #xtickNames = plt.setp(ax, xticklabels=[' ']+self.expListNames)
        #plt.setp(xtickNames, rotation=45, fontsize=8)

        if self.saveas != None:
            fig.savefig(self.saveas)
            
