.. cytostream nogui tutorial file, created by ARichards

================
Project creation
================

The full example file for this example can be downloaded as a script:
:download:`BasicExample.py </examples/BasicExample.py>`. In
order to run this example on your computer Cytostream must be
installed and the following data files need to be downloaded to the
same directory that you intend to run this example from.

* :download:`G69019FF_Costim_CD4.fcs </examples/G69019FF_Costim_CD4.fcs>`
* :download:`G69019FF_SEB_CD4.fcs </examples/G69019FF_SEB_CD4.fcs>`
* :download:`G69019FF_CMVpp65_CD4.fcs </examples/G69019FF_CMVpp65_CD4.fcs>`

Importing Cytostream
********************

Imports the NoGuiClass form Cytostream.

.. literalinclude:: /examples/BasicExample.py
   :language: python
   :emphasize-lines: 4
   :lines: 1-4

Required arguments
******************

If you have trouble importing cytostream then visit the
:doc:`/Installation` page.  Next we need to give a name to the project
and specify its location (*homeDir*).

.. literalinclude:: /examples/BasicExample.py
   :language: python
   :lines: 5-10

The fcs files are then specified in a python list.

.. literalinclude:: /examples/BasicExample.py
   :language: python
   :lines: 10-14

Finally we use the NoGuiAnalysis object to load the files into a
cytostream project which is completely contained in the specified
*homeDir*.

Creating a project
******************

.. literalinclude:: /examples/BasicExample.py
   :language: python
   :lines: 14-19

During the creation of a project NoGuiAnalysis attempts map each
channel automatically to a name that it understands and we can check
to see if all channels were identified by

.. literalinclude:: /examples/BasicExample.py
   :language: python
   :lines: 20-22

If the output of this variable is *False* or if you wish to learn more
about how to map channels to cytosteams list of official names the see
:doc:`NoGuiChannelNameMapping`.

Several assumption are made in this example. First, because these
files are subsets of events exported from another software these data
have been previously compensated so the input argument *autoComp* is
set to False, however the default is True.  For more visit
:doc:`NoGuiCompensationTransformation`.
