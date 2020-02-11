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
import xrftomo
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, signal
import scipy.fftpack as spf
import string
#import cv2
from PIL import Image, ImageChops, ImageOps
import tomopy
from skimage import filters
from skimage.measure import regionprops




class SinogramActions(QtWidgets.QWidget):
    dataSig = pyqtSignal(np.ndarray, name='dataSig')

    def __init__(self):
        super(SinogramActions, self).__init__()
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
    # def runCenterOfMass(self, element, data, thetas):
    #     '''
    #     Center of mass alignment
    #     Variables
    #     -----------
    #     element: int
    #         element index
    #     data: ndarray
    #         4D xrf dataset ndarray [elements, theta, y,x]
    #     thetas: ndarray
    #         sorted projection angle list
    #     '''
    #     num_projections = data.shape[1]
    #     com = zeros(num_projections)
    #     temp = zeros(data.shape[3])
    #     temp2 = zeros(data.shape[3])
    #     for i in arange(num_projections):
    #         temp = sum(data[element, i, :, :] - data[element, i, :10, :10].mean(), axis=0)
    #         numb2 = sum(temp)
    #         for j in arange(data.shape[3]):
    #             temp2[j] = temp[j] * j
    #         if numb2 <= 0:
    #             numb2 = 1
    #         numb = float(sum(temp2)) / numb2
    #         if numb == NaN:
    #             numb = 0.000
    #         com[i] = numb

    #     x=thetas
    #     fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
    #     errfunc = lambda p, x, y: fitfunc(p, x) - y
    #     p0 = [100, 100, 100]
    #     self.centers, success = optimize.leastsq(errfunc, p0, args=(x, com))
    #     centerOfMassDiff = fitfunc(self.centers, x) - com

    #     #set some label within the sinogram widget to the string defined in the line below
    #     # self.lbl.setText("Center of Mass: " + str(p1[2]))

    #     num_projections = data.shape[1]
    #     for i in arange(num_projections):
    #         self.x_shifts[i] += int(centerOfMassDiff[i])
    #         data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(self.x_shifts[i])), axis=2)
    #     #set some status label
    #     self.alignmentDone()
    #     # return data, self.x_shifts, self.centers
    #     return data, self.x_shifts

    def runCenterOfMass(self, element, data, thetas, weighted = True, shift_y = False):

        num_projections = data.shape[1]
        view_center_x = data.shape[3]//2
        view_center_y = data.shape[2]//2

        x_shifts = []
        y_shifts = []
        w_x_shifts = []
        w_y_shifts = []
        tmp_lst = []
        if weighted:
            for i in range(num_projections):
                image = data[element, i]
                threshold_value = filters.threshold_otsu(image)
                labeled_foreground = (image > threshold_value).astype(int)
                properties = regionprops(labeled_foreground, image)
                weighted_center_of_mass = properties[0].weighted_centroid
                w_x_shifts.append(int(round(view_center_x - weighted_center_of_mass[1])))
                w_y_shifts.append(int(round(view_center_y - weighted_center_of_mass[0])))
                data = self.shiftProjectionX(data, i, w_x_shifts[i])
                if shift_y:
                    data = self.shiftProjectionY(data, i, w_y_shifts[i])

            if not shift_y: 
                w_y_shifts = np.asarray(w_y_shifts)*0
            return data, np.asarray(w_x_shifts), np.asarray(w_y_shifts)

        if not weighted:
            for i in range(num_projections):
                image = data[element, i]
                threshold_value = filters.threshold_otsu(image)
                labeled_foreground = (image > threshold_value).astype(int)
                properties = regionprops(labeled_foreground, image)
                center_of_mass = properties[0].centroid
                x_shifts.append(int(round(view_center_x -center_of_mass[1])))
                y_shifts.append(int(round(view_center_y - center_of_mass[0])))
                data = self.shiftProjectionX(data, i, x_shifts[i])
                if shift_y:
                    data = self.shiftProjectionY(data, i, y_shifts[i])
                    
            if not shift_y: 
                y_shifts = np.asarray(y_shifts)*0
            return data, np.asarray(x_shifts), np.asarray(y_shifts)

    def shiftProjectionX(self, data, index, displacement):
        data[:,index] = np.roll(data[:,index],displacement,axis=2)
        return data

    def shiftProjectionY(self, data, index, displacement):
        data[:,index] = np.roll(data[:,index],displacement,axis=1)
        return data

    def shift(self, sinogramData, data, shift_number, col_number):
        '''
        shifts sinogram column of pixels up or down.
        Variables
        -----------
        sinogramData: ndarray
            3D array containing sinogram images for each row of data
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        shift_number: int
            amount of pixel shifting done per column 
        col_number: int
        '''
        num_projections = data.shape[1]
        regShift = zeros(sinogramData.shape[0], dtype=np.int)
        sinogramData[col_number * 10:col_number * 10 + 10, :] = np.roll(sinogramData[col_number * 10:col_number * 10 + 10, :], shift_number, axis=1)
        regShift[col_number] += shift_number
        for i in arange(num_projections):
            data[:,i,:,:] = np.roll(data[:,i,:,:], regShift[i], axis=2)
        return data, sinogramData  

    def shiftDataX(self, data, displacement):
        for i in range(data.shape[1]):
            data[:,i] = np.roll(data[:,i],displacement, axis=2)
        return data

    def slope_adjust(self, sinogramData, data, shift, delta):
        '''
        Sinograms are oftwen skewed when using xcor alignment method. slope_adjust offsets the sinogram's slope by 'delta' pixels
        Variables
        -----------
        sinogramData: ndarray
            3D array containing sinogram images for each row of data
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        shift: int
            number of pixel to shift sinogram up or down by.
        delta: int
            number of pixels to shift by at right-hand side of sinogram.
        '''

        num_projections = data.shape[1]
        step = round(delta/num_projections)
        lin_shift = [int(x) for x in np.linspace(0, delta, num_projections)]
        lin_shift = [x + shift for x in lin_shift]

        for i in range(num_projections):
            data, sinogramData = self.shift(sinogramData, data, lin_shift[i], i)
            data[:,i] = np.roll(data[:,i],shift,axis=1)

        return lin_shift, data, sinogramData
        
    def crossCorrelate(self, element, data):
        '''
        cross correlate image registration
        Variables
        -----------
        element: int
            element index
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
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
            self.y_shifts[i + 1] += -t0

        self.alignmentDone()
        return data, self.x_shifts, self.y_shifts

    def crossCorrelate2(self, data):
        '''
        cross correlate image registration aplies to all loaded elements.
        Variables
        -----------
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        for i in arange(num_projections - 1):
            flat = np.sum(data, axis=0)
            a = flat[i]
            b = flat[i + 1]
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
            self.y_shifts[i + 1] += -t0

        self.alignmentDone()
        return data, self.x_shifts, self.y_shifts

    def phaseCorrelate(self, element, data):
        '''
        Phase correlate image registration
        Variables
        -----------
        element: int
            element index
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
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
            self.y_shifts[i + 1] += -t0
        self.alignmentDone()
        return data, self.x_shifts, self.y_shifts

    # def align_y_top(self, element, data):
    #     '''
    #     This alingment method sets takes a hotspot or a relatively bright and isolated part of the projection and moves it to the 
    #     top of the ROI boundary. It does this for all projections, effectively adjusting for vertical drift or stage wobble. 

    #     Variables
    #     -----------
    #     element: int
    #         element index
    #     data: ndarray
    #         4D xrf dataset ndarray [elements, theta, y,x]
    #     '''
    #     self.data = data
    #     num_projections = data.shape[1]
    #     tmp_data = data[element,:,:,:]
    #     bounds = self.get_boundaries(tmp_data,5)
    #     y_bot = np.asarray(bounds[3])
    #     translate = y_bot[0]-y_bot
    #     # self.data = np.roll(data, int(np.round(self.y_shifts)), axis=1)
    #     self.y_shifts -=translate

    #     for i in range(num_projections):
    #         self.data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(translate[i])), axis=1)

    #     self.alignmentDone()
    #     return self.y_shifts, self.data 

    def align2edge(self, element, data, loc, threshold):
        '''
        This alingment method sets takes a hotspot or a relatively bright and isolated part of the projection and moves it to the 
        top of the ROI boundary. It does this for all projections, effectively adjusting for vertical drift or stage wobble. 

        Variables
        -----------
        element: int
            element index
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        loc: bool
            0 = bottom, 1 = top
        '''
        self.data = data
        num_projections = data.shape[1]
        tmp_data = data[element,:,:,:]
        bounds = self.get_boundaries(tmp_data,threshold)
        edge = np.asarray(bounds[2+loc])
        translate = -edge

        # self.data = np.roll(data, int(np.round(self.y_shifts)), axis=1)
        self.y_shifts -=translate

        for i in range(num_projections):
            self.data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(translate[i])), axis=1)

        self.alignmentDone()
        return self.y_shifts, self.data 

    def get_boundaries(self, data, coeff):
        '''
        Identifies the saple's envelope and creates a rectangular boundary over each projection, then return a dictionary containing the
        left, right, top, and bottom boundary positions. 
        Variables
        -----------
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        coeff: int
            element index
        '''
        bounds = {}
        bounds[0] = []  # x_left
        bounds[1] = []  # x_right
        bounds[2] = []  # y_top
        bounds[3] = []  # y_bottom

        num_proj = len(data)
        for i in range(num_proj):
            col_sum = np.sum(data[i], axis=0) / data[i].shape[1]
            row_sum = np.sum(data[i], axis=1) / data[i].shape[0]
            noise_col = np.sort(col_sum[col_sum > 0])[:1]
            noise_row = np.sort(row_sum[row_sum > 0])[:1]

            if noise_col <= noise_row:
                noise = noise_col
            else:
                noise = noise_row

            upper_thresh_col = np.sort(col_sum)[::-1][:1]
            diffcol = upper_thresh_col - noise
            y_thresh = diffcol * coeff / 100 + noise

            upper_thresh_row = np.sort(row_sum)[::-1][:1]
            diffrow = upper_thresh_row - noise
            x_thresh = diffrow * coeff / 100 + noise

            for j in range(len(col_sum)):
                if col_sum[j] >= y_thresh:
                    bounds[0].append(j)
                    break
            for j in range(len(col_sum)):
                if col_sum[len(col_sum) - j - 1] >= y_thresh:
                    bounds[1].append(len(col_sum) - j - 1)
                    break
            for j in range(len(row_sum)):
                if row_sum[len(row_sum) - j - 1] >= x_thresh:
                    bounds[2].append(len(row_sum) - j - 1)
                    break
            for j in range(len(row_sum)):
                if row_sum[j] >= x_thresh:
                    bounds[3].append(j)
                    break
        return bounds

    def iterative_align(self, element, data, thetas, pad, blur_bool, rin, rout, center, algorithm, upsample_factor, save_bool, debug_bool, iters=5):
        '''
        iterative alignment method from TomoPy
        Variables
        -----------
        element: int
            element index
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        thetas: ndarray
            sorted projection angle list
        iters: int
            number of iterations
        '''
        num_projections = data.shape[1]
        prj = data[element]
        # prj = np.sum(data, axis=0)
        prj = tomopy.remove_nan(prj, val=0.0)
        prj[np.where(prj == np.inf)] = 0.0
        self.thetas = thetas


        # self.get_iter_paraeters()


        prj, sx, sy, conv = tomopy.align_joint(prj, thetas, iters=iters, pad=pad,
                            blur=blur_bool, rin=rin, rout=rout, center=center, algorithm=algorithm, 
                            upsample_factor=upsample_factor, save=save_bool, debug=debug_bool)
        self.x_shifts = np.round(sx).astype(int)
        self.y_shifts = np.round(sy).astype(int)

        for i in range(num_projections):
            data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(self.y_shifts[i])), axis=1)
            data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(self.x_shifts[i])), axis=2)
        
        return self.x_shifts, self.y_shifts, data

    def alignFromText2(self, fileName, data):
        '''
        align by reading text file that saved prior image registration
        alignment info is saved in following format: name of the file, xshift, yshift
        by locating where the comma(,) is we can extract information:
        name of the file(string before first comma),
        yshift(string after first comma before second comma),
        xshift(string after second comma)
        Variables
        -----------
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]

        '''
        try:
            ##### for future reference "All File (*);;CSV (*.csv *.CSV)"

            #TODO: if text file is not in correct format, do nothing, return and display reason for error.
            file = open(fileName[0], 'r')
            read = file.readlines()
            datacopy = zeros(data.shape)
            datacopy[...] = data[...]
            data[np.isnan(data)] = 1
            num_projections = data.shape[1]
            y_shifts = np.zeros(num_projections)
            x_shifts = np.zeros(num_projections)
            for i in arange(num_projections):
                j = i + 1
                secondcol = read[j].rfind(",")
                firstcol = read[j][:secondcol].rfind(",")
                y_shifts[i] = int(float(read[j][secondcol + 1:-1]))
                x_shifts[i] = int(float(read[j][firstcol + 1:secondcol]))
                data[:, i, :, :] = np.roll(data[:, i, :, :], int(x_shifts[i]), axis=2)
                data[:, i, :, :] = np.roll(data[:, i, :, :], int(-y_shifts[i]), axis=1)

            file.close()
            self.alignmentDone()
            # return data, self.x_shifts, self.y_shifts, self.centers
            return data, x_shifts, y_shifts
        except IndexError:
            print("index missmatch between align file and current dataset ")
        except IOError:
            print("choose file please")
        except TypeError: 
            print("choose file please")
        return

    def alignmentDone(self):
        '''send message that alignment has been done'''
        print("Alignment has been completed")

    def find_center(self, tomo, thetas, slice_index, init_center, tol, mask_bool, ratio):
        center = tomopy.find_center(tomo, thetas, slice_index, init_center, tol, mask_bool, ratio)
        return center[0]

    def rot_center3(self, thetasum, ave_mode = None, limit = None, return_all = False):
        # thetasum: 1d or 2d array of summed projections. (z,x)
        if thetasum.ndim == 1:
            thetasum = thetasum[None,:]
        T = spf.fft(thetasum, axis = 1)
        # Collect real and imaginary coefficients.
        real, imag = T[:,1].real, T[:,1].imag
        rows = thetasum.shape[0]
        cols = thetasum.shape[1]
        # In a sinogram the feature may be more positive or less positive than the background (i.e. fluorescence vs
        # absorption contrast). This can mess with the T_phase value so we multiply by the sign of the even function
        # to account for this.
        T_phase = np.arctan2(imag*np.sign(real),real*np.sign(real))
        if ave_mode == 'Mean':
            # Use the mean of the centers from each row as center shift.
            # Good for objects filling the field of view (i.e. local/roi tomography)
            return np.mean(T_phase)/(np.pi*2)*cols

        elif ave_mode == 'Median':
            # Use median value as center shift.
            return np.median(T_phase)/(np.pi*2)*cols

        elif ave_mode == 'Local':
            # Use local mean from window about the median vlimitalue as center shift.
            # Good for objects fully contained within the field of view.
            # Default window is 2*rows//10
            med = np.median(T_phase)
            if limit == None:
                return tmean(T_phase, limits = (med-10, med+10))/(np.pi*2)*cols
            else:
                return tmean(T_phase, limits = (med-limit, med+limit))/(np.pi*2)*cols
        else:
            # Use value from center row as center shift.
            # Fastest option.
            if return_all:
                return T_phase/(np.pi*2)*cols
            return T_phase[rows//2]/(np.pi*2)*cols