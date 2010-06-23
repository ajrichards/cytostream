import sys,os,unittest,time,re
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))
import subprocess
from Model import Model
import numpy as np

## test class for the main window function
class ModelTest(unittest.TestCase):
       
    def setUp(self):
        self.projectID = 'Demo'
        self.homeDir = os.path.join("..","cytostream","projects",self.projectID)
        self.model = Model()
        self.model.initialize(self.projectID, self.homeDir)
        self.fcsPathName = os.path.join("..","cytostream","example_data", "3FITC_4PE_004.fcs") 
        self.fcsFileName ="3FITC_4PE_004.fcs" 

    def testPyfcmLoadFcsFile(self):
        data = self.model.pyfcm_load_fcs_file(self.fcsFileName)
        events,channels = np.shape(data)
        self.assertEqual(events,94569)
        self.assertEqual(channels,4)

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
