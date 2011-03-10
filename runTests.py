#!/usr/bin/python 
import unittest,sys,os,getopt

import matplotlib as mpl
if mpl.get_backend() == 'MacOSX':
    mpl.use('Agg')

from unittests import *
unittest.main()
