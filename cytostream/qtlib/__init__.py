from BasicWidgets import Slider, ProgressBar, DisplayImage
from EditMenu import EditMenu
from FileSelector import FileSelector
from SubsetSelector import SubsetSelector
from MenuFunctions import create_menubar_toolbar, create_action, add_actions
from BulkNewProject import BulkNewProject
from OpenExistingProject import OpenExistingProject
from ScatterPlotter import ScatterPlotter
from MultiplePlotter import MultiplePlotter
from TwoWayViewer import TwoWayViewer
from DataProcessingCenter import DataProcessingCenter
from QualityAssuranceCenter import QualityAssuranceCenter
from ThumbnailViewer import ThumbnailViewer
from ModelCenter import ModelCenter
from ModelDock import ModelDock
from PipelineDock import PipelineDock
from BlankPage import BlankPage
from ResultsNavigationDock import ResultsNavigationDock
from OneDimViewer import OneDimViewer
from OneDimViewerDock import OneDimViewerDock
from LeftDock import add_left_dock, remove_left_dock
from StateTransitions import move_to_initial, move_to_data_processing,move_to_open, move_to_quality_assurance
from StateTransitions import move_to_model, move_transition
from MainWindow import MainWindow
#from Main import Main
