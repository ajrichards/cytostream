#!/usr/bin/python 
import unittest,sys,os,getopt

## change working dir
os.chdir(os.path.join(".","cytostream"))
sys.path.append(os.path.join("..","unittests","data"))

from unittests import *
unittest.main()
