#!/usr/bin/env python

import os
import fcm
import fcm.statistics
import pickle
import numpy as np

print 'loading data'
fileNameFCS = os.path.join("..","cytostream","example_data","3FITC_4PE_004.fcs")
file = fcm.loadFCS(fileNameFCS)
print 'loading model'
mod = fcm.statistics.DPMixtureModel(file, 16)
mod.fit(verbose=True)


full = mod.get_results()

print full.pis


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
