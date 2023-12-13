#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.           #
#                                                                         #
#                       Software Name: XRFtomo                            #
#                                                                         #
#                   By: Argonne National Laboratory                       #
#                                                                         #
#                       OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#                                                                         #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the           #
#    distribution.                                                        #
#                                                                         #
# 3. Neither the name of the copyright holder nor the names of its        #
#    contributors may be used to endorse or promote products derived      #
#    from this software without specific prior written permission.        #
#                                                                         #
#                               DISCLAIMER                                #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT    #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT     #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    #
###########################################################################

"""
Module for importing raw data files.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import xrftomo
import h5py
from skimage import io
import csv
import os
import sys

__author__ = "Francesco De Carlo, Fabricio S. Marin"
__copyright__ = "Copyright (c) 2018, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'

class ReadOptions(object):

    def __init__(self, parent):
        super(ReadOptions, self).__init__()
        self.parent = parent
        sys.stdout = xrftomo.gui.Stream(newText=self.parent.onUpdateText)

    def find_elements(self, channel_names):
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
             elements.append(str(xrftomo.ELEMENTS[i].symbol))

        elements = sorted(set(channel_names) & set(elements), key = channel_names.index)

        return elements


    def read_channel_names(self, fname, element_tag):
        """
        Read the channel names

        Parameters
        ----------
        fname : str
            String defining the file name
        element_tag : str
            String defining the hdf5 channel tag name (ex. MAPS/channel_names)
        Returns
        -------
        channel_names : list
            List of channel names

        """
        img = h5py.File(fname, "r")
        element_list = list(img[element_tag])
        element_list = [x.decode("utf-8") for x in element_list]
        return(element_list)

    def read_projection(self, fname, element, data_tag, element_tag):
        """
        Reads a projection for a given element from a single xrf hdf file

        Parameters
        ----------
        fname : str
            String defining the file name
        element : str
            String defining the element to select
        data_tag: str
            data tag for corresponding dataset (ex. MAPS/XRF_roi)
        element_tag : str
            String defining the hdf5 channel tag name (ex. channel_names)

        Returns
        -------
        ndarray: ndarray
            projection

        """
        elements = self.read_channel_names(fname, element_tag)
        if elements == []:
            return
        img = h5py.File(fname, "r")
        idx = elements.index(element)
        projection = img[data_tag][idx]
        return projection

    def load_thetas(self, files, theta_tag, method = 1):
        thetas = []
        if method==1:
            img = h5py.File(files[0], 'r')
            pv = theta_tag.split("/")[-1]
            pvs = img["/".join(theta_tag.split("/")[:-1])]
            idx = [i for i, s in enumerate(pvs) if pv in s.decode("utf8")][0]
            img.close()

        for file in files:
            try:
                if method ==1:
                    img = h5py.File(file, 'r')
                    try:
                        # TODO: some files do not have extra_pvs tag within the mda folder causng this method to fail even if
                        # previous files succeeded;. Try except will then try the legacy h5 structure which will also fail.
                        theta = float(img["/".join(theta_tag.split("/")[:-2])+"/Values"][idx].decode("utf-8"))
                        thetas.append(theta)
                    except:
                        if len(thetas)>2:
                            print("problem with {}".format(file))
                            pass
                        else:
                            break

                elif method ==2:
                    theta = float(img[theta_tag][0])
                    thetas.append(theta)
            except:
                try:
                    #TODO: this is stupid, we need to standardize h5 file structure
                    img = h5py.File(file, 'r')
                    theta = float(img["/".join(theta_tag.split("/")[:-1])][idx].decode("utf-8").split(",")[-1])
                    thetas.append(theta)
                except:
                    print("error reading thetas position for file: {}".format(file))
                    return

        if method == 3:
            for file in files:
                img = h5py.File(file, 'r')
                try:
                    theta = float(img["MAPS/extra_pvs_as_csv/"][657].decode("utf-8").split(",")[-1])
                    thetas.append(theta)
                except:
                    print("trying other pv path")
                try:
                    theta = float(img["MAPS/Scan/Extra_PVs/Values/"][591].decode("utf-8"))
                    thetas.append(theta)
                except:
                    print("trying other pv path")

        return thetas

    def load_thetas_file(self, path_file):

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

    def read_mic_xrf(self, path_files, elements, data_tag, element_tag):
        """
        Converts hdf files to numpy arrays for plotting and manipulation

        Parameters
        ----------
        path_files: list
            List of (path + filenames)
        theta_index : int
            Index where theta is saved under in the hdf MAPS/extra_pvs_as_csv tag
            This is: 2-ID-E: 663; 2-ID-E (prior 2017): *657*; BNP: 8
        data_tag: str
            data tag for corresponding roi_tag (ex. MAPS/XRF_roi)
        channel_tag : str
            String defining the hdf5 channel tag name (ex. channel_names)

        Returns
        -------
        ndarray: ndarray
            4D array [elements, projection, y, x]
        """

        max_y, max_x = 0, 0
        num_files = len(path_files)
        num_elements = len(elements)
        #get max dimensons
        for i in range(num_files):
            proj = self.read_projection(path_files[i], elements[0], data_tag, element_tag)
            if proj is None:
                pass
            else:
                if proj.shape[0] > max_y:
                    max_y = proj.shape[0]
                if proj.shape[1] > max_x:
                    max_x = proj.shape[1]

        data = np.zeros([num_elements,num_files, max_y, max_x])
        #get data
        for i in range(num_elements):
            for j in range(num_files):
                proj = self.read_projection(path_files[j], elements[i], data_tag, element_tag)
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

        data[np.isnan(data)] = 0.0001
        data[data == np.inf] = 0.0001
        return data

    def read_tiffs(self, fnames):

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