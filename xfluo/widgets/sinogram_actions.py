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
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENTn SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, signal

class SinogramActions(QtWidgets.QWidget):
    dataSig = pyqtSignal(np.ndarray, name='dataSig')

    def __init__(self):
        super(SinogramActions, self).__init__()

    def runCenterOfMass2(self, element, row, data, thetas):
        '''
        second version of runCenterOfMass
        self.com: center of mass vector
        element: the element chosen for center of mass
        '''
        num_projections = data.shape[1]
        self.xshift = zeros(num_projections, dtype=np.int)
        com = zeros(num_projections)
        temp = zeros(data.shape[3])
        temp2 = zeros(data.shape[3])
        p1 = [100, 100, data.shape[3] / 2]
        for i in arange(num_projections):
            temp = sum(data[element, i, :, :] - data[element, i, :10, :10].mean(), axis=0)
            # temp = sum(data[element, i,row-  / 2: row + 10 / 2, :] - data[element, i, :10, :10].mean(), axis=0)
            numb2 = sum(temp)
            for j in arange(data.shape[3]):
                temp2[j] = temp[j] * j
            numb = float(sum(temp2)) / numb2
            com[i] = numb
        centerOfMassDiff = self.fitCenterOfMass(com, x=thetas)

        #set some label within the sinogram widget to the string defined in the line below
        # self.lbl.setText("Center of Mass: " + str(p1[2]))

        data = self.alignCenterOfMass(data, centerOfMassDiff, self.xshift)

        return data
        
    def fitCenterOfMass(self, com, x):
        fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [100, 100, 100]
        p1, success = optimize.leastsq(errfunc, p0, args=(x, com))
        centerOfMassDiff = fitfunc(p1, x) - com
        return centerOfMassDiff

    def alignCenterOfMass(self, data, centerOfMassDiff, xshift):
        '''
        Align center of Mass
        '''
        num_projections = data.shape[1]
        
        for i in arange(num_projections):
            xshift[i] += int(centerOfMassDiff[i])
            data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(xshift[i])), axis=2)
        #set some status label
        # self.lbl.setText("Alignment has been completed")
        return data

    def shift(self, sinogramData, data, shift_number, col_number):
        num_projections = data.shape[1]
        regShift = zeros(sinogramData.shape[0], dtype=np.int)
        sinogramData[col_number * 10:col_number * 10 + 10, :] = np.roll(sinogramData[col_number * 10:col_number * 10 + 10, :], shift_number, axis=1)
        regShift[col_number] += shift_number
        for i in arange(num_projections):
            data[:,i,:,:] = np.roll(data[:,i,:,:], regShift[i], axis=2)
        return data, sinogramData

