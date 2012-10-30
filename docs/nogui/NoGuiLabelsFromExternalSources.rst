.. cytostream nogui tutorial file, created by ARichards

================================
Importing labels into cytostream
================================

The full example file for this example can be downloaded as a script:
:download:`LoadingExternalLabels.py </examples/LoadingExternalLabels.py>`. 


Initializing a project
**********************

In the same way we initialize a project in the
:doc:`NoGuiProjectCreation` example. we do the same here.

.. literalinclude:: /examples/LoadingExternalLabels.py
   :language: python
   :emphasize-lines: 4-5
   :lines: 1-29

The highlighted lines are used to import the functions necessary to
run kmeans clustering from `scikit-learn
<http://scikit-learn.org/stable>`_.

Run a model
***********

At this point a model may be run within Python or event labels may be
loaded from external sources using Python.  In fact, the labels may
come from anywhere---they must however be a label for each event in
the file and the order must be preserved.

.. literalinclude:: /examples/LoadingExternalLabels.py
   :language: python
   :emphasize-lines: 13,20
   :lines: 30-52

The important lines used to save labels and a labels log file are highlighted.

For consistency it is recommended that a labels file is loaded for 
each file in a project under a given **labelsID**.


Loading the labels
******************

To load the labels stored in a given project use:

.. literalinclude:: /examples/LoadingExternalLabels.py
   :language: python
   :lines: 53-56

As shown the **getLog** flag may be used determine whether or not the
log file is returned.

