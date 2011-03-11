#!/usr/bin/python

import sys,getopt,os,re,cPickle,time,csv
import fcm
from cytostream.tools import read_txt_to_file_channels, read_txt_into_array

if len(sys.argv) < 3:
    print sys.argv[0] + " -f filePath -h homeDir -d dataType -t transform"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:d:t:c:')
except getopt.GetoptError:
    print sys.argv[0] + "-f filePath -h homeDir -d dataType"
    print "Note: fileName (-f) full file path" 
    print "      homeDir  (-h) home directory for current project"
    print "             k (-d) data type ('fcs','comma','tab')"
    print " fileChansPath (-c) file channels path"
    sys.exit()

transform = 'log'
filePath = None
homeDir = None
dataType = 'fcs'
for o, a in optlist:
    if o == '-f':
        filePath = a
    if o == '-h':
        homeDir = a
    if o == '-d':
        dataType = a
    if o == '-t':
        transform = a
    if o == '-c':
        fileChannelsPath = a

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

if os.path.isfile(filePath) == False:
    print "INPUT ERROR: file path does not exist", filePath
    sys.exit()

if dataType not in ['fcs','tab','comma']:
    print "INPUT ERROR: bad data type specified", dataType
    sys.exit()

if transform not in ['logicle','log']:
    print "INPUT ERROR: bas data transform specified ", dataType
    sys.exit()
    
## variables
projName = os.path.split(homeDir)[-1]

if dataType == 'fcs':
    fcsData = fcm.loadFCS(filePath,transform=transform)
    fileChannels = fcsData.channels
elif dataType == 'comma':
    fcsData = read_txt_into_array(filePath,delim=',')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)
elif dataType == 'tab':
    fcsData = read_txt_into_array(filePath,delim='\t')
    fileChannels = read_txt_to_file_channels(fileChannelsPath)

## save the np.array of data and the channels
newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
newDataFileName = newFileName + "_data_original.pickle"
newChanFileName = newFileName + "_channels_original.pickle" 

tmp1 = open(os.path.join(homeDir,'data',newDataFileName),'w')
tmp2 = open(os.path.join(homeDir,'data',newChanFileName),'w')
data = fcsData[:,:].copy()
cPickle.dump(data,tmp1)
cPickle.dump([chan for chan in fileChannels],tmp2)
tmp1.close()
tmp2.close()
