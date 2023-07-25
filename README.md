Documentation
=============

To be completed


Pre-requisites
==============

Install Anaconda3 and create a python 3.6 conda environment:

    $ conda create -n xrf
    $ source activate xrf
    
add conda channels:

    $ conda config --add channels conda-forge
    $ conda config --add channels fabriciosm

Installation
============

Install with: 

    $ conda install -c fabriciosm xrftomo 

Usage
=====

You can run xrftomo using a command line, for a full list of options use: 

    $ bin/xrftomo gui -h

or a GUI with:

    $ xrftomo gui
    $ xrftomo gui --experimental

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
