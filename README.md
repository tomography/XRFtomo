Documentation
=============

* Readthedocs: https://xfluo.readthedocs.io/en/latest/index.html



Features
========

* X-ray fluorescence data processing.


Pre-requisites
==============

Create a python 3.7 conda environment:

    $ conda create -n py37 python=3.7
    $ source activate py37

Make sure that the packages listed in the requirements.txt file are installed


Installation
============
   
    $ git clone https://github.com/tomography/xfluo.git
    $ cd xfluo
    $ python setup.py install

in the prepared virtualenv or as root for system-wide installation.


Usage
=====

You can run xfluo using a command line, for a full list of options use: 

    $ bin/xfluo gui -h

or a GUI with:

    $ bin/xfluo gui

```
If your python installation is in a location different from #!/usr/bin/env python please edit the first line of the bin/xfluo file to match yours.
```

You can also load configuration parameters from a configuration file called
`xfluo.conf`. You can create a template with

    $ xfluo init

 
Contribute
==========

* Issue Tracker: https://github.com/tomography/xfluo/issues
* Documentation: https://github.com/tomography/xfluo/tree/master/docs
* Source Code: https://github.com/tomography/xfluo/tree/master/xfluo

License
=======

The project is licensed under the 
`BSD-3 <https://github.com/tomography/xfluo/blob/master/LICENSE.txt>`_ license.
