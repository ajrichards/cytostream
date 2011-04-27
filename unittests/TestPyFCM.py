#!/usr/bin/env python

import os,time
import fcm
import fcm.statistics
import pickle
import numpy as np

#print 'listing shared library depens.'
#os.system("ldd /home/clemmys/research/py-fcm-gpu/src/statistics/_cdp.so")

print 'loading data'
#fileNameFCS = os.path.join("..","cytostream","example_data","3FITC_4PE_004.fcs")
fileNameFCS = "/home/clemmys/research/eqapol/donors/../materials/EQAPOL_4c_ICS_Donor_Screening/Assay_Data/EQAPOL_4c_ICS_08Apr11/FCS files/H6904VB6_01 Costim 3 C3.031"
fileFCS = fcm.loadFCS(fileNameFCS)

print 'get subsample'
subsample = 1e4
np.random.seed(99)
n,d = np.shape(fileFCS)
subsampleIndices = np.random.random_integers(0,n-1,subsample)
data = fileFCS[subsampleIndices,:]

print 'loading model'
mod = fcm.statistics.DPMixtureModel(data, 16)
print 'cuda device:', mod.cdp.getdevice()

print 'running model'
modelRunStart = time.time()
mod.fit(verbose=False)
modelRunStop = time.time()
print "model run time: %s"%(modelRunStop - modelRunStart)

#full = mod.get_results()
#print full.pis
#classifyComponents = full.classify(data)
#modes = full.make_modal()
#classifyModes = modes.classify(data)


#print 'dumping fit'
#tmp = open('/home/jolly/Projects/Janet_Normal_data/pickle/full.pickle','w')
#pickle.dump(full, tmp)
#tmp.close()
#print 'making modal'
#modal = fufill.mamodal()
#print 'dumping modal'
#tmp = open('/home/jolly/Projects/Janet_Normal_data/pickle/modal.pickle','w')
#pickle.dump(modal, tmp)
#tmp.close()
#print 'done'
#print file.summary()
#print 'channels',file.channels
#print 'scatters',file.scatters
#print 'markers',file.markers



#comp,mark = fcm.load_compensate_matrix('/home/jolly/Projects/Janet_Normal_data/data/CompMatrixDenny06Nov09jhe')
