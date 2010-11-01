#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

class DotPlotCreator():

    def __init__(self,newLabelLists,expListNames,saveas=None):

        self.newLabelLists = newLabelLists
        self.expListNames = expListNames
        self.saveas = saveas
        #self.subplotRows = subplotRows
        #self.subplotCols = subplotCols
        
        self.colors = ['b','g','r','c','m','y','k','orange','#AAAAAA','#FF6600',
                       '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',
                       '#FA58AC','#8A0808','#D8D8D8','#336666','#996633',"#FFCCCC",
                       "#FF9966","#009999","#FF0099","#996633","#990000","#660000",
                       "#330066","#99FF99","#FF99FF","#333333","#CC3333","#CC9900",
                       "#003333","#66CCFF","#CCFFFF","#AA11BB","#000011","#FFCCFF",
                       "#009999","#110000","#AAAAFF","#990000","#880022","#BBBBBB"]

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
            
            colToPlot = np.array(colToPlot) * 500
            ax.scatter(np.array([i+1]).repeat(len(self.masterLabelList)),range(1,len(self.masterLabelList)+1),marker='o',s=colToPlot,alpha=0.7)

        ax.set_ylim([0,len(self.masterLabelList) + 1])
        ax.set_xlim([0,len(self.newLabelLists) + 1])
        xtickNames = plt.setp(ax, xticklabels=[' ']+self.expListNames)
        plt.setp(xtickNames, rotation=45, fontsize=8)

        if self.saveas != None:
            fig.savefig(self.saveas)
            
