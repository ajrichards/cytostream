.. Cytostream documentation, created by ARichards

========================
Cytostream API Tutorials
========================
Tutorials to use cytostream through the use of Python scripting
_______________________________________________________________

Cytostream is a project centric software and it was developed so that
projects could be created using the graphical interface or through
interaction or with a simple Python class called NoGuiAnalysis.  As
with the GUI version of cytostream the NoGuiAnalysis can load FCS,
NumPy array, and comma separated value (csv) formatted data into a
project.

In fact everything that the Cytostream GUI has to offer is available
through the NoGuiAnalysis class.  This is convenient for biologists
who wish to use both the GUI and the programmatic interfaces.  For
example one could create and run the models for several projects using
the scripting interface then the GUI would serve to explore the
results and create reports.

The NoGuiAnalysis class has however only the minimum required amount
of functions to replicate the GUI analysis in order to provide unit
test coverage.  To some users the options may be limited.  If this is
the case then these users may feel more at home in the environment
offered by `FCM <http://code.google.com/p/py-fcm>`_, which is the
underlying engine for Cytostream.


.. toctree::
   :maxdepth: 1

   /nogui/NoGuiProjectCreation
   /nogui/NoGuiCompensationTransformation
   /nogui/NoGuiQualityAssurance
   /nogui/NoGuiRunningModels
   /nogui/NoGuiLabelsFromExternalSources
   /nogui/NoGuiChannelNameMapping

Useful links
^^^^^^^^^^^^

   * `The Python tutorial <http://docs.python.org/tutorial>`_
   * `NumPy tutorial <http://scipy.org/NumPy_Tutorial>`_
   * `NumPy for MATLAB users <http://www.scipy.org/NumPy_for_Matlab_Users>`_ 
