#!/usr/bin/env python                                                                                                                                                                                                                                                         

from distutils.core import setup

setup(name='cytostream',
            version='0.1',
            description='A gui to carry out flow cytometry analyses using mixture models',
            author='Adam J Richards, ',
            author_email='adam.richards@stat.duke.edu',
            url='http://code.google.com/p/cytostream/',
            packages=['cytostream','cytostream.qtlib','cytostream.tools'],
            long_description = '',
            license='GNU GPL v3',
            )
