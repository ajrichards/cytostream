#!/usr/local/bin/python

'''
Cytostream

Adam Richards
adam.richards@stat.duke.edu

'''

import sys,os,re

if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'qtlib'))

## general classes
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from Logging import Logger
from Model import Model
from Controller import Controller

### qtlib classes
from BasicWidgets import Slider, ProgressBar, DisplayImage
from FileSelector import FileSelector
from MenuFunctions import create_menubar_toolbar
from BulkNewProject import BulkNewProject
from OpenExistingProject import OpenExistingProject
from ScatterPlotter import ScatterPlotter
from DataProcessingCenter import DataProcessingCenter
from DataProcessingDock import DataProcessingDock
from QualityAssuranceDock import QualityAssuranceDock
from ThumbnailViewer import ThumbnailViewer
from ModelCenter import ModelCenter
from ModelDock import ModelDock
from PipelineDock import PipelineDock
from BlankPage import BlankPage
from ResultsNavigationDock import ResultsNavigationDock
from OneDimViewer import OneDimViewer
from OneDimViewerDock import OneDimViewerDock
from LeftDock import add_left_dock

## main classes
from MainWindow import MainWindow
from Main import Main
