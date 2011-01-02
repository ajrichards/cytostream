import sys,os,unittest,time,re
from cytostream import Controller, Model

## test class for the Model
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
        self.homeDir = os.path.join(BASEDIR,"cytostream","projects",self.projectID)
        self.model = Model()
        self.model.initialize(self.projectID, self.homeDir)
        self.fcsFilePathName = os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")
        self.fileName = "3FITC_4PE_004.fcs"
        self.assertTrue(os.path.isfile(self.fcsFilePathName))

        ## load the file
        self.model.load_files([self.fcsFilePathName])
        fileName = re.sub('\.fcs|\.txt|\.out','',self.fileName)
        newDataFileName = fileName +"_data_original.pickle"
        newChanFileName = fileName +"_channels_original.pickle"

    def testLoadFile(self):
        ## test that events and channels may be retrieved 
        self.model.load_files([self.fcsFilePathName])
        fileName = re.sub('\.fcs|\.txt|\.out','',self.fileName)
        newDataFileName = fileName +"_data_original.pickle"
        newChanFileName = fileName +"_channels_original.pickle"

        self.assertTrue(os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)))
        self.assertTrue(os.path.isfile(os.path.join(self.homeDir,'data',newChanFileName)))

    def testGetEventsChannels(self):
        fileName = re.sub('\.fcs|\.txt|\.out','',self.fileName)
        events = self.model.get_events(fileName,subsample='original')
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)
        fileChannels = self.model.get_file_channel_list(fileName)
        self.assertEqual(len(fileChannels),4)

    def testGetMasterChannelList(self):
        allChannels = self.model.get_master_channel_list()
        self.assertEqual(len(allChannels),4)

    def testGetSubsampleIndices(self):
        fromStrInput = self.model.get_subsample_indices('1e3')
        fromIntInput = self.model.get_subsample_indices(1000)
        self.assertEqual(len(fromStrInput),1000)
        self.assertEqual(len(fromIntInput),1000)

### Run the tests 
if __name__ == '__main__':
    unittest.main()
