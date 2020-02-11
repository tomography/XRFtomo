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
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENTn SHALL UChicago    #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xrftomo
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, signal
from skimage import exposure
import tomopy

#testing
from skimage.exposure import equalize_hist
from skimage.morphology import remove_small_objects, disk
from skimage import exposure
from skimage.filters import rank
import skimage
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from scipy import ndimage as ndi
from scipy import fftpack
from scipy.stats import tmean

class ImageProcessActions(QtWidgets.QWidget):

	def __init__(self):
		super(ImageProcessActions, self).__init__()
		self.hotSpotNumb = 0
		self.x_shifts = None
		self.y_shifts = None
		self.centers = None

	def shiftProjectionY(self, data, index, displacement):
		data[:,index] = np.roll(data[:, index], displacement, axis=1)
		return data

	def shiftProjectionX(self, data, index, displacement):
		data[:,index] = np.roll(data[:,index],displacement,axis=2)
		return data

	def shiftDataY(self, data, displacement):
		for i in range(data.shape[1]):
			data[:,i] = np.roll(data[:,i],displacement,axis=1)
		return data

	def shiftDataX(self, data, displacement):
		for i in range(data.shape[1]):
			data[:,i] = np.roll(data[:,i],displacement, axis=2)
		return data

	# def normalize(self, data, element):
	# 	normData = data[element, :, :, :]
	# 	for i in range((normData.shape[0])):
	# 		temp = normData[i, :, :]
	# 		tempMax = temp.max()
	# 		tempMin = temp.min()
	# 		temp = (temp - tempMin) / tempMax * 10000
	# 		data[element, i, :, :] = temp
	# 	return data


	def reshape_data(self, data, x_upscale, y_upscale):
		new_data = data.repeat(y_upscale, axis=2).repeat(x_upscale, axis=3)
		return new_data

	def remove_hotspots(self, data, element):
		imgs = data[element]
		max_val = np.max(imgs)
		for i in range(imgs.shape[0]):
			img = imgs[i]
			img[img > 0.5*max_val] = 0.5*max_val
			data[element,i] = img
		return data

	def equalize(self, data, element):
		# Equalization
		global_mean = np.mean(data[element,:,:,:])
		for i in range(data.shape[1]):
			local_mean = np.mean(data[element,i,:,:])
			coeff = global_mean/local_mean
			data[element,i] = data[element,i]*coeff
			img = data[element,i]
			# data[element,i] = exposure.equalize_hist(img)
			img *= 1/img.max()
			data[element,i] = exposure.equalize_adapthist(img)
		return data

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
		

	def cut(self, data, x_pos, y_pos, x_size, y_size):
		'''
		crops dataset to ROI dimensions

		Variables
		-----------
		data: ndarray
			4D xrf dataset ndarray [elements, theta, y,x]
		x_pos: ndarray
			ROI x coordinate with respect to plot window
		y_pos: int
			ROI y coordinate with respect to plot window
		x_size: int
			ROI pixel dimension in x
		y_size: int
			ROI pixel dimension in y
		'''
		num_elements = data.shape[0]
		num_projections = data.shape[1]
		temp_data = zeros([num_elements,num_projections, y_size, x_size])

		for i in range(num_projections):
			for j in range(num_elements):
				y0 = int(round(abs(y_pos)) - y_size)
				y1 = int(round(abs(y_pos)))
				x0 = int(round(x_pos))
				x1 = int(round(x_pos) + x_size)
				temp_data[j,i,:,:] = data[j, i, y0:y1, x0:x1]
		print("done")
		data = temp_data
		return data

	# def gauss33(self):
	# 	result = self.gauss2D(shape=(3, 3), sigma=1.3)
	# 	print(result)
	# 	return result

	# def gauss55(self):
	# 	result = self.gauss2D(shape=(5, 5), sigma=1.3)
	# 	print(result)
	# 	return result

	# def gauss2D(self, shape=(3, 3), sigma=0.5):
	# 	"""s
	# 	2D gaussian mask - should give the same result as MATLAB's
	# 	fspecial('gaussian',[shape],[sigma])
	# 	"""
	# 	m, n = [(ss - 1.) / 2. for ss in shape]
	# 	y, x = np.ogrid[-m:m + 1, -n:n + 1]
	# 	h = np.exp(-(x * x + y * y) / (2. * sigma * sigma))
	# 	h[h < np.finfo(h.dtype).eps * h.max()] = 0
	# 	sumh = h.sum()
	# 	if sumh != 0:
	# 		h /= sumh
	# 	return h

	def copy_background(self, img):
		'''
		crops dataset to ROI dimensions

		Variables
		-----------
		img: ndarray
			2D array enclosed by ROI for currently selected element.
		'''
		self.meanNoise = np.mean(img)
		self.stdNoise = np.std(img)
		return self.meanNoise, self.stdNoise

	def paste_background(self, data, element, projection, x_pos, y_pos, x_size, y_size, img, meanNoise, stdNoise):
		'''
		crops dataset to ROI dimensions

		Variables
		-----------
		data: ndarray
			4D xrf dataset ndarray [elements, theta, y,x]
		element: int
			element index
		projection: int
			projection index
		x_pos: ndarray
			ROI x coordinate with respect to plot window
		y_pos: int
			ROI y coordinate with respect to plot window
		x_size: int
			ROI pixel dimension in x
		y_size: int
			ROI pixel dimension in y
		img: ndarray
			2D array output from "copy_background" function.
		'''
		frame_boundary = img >=0
		noise_generator = np.random.normal(meanNoise, stdNoise, (y_size, x_size))*frame_boundary

		data[element,projection,
			int(round(abs(y_pos)) - y_size/2):int(round(abs(y_pos)) + y_size/2),
			int(round(x_pos) - x_size/2):int(round(x_pos) + x_size/2)] = noise_generator
		return data

	def exclude_projection(self, index, data, thetas, fnames, x_shifts, y_shifts):
		'''
		crops dataset to ROI dimensions

		Variables
		-----------
		index: int
			projection number from zero.
		data: ndarray
			4D xrf dataset ndarray [elements, theta, y,x]
		thetas: ndarray
			sorted projection angle list
		fnames: list
			list of strings containing filenames
		x_shifts: ndarray
			1D array containg pixel offset distance (in x), each value corresponging to one projection
		y_shifts: ndarray
			1D array containg pixel offset distance (in y), each value corresponging to one projection
		'''
		num_projections = len(thetas)
		data = np.delete(data, index, 1)
		thetas = np.delete(thetas, index, 0)
		y_shifts = np.delete(y_shifts, index, 0)
		x_shifts = np.delete(x_shifts, index, 0)
		fnames.pop(index)

		if index>0:
			index -= 1
			num_projections -=1
		else:
			num_projections -= 1

		return index, data, thetas, fnames, x_shifts, y_shifts

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
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, posMat, data)
#****************
		num_projections = data.shape[1]
		y_shifts = np.zeros(num_projections)
		x_shifts = np.zeros(num_projections)
		for j in arange(num_projections):

			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				yyshift = int(round(y_size//2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
				xxshift = int(round(x_size//2 - hotSpotX[j] - hs_x_pos[j] + hs_x_pos[firstPosOfHotSpot]))
				data[:, j, :, :] = np.roll(np.roll(data[:, j, :, :], xxshift, axis=2), yyshift, axis=1)

			if hs_x_pos[j] == 0:
				xxshift = 0
			if hs_y_pos[j] == 0:
				yyshift = 0

			x_shifts[j] = xxshift
			y_shifts[j] = -yyshift

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
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, self.posMat, data)
#****************
		num_projections = data.shape[1]
		y_shifts = np.zeros(num_projections)
		x_shifts = np.zeros(num_projections)
		thetas  = np.asarray(thetas)
		for j in arange(num_projections):

			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				xxshift = int(round(x_size//2 - hotSpotX[j]))
				yyshift = int(round(y_size//2 - hotSpotY[j]))
			if hs_x_pos[j] == 0:
				xxshift = 0
			if hs_y_pos[j] == 0:
				yyshift = 0

			x_shifts[j] = xxshift
			y_shifts[j] = yyshift

		hotspotXPos = zeros(num_projections, dtype=np.int)
		hotspotYPos = zeros(num_projections, dtype=np.int)
		for i in arange(num_projections):
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
			data[:, i, :, :] = np.roll(data[:, i, :, :], y_shifts[i], axis=1)

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
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, x_size, y_size, hs_group, self.posMat, data)
		num_projections = data.shape[1]
		y_shifts = np.zeros(num_projections)
		for j in arange(num_projections):
			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				yyshift = int(round(y_size//2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
				data[:, j, :, :] = np.roll(data[:, j, :, :], yyshift, axis=1)

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
		hs_x_pos = zeros(num_projections, dtype=np.int)
		hs_y_pos = zeros(num_projections, dtype=np.int)
		hs_array = zeros([num_projections, y_size//2*2, x_size//2*2], dtype=np.int)

		for i in arange(num_projections):
			hs_x_pos[i] = int(round(self.posMat[hs_group, i, 0]))
			hs_y_pos[i] = int(abs(round(self.posMat[hs_group, i, 1])))

			if hs_x_pos[i] != 0 and hs_y_pos[i] != 0:
				if hs_y_pos[i] < - y_size//2:	# if ROI is past top edge of projection
					hs_y_pos[i] = y_size
				if hs_y_pos[i] > (data.shape[2] - y_size//2): # if ROI is past top bottom of projection
					hs_y_pos[i] = data.shape[2] - y_size//2
				if hs_x_pos[i] < x_size//2:	# if ROI is past left edge of projection
					hs_x_pos[i] = x_size//2
				if hs_x_pos[i] > (data.shape[3] - x_size//2): # if ROI is past right edge of projection
					hs_x_pos[i] = data.shape[3] - x_size//2
				y0 = hs_y_pos[i] - y_size//2
				y1 = hs_y_pos[i] + y_size//2
				x0 = hs_x_pos[i] - x_size//2
				x1 = hs_x_pos[i] + x_size//2
				hs_array[i, :, :] = data[element, i, y0:y1, x0:x1]

		hotSpotX = zeros(num_projections, dtype=np.int)
		hotSpotY = zeros(num_projections, dtype=np.int)
		new_hs_array = zeros(hs_array.shape, dtype=np.int)
		new_hs_array[...] = hs_array[...]
		firstPosOfHotSpot = 0

		add = 1
		for i in arange(num_projections):
			if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
				firstPosOfHotSpot += add
			if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
				img = hs_array[i, :, :]
				print(img.sum(), i)
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
		fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
		errfunc = lambda p, x, y: fitfunc(p, x) - y
		p0 = [100, 100, 100]
		self.centers, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
		self.centerOfMassDiff = fitfunc(p0, x) - com
		print(self.centerOfMassDiff)

	def fitCenterOfMass2(self, com, x):
		fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + self.centers[2]
		errfunc = lambda p, x, y: fitfunc(p, x) - y
		p0 = [100, 100]
		p2, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
		self.centerOfMassDiff = fitfunc(p2, x) - com
		print(self.centerOfMassDiff)

	def alignCenterOfMass2(self, hotspotProj, data):
		j = 0
		for i in hotspotProj:
			self.x_shifts[i] += int(self.centerOfMassDiff[j])

			data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(self.x_shifts[i])), axis=2)
			j += 1

		#set some label to be show that the alignment has completed. perhaps print this in a logbox
		# self.lbl.setText("Alignment has been completed")
	def fitgaussian(self, data):
		"""
		Returns (height, x, y, width_x, width_y)
		the gaussian parameters of a 2D distribution found by a fit
		"""
		params = self.moments(data)
		errorfunction = lambda p: ravel(self.gaussian(*p)(*indices(data.shape)) - data)
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
			X, Y = indices(data.shape)
			x = (X * data).sum() / total
			y = (Y * data).sum() / total

		col = data[:, int(y)]

		if col.sum() == 0:
			width_x = 0
		else:
			width_x = sqrt(abs((arange(col.size) - y) ** 2 * col).sum() / col.sum())
		# TODO: rundime wasrning: invalid value encountered in double_scalars

		row = data[int(x), :]
		if row.sum() == 0:
			width_y = 0
		else:
			width_y = sqrt(abs((arange(row.size) - x) ** 2 * row).sum() / row.sum())

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

		return lambda x, y: height * exp(-(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

	def clrHotspot(self, posMat):
		'''
		resets
		hotspot position matrix
		'''
		posMat[...] = zeros_like(posMat)
		return posMat


	def create_mask(self, data, mask_thresh = None, scale = .8):
		# Remove nan values
		mask_nan = np.isfinite(data)
		data[~np.isfinite(data)] = 0
		#     data /= data.max()
		# Median filter with disk structuring element to preserve cell edges.
		data = ndi.median_filter(data, size=int(data.size**.5*.05), mode = 'nearest')
		#     data = rank.median(data, disk(int(size**.5*.05)))
		# Threshold
		if mask_thresh == None:
			mask_thresh = np.nanmean(data)*scale/np.nanmax(data)
		mask = np.isfinite(data)
		mask[data/np.nanmax(data) < mask_thresh] = False
		# Remove small spots
		mask = remove_small_objects(mask, data.size//100)
		# Remove small holes
		mask = ndi.binary_fill_holes(mask)
		return mask*mask_nan

	def equalize_hist_ev(self, image, nbins=2**16, mask=None, shift_funct = np.median):
		# For global_shift use np.median if hot spots are present and np.mean otherwise
		if mask is not None:
			mask = np.array(mask, dtype=bool)
			cdf, bin_centers = self.cumulative_distribution(image[mask], nbins)
			if bin_centers.shape[0] > cdf.shape[0]:
				bin_centers = bin_centers[:-1]
			m = shift_funct(image[mask])
		else:#eq_hsv
			cdf, bin_centers = self.cumulative_distribution(image, nbins)
			m = shift_funct(image)
			if bin_centers.shape[0] > cdf.shape[0]:
				bin_centers = bin_centers[:-1]
		out = np.interp(image.flat, bin_centers, cdf)
		out_m = np.interp(m, bin_centers, cdf)
		return out.reshape(image.shape), out_m

	def cumulative_distribution(self, image, nbins=2**16):
		hist, bin_centers = histogram(image, nbins)
		img_cdf = hist.cumsum()
		img_cdf = img_cdf / float(img_cdf[-1])
		return img_cdf, bin_centers


	# HISTOGRAM EQUALIZATION ADAPTED FROM skimage.exposure.equalize_hist
	def histogram(self, image, nbins=2**16, source_range='image', normalize=False):
		sh = image.shape
		if len(sh) == 3 and sh[-1] < 4:
			print("This might be a color image. The histogram will be "
				"computed on the flattened image. You can instead "
				"apply this function to each color channel.")

		image = image.flatten()
		# For integer types, histogramming with bincount is more efficient.
		if np.issubdtype(image.dtype, np.integer):
			hist, bin_centers = _bincount_histogram(image, source_range)
		else:
			pass
		if source_range == 'image':
				hist_range = None
		elif source_range == 'dtype':
			hist_range = skimage.dtype_limits(image, clip_negative=False)
		else:
			ValueError('Wrong value for the `source_range` argument')
		hist, bin_edges = np.histogram(image, bins=nbins, range=hist_range)
		bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.

		if normalize:
			hist = hist / np.sum(hist)
		return hist, bin_centers