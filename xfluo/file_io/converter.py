#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2018. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import xfluo
import numpy as np
from pylab import *

__author__ = "Fabricio S. Marin"
__copyright__ = "Copyright (c) 2019, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'
__all__ = ['convert_to_array']

def convert_to_array(path_files, use_elements, theta_index, img_tag, data_tag, element_tag):

    """
    Converts hdf files to numpy arrays for plotting and manipulation.

    Parameters
    ----------
    path_files: list
    	List of path+filenames
    use_elements : list
        List of string element names selected in checkboxes
    theta_index: int
        index position of theta PV
    img_tag: str
        image tag for hdf file
    data_tag: str
        data tag for corresponding image tag 
    element_tag: str
        The element tag contianing a list of elements for the particular data tag.
    Returns
    -------
    ndarray: ndarray
        4D array [elements, projection, y, x]
    """

    elements = xfluo.read_elements(path_files[0], img_tag, element_tag)
    max_y, max_x = 0, 0
    for i in range(len(path_files)):
        proj, dummy = xfluo.read_projection(path_files[i], elements[0], theta_index, img_tag, data_tag, element_tag)
        if proj.shape[0] > max_y:
            max_y = proj.shape[0]
        if proj.shape[1] > max_x:
            max_x = proj.shape[1]

    data = zeros([len(use_elements),len(path_files), max_y, max_x])

    for i in range(len(use_elements)):
        indx = use_elements.index(use_elements[i])

        for j in range(len(path_files)):
            proj, theta = xfluo.read_projection(path_files[j], elements[indx], theta_index, img_tag, data_tag, element_tag)
            img_y = proj.shape[0]
            img_x = proj.shape[1]
            dx = np.floor((max_x-img_x)/2).astype(int)
            dy = np.floor((max_y-img_y)/2).astype(int)
            data[i, j, dy:img_y+dy, dx:img_x+dx] = proj
    data[isnan(data)] = 0.0001
    data[data == inf] = 0.0001

    return data

