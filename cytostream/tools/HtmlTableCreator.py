#!/usr/bin/env python

import re
import numpy as np
import matplotlib.pyplot as plt
from cytostream.tools import get_all_colors
from matplotlib.ticker import MaxNLocator

class HtmlTableCreator():

    def __init__(self,newLabelLists,expListNames,saveas=None,covariates=None):

        self.newLabelLists = newLabelLists
        self.expListNames = expListNames
        self.fontSize = 10
        self.covariates = covariates
        self.fontName = 'arial'
        self.colors = get_all_colors()

        if saveas != None and re.search("html",saveas):            
            self.saveas = saveas
        elif saveas != None and re.search("html",saveas) == False:
            print "WARNING: bad html file name given using default"
            self.saveas = "alignment_summary_table.html"
        else:
            self.saveas = "alignment_summary_table.html"

        self.masterLabelList = self.get_master_index_list()
        self.create_table()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def create_table(self):
        ### make the html main file  
        f = open(self.saveas,'w')
        f.write("<html>\n")
        f.write("<title>" + "file alignment table" + "</title\n>")
        f.write("<h1 align='center'>" + "file alignment table" + "</h1>\n")
        #f.write("<a href=" + "'." + os.path.sep + "go_summary" + os.path.sep + self.analysisID + "_go_summary.csv'>GO summary</a><br>\n")

        f.write("<table border='1' align='center'>\n")
        f.write("<tr>\n")
        f.write("<td align='center'>" + 'File Index' + "</td>")
        if self.covariates != None:
            for covar in self.covariates.keys():
                f.write("<td align='center'>" + covar + "</td>")
        for label in self.masterLabelList:
                f.write("<td align='center'>" + str(int(label)) + "</td>")        
        f.write("\n")
        f.write("</tr>\n")

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

            f.write("<td align='center'>" + str(int(i)) + "</td>")
            if self.covariates != None:
                for key,item in self.covariates.iteritems():
                    f.write("<td align='center'>" + item[i] + "</td>")
            for percent in colToPlot:
                f.write("<td align='center'>" + str(round(percent,2)) + "</td>")        
            f.write("\n")
            f.write("</tr>\n")

        f.write("</table>")
        f.write("</html>")
        f.close()

    
                   
