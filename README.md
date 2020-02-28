Documentation
=============

To be completed


Pre-requisites
==============

Install Anaconda and create a python 3.7 conda environment:

    $ conda create -n py37 python=3.7
    $ source activate py37
    
add conda channels:

    $ conda config --add channels conda-forge
    $ conda config --add channels fabriciosm

Installation
============

Install with: 

    $ conda install -c fabriciosm xrftomo 

OR install from source along with all dependencies:

    $ git clone https://github.com/FabricioSMarin/xrftomo.git
    $ cd xrftomo
    $ conda install -c conda-forge dxchange
    $ conda install -c conda-forge tomopy
    $ conda install -c conda-forge pyqt
    $ conda install -c conda-forge h5py
    $ conda install -c conda-forge scikit-image
    $ conda install -c conda-forge pandas
    $ conda install -c conda-forge seaborn
    $ conda install -c conda-forge pyqtgraph
    $ conda install -c conda-forge scipy
    $ conda install git
    $ conda install numpy


    $ python setup.py install
    $ cd bin 
    $ python xrftomo init

in the prepared virtualenv or as root for system-wide installation.

Usage
=====

You can run xrftomo using a command line, for a full list of options use: 

    $ bin/xrftomo gui -h

or a GUI with:

    $ bin/xrftomo gui
    $ or double-click on xrftomo.sh

```
If your python installation is in a location different from #!/usr/bin/env python please edit the first line of the bin/xrftomo file to match yours.
```

You can also load configuration parameters from a configuration file called
`xrftomo.conf`. You can create a template with

    $ xrftomo init
    $ or double-click xrftomo_init.sh

Contribute
==========

* Issue Tracker: https://github.com/tomography/xrftomo/issues
* Documentation: to be completed
* Source Code: https://github.com/tomography/xrftomo/tree/master/xrftomo

License
=======

The project is licensed under the 
`BSD-3 <https://github.com/tomography/xrftomo/blob/master/LICENSE.txt>`_ license.
