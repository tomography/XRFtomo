Documentation
=============

* Readthedocs: https://xfluo.readthedocs.io/en/latest/index.html

Features
========

* X-ray fluorescence data processing.


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
    $ conda install -c fabriciosm xfluo 

OR install from source along with all dependencies:

    $ git clone https://github.com/FabricioSMarin/xfluo.git
    $ cd xfluo
    $ conda install -c conda-forge dxchange
    $ conda install -c conda-forge tomopy
    $ conda install -c conda-forge ...

    $ python setup.py install
    $ cd bin 
    $ python xfluo init

in the prepared virtualenv or as root for system-wide installation.

Usage
=====

You can run xfluo using a command line, for a full list of options use: 

    $ bin/xfluo gui -h

or a GUI with:

    $ bin/xfluo gui
    $ or double-click on xfluo.sh

```
If your python installation is in a location different from #!/usr/bin/env python please edit the first line of the bin/xfluo file to match yours.
```

You can also load configuration parameters from a configuration file called
`xfluo.conf`. You can create a template with

    $ xfluo init
    $ or double-click xfluo_init.sh

Contribute
==========

* Issue Tracker: https://github.com/tomography/xfluo/issues
* Documentation: https://github.com/tomography/xfluo/tree/master/docs
* Source Code: https://github.com/tomography/xfluo/tree/master/xfluo

License
=======

The project is licensed under the 
`BSD-3 <https://github.com/tomography/xfluo/blob/master/LICENSE.txt>`_ license.
