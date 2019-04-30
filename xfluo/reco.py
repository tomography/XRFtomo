import os
import logging
import glob
import tempfile
import sys
import numpy as np
import tomopy

LOG = logging.getLogger(__name__)

def tomo(params):

    # use https://github.com/tomography/ufot/blob/master/ufot/reco.py 
    # as a template
    # this module allows for batch reconstruction of multiple data set using
    # the parameters selected/optimized with the xfluo GUI
    # to run it use bin/xfluo rec
    print ("do nothing for now ...")

    rec = True

    return rec