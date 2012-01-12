#!/usr/bin/python

import sys,getopt,os,re,time,csv,ast,cPickle
import numpy as np
import fcm
from cytostream.tools import read_txt_to_file_channels, read_txt_into_array

if len(sys.argv) < 3:
    print sys.argv[0] + " -f filePath -h homeDir -d dataType -t transform"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:d:t:c:m:a:')
except getopt.GetoptError:
    print sys.argv[0] + "-f filePath -h homeDir -d dataType"
    print "Note: fileName (-f) full file path" 
    print "      homeDir  (-h) home directory for current project"
    print "             k (-d) data type ('fcs','comma','tab')"
    print " fileChansPath (-c) file channels path"
    print " autoComp      (-a) auto compensation flag"
    sys.exit()

transform = 'log'
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

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

autoComp = ast.literal_eval(str(autoComp))
if autoComp not in [True,False]:
    print "WARNING: LoadFile invalid value for autoComp", autoComp
    autoComp = True

if os.path.isfile(filePath) == False:
    print "INPUT ERROR: file path does not exist", filePath
    sys.exit()

if compensationFilePath != "None" and os.path.isfile(filePath) == False:
    print "INPUT ERROR: compensation matrix file  path does not exist", compensationFilePath
    sys.exit()

if dataType not in ['fcs','tab','comma','array']:
    print "INPUT ERROR: bad data type specified", dataType
    sys.exit()

if transform not in ['logicle','log',None]:
    print "INPUT ERROR: bas data transform specified ", transform
    sys.exit()

## variables
projName = os.path.split(homeDir)[-1]

if dataType == 'fcs':
    if compensationFilePath != "None":
        osidx, ospill = fcm.load_compensate_matrix(compensationFilePath)
        fcsData = fcm.loadFCS(filePath,sidx=osidx,spill=ospill,auto_comp=autoComp)
    else:
        fcsData = fcm.loadFCS(filePath,auto_comp=autoComp)
    fileChannels = fcsData.channels

    if transform != None:
        pass
    if transform == 'logicle':
        fcsData.logicle(scale_max=262144)
    if transform == 'log':
        fcsData.log(fcsData.markers)

elif dataType == 'comma':
    fcsData = read_txt_into_array(filePath,delim=',')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)
elif dataType == 'tab':
    fcsData = read_txt_into_array(filePath,delim='\t')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)
    
## prepare to save np.array of data and the channels
newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
newDataFileName = newFileName + "_data.array"
newDataFilePath = os.path.join(homeDir,'data',newDataFileName) 
newChanFileName = newFileName + "_channels.pickle" 
newChanFilePath = os.path.join(homeDir,'data',newChanFileName)

## save
data = fcsData[:,:].copy()
data.tofile(newDataFilePath)
fileChannels = [chan for chan in fileChannels]
tmp = open(newChanFilePath,'w')
cPickle.dump(fileChannels,tmp)
tmp.close()
