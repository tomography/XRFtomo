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

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, signal
import scipy.fftpack as spf
import string

class SinogramActions(QtWidgets.QWidget):
    dataSig = pyqtSignal(np.ndarray, name='dataSig')

    def __init__(self):
        super(SinogramActions, self).__init__()
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
    def runCenterOfMass(self, element, row, data, thetas):
        '''
        second version of runCenterOfMass
        self.com: center of mass vector
        element: the element chosen for center of mass
        '''
        num_projections = data.shape[1]
        com = zeros(num_projections)
        temp = zeros(data.shape[3])
        temp2 = zeros(data.shape[3])
        for i in arange(num_projections):
            temp = sum(data[element, i, :, :] - data[element, i, :10, :10].mean(), axis=0)
            numb2 = sum(temp)
            for j in arange(data.shape[3]):
                temp2[j] = temp[j] * j
            numb = float(sum(temp2)) / numb2
            com[i] = numb

        x=thetas
        fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [100, 100, 100]
        self.centers, success = optimize.leastsq(errfunc, p0, args=(x, com))
        centerOfMassDiff = fitfunc(self.centers, x) - com

        #set some label within the sinogram widget to the string defined in the line below
        # self.lbl.setText("Center of Mass: " + str(p1[2]))

        num_projections = data.shape[1]
        for i in arange(num_projections):
            self.x_shifts[i] += int(centerOfMassDiff[i])
            data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(self.x_shifts[i])), axis=2)
        #set some status label
        self.alignmentDone()
        # return data, self.x_shifts, self.centers
        return data, self.x_shifts

    # def runCenterOfMass2(self, element, row, data, thetas):
    #     '''
    #     second version of runCenterOfMass
    #     self.com: center of mass vector
    #     element: the element chosen for center of mass
    #     '''
    #     num_projections = data.shape[1]
    #     com = zeros(num_projections)
    #     temp = zeros(data.shape[3])
    #     temp2 = zeros(data.shape[3])
    #     try: 
    #         for i in arange(num_projections):
    #             temp = sum(data[element, i, row - 10//2: row + 10 // 2, :] - data[element, i, :10, :10].mean(), axis=0)
    #             numb2 = sum(temp)
    #             for j in arange(data.shape[3]):
    #                 temp2[j] = temp[j] * j
    #             numb = float(sum(temp2)) / numb2
    #             com[i] = numb
    #     except e:
    #         print(e)

    #     x=thetas
    #     fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + self.centers[2]
    #     errfunc = lambda p, x, y: fitfunc(p, x) - y
    #     p0 = [100, 100]
    #     p2, success = optimize.leastsq(errfunc, p0[:], args=(x, com))
    #     centerOfMassDiff = fitfunc(p2, x) - com        

    #     j = 0
    #     num_projections = data.shape[1]
    #     for i in arange(num_projections):
    #         self.x_shifts[i] += int(centerOfMassDiff[j])
    #         data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(self.x_shifts[i])), axis=2)
    #         j += 1
    #     self.alignmentDone()
    #     return data, self.x_shifts, p2

    def shift(self, sinogramData, data, shift_number, col_number):
        num_projections = data.shape[1]
        regShift = zeros(sinogramData.shape[0], dtype=np.int)
        sinogramData[col_number * 10:col_number * 10 + 10, :] = np.roll(sinogramData[col_number * 10:col_number * 10 + 10, :], shift_number, axis=1)
        regShift[col_number] += shift_number
        for i in arange(num_projections):
            data[:,i,:,:] = np.roll(data[:,i,:,:], regShift[i], axis=2)
        return data, sinogramData

    def crossCorrelate(self, element, data):

        num_projections = data.shape[1]

        for i in arange(num_projections - 1):
            a = data[element, i, :, :]
            b = data[element, i + 1, :, :]

            fa = spf.fft2(a)
            fb = spf.fft2(b)
            shape = a.shape
            c = abs(spf.ifft2(fa * fb.conjugate()))
            t0, t1 = np.unravel_index(np.argmax(c), a.shape)
            if t0 > shape[0] // 2:
                t0 -= shape[0]
            if t1 > shape[1] // 2:
                t1 -= shape[1]

            data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t0, axis=1)
            data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t1, axis=2)
            self.x_shifts[i + 1] += t1
            self.y_shifts[i + 1] += t0

        self.alignmentDone()
        return data, self.x_shifts, self.y_shifts

    def phaseCorrelate(self, element, data):

        num_projections = data.shape[1]
        for i in arange(num_projections - 1):
            # onlyfilenameIndex=self.fileNames[i+1].rfind("/")
            a = data[element, i, :, :]
            b = data[element, i + 1, :, :]

            fa = spf.fft2(a)
            fb = spf.fft2(b)

            shape = a.shape
            c = abs(spf.ifft2(fa * fb.conjugate() / (abs(fa) * abs(fb))))
            t0, t1 = np.unravel_index(np.argmax(c), a.shape)
            if t0 > shape[0] // 2:
                t0 -= shape[0]
            if t1 > shape[1] // 2:
                t1 -= shape[1]

            data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t0, axis=1)
            data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t1, axis=2)
            self.x_shifts[i + 1] += t1
            self.y_shifts[i + 1] += t0
        self.alignmentDone()
        return data, self.x_shifts, self.y_shifts

    def matchTermplate(self):
        pass

    # def alignFromText(self, data):
    #     '''
    #     align by reading text file that saved prior image registration
    #     alignment info is saved in following format: name of the file, xshift, yshift
    #     by locating where the comma(,) is we can extract information:
    #     name of the file(string before first comma),
    #     yshift(string after first comma before second comma),
    #     xshift(string after second comma)
    #     '''

    #     try:
    #         fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath(), "TXT (*.txt)")
    #         ##### for future reference "All File (*);;CSV (*.csv *.CSV)"

    #         fname = open(fileName[0], 'r')
    #         read = fname.readlines()
    #         datacopy = zeros(data.shape)
    #         datacopy[...] = data[...]
    #         data[np.isnan(data)] = 1
    #         num_projections = data.shape[1]
    #         for i in arange(num_projections):
    #             onlyfilenameIndex = fname[i].rfind("/")
    #             for j in arange(len(read)):
    #                 if string.find(read[j], fname[i][onlyfilenameIndex + 1:]) != -1:
    #                     secondcol = read[j].rfind(",")  ## find second ,
    #                     firstcol = read[j][:secondcol].rfind(",")
    #                     self.y_shifts[i] += int(float(read[j][secondcol + 1:-1]))
    #                     self.x_shifts[i] += int(float(read[j][firstcol + 1:secondcol]))
    #                     data[:, i, :, :] = np.roll(data[:, i, :, :], self.x_shifts[i], axis=2)
    #                     data[:, i, :, :] = np.roll(data[:, i, :, :], self.y_shifts[i], axis=1)
    #                 if string.find(read[j], "rotation axis") != -1:
    #                     commapos = read[j].rfind(",")
    #                     self.centers[2] = float(read[j][commapos + 1:-1])
    #         f.close()
    #         self.alignmentDone()
    #         return data, self.x_shifts, self.y_shifts, self.centers
    #     except IOError:
    #         print("choose file please")

    def alignFromText2(self, data):
        '''
        align by reading text file that saved prior image registration
        alignment info is saved in following format: name of the file, xshift, yshift
        by locating where the comma(,) is we can extract information:
        name of the file(string before first comma),
        yshift(string after first comma before second comma),
        xshift(string after second comma)
        '''
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath(), "TXT (*.txt)")
            ##### for future reference "All File (*);;CSV (*.csv *.CSV)"

            file = open(fileName[0], 'r')
            read = file.readlines()
            datacopy = zeros(data.shape)
            datacopy[...] = data[...]
            data[np.isnan(data)] = 1
            num_projections = data.shape[1]
            for i in arange(num_projections):
                j = i + 1
                secondcol = read[j].rfind(",")
                firstcol = read[j][:secondcol].rfind(",")
                self.y_shifts[i] += int(float(read[j][secondcol + 1:-1]))
                self.x_shifts[i] += int(float(read[j][firstcol + 1:secondcol]))
                data[:, i, :, :] = np.roll(data[:, i, :, :], self.x_shifts[i], axis=2)
                data[:, i, :, :] = np.roll(data[:, i, :, :], self.y_shifts[i], axis=1)

            file.close()
            self.alignmentDone()
            # return data, self.x_shifts, self.y_shifts, self.centers
            return data, self.x_shifts, self.y_shifts
        except IOError:
            print("choose file please")

    # def alignfromHotspotxt(self):
    #     pass

    def alignmentDone(self):
        '''send message that alignment has been done'''
        print("Alignment has been completed")
