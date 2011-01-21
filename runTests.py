#!/usr/bin/python 
import unittest,sys,os,getopt

import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')

from unittests import *
unittest.main()
