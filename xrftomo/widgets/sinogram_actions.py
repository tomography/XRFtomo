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
import scipy.fftpack as spf
from scipy import ndimage, optimize, signal
import tomopy
from skimage import filters
from skimage.measure import regionprops
from skimage.feature import register_translation
import numpy as np

class SinogramActions(QtWidgets.QWidget):
    def __init__(self):
        super(SinogramActions, self).__init__()
        self.x_shifts = None
        self.y_shifts = None
        self.original_data = None
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
    #     weighted: bool
    #         run center of mass or weighted center of mass
    #     shift_y: bool
    #         align in y as well as x 
    #     '''
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
                data = self.shiftProjection(data, w_x_shifts[i], 0, i)
                if shift_y:
                    data = self.shiftProjection(data, 0, w_y_shifts[i], i)

            if not shift_y: 
                w_y_shifts = np.asarray(w_y_shifts)*0
            return data, np.asarray(w_x_shifts), -np.asarray(w_y_shifts)

        if not weighted:
            for i in range(num_projections):
                image = data[element, i]
                threshold_value = filters.threshold_otsu(image)
                labeled_foreground = (image > threshold_value).astype(int)
                properties = regionprops(labeled_foreground, image)
                center_of_mass = properties[0].centroid
                x_shifts.append(int(round(view_center_x -center_of_mass[1])))
                y_shifts.append(int(round(view_center_y - center_of_mass[0])))
                data = self.shiftProjection(data, x_shifts[i], 0, i)
                if shift_y:
                    data = self.shiftProjection(data, 0, y_shifts[i], i)
                    
            if not shift_y: 
                y_shifts = np.asarray(y_shifts)*0
            return data, np.asarray(x_shifts), -np.asarray(y_shifts)

    def shiftProjection(self, data, x, y, index):
        X = int(x//1)
        Y = int(y//1)
        x = x - X
        y = y - Y 

        if x > 0: 
            x_dir = 1
        elif x < 0:
            x_dir = -1
        else:
            x_dir = 0

        if y > 0: 
            y_dir = 1
        elif x < 0:
            y_dir = -1
        else:
            y_dir = 0

        data[:,index] = np.roll(data[:,index], Y, axis=1)  #negative because image coordinates are flipped
        data[:,index] = np.roll(data[:,index], X, axis=2)

        if x_dir == 0 and y_dir == 0:
            return data

        else:
            data_a = data*x
            data_b = data*(1-x)
            data_b = self.shiftProjection(data_b,x_dir,0, index)
            data_c = data_a+data_b

            data_a = data_c*y
            data_b = data_c*(1-y)
            data_b = self.shiftProjection(data_b,0,y_dir, index)
            data = data_a+data_b

            return data

    def shiftStack(self, data, x, y):
        X = int(x//1)
        Y = int(y//1)
        x = x - X
        y = y - Y 

        if x > 0: 
            x_dir = 1
        elif x < 0:
            x_dir = -1
        else:
            x_dir = 0

        if y > 0: 
            y_dir = 1
        elif x < 0:
            y_dir = -1
        else:
            y_dir = 0

        for i in range(data.shape[1]):
            data[:,i] = np.roll(data[:,i],Y,axis=1)
        for i in range(data.shape[1]):
            data[:,i] = np.roll(data[:,i],X, axis=2)

        if x_dir == 0 and y_dir == 0:
            return data

        else:
            data_a = data*x
            data_b = data*(1-x)
            data_b = self.shiftStack(data_b,x_dir,0)
            data_c = data_a+data_b

            data_a = data_c*y
            data_b = data_c*(1-y)
            data_b = self.shiftStack(data_b,0,y_dir)
            data = data_a+data_b

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
        regShift = np.zeros(sinogramData.shape[0], dtype=np.int)
        sinogramData[col_number * 10:col_number * 10 + 10, :] = np.roll(sinogramData[col_number * 10:col_number * 10 + 10, :], shift_number, axis=1)
        regShift[col_number] += shift_number
        for i in range(num_projections):
            # data[:,i,:,:] = np.roll(data[:,i,:,:], regShift[i], axis=2)
            data = self.shiftProjection(data, regShift[i],0,i)
        return data, sinogramData  

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
        #TODO: make this a continuou (subpixel/fractional) shift
        lin_shift = [x + shift for x in lin_shift]

        for i in range(num_projections):
            data, sinogramData = self.shift(sinogramData, data, lin_shift[i], i)
            # data[:,i] = np.roll(data[:,i],shift,axis=1)
            # data = self.shiftProjection(data,shift,0,i)

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
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)
        for i in range(num_projections - 1):
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

            # data[:, i + 1] = np.roll(data[:, i + 1], t0, axis=1)
            # data[:, i + 1] = np.roll(data[:, i + 1], t1, axis=2)
            data = self.shiftProjection(data,t1,t0,i+1)

            x_shifts[i + 1] += t1
            y_shifts[i + 1] += t0

        self.alignmentDone()
        return data, x_shifts, -y_shifts

    def crossCorrelate2(self, element, data):
        '''
        cross correlate image registration aplies to all loaded elements.
        Variables
        -----------
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)

        for i in range(1, num_projections):

            shift, error, diffphase = register_translation(data[element,i-1], data[element,i])
            # shift, error, diffphase = register_translation(data[element,i-1], data[element,i], 100)

            x_shifts[i] += round(shift[1],2)
            y_shifts[i] += round(shift[0],2)
            # data[:, i] = np.roll(data[:, i], y_shifts[i], axis=1)
            # data[:, i] = np.roll(data[:, i], x_shifts[i], axis=2)
            data = self.shiftProjection(data,x_shifts[i],y_shifts[i],i)


        self.alignmentDone()
        return data, x_shifts, -y_shifts

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
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)
        for i in range(num_projections - 1):
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

            # data[:, i + 1] = np.roll(data[:, i + 1], t0, axis=1)
            # data[:, i + 1] = np.roll(data[:, i + 1], t1, axis=2)
            data = self.shiftProjection(data,t1,t0,i+1)

            x_shifts[i + 1] += t1
            y_shifts[i + 1] += -t0
        self.alignmentDone()
        return data, x_shifts, y_shifts
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
        num_projections = data.shape[1]
        y_shifts = np.zeros(num_projections)
        tmp_data = data[element,:,:,:]
        bounds = self.get_boundaries(tmp_data,threshold)
        edge = np.asarray(bounds[2+loc])
        translate = -edge

        # self.data = np.roll(data, int(np.round(self.y_shifts)), axis=1)
        y_shifts -= translate

        for i in range(num_projections):
            # data[:,i] = np.roll(data[:,i], int(np.round(translate[i])), axis=1)
            data = self.shiftProjection(data, 0, np.round(translate[i],2), i)

        self.alignmentDone()
        return y_shifts, data 

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
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)
        prj = data[element]
        # prj = np.sum(data, axis=0)
        prj = tomopy.remove_nan(prj, val=0.0)
        prj[np.where(prj == np.inf)] = 0.0

        # self.get_iter_paraeters()

        prj, sx, sy, conv = tomopy.align_joint(prj, thetas, iters=iters, pad=pad,
                            blur=blur_bool, rin=rin, rout=rout, center=center, algorithm=algorithm, 
                            upsample_factor=upsample_factor, save=save_bool, debug=debug_bool)
        x_shifts = np.round(sx,2)
        y_shifts = np.round(sy,2)

        for i in range(num_projections):
            # data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(y_shifts[i])), axis=1)
            # data[:,i,:,:] = np.roll(data[:,i,:,:], int(np.round(x_shifts[i])), axis=2)
            data = self.shiftProjection(data, x_shifts[i], y_shifts[i], i)
        
        return x_shifts, y_shifts, data

    def alignFromText2(self, fileName, data, data_fnames, x_padding=0):
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
            #unalign first, y_axis possibly inverted. 
            num_projections = data.shape[1]
            x_shifts = self.x_shifts
            y_shifts = self.y_shifts
            fnames = []
            for i in range(num_projections):
                data = self.shiftProjection(data,-x_shifts[i],y_shifts[i], i)

            #read alignment data
            file = open(fileName[0], 'r')
            read = file.readlines()
            datacopy = np.zeros(data.shape)
            datacopy[...] = data[...]
            data[np.isnan(data)] = 1
            num_projections = data.shape[1]
            y_shifts = np.zeros(num_projections)
            x_shifts = np.zeros(num_projections)

            #If alignment contains more shifts than there are projections, only align entries with matching fnmaes

            alignment_mask = []
            tmp_y = []
            tmp_x = []

            if len(read[1].split(',')) == 2:
                for i in range(len(read)-1):
                    j = i + 1
                    print(str(j))
                    fnames.append(str(i))
                    tmp_y.append(round(float(read[j].split(",")[1])))
                    tmp_x.append(round(float(read[j].split(",")[0])))
                    alignment_mask.append(1)

            if len(read[1].split(',')) == 3:
                for i in range(len(read)-1):
                    j = i + 1
                    print(str(j))
                    fnames.append(read[j].split(",")[0])
                    tmp_y.append(round(float(read[j].split(",")[2])))
                    tmp_x.append(round(float(read[j].split(",")[1])))
                    if fnames[i] in data_fnames:
                        alignment_mask.append(1)
                    else:
                        alignment_mask.append(0)
            tmp_x = np.asarray(tmp_x)
            tmp_y = np.asarray(tmp_y)
            fnames = np.asarray(fnames)
            alignment_mask = np.asarray(alignment_mask)

            tmp_x = tmp_x[alignment_mask==1]
            tmp_y = tmp_y[alignment_mask==1]
            num_projections = len(tmp_y)


            for i in range(num_projections):
                # j = i + 1
                # secondcol = round(float(read[j].split(",")[2]))
                # firstcol = round(float(read[j].split(",")[1]))
                # y_shifts[i] = secondcol
                # x_shifts[i] = firstcol
                #
                y_shifts[i] = tmp_y[i]
                x_shifts[i] = tmp_x[i]

                x_shifts = list(x_shifts)
                y_shifts = list(y_shifts)
                x_shifts[i] = self.unwind(x_shifts[i], data.shape[3]-x_padding*2)
                print(i)
                data = self.shiftProjection(data,x_shifts[i],-y_shifts[i],i)

            file.close()
            self.alignmentDone()
            return data, x_shifts, y_shifts
        except IndexError:
            print("index missmatch between align file and current dataset ")
        except IOError:
            print("choose file please")
        except TypeError: 
            print("choose file please")
        return

    def unwind(self, x_shift, x_range):
        # TODO: x_range for unwind() must take into account the x padding, simply using data.shape wont work.
        # need to add padding if it exists
        # see which one works: original data.shape[3] or original data.shape[3] AND padding
        #
        if x_shift >= x_range/2:
            x_shift = x_shift - x_range
        elif x_shift <= -x_range/2:
            x_shift = x_shift + x_range

        return x_shift

    def alignmentDone(self):
        '''send message that alignment has been done'''
        print("Alignment has been completed")

    def find_center(self, tomo, thetas, slice_index, init_center, tol, mask_bool, ratio):
        center = tomopy.find_center(tomo, thetas, slice_index, init_center, tol, mask_bool, ratio)
        return center[0]

    def move_rot_axis(self, thetas, center, rAxis_pos, theta_pos):
        #set 0th angle to 
        num_theas = thetas.shape[0]
        pos_from_center = [rAxis_pos - center]
        angle_offset = -180-theta_pos
        thetas = thetas + angle_offset
        rads = np.radians(thetas)
        # angle_increments = rads[1:]-rads[:-1]
        offsets = pos_from_center[0]*np.cos(rads)
        # adjustment = pos_from_center[0]*-1 - offsets[0]
        # offsets += adjustment
        return offsets
        
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
                return np.tmean(T_phase, limits = (med-10, med+10))/(np.pi*2)*cols
            else:
                return np.tmean(T_phase, limits = (med-limit, med+limit))/(np.pi*2)*cols
        else:
            # Use value from center row as center shift.
            # Fastest option.
            if return_all:
                return T_phase/(np.pi*2)*cols
            return T_phase[rows//2]/(np.pi*2)*cols

    def hotspot2line(self, element, x_size, y_size, hs_group, posMat, data):
        '''
        aligns projections to a line based on hotspot information

        Variables
        -----------
        element: int
            element index
        x_size: int
            ROI pixel dimension in x
        y_size: int
            ROI pixel dimension in y
        hs_group: int
            hotspot group number
        posMat: ndarray
            position matrix.
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        #TODO: onsider having posMat as part of the history state and have it update one level up.
        self.posMat = posMat
        self.posMat[0] = posMat[0] + x_size//2
        self.posMat[1] = posMat[1] + y_size//2
        hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, posMat, data)
#****************
        num_projections = data.shape[1]
        y_shifts = np.zeros(num_projections)
        x_shifts = np.zeros(num_projections)
        for j in range(num_projections):

            if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
                yyshift = int(round(y_size//2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
                xxshift = int(round(x_size//2 - hotSpotX[j] - hs_x_pos[j] + hs_x_pos[firstPosOfHotSpot]))
                # data[:, j, :, :] = np.roll(np.roll(data[:, j, :, :], xxshift, axis=2), yyshift, axis=1)
                data = self.shiftProjection(data, xxshift,yyshift,j)
            if hs_x_pos[j] == 0:
                xxshift = 0
            if hs_y_pos[j] == 0:
                yyshift = 0

            x_shifts[j] = xxshift
            y_shifts[j] = yyshift

        print("align done")
        return data, x_shifts, y_shifts

    def hotspot2sine(self, element, x_size, y_size, hs_group, posMat, data, thetas):
        '''
        aligns projections to a sine curve based on hotspot information

        Variables
        -----------
        element: int
            element index
        x_size: int
            ROI pixel dimension in x
        y_size: int
            ROI pixel dimension in y
        hs_group: int
            hotspot group number
        posMat: ndarray
            position matrix. 2
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        thetas: ndarray
            sorted projection angle list
        '''
        self.posMat = posMat
        self.posMat[0] = posMat[0] + x_size//2
        self.posMat[1] = posMat[1] + y_size//2

        hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, self.posMat, data)
#****************
        num_projections = data.shape[1]
        y_shifts = np.zeros(num_projections)
        x_shifts = np.zeros(num_projections)
        thetas  = np.asarray(thetas)
        for j in range(num_projections):

            if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
                xxshift = int(round(x_size//2 - hotSpotX[j]))
                yyshift = int(round(y_size//2 - hotSpotY[j]))
            if hs_x_pos[j] == 0:
                xxshift = 0
            if hs_y_pos[j] == 0:
                yyshift = 0

            x_shifts[j] = xxshift
            y_shifts[j] = yyshift

        hotspotXPos = np.zeros(num_projections, dtype=np.int)
        hotspotYPos = np.zeros(num_projections, dtype=np.int)
        for i in range(num_projections):
            hotspotYPos[i] = int(round(hs_y_pos[i]))
            hotspotXPos[i] = int(round(hs_x_pos[i]))
        hotspotProj = np.where(hotspotXPos != 0)[0]

        theta_tmp = thetas[hotspotProj]
        com = hotspotXPos[hotspotProj]

        if hs_group == 0:
            self.fitCenterOfMass(com, x=theta_tmp)
        else:
            self.fitCenterOfMass2(com, self.centers, x=theta_tmp)
        self.alignCenterOfMass2(hotspotProj, data)

        ## yfit
        for i in hotspotProj:
            y_shifts[i] = int(hotspotYPos[hotspotProj[0]]) - int(hotspotYPos[i])
            # data[:, i] = np.roll(data[:, i], y_shifts[i], axis=1)
            data = self.shiftProjection(data, 0,y_shifts[i],i)

        #update reconstruction slider value
        # self.recon.sld.setValue(self.centers[2])

        print("align done")
        self.centers = list(np.round(self.centers))
        return data, x_shifts, y_shifts


    def setY(self, element, x_size, y_size, hs_group, posMat, data):
        '''
        aligns projections vertically
        Variables
        -----------
        element: int
            element index
        x_size: int
            ROI pixel dimension in x
        y_size: int
            ROI pixel dimension in y
        hs_group: int
            hotspot group number
        posMat: ndarray
            position matrix. 2
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        self.posMat = posMat
        self.posMat[0] = posMat[0] + x_size//2
        self.posMat[1] = posMat[1] + y_size//2

        hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, self.posMat, data)
        num_projections = data.shape[1]
        y_shifts = np.zeros(num_projections)
        for j in range(num_projections):
            if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
                yyshift = int(round(y_size//2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
                # data[:, j] = np.roll(data[:, j], yyshift, axis=1)
                data = self.shiftProjection(data,0, yyshift,j)

            if hs_y_pos[j] == 0:
                yyshift = 0

            y_shifts[j] = -yyshift

        print("align done")

        return data, y_shifts

    def alignment_parameters(self, element, x_size, y_size, hs_group, posMat, data):
        '''
        gathers parameters for alignment functions
        Variables
        -----------
        element: int
            element index
        x_size: int
            ROI pixel dimension in x
        y_size: int
            ROI pixel dimension in y
        hs_group: int
            hotspot group number
        posMat: ndarray
            position matrix. 2
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        self.posMat = posMat

        num_projections = data.shape[1]
        hs_x_pos = np.zeros(num_projections, dtype=np.int)
        hs_y_pos = np.zeros(num_projections, dtype=np.int)
        hs_array = np.zeros([num_projections, y_size//2*2, x_size//2*2], dtype=np.int)

        for i in range(num_projections):
            hs_x_pos[i] = int(round(self.posMat[hs_group, i, 0]))
            hs_y_pos[i] = int(abs(round(self.posMat[hs_group, i, 1])))

            if hs_x_pos[i] != 0 and hs_y_pos[i] != 0:
                if hs_y_pos[i] > (data.shape[2] - y_size//2):   # if ROI is past top edge of projection
                    hs_y_pos[i] = data.shape[2] - y_size//2
                if hs_y_pos[i] < y_size//2: # if ROI is past bottom of projection
                    hs_y_pos[i] = y_size//2
                if hs_x_pos[i] < x_size//2: # if ROI is past left edge of projection
                    hs_x_pos[i] = x_size//2
                if hs_x_pos[i] > (data.shape[3] - x_size//2): # if ROI is past right edge of projection
                    hs_x_pos[i] = data.shape[3] - x_size//2
                y0 = hs_y_pos[i] - y_size//2
                y1 = hs_y_pos[i] + y_size//2
                x0 = hs_x_pos[i] - x_size//2
                x1 = hs_x_pos[i] + x_size//2
                hs_array[i, :, :] = data[element, i, (data.shape[2] - y1):(data.shape[2] - y0), x0:x1]

        hotSpotX = np.zeros(num_projections, dtype=np.int)
        hotSpotY = np.zeros(num_projections, dtype=np.int)
        new_hs_array = np.zeros(hs_array.shape, dtype=np.int)
        new_hs_array[...] = hs_array[...]
        firstPosOfHotSpot = 0

        add = 1
        for i in range(num_projections):
            if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
                firstPosOfHotSpot += add
            if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
                img = hs_array[i, :, :]
                a, x, y, b, c = self.fitgaussian(img)
                hotSpotY[i] = x
                hotSpotX[i] = y
                yshift_tmp = int(round(y_size - hotSpotY[i]))
                xshift_tmp = int(round(x_size - hotSpotX[i]))
                new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], xshift_tmp, axis=1)
                new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], yshift_tmp, axis=0)
                add = 0

        return hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data

    def fitCenterOfMass(self, com, x):
        fitfunc = lambda p, x: p[0] * np.sin(2 * np.pi / 360 * (x - p[1])) + p[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [100, 100, 100]
        self.centers, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
        self.centerOfMassDiff = fitfunc(p0, x) - com
        print(self.centerOfMassDiff)
        
    def alignCenterOfMass2(self, hotspotProj, data):
        j = 0
        for i in hotspotProj:
            self.x_shifts[i] += int(self.centerOfMassDiff[j])

            # data[:, i] = np.roll(data[:, i], int(round(self.x_shifts[i])), axis=2)
            data = self.shiftProjection(data, self.x_shifts[i],0,i)
            j += 1

      #set some label to be show that the alignment has completed. perhaps print this in a logbox

    def fitCenterOfMass2(self, com, x):
        fitfunc = lambda p, x: p[0] * np.sin(2 * np.pi / 360 * (x - p[1])) + self.centers[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [100, 100]
        p2, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
        self.centerOfMassDiff = fitfunc(p2, x) - com
        print(self.centerOfMassDiff)

    def fitgaussian(self, data):
        """
        Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution found by a fit
        """
        params = self.moments(data)
        errorfunction = lambda p: np.ravel(self.gaussian(*p)(*np.indices(data.shape)) - data)
        p, success = optimize.leastsq(errorfunction, params)
        return p

    def moments(self, data):
        """
        Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution by calculating its
        moments
        """
        total = data.sum()
        if total == 0:
            x = 0
            y = 0
        else:
            X, Y = np.indices(data.shape)
            x = (X * data).sum() / total
            y = (Y * data).sum() / total

        col = data[:, int(y)]

        if col.sum() == 0:
            width_x = 0
        else:
            width_x = np.sqrt(abs((np.arange(col.size) - y) ** 2 * col).sum() / col.sum())
        # TODO: rundime wasrning: invalid value encountered in double_scalars

        row = data[int(x), :]
        if row.sum() == 0:
            width_y = 0
        else:
            width_y = np.sqrt(abs((np.arange(row.size) - x) ** 2 * row).sum() / row.sum())

        height = data.max()

        return height, x, y, width_x, width_y

    def gaussian(self, height, center_x, center_y, width_x, width_y):
        """
        Returns a gaussian function with the given parameters
        """
        width_x = float(width_x)
        width_y = float(width_y)
        if width_x == 0:
            return lambda x, y: 0
        if width_y == 0:
            return lambda x, y: 0

        # ss = lambda x, y: height * exp(-(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

        return lambda x, y: height * np.exp(-(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

    def clrHotspot(self, posMat):
        '''
        resets
        hotspot position matrix
        '''
        posMat[...] = np.zeros_like(posMat)
        return posMat
