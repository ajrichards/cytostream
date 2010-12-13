import sys,os,unittest,time,re
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))
import subprocess
from Model import Model
import numpy as np

## test class for the main window function
class ModelTest(unittest.TestCase):

    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        self.projectID = 'utest'
        self.homeDir = os.path.join(BASEDIR,"gdiqt4","projects",self.projectID)
        self.model = Model()
        self.model.initialize(self.projectID, self.homeDir)
        self.fcsPathName = os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs") 
        self.fcsFileName ="3FITC_4PE_004.fcs" 
        self.assertTrue(os.path.isfile(self.testFilePathName))

    def testPyfcmLoadFcsFile(self):
        ## test that events and channels may be retrieved 
        #fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        #fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        #events = self.model.get_events(fileName,subsample='original')
        #self.assertEqual(events.shape[0],94569)
        #self.assertEqual(events.shape[1],4)
        self.model.load_files([self.testFilePathName])
        fName = re.sub('\s+','_',os.path.split(self.fileName)[-1])
        fName = re.sub('\.fcs|\.txt|.\out','',fName)
        events = self.model.get_events(fName,subsample='original')
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)
       
        fileChannels = self.model.get_file_channel_list(fName,subsample='original')
        self.assertEqual(len(fileChannels),4)

    def testGetMasterChannelList(self):
        allChannels = self.model.get_master_channel_list()
        self.assertEqual(len(allChannels),4)

    def testGetSubsampleIndices(self):
        fromStrInput = self.model.get_subsample_indices('1e3')
        fromIntInput = self.model.get_subsample_indices(1000)
        self.assertEqual(len(fromStrInput),1000)
        self.assertEqual(len(fromIntInput),1000)

    def testGetFileChannelList(self):
        fileChannelList = self.model.get_file_channel_list(self.fcsFileName)
        self.assertEqual(len(fileChannelList),4)

    #def testLoadFile(self):
    #    ## test that events and channels may be retrieved
    #    self.model.load_files([self.testFilePathName])
    #    fName = re.sub('\s+','_',os.path.split(self.fileName)[-1])
    #    fName = re.sub('\.csv|\.txt','',fName)
    #    geneList = self.model.get_genes(fName)
    #    self.assertEqual(len(geneList),7)

    #def testGetAllGeneLists(self):
    #    allGeneLists = get_gene_list_names(self.homeDir)
    #    self.assertEqual(len(allGeneLists),1)

### Run the tests 
if __name__ == '__main__':
    unittest.main()

'''
## test class for the main window function
class ModelTest(unittest.TestCase):
       
    def setUp(self):
        self.projectID = 'utest'
        self.homeDir = os.path.join("..","cytostream","projects",self.projectID)
        self.model = Model()
        self.model.initialize(self.projectID, self.homeDir)
        self.fcsPathName = os.path.join("..","cytostream","example_data", "3FITC_4PE_004.fcs") 
        self.fcsFileName ="3FITC_4PE_004.fcs" 

    def testPyfcmLoadFcsFile(self):
        ## test that events and channels may be retrieved 
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.model.get_events(fileName,subsample='original')
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)

        fileChannels = self.model.get_file_channel_list(fileName,subsample='original')
        self.assertEqual(len(fileChannels),4)

    def testGetMasterChannelList(self):
        allChannels = self.model.get_master_channel_list()
        self.assertEqual(len(allChannels),4)

    def testGetSubsampleIndices(self):
        fromStrInput = self.model.get_subsample_indices('1e3')
        fromIntInput = self.model.get_subsample_indices(1000)
        self.assertEqual(len(fromStrInput),1000)
        self.assertEqual(len(fromIntInput),1000)

    def testGetFileChannelList(self):
        fileChannelList = self.model.get_file_channel_list(self.fcsFileName)
        self.assertEqual(len(fileChannelList),4)

### Run the tests 
if __name__ == '__main__':
    unittest.main()
'''
