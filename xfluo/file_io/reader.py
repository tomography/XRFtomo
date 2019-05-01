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

"""
Module for importing raw data files.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import dxchange
import numpy as np 

__author__ = "Francesco De Carlo, Fabricio S. Marin"
__copyright__ = "Copyright (c) 2018, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'
__all__ = ['read_projection',
           'read_elements',
           'find_index',
           'read_mic_xrf']

def find_index(a_list, element):
    try:
        return a_list.tolist().index(element)
    except ValueError:
        return None


def read_elements(h5fname, img_tag, element_tag):
    return(dxchange.read_hdf5(h5fname, "{}/{}".format(img_tag, element_tag)))

def read_channel_names(h5fname):
    b_channel_names = dxchange.read_hdf5(h5fname, "MAPS/channel_names")
    channel_names = []
    for i, e in enumerate(b_channel_names):
        channel_names.append(e.decode('utf-8'))
    return(channel_names)


def read_projection(fname, element, img_tag, data_tag, element_tag):
    """
    Reads a projection for a given element from a single xrf hdf file.

    Parameters
    ----------
    fname : str
        String defining the file name

    element : 
        String defining the element to select
    

    Returns
    -------
    ndarray
        projection
    
    """

    elements = read_elements(fname, img_tag, element_tag)

    # if theta_index == None:
    #     print(fname)
    #     projections = dxchange.read_hdf5(fname, "{}/{}".format(img_tag,data_tag))
    #     # theta = dxchange.read_hdf5(fname, "{}/theta".format(img_tag))

    # else:
    print(fname)
    projections = dxchange.read_hdf5(fname, "{}/{}".format(img_tag,data_tag))
        # theta = dxchange.read_hdf5(fname, "MAPS/extra_pvs_as_csv")[theta_index].split(b',')[1]

    return projections[find_index(elements, element)]


def read_projection_old(fname, element, theta_index, img_tag, data_tag, element_tag):
    """
    Reads a projection for a given element from an hdf file.

    Parameters
    ----------
    fname : str
        String defining the file name
    element : 
        String defining the element to select
    theta_index :
        index where theta is saved under in the hdf MAPS/extra_pvs_as_csv tag

    Returns
    -------
    float
        projection angle
    ndarray
        projection
    """

    elements = read_elements(fname, img_tag, element_tag)

    if theta_index == None:
        print(fname)
        projections = dxchange.read_hdf5(fname, "{}/{}".format(img_tag,data_tag))
        theta = dxchange.read_hdf5(fname, "{}/theta".format(img_tag))

    else:
        print(fname)
        projections = dxchange.read_hdf5(fname, "{}/{}".format(img_tag,data_tag))
        theta = dxchange.read_hdf5(fname, "MAPS/extra_pvs_as_csv")[theta_index].split(b',')[1]

    return projections[find_index(elements, element)], theta


def read_mic_xrf(path_files, element_index, theta_index, img_tag, data_tag, element_tag):

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

    elements = read_elements(path_files[0], img_tag, element_tag)
    max_y, max_x = 0, 0
    for i in range(len(path_files)):
        proj = read_projection(path_files[i], elements[0], img_tag, data_tag, element_tag)
        if proj.shape[0] > max_y:
            max_y = proj.shape[0]
        if proj.shape[1] > max_x:
            max_x = proj.shape[1]

    data = np.zeros([len(element_index),len(path_files), max_y, max_x])

    for i in range(len(element_index)):
        indx = element_index[i]

        for j in range(len(path_files)):
            proj = read_projection(path_files[j], elements[indx], img_tag, data_tag, element_tag)
            img_y = proj.shape[0]
            img_x = proj.shape[1]
            dx = np.floor((max_x-img_x)/2).astype(int)
            dy = np.floor((max_y-img_y)/2).astype(int)
            data[i, j, dy:img_y+dy, dx:img_x+dx] = proj
    data[np.isnan(data)] = 0.0001
    data[data == np.inf] = 0.0001

    return data

