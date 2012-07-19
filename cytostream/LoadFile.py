#!/usr/bin/python

import sys,getopt,os,re,time,csv,ast,cPickle,time
import numpy as np
import fcm
from Logging import Logger

if len(sys.argv) < 3:
    print sys.argv[0] + " -f filePath -h homeDir -d dataType -t transform"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:d:t:c:m:a:l:')
except getopt.GetoptError:
    print sys.argv[0] + "-f filePath -h homeDir -d dataType"
    print "Note: fileName   (-f) full file path" 
    print "      homeDir    (-h) home directory for current project"
    print "             k   (-d) data type ('fcs','comma','tab')"
    print " fileChansPath   (-c) file channels path"
    print " autoComp        (-a) auto compensation flag"
    print " logicleScaleMax (-l) logicle scale maximum"
    sys.exit()

transform = 'logicle'
filePath = None
homeDir = None
dataType = 'fcs'
autoComp = True
for o, a in optlist:
    if o == '-f':
        filePath = a
    if o == '-h':
        homeDir = a
    if o == '-d':
        dataType = a
    if o == '-t':
        transform = a
    if o == '-a':
        autoComp = a
    if o == '-c':
        fileChannelsPath = a
    if o == '-m':
        compensationFilePath = a
    if o == '-l':
        logicleScaleMax = int(float(a))

if dataType != 'fcs':
    from cytostream.tools import read_txt_to_file_channels, read_txt_into_array

#fcsData = fcm.loadFCS(filePath)
#print 'hello'
#data = fcm.loadFCS('/home/clemmys/research/eqapol/sendout1/analysis1/EQAPOL_4C_Pregated/CD8+Cyto+/101_08Jul11_C05_013_CD8_Cyto.fcs')

if homeDir == None:
    print "INPUT ERROR: LoadFile.py --- no home dir specified", homeDir
    sys.exit()

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: LoadFile.py --- not a valid project", homeDir
    sys.exit()

autoComp = ast.literal_eval(str(autoComp))
if autoComp not in [True,False]:
    print "WARNING: LoadFile.py --- invalid value for autoComp", autoComp
    autoComp = True

if os.path.isfile(filePath) == False:
    print "INPUT ERROR: LoadFile.py --- file path does not exist", filePath
    sys.exit()

if compensationFilePath != "None" and os.path.isfile(filePath) == False:
    print "INPUT ERROR: LoadFile.py --- compensation matrix file  path does not exist", compensationFilePath
    sys.exit()

if dataType not in ['fcs','tab','comma','array']:
    print "INPUT ERROR: LoadFile.py --- bad data type specified", dataType
    sys.exit()

if str(transform) not in ['logicle','log','None']:
    print "INPUT ERROR: LoadFile.py --- bad data transform specified ", transform
    sys.exit()

## variables
projName = os.path.split(homeDir)[-1]

if dataType == 'fcs':
    if str(compensationFilePath) != "None":
        osidx, ospill = fcm.load_compensate_matrix(compensationFilePath)
        fcsData = fcm.loadFCS(filePath,sidx=osidx,spill=ospill,auto_comp=autoComp,transform=None)
    else:
        fcsData = fcm.loadFCS(filePath,auto_comp=autoComp,transform=None)

    ## get channel max
    scaleMax = int(fcsData.notes.text['p1r'])
    if scaleMax == 1024:
        log = Logger()
        log.initialize(homeDir,load=True)
        log.log['logicle_scale_max'] = scaleMax 
        log.write()
        logicleScaleMax = scaleMax
    
    ## handle transform
    isTransformed = False
    if str(transform) == 'None':
        isTransformed = True
    
    if fcsData.notes.header['version'] < 2.0:
        isTransformed = True

    if isTransformed == False:
        if transform == 'logicle':
            fcsData.logicle(scale_max=logicleScaleMax)
        if transform == 'log':
            fcsData.log()
    
    ## for debugging
    #print transform
    #print autoComp
    #fcsData = fcm.loadFCS(filePath,auto_comp=True,trasform=None)
    
    ## get channels
    fileChannels = fcsData.channels
    
elif dataType == 'comma':
    fcsData = read_txt_into_array(filePath,delim=',')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)
elif dataType == 'tab':
    fcsData = read_txt_into_array(filePath,delim='\t')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)
    
## prepare to save np.array of data and the channels
newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
newDataFileName = newFileName + "_data.npy"
newDataFilePath = os.path.join(homeDir,'data',newDataFileName) 
newChanFileName = newFileName + "_channels.pickle" 
newChanFilePath = os.path.join(homeDir,'data',newChanFileName)

## save
data = fcsData[:,:].copy()
np.save(newDataFilePath,data)

## save channels
fileChannels = [chan for chan in fileChannels]
tmp = open(newChanFilePath,'w')
cPickle.dump(fileChannels,tmp)
tmp.close()
