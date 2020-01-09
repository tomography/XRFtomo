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
from skimage import io
import csv
import os

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
           'load_thetas_2ide',
           'read_exchange_file',
           'read_tiffs',
           'load_thetas_file']

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
    try:
        b_channel_names = dxchange.read_hdf5(fname, "{}/{}".format(hdf_tag, channel_tag))
    except:
        print("File signature not found for {}, check file integrity".format(fname))
        return []
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
    if elements == []:
        return
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
            hFile = h5py.File(path_files[i], 'r')
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
            hFile = h5py.File(path_files[i], "r")
            thetas.append(float(hFile[data_tag]['theta'][0]))
        except:
            pass
    return thetas

def load_thetas_2ide(path_files, data_tag):
    thetas = []
    for i in range(len(path_files)):
        try:
            hFile = h5py.File(path_files[i])
            thetas.append(float(hFile[data_tag]['theta'][0]))
        except:
            pass
    return thetas

def load_thetas_file(path_file):

    name, ext = os.path.splitext(path_file)
    fnames = []
    thetas = []
    if ext == ".txt":
        text_file = open(path_file, "r")
        #TODO: check if fnames are present and save them to list, if not, just get thetas
        lines = text_file.readlines()
        text_file.close()
        try:
            cols = len(lines[0].split(","))
        except IndexError:
            print("invalid file formatting")
            return [], []
        if cols == 2:
            thetas = [float(lines[1:][i].split(",")[1]) for i in range(len(lines)-1)]
            fnames = [lines[1:][i].split(",")[0] for i in range(len(lines)-1)]
            return fnames, thetas

        elif cols ==1:
            thetas = [float(lines[1:][i].split("\n")[0]) for i in range(len(lines)-1)]
            return [], thetas

    elif ext == ".csv" or ext == ".CSV":
        with open('example.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            #TODO: check if fnames are present and save them to list, if not, just get thetas
            thetas = readCSV[0]
            fnames = readCSV[1]
            return fnames, thetas

    else:
        return 




def load_thetas_13(path_files, data_tag):
    pass

def read_mic_xrf(path_files, elements, hdf_tag, roi_tag, channel_tag, scaler_name):
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

    element_names = read_channel_names(path_files[0], hdf_tag, channel_tag)
    max_y, max_x = 0, 0
    num_files = len(path_files)
    num_elements = len(elements)
    #get max dimensons
    for i in range(num_files):
        #TODO: this errors out when loading h5/C+ after h5/MapsPy
        proj = read_projection(path_files[i], element_names[0], hdf_tag, roi_tag, channel_tag)
        if proj is None:
            pass
        else:
            if proj.shape[0] > max_y:
                max_y = proj.shape[0]
            if proj.shape[1] > max_x:
                max_x = proj.shape[1]

    data = np.zeros([num_elements,num_files, max_y, max_x])
    scalers = np.zeros([num_files,max_y,max_x])
    quants= np.zeros([num_elements,num_files])
    #get data
    for i in range(num_elements):
        for j in range(num_files):
            proj = read_projection(path_files[j], elements[i], hdf_tag, roi_tag, channel_tag)
            if proj is None:
                pass
            if proj is not None:
                img_y = proj.shape[0]
                img_x = proj.shape[1]
                dx = (max_x-img_x)//2
                dy = (max_y-img_y)//2
                try:
                    data[i, j, dy:img_y+dy, dx:img_x+dx] = proj
                except ValueError:
                    print("WARNING: possible error with file: {}. Check file integrity. ".format(path_files[j]))
                    data[i, j] = np.zeros([max_y,max_x])

    #get scalers
    if scaler_name == 'None':
        scalers = np.ones([num_files, max_y, max_x])
        quants = np.ones([num_elements, num_files])
        data[np.isnan(data)] = 0.0001
        data[data == np.inf] = 0.0001
        return data, quants, scalers

    for j in range(num_files):
        scaler = read_scaler(path_files[j], hdf_tag, scaler_name)
        scaler_x = scaler.shape[1]
        scaler_y = scaler.shape[0]
        dx = (max_x-scaler_x)//2
        dy = (max_y-scaler_y)//2
        scalers[j,dy:scaler_y+dy, dx:scaler_x+dx] = scaler
    #get quants
    for i in range(num_elements):
        for j in range(num_files):
            quant_name = scaler_name
            quant = read_quant(path_files[j], elements[i], hdf_tag, quant_name, channel_tag)
            quants[i,j] = quant

    data[np.isnan(data)] = 0.0001
    data[data == np.inf] = 0.0001
    scalers[np.isnan(scalers)] = 0.0001
    scalers[scalers == np.inf] = 0.0001
    quants[np.isnan(quants)] = 0.0001
    quants[quants == np.inf] = 0.0001

    return data, quants, scalers

def read_scaler(fname, hdf_tag, scaler_name):
    try:
        scaler_names = read_channel_names(fname, hdf_tag, 'scaler_names')
        all_scaler = dxchange.read_hdf5(fname, "{}/{}".format(hdf_tag, 'scalers'))
    except:
        scaler_names = read_channel_names(fname, 'MAPS', 'scaler_names')
        all_scaler = dxchange.read_hdf5(fname, "{}/{}".format('MAPS', 'scalers'))
        
    return all_scaler[find_index(scaler_names, scaler_name)]

def read_quant(fname, element, hdf_tag, quant_name, channel_tag):
    elements = read_channel_names(fname, hdf_tag, channel_tag)
    elem_idx = find_index(elements,element)

    try:
        quant_names = read_channel_names(fname, hdf_tag, 'quant_names')
        all_quants = dxchange.read_hdf5(fname, "{}/{}".format(hdf_tag, 'quant'))
    except:
        quant_names = ['SRcurrent','us_ic','ds_ic']
        all_quants = dxchange.read_hdf5(fname, "{}/{}".format('MAPS', 'XRF_roi_quant'))

    quant_idx = find_index(quant_names,quant_name)
    return all_quants[quant_idx][0][elem_idx]

def read_tiffs(fnames):

    #TODO:check if fnames is a series of tiffs or a single tiff stack
    max_x, max_y = 0,0
    num_files = len(fnames)
    for i in fnames: 
        im = io.imread(i)
        if im.shape[0] > max_y:
            max_y = im.shape[0]
        if im.shape[1] > max_x:
            max_x = im.shape[1]
    data = np.zeros([1,num_files, max_y, max_x])

    for i in range(len(fnames)):
        im = io.imread(fnames[i])
        img_y = im.shape[0]
        img_x = im.shape[1]
        dx = (max_x-img_x)//2
        dy = (max_y-img_y)//2
        data[0,i, dy:img_y+dy, dx:img_x+dx] = im

    return data

def read_exchange_file(fname):
    data, elements, thetas = [],[],[]
    hFile = h5py.File(fname[0])
    tmp_elements = hFile['exchange']['elements'].value
    elements = [x.decode('utf-8') for x in tmp_elements]
    thetas = hFile['exchange']['theta'].value
    data = hFile['exchange']['data'].value

    return data, elements, thetas
