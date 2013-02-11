#!/usr/bin/env python                          
import sys,os,unittest
from cytostream import Controller, NoGuiAnalysis
from cytostream.stats import get_positivity_threshold,get_positive_events

'''
description - Tests the positivity thresholding scripts
'''

__author__ = "AJ Richards"

class PositivityThresholding(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(debug=False)
        self.dataDir = os.path.realpath(os.path.join(self.controller.baseDir,'example_data'))
        self.sandbox = os.path.realpath(os.path.join(self.controller.baseDir,'sandbox'))

    def test_for_data(self):
        self.assertTrue(os.path.isdir(self.dataDir))
        self.assertTrue(os.path.exists(os.path.join(self.dataDir,"G69019FF_Costim_CD4.fcs")))
        self.assertTrue(os.path.exists(os.path.join(self.dataDir,"G69019FF_SEB_CD4.fcs")))
        self.assertTrue(os.path.exists(os.path.join(self.dataDir,"G69019FF_CMVpp65_CD4.fcs")))
        
    def test_positivity_scirpts(self):

        ## declare variables
        cytokine = 'IL2'
        beta = 0.2
        theta = 1.0
        stimulationList = "CMVpp65"
     
        ## specify the file path list
        fileNameList = ["G69019FF_Costim_CD4.fcs","G69019FF_SEB_CD4.fcs","G69019FF_CMVpp65_CD4.fcs"]
        filePathList = [os.path.join(self.dataDir, fn) for fn in fileNameList]
        homeDir = os.path.join(self.sandbox,'positivity')
        nga = NoGuiAnalysis(homeDir,filePathList,autoComp=False)
        allFiles = nga.get_file_names()
        fileChannels = nga.get_file_channels()

        ## find the positivity threshold
        posControlFile = 'G69019FF_SEB_CD4'
        negControlFile = 'G69019FF_Costim_CD4'
        positiveEvents = nga.get_events(posControlFile)
        negativeEvents = nga.get_events(negControlFile)
        fResults = get_positivity_threshold(negativeEvents,positiveEvents,nga.channelDict[cytokine],
                                            beta=beta,theta=theta)

        ## get the percentages and indices of the positive events
        eventsList = [nga.get_events(fn) for fn in allFiles]
        percentages,idx = get_positive_events(allFiles,nga.channelDict[cytokine],
                                              fResults['threshold'],eventsList)

        ## ensure correct results
        self.assertTrue(percentages["G69019FF_Costim_CD4"] < 1.0)
        self.assertTrue(percentages["G69019FF_CMVpp65_CD4"] < 5.0)
        self.assertTrue(percentages["G69019FF_SEB_CD4"] < 30.0)

### Run the tests 
if __name__ == '__main__':
    unittest.main()
