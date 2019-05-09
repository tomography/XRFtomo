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
import xfluo
import h5py

__author__ = "Francesco De Carlo, Fabricio S. Marin"
__copyright__ = "Copyright (c) 2018, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'
__all__ = ['find_elements',
           'read_theta',
           'read_projection',
           'read_channel_names',
           'read_mic_xrf',
           'load_thetas',
           'load_thetas_legacy',
           'load_thetas_9idb',
           'load_thetas_2ide']


def find_index(a_list, element):
    try:
        return a_list.index(element)
    except ValueError:
        return None


def find_elements(channel_names):
    """
    Extract a sorted element list from a channel list

    Parameters
    ----------
    channel_names : list
        List of channel names

    Returns
    -------
    elements : list
        Sorted list of elements
    
    """

    elements = []
    for i in range(1, 110, 1): 
         elements.append(str(xfluo.ELEMENTS[i].symbol))

    elements = sorted(set(channel_names) & set(elements), key = channel_names.index)

    return elements


def read_channel_names(fname, hdf_tag, channel_tag):
    """
    Read the channel names

    Parameters
    ----------
    fname : str
        String defining the file name
    hdf_tag : str
        String defining the hdf5 data_tag name (ex. MAPS)
    channel_tag : str
        String defining the hdf5 channel tag name (ex. channel_names)

    Returns
    -------
    channel_names : list
        List of channel names
    
    """
    b_channel_names = dxchange.read_hdf5(fname, "{}/{}".format(hdf_tag, channel_tag))
    channel_names = []
    for i, e in enumerate(b_channel_names):
        channel_names.append(e.decode('utf-8'))
    return(channel_names)


def read_projection(fname, element, hdf_tag, roi_tag, channel_tag):
    """
    Reads a projection for a given element from a single xrf hdf file

    Parameters
    ----------
    fname : str
        String defining the file name
    element : str
        String defining the element to select
    hdf_tag : str
        String defining the hdf5 data_tag name (ex. MAPS)
    roi_tag: str
        data tag for corresponding roi_tag (ex. XRF_roi)
    channel_tag : str
        String defining the hdf5 channel tag name (ex. channel_names)
    

    Returns
    -------
    ndarray: ndarray
        projection
    
    """

    elements = read_channel_names(fname, hdf_tag, channel_tag)

    print(fname)
    projections = dxchange.read_hdf5(fname, "{}/{}".format(hdf_tag, roi_tag))

    return projections[find_index(elements, element)]


def read_theta(path_files, theta_index, hdf_tag):
    """
    Reads hdf file and returns theta

    Parameters
    ----------
    path_files: list
        List of path+filenames
    theta_index : int
        Index where theta is saved under in the hdf MAPS/extra_pvs_as_csv tag
        This is: 2-ID-E: 663; 2-ID-E (prior 2017): *657*; BNP: 8
    hdf_tag : str
        String defining the hdf5 data_tag name (ex. MAPS)

    Returns
    -------
    ndarray: ndarray
        1D array [theta]
    """

    for i in range(len(path_files)):
        if theta_index == None:
            theta = float(dxchange.read_hdf5(path_files[i], "{}/theta".format(hdf_tag)))
            print(theta)
        else:
            theta = float(dxchange.read_hdf5(path_files[i], "{}/extra_pvs_as_csv".format(hdf_tag))[theta_index].split(b',')[1])
            print(theta)
    return theta


def load_thetas(path_files, data_tag, version, *thetaPV):
    
    if version == 0:
        return load_thetas_legacy(path_files, thetaPV[0])

    if version == 1:
        return load_thetas_9idb(path_files, data_tag)

    if version == 2:
        return load_thetas_2ide(path_files, data_tag)


def load_thetas_legacy( path_files, thetaPV):
    thetaBytes = thetaPV.encode('ascii')
    thetas = []
    for i in range(len(path_files)):
        try:
            hFile = h5py.File(path_files[i])
            extra_pvs = hFile['/MAPS/extra_pvs']
            idx = np.where(extra_pvs[0] == thetaBytes)
            if len(idx[0]) > 0:
                thetas.append(float(extra_pvs[1][idx[0][0]]))
        except:
            pass
    return thetas

def load_thetas_9idb(path_files, data_tag):
    thetas = []
    for i in range(len(path_files)):
        try:
            hFile = h5py.File(path_files[i])
            thetas.append(float(hFile[data_tag]['theta'].value[0]))
        except:
            pass
    return thetas

def load_thetas_2ide(path_files, data_tag):
    thetas = []
    for i in range(len(path_files)):
        try:
            hFile = h5py.File(path_files[i])
            thetas.append(float(hFile[data_tag]['theta'].value[0]))
        except:
            pass
    return thetas

def load_thetas_13(path_files, data_tag):
    pass

def read_mic_xrf(path_files, element_index, hdf_tag, roi_tag, channel_tag):
    """
    Converts hdf files to numpy arrays for plotting and manipulation

    Parameters
    ----------
    path_files: list
        List of (path + filenames)
    theta_index : int
        Index where theta is saved under in the hdf MAPS/extra_pvs_as_csv tag
        This is: 2-ID-E: 663; 2-ID-E (prior 2017): *657*; BNP: 8
    hdf_tag : str
        String defining the hdf5 data_tag name (ex. MAPS)
    roi_tag: str
        data tag for corresponding roi_tag (ex. XRF_roi)
    channel_tag : str
        String defining the hdf5 channel tag name (ex. channel_names)

    Returns
    -------
    ndarray: ndarray
        4D array [elements, projection, y, x]
    """

    elements = read_channel_names(path_files[0], hdf_tag, channel_tag)
    max_y, max_x = 0, 0
    for i in range(len(path_files)):
        proj = read_projection(path_files[i], elements[0], hdf_tag, roi_tag, channel_tag)
        if proj.shape[0] > max_y:
            max_y = proj.shape[0]
        if proj.shape[1] > max_x:
            max_x = proj.shape[1]

    data = np.zeros([len(element_index),len(path_files), max_y, max_x])

    for i in range(len(element_index)):
        indx = element_index[i]

        for j in range(len(path_files)):
            proj = read_projection(path_files[j], elements[indx], hdf_tag, roi_tag, channel_tag)
            img_y = proj.shape[0]
            img_x = proj.shape[1]
            dx = np.floor((max_x-img_x)/2).astype(int)
            dy = np.floor((max_y-img_y)/2).astype(int)
            data[i, j, dy:img_y+dy, dx:img_x+dx] = proj
    data[np.isnan(data)] = 0.0001
    data[data == np.inf] = 0.0001
   
    return data

