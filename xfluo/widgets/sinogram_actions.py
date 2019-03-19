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

class SinogramActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')

	def __init__(self):
		super(SinogramActions, self).__init__()

    def runCenterOfMass2(self):
        '''
        second version of runCenterOfMass
        self.com: center of mass vector
        self.comelem: the element chosen for center of mass
        '''



        self.com = zeros(self.projections)
        temp = zeros(self.data.shape[3])
        temp2 = zeros(self.data.shape[3])
        self.comelem = self.sino.combo.currentIndex()
        for i in arange(self.projections):
            temp = sum(self.data[self.comelem, i,
                       self.sino.sld.value() - self.thickness / 2:self.sino.sld.value() + self.thickness / 2,
                       :] - self.data[self.comelem, i, :10, :10].mean(), axis=0)
            # temp=sum(self.data[self.comelem,i,:,:]-1, axis=0)
            numb2 = sum(temp)
            for j in arange(self.data.shape[3]):
                temp2[j] = temp[j] * j
            numb = float(sum(temp2)) / numb2
            self.com[i] = numb
        self.fitCenterOfMass(x=self.theta)
        self.lbl.setText("Center of Mass: " + str(self.p1[2]))
        self.alignCenterOfMass()
        
        #return a bunch of parameters, rerun sinogram()




    # def fitCenterOfMass(self, ang):
    #     '''
    #     Find a position difference between center of mass of first projection
    #     and center of other projections.
    #     If we use this difference, centers will be aligned in a straigh line

    #     Parameters
    #     -----------
    #     ang: ndarray
    #           angle

    #     Variables
    #     ------------
    #     self.centerOfMassDiff: ndarray
    #           Difference of center of mass of first projections and center
    #           of other projections
    #     self.com: ndarray
    #           The position of center of mass
    #     '''
    #     self.centerOfMassDiff = self.com[0] - self.com



        # def alignCenterOfMass(self):
        # '''
        # Align center of Mass

        # Variables
        # ------------
        # self.centerOfMassDiff: ndarray
        #       Difference of center of mass of first projections and center
        #       of other projections
        # self.projections: number
        #       number of projections
        # self.xshift: ndarray
        #       shift in x direction
        # self.data: ndarray
        #       4D data [element,projections,y,x]
        # '''
        # for i in arange(self.projections):
        #     self.xshift[i] += int(self.centerOfMassDiff[i])
        #     self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], int(round(self.xshift[i])), axis=2)
        # self.lbl.setText("Alignment has been completed")



    # def sinoShift(self):
    #     '''
    #     shift images and record in data array

    #     Variables
    #     -----------
    #     self.data: ndarray
    #           4D tomographic data [element,projections,y,x]
    #     self.sinoView.view.regShift: ndarray
    #           horizontal shift registered by manually shifting on sinogram
    #           winodow.
    #     '''
    #     for i in arange(self.projections):
    #         self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.sinoView.view.regShift[i], axis=2)
