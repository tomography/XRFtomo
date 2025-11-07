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

from PyQt5 import QtGui, QtCore, QtWidgets
import scipy.fftpack as spf
from scipy import ndimage, optimize, signal
import tomopy
from skimage import filters
from skimage.measure import regionprops
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2gray
from skimage.transform import warp
from skimage.registration import optical_flow_tvl1, optical_flow_ilk
import scipy.ndimage
from skimage.registration import phase_cross_correlation
from scipy.signal import find_peaks
import matplotlib; matplotlib.use('Qt5Agg')

class SinogramActions(QtWidgets.QWidget):
    def __init__(self):
        super(SinogramActions, self).__init__()
        self.x_shifts = None
        self.y_shifts = None
        self.original_data = None
        self.padding = None

    def run_fit_peaks(self,element,data):
        stack = data[element]
        num_proj = stack.shape[0]
        y_midpt = data[element].shape[1]//2
        x_midpt = data[element].shape[2]//2

        x_shifts = np.zeros(num_proj)
        y_shifts = np.zeros(num_proj)

        for i in range(num_proj):
            img=stack[i]
            row = np.sum(img, axis=0)
            col = np.sum(img, axis=1)
            maxx_index = np.argmax(row)
            maxy_index = np.argmax(col)
            x_shifts[i] = x_midpt - maxx_index
            y_shifts[i] = y_midpt - maxy_index
            data = self.shiftProjection(data,x_shifts[i],y_shifts[i],i)
            # data[:,i] = scipy.ndimage.shift(data[element,i], x_shifts[i], output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)
        print("pause")
        return data, x_shifts, y_shifts


    def runOpFlow(self, element,data):
        try:
            # --- Load the sequence
            imgs = data[element]

            image0 = imgs[0]
            image1 = np.fliplr(imgs[-1])

            img1_max = image1.max()
            #need to normalize to 1
            image0 = image0 / image0.max()
            image1 = image1 / image1.max()

            # --- Compute the optical flow
            v, u = optical_flow_tvl1(image0, image1)

            # --- Use the estimated optical flow for registration
            nr, nc = image0.shape
            row_coords, col_coords = np.meshgrid(np.arange(nr), np.arange(nc),indexing='ij')
            image1_warp = warp(image1, np.array([row_coords + v, col_coords + u]),mode='nearest')

            #convert to original scale
            image1_warp = np.fliplr(image1_warp*img1_max)
            data[element,-1] = image1_warp
        except Exception as error:
            print("runOpFlow error: ", error)
        return data


    def runCenterOfMass(self, element, data):
        '''
        Center of mass alignment
        Variables
        -----------
        element: int
            element index
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        thetas: ndarray
            sorted projection angle list
        '''
        num_projections = data.shape[1]
        view_center_x = data.shape[3]//2
        view_center_y = data.shape[2]//2

        w_x_shifts = []
        w_y_shifts = []
        for i in range(num_projections):
            image = data[element, i]
            threshold_value = filters.threshold_otsu(image)
            labeled_foreground = (image > threshold_value).astype(int)
            properties = regionprops(labeled_foreground, image)
            #TODO: if input image is blank, WCoM will fail, create an exception case.
            weighted_center_of_mass = properties[0].weighted_centroid
            w_x_shifts.append(int(round(view_center_x - weighted_center_of_mass[1])))
            w_y_shifts.append(int(round(view_center_y - weighted_center_of_mass[0])))
            data = self.shiftProjection(data, w_x_shifts[i], 0, i)
            data = self.shiftProjection(data, 0, w_y_shifts[i], i)

        return data, np.asarray(w_x_shifts), -np.asarray(w_y_shifts)


    def shift_all(self, data, x_shifts, y_shifts = None):
        num_elements = data.shape[0]
        num_projections = data.shape[1]
        if y_shifts is None:
            for i in range(num_elements):
                for j in range(num_projections):
                    data[i,j] = scipy.ndimage.shift(data[i,j], (np.zeros_like(x_shifts)[j],x_shifts[j]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)
        else:
            for i in range(num_elements):
                for j in range(num_projections):
                    data[i,j] = scipy.ndimage.shift(data[i,j],(-y_shifts[j],x_shifts[j]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)

        return data
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
        regShift = np.zeros(sinogramData.shape[0], dtype="int")
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

            x_shifts[i + 1] += t1
            y_shifts[i + 1] += t0

        self.alignmentDone()
        return x_shifts, -y_shifts

    def crossCorrelate2(self, element, data):
        '''
        cross correlate image registration aplies to all loaded elements.
        Variables
        -----------
        element: index of 0th  element in data.
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)
        for i in range(1, num_projections):
            shift, error, diffphase = phase_cross_correlation(data[element,i-1], data[element,i],upsample_factor=100)
            x_shifts[i] += round(shift[1],2)
            y_shifts[i] += round(shift[0],2)
            # data[:,i] = scipy.ndimage.shift(data[:,i],(y_shifts[i],x_shifts[i]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)
            for j in range(data.shape[0]):
                data[j,i] = scipy.ndimage.shift(data[j,i], (y_shifts[i], x_shifts[i]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)

        self.alignmentDone()
        return data, x_shifts, -y_shifts

    def xcor_ysum_orig(self, element, data):
        '''
        cross correlate row sum of 3D data
        Variables
        -----------
        element: index of 0th  element in data.
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)

        row_sums = np.array([np.sum(data[element, i],axis=1) for i in range(data.shape[1])])
        row_sums_orig = np.copy(row_sums)
        new_row_sums = np.copy(row_sums)

        row_sums_squd = np.sum(row_sums**2, axis=0)
        peaks, dummy = find_peaks(row_sums_squd, prominence=(row_sums_squd.max() / 5, row_sums_squd.max()))
        peak_locs = np.flip(peaks[np.argsort(row_sums_squd[peaks])])
        num_peaks = len(peaks)

        plt.figure()
        #downsample to only 20 projections or less
        # dummy = self.multiplot(row_sums_orig)

        if num_peaks>1:
            # select 2nd peak
            tail = int(peak_locs[1] - 20)
            head = int(peak_locs[1] + 20)
            new_row_sums = new_row_sums[:,tail:head]
        else:
            # select 1st peak
            tail = int(peak_locs[0] - 20)
            head = int(peak_locs[0] + 20)
            new_row_sums = new_row_sums[:,tail:head]


        #fit max peaks, first pass...
        num_peaks = row_sums.shape[0]
        max_peak_locs = np.zeros(num_peaks)
        for i in range(num_peaks):
            sum_sqrd = row_sums[i]** 2
            norm_arr = sum_sqrd/sum_sqrd.max()
            peaks, dummy = find_peaks(norm_arr, prominence=(1/5,1))
            max_locs = np.flip(peaks[np.argsort(sum_sqrd[peaks])])
            max_peak_locs[i] = max_locs[0]

        for i in range(1, num_projections):
            shift = max_peak_locs[i]-max_peak_locs[0]
            y_shifts[i] -= shift
            row_sums[i] = scipy.ndimage.shift(row_sums[i], y_shifts[i], output=None, order=3, mode='wrap', cval=0.0, prefilter=True)

        y_shifts2 = np.zeros_like(y_shifts)
        for i in range(1, num_projections):
            shift, error, diffphase = phase_cross_correlation(row_sums[i-1]**2, row_sums[i]**2,upsample_factor=100)
            y_shifts2[i] += round(shift[0],2)

        y_shifts2= self.tweak_shifts(y_shifts2, row_sums)

        for i in range(len(y_shifts)):
            row_sums[i] = scipy.ndimage.shift(row_sums[i], y_shifts2[i], output=None, order=3, mode='wrap', cval=0.0, prefilter=True)

        ##push edges
        shifts = self.push_edge(new_row_sums)

        for i in range(len(y_shifts)):
            new_row_sums[i] = scipy.ndimage.shift(new_row_sums[i], y_shifts[i], output=None, order=3, mode='wrap', cval=0.0, prefilter=True)
            row_sums[i] = scipy.ndimage.shift(row_sums[i], y_shifts[i], output=None, order=3, mode='wrap', cval=0.0, prefilter=True)
            for j in range(data.shape[0]):
                data[j,i] = scipy.ndimage.shift(data[j,i], (y_shifts[i], 0), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)

        self.alignmentDone()
        return data, x_shifts, y_shifts

    def xcor_ysum(self, element, data):
        '''
        cross correlate row sum of 3D data
        Variables
        -----------
        element: index of 0th  element in data.
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        x_shifts = np.zeros(num_projections)
        row_sums = np.array([np.sum(data[element, i],axis=1) for i in range(num_projections)])
        row_sums_orig = np.copy(row_sums)
        dummy = self.multiplot(row_sums_orig)
        try:
            row_sums = scipy.signal.savgol_filter(row_sums, 11, 2, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
        except:
            row_sums = scipy.signal.savgol_filter(row_sums, 3, 2, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)

        ##push edges
        #does not work with datasets that has a lot of self-absorbtion,
        y_shifts = self.push_edge(row_sums,1,0.7)
        # y_shifts = []
        # other_arr = np.zeros_like(row_sums)
        # for i in range(1, row_sums.shape[0]):
        #     shift, error, diffphase = phase_cross_correlation(row_sums[i-1], row_sums[1], upsample_factor=100)
        #     y_shifts.append(shift)
        #     row_sums[i] = scipy.ndimage.shift(row_sums[i], shift, output = None, order = 3, mode = 'grid-wrap', cval = 0.0, prefilter = True)
        #     other_arr[i] = row_sums[i]/row_sums[i].max()
        # row_sums = scipy.ndimage.shift(row_sums, y_shifts, output=None, order=3, mode='wrap', cval=0.0, prefilter=True)

        dummy = self.multiplot(row_sums)
        # plt.figure()
        # plt.plot(np.rot90(row_sums))
        # plt.figure()
        # plt.plot(np.rot90(other_arr))

        plt.show()
        self.alignmentDone()
        return x_shifts, y_shifts


    def push_edge(self, arr, side=0,threshold=0.6):

        num_rows = arr.shape[0]
        Lindx = []
        Rindx = []
        norm_arr = np.zeros_like(arr)
        for i in range(num_rows):
            norm_arr[i] = arr[i]/arr[i].max()

        for i in range(num_rows):
            max_val = norm_arr[i].max()
            idx = np.where(norm_arr[i]>max_val*threshold)
            Lindx.append(idx[0][0])
            Rindx.append(idx[0][-1])

        l_shifts = [Lindx[i] - Lindx[0] for i in range(1,len(Lindx))]
        r_shifts = [Rindx[i] - Rindx[0] for i in range(1,len(Rindx))]
        l_shifts.insert(0,0)
        r_shifts.insert(0,0)
        if side==0:
            return l_shifts
        elif side ==1:
            return r_shifts
        else:
            print("problem")
            return l_shifts



    def relax_edge(self, arr, N):

        if len(arr.shape) >=2:
            new_arr = np.zeros_like(arr)
            for i in range(new_arr.shape[0]):
                for j in range(N):
                    new_arr[i] = self.trim_edge(arr[i])
                new_arr[i][-1]=0
                new_arr[i][0]=0

            return new_arr
        else:
            #TODO: check array size, if tail_head exceeds bounds, raise exception.
            for i in range(N):
                new_arr = self.trim_edge(arr)
            return new_arr

    def trim_edge(self, arr):
        arr_max = abs(arr.max())
        arr_length = arr.shape[0]
        for i in range(1, arr_length):
            l_diff = abs(arr[i]-arr[i-1])
            r_diff = abs(arr[-i-1] - arr[-i])
            if l_diff > arr_max*0.50:
                arr[i] = 0
                break
            if r_diff >= arr_max*0.50:
                arr[-i-1] = 0
                break
        return arr




    def xcor_dysum(self, element, data):

        '''
        cross correlate row sum of 3D data
        Variables
        -----------
        element: index of 0th  element in data.
        data: ndarray
            4D xrf dataset ndarray [elements, theta, y,x]
        '''
        num_projections = data.shape[1]
        x_shifts = np.zeros(num_projections)
        y_shifts = np.zeros(num_projections)

        yrange = data.shape[2]
        xrange = data.shape[3]
        dy = 0.1
        dx = 0.1

        dy_arr = np.zeros((data.shape[1], data.shape[2]))
        tail_head = int(dy_arr.shape[1] * 0.15)

        stack = np.copy(data[element])
        for i in range(num_projections):

            plotv = np.sum(stack[i], axis=1) * yrange * 0.2 / (np.sum(stack, axis=2).max())
            plotv = scipy.signal.savgol_filter(plotv, 11, 2, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
            plot_dy = np.gradient(plotv, dy)
            plot_dy = scipy.signal.savgol_filter(plot_dy, 11, 2, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)

            ploty_dy = plot_dy * xrange * 0.1 / plot_dy.max()
            dy_arr[i]= ploty_dy**2
            dy_arr[i] = dy_arr[i] / dy_arr[i].max()
        # dy_arr = self.remove_false_peak(dy_arr,4)
        dy_arr_orig = np.copy(dy_arr)

        #plot staggered row sums
        dummy = self.multiplot(dy_arr_orig)
        new_dy_arr = np.copy(dy_arr)
        y_shifts_3 = self.push_edge(new_dy_arr,0,0.80)
        y_shifts = y_shifts+y_shifts_3

        #shift complete array
        for i in range(num_projections):
            dy_arr[i] = scipy.ndimage.shift(dy_arr[i], -y_shifts[i], output=None, order=3, mode='wrap', cval=0.0, prefilter=True)
            stack[i] = scipy.ndimage.shift(stack[i], (-y_shifts[i], 0), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)

        dummy = self.multiplot(dy_arr)

        plt.figure()
        plt.plot(np.rot90(dy_arr))
        plt.plot(np.ones_like(dy_arr)*0.8)
        plt.figure()
        plt.plot(np.rot90(dy_arr_orig))
        plt.plot(np.ones_like(dy_arr)*0.8)
        plt.figure()
        plt.plot(y_shifts)
        plt.show()

        self.alignmentDone()
        return x_shifts, y_shifts


    def remove_false_peak(self,arr, N):
        num_rows = arr.shape[0]
        arr_orig = arr.copy()
        arr = arr**2
        canvas = np.zeros((arr.shape[0], arr.shape[1]+4)) #pad each edge with two zeros
        canvas2 = np.zeros((arr.shape[0], arr.shape[1]+4)) #pad each edge with two zeros
        canvas[:,2:-2]=arr
        canvas2[:,2:-2]=arr_orig
        for n in range(N):
            # self.multiplot(canvas)
            for i in range(num_rows):
                row = canvas[i]
                peaks, dummy = find_peaks(row, prominence=(row.max() / 5, row.max()))
                num_peaks = len(peaks)
                peak_vals = row[peaks]

                for j in range(len(peak_vals)):
                    if peak_vals[j] > 7*arr[i].std():
                        tail = peaks[j]-1
                        head = peaks[j]+1
                        if tail < 0:
                            tail = 0
                        if head > canvas.shape[1]:
                            head = canvas.shape[1] - 1
                        canvas[i,tail:head]=0
                        canvas2[i,tail:head]=0

        new_arr = canvas2[:,2:-2]
        return new_arr





    def multiplot(self, arr):
        plt.figure()
        num_pks = arr.shape[0]
        pks = []
        for i in range(num_pks):
            sum_dy_sqrd = arr[i]** 2
            norm_arr = sum_dy_sqrd/ sum_dy_sqrd.max() + i * 0.2
            plt.plot(np.arange(arr.shape[1]),norm_arr )
            peaks, dummy = find_peaks(sum_dy_sqrd, prominence=(sum_dy_sqrd.max() / 5, sum_dy_sqrd.max()))
            pks.append(peaks)
            plt.plot(peaks, norm_arr[peaks], "x")
        return pks


    def tweak_shifts(self,shifts, arr):
        #look at derivative, find peaks
        dx = np.gradient(shifts, 0.1) ** 2
        arr_width = arr.shape[1]        #ssuming stack of 1 d arrays

        #create difference array
        sd = np.array([shifts[i]-shifts[i-1] for i in range(1,len(shifts))])
        sd = np.insert(sd, 0, 0, axis=0)
        peak_locs = np.where(sd**2>arr_width*5)[0]
        # peak_locs = np.where(sd**2>3*np.mean(sd**2))[0]
        num_peaks = len(peak_locs)
        # plt.figure()
        # plt.plot(abs(sd))
        # plt.plot(peak_locs, abs(sd)[peak_locs], "x")
        # plt.plot(shifts)

        if num_peaks>0:
            pass
        else:
            return shifts

        #check difference_array:
        mean_shift = abs(shifts[np.where(sd**2<3*np.mean(sd**2))[0]]).mean()
        high = False
        low = False
        new_shifts = shifts.copy()
        for i in range(1,len(sd)):
            if i in peak_locs:
                if sd[i]>0 and not low:                         ## mid to high -▔
                    high=True
                    low=False
                    new_shifts[i] = new_shifts[i] - arr_width
                elif sd[i]<0 and high:                          ## high to mid ▔-
                    high=False
                    low = False
                elif sd[i]>0 and low:                           ## low to mid _-
                    low=False
                    high=False
                elif sd[i]<0 and not low:                        ## mid to low -_
                    high=False
                    low=True
                    new_shifts[i] = new_shifts[i] + arr_width
            elif high:
                new_shifts[i] = new_shifts[i] - arr_width
            elif low:
                new_shifts[i] = new_shifts[i] + arr_width
            else:
                pass
        # plt.plot(shifts)
        return new_shifts

    def xcor_sino(self, element, layer, data):
        #sino is 2d array)
        #TODO: iterate through layers and select layer with single feature (i.e. line sinogram)
        if layer==None:
            for i in range(data.shape[2]):
                sino = data[element, :, i, :]

        sino = data[element,:,layer,:] #TODO: IndexError when contrained to ROI
        x_shifts = np.zeros(data.shape[1])
        for i in range(1,sino.shape[0]):
            shift, error, diffphase = phase_cross_correlation(sino[0], sino[i], upsample_factor=100)
            x_shifts[i] = shift[0]


        return x_shifts

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
        img = data[element,:,:,:]

        bounds = self.get_boundaries(img,threshold)
        edge = np.asarray(bounds[2+loc])
        translate = -edge

        # self.data = np.roll(data, int(np.round(self.y_shifts)), axis=1)
        y_shifts -= translate

        self.alignmentDone()
        return y_shifts

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
        prj = tomopy.remove_nan(prj, val=0.0)
        prj[np.where(prj == np.inf)] = 0.0

        thetas = thetas*np.pi/180

        prj, sx, sy, conv = tomopy.align_joint(prj, thetas, iters=iters, pad=pad,
                            blur=blur_bool, rin=rin, rout=rout, center=center, algorithm=algorithm,
                            upsample_factor=upsample_factor, save=save_bool, debug=debug_bool)
        x_shifts = np.round(sx,2)
        y_shifts = np.round(sy,2)

        for i in range(num_projections):
            data = self.shiftProjection(data, x_shifts[i], y_shifts[i], i)

        return x_shifts, y_shifts, data
    def sequential_align(self, element, data, thetas, pad, blur_bool, rin, rout, center, algorithm, upsample_factor, save_bool, debug_bool, iters=5):
        '''
        sequential re-projection algorithm from TomoPy
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
        prj = tomopy.remove_nan(prj, val=0.0)
        prj[np.where(prj == np.inf)] = 0.0

        thetas = thetas*np.pi/180

        prj, sx, sy, conv = tomopy.align_seq(prj, thetas, iters=iters, pad=pad,
                            blur=blur_bool, rin=rin, rout=rout, center=center, algorithm=algorithm,
                            upsample_factor=upsample_factor, save=save_bool, debug=debug_bool)
        x_shifts = np.round(sx,2)
        y_shifts = np.round(sy,2)

        for i in range(num_projections):
            data = self.shiftProjection(data, x_shifts[i], y_shifts[i], i)

        return x_shifts, y_shifts, data

    def alignFromNPY(self, fileName, data, data_fnames, x_padding=0):

        try:
            file = np.load(fileName[0])
            x_shifts = np.array([eval(item) for item in file[1]])
            y_shifts = np.array([eval(item) for item in file[2]])
            datacopy = np.zeros(data.shape)
            datacopy[...] = data[...]
            data[np.isnan(data)] = 1
            data = self.shift_all(data, x_shifts, y_shifts)
            self.alignmentDone()
            return data, x_shifts, y_shifts
        except IndexError:
            print("index missmatch between align file and current dataset ")
        except IOError:
            print("choose file please")
        except TypeError:
            print("choose file please")
        return

    def alignFromText(self, fileName, data, data_fnames, x_padding=0):

        try:
            data_fnames = [file.split("/")[-1] for file in data_fnames]
            #read alignment data
            fnames = []
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

                    fnames.append(str(i))
                    tmp_y.append(round(float(read[j].split(",")[1])))
                    tmp_x.append(round(float(read[j].split(",")[0])))
                    alignment_mask.append(1)

            if len(read[1].split(',')) == 3:
                for i in range(len(read)-1):
                    j = i + 1
                    print(str(j))
                    fname = read[j].split(",")[0].split("/")[-1]
                    fnames.append(fname)
                    tmp_y.append(round(float(read[j].split(",")[2])))
                    tmp_x.append(round(float(read[j].split(",")[1])))
                    if fnames[i] in data_fnames[i]:
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

            y_shifts = list(tmp_y)
            x_shifts = list(tmp_x)
            # data = self.subpixshift_data(data, x_shifts, y_shifts)
            data = self.shift_all(data, x_shifts, y_shifts)
            # data= scipy.ndimage.shift(data, y_shifts[i], x_shifts[i], output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)

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


    def subpixshift_data(self,data,x_shifts,y_shifts):
        dim = len(data.shape)
        if dim > 4:
            print("ERR: array dimensions too big, expected dim <=4")
        if dim == 4:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    data[i,j] = scipy.ndimage.shift(data[i,j], (-y_shifts[j], x_shifts[j]), output=None, order=3, mode='wrap', cval=0.0, prefilter=True)
        return data


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

    def discontinuity_check(self, data, x_shifts, max_diff):
        x_size = data.shape[3]
        idx_x = [idx+1 for idx, val in enumerate(np.diff(x_shifts)) if val > max_diff or val < -max_diff]
        idx_x = np.asarray(idx_x)
        mask = np.zeros_like(x_shifts)
        toggle = 0

        for i in range(len(x_shifts)-1):
            if i in idx_x:
                toggle +=1
                toggle = toggle%2
            mask[i] = toggle

        if x_shifts[0] >= 0:
            x_shifts = x_shifts+mask*x_size
        if x_shifts[0] < 0:
            x_shifts = x_shifts-mask*x_size

        return x_shifts


    def validate_alignment(self,data,x_shifts,y_shifts=None):
        if y_shifts is not None:

            x_size = data.shape[3]
            y_size = data.shape[2]
            num_shifts = len(x_shifts)
            for i in range(num_shifts):
                if abs(x_shifts[i]) > x_size:
                    x_shifts[i] = int(x_shifts[i]%x_size*np.sign(x_shifts[i]))
                if abs(y_shifts[i]) > y_size:
                    y_shifts[i] = int(y_shifts[i]%y_size*np.sign(y_shifts[i]))

            return x_shifts, y_shifts
        else:
            x_size = data.shape[3]
            num_shifts = len(x_shifts)
            for i in range(num_shifts):
                if abs(x_shifts[i]) > x_size:
                    x_shifts[i] = int(x_shifts[i] % x_size * np.sign(x_shifts[i]))

            return x_shifts



        pass

    def pirt(self, ntau, ntheta, anglefile,sinofile, matfile, nslices=1, nsubcommms=1, overall_sweeps=1, alt_outer_its=15,
             lt_sample_its=5, als_shift_its=2, joint_its=100, joint=False, alternating=False, regularize=False,
             combine_mean=False, combine_median=False, synthetic=False):
        """mpirun  -np num_mpi_ranks ./pirt \
        -runtime-option value

        INPUT
        anglefile.h5
        └theta
          └angles       [float64: 100]

        sinofile.h5
        |sino0
        │ └sinogram  [float64: 25600]
        ├sino1
        │ └sinogram  [float64: 25600]
        ......

        OUTPUT
        sol_0.h5
        ├cor
        │ ├shifts[float64: 150]
        │ └sinogram[float64: 76800]
        └reconstruction
        └solution[float64: 262144]
        mpirun -np 4 /home/beams/MARINF/conda/pirt/src/pirt -sinofile /home/beams/MARINF/conda/pirt/tests/data/softwood_512.h5 -anglefile /home/beams/MARINF/conda/pirt/tests/data/theta_150.h5 -ntau 5>

        mpirun -np 4 /path/to/pirt -sinofile /sino/file.h5 -anglefile /angle/file.h5 -ntau 5
        """


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
        #TODO: consider having posMat as part of the history state and have it update one level up.
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

        hotspotXPos = np.zeros(num_projections, dtype="int")
        hotspotYPos = np.zeros(num_projections, dtype="int")
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
        hs_x_pos = np.zeros(num_projections, dtype="int")
        hs_y_pos = np.zeros(num_projections, dtype="int")
        hs_array = np.zeros([num_projections, y_size//2*2, x_size//2*2], dtype="int")

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

        hotSpotX = np.zeros(num_projections, dtype="int")
        hotSpotY = np.zeros(num_projections, dtype="int")
        new_hs_array = np.zeros(hs_array.shape, dtype="int")
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
