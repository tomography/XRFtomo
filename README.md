Documentation
=============

To be completed


Pre-requisites
==============
add conda channels:

    $ conda config --add channels conda-forge
    $ conda config --set channel_priority strict

Install Anaconda3, create a python 3.12 conda environment, install libmamba solver:

    $ conda create -n py312
    $ conda activate py312
    $ conda install -n base conda-libmamba-solver
    $ conda config --set solver libmamba

Installation
============

cd into desired directory and nstall CPU-only version with: 

    $ cd
    $ clone https://github.com/tomography/XRFtomo.git
    $ cd XRFtomo
    $ conda install --file requirements.txt -c conda-forge

Usage
=====

You can run xrftomo using a command line, for a full list of options use: 

    $ xrftomo gui -h

or a GUI with:

    $ xrftomo gui
    $ xrftomo gui --experimental


Contribute
==========

* Issue Tracker: https://github.com/tomography/xrftomo/issues
* Documentation: to be completed
* Source Code: https://github.com/tomography/xrftomo/tree/master/xrftomo

License
=======

The project is licensed under the 
`BSD-3 <https://github.com/tomography/xrftomo/blob/master/LICENSE.txt>`_ license.
