import sys,os

## add the leftdock files
if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",self.baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'leftdock'))

## files requiring no cytostream deps
from MoreInfo import *
from BasicWidgets import Slider, ProgressBar, Imager, RadioBtnWidget,Waiting
from BasicFunctions import move_transition
from OpenExistingProject import OpenExistingProject
from EditMenu import EditMenu
from Preferences import Preferences
from ChannelSelector import ChannelSelector
from FileSelector import FileSelector
from PlotSelector import PlotSelector
from PlotTickControls import PlotTickControls
from SubsampleSelector import SubsampleSelector
from VizModeSelector import VizModeSelector
from ModelToRunSelector import ModelToRunSelector
from ModelTypeSelector import ModelTypeSelector
from KSelector import KSelector
from TextEntry import TextEntry
from OneDimViewer import OneDimViewer

## files requireing only 1st level deps
from DataProcessingCenter import DataProcessingCenter
from QualityAssuranceCenter import QualityAssuranceCenter
from ModelCenter import ModelCenter
from ResultsNavigationCenter import ResultsNavigationCenter
from FileAlignerCenter import FileAlignerCenter
from LeftDock import add_left_dock, remove_left_dock
from Transitions import Transitions
from MenuFunctions import create_menubar_toolbar, create_action, add_actions, restore_docks
from CytostreamPlotter import CytostreamPlotter
#from MultiplePlotter import MultiplePlotter
from NWayViewer import NWayViewer

from ThumbnailViewer import ThumbnailViewer
from PipelineDock import PipelineDock
from MainWindow import MainWindow

