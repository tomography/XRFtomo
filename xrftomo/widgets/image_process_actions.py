# #########################################################################
# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.        	  #
#    																	  #
#						Software Name: XRFtomo							  #
#																		  #
#					By: Argonne National Laboratory						  #
#																		  #
#						OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#																		  #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the 		  #
#    distribution.														  #
# 									                                      #
# 3. Neither the name of the copyright holder nor the names of its 		  #
#    contributors may be used to endorse or promote products derived 	  #
#    from this software without specific prior written permission.		  #
#																		  #
#								DISCLAIMER								  #
#							  											  #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 	  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 	  #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 	  #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 		  #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 	  #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.	  #
###########################################################################


from PyQt5 import QtWidgets, QtCore, QtGui
from scipy import ndimage, optimize, signal
import numpy as np

#testing
from skimage.exposure import equalize_hist
from skimage.morphology import remove_small_objects, disk
from skimage import exposure
from skimage.filters import rank
import skimage
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

		data[:,index] = np.roll(data[:, index], Y, axis=1)
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
			data[:,i] = np.roll(data[:,i],Y,axis=1) #negative because image coordinates are flipped
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
		if x_upscale < 1:
			pass
		else: 
			new_data = data.repeat(x_upscale, axis=3)

		if y_upscale < 1: 
			pass
		else:
			new_data = data.repeat(y_upscale, axis=2)

		return new_data

	def padData(self,data,x,y, x_shifts, y_shifts, clip_edges):
		data_shape = data.shape

		if len(data_shape) == 4 and clip_edges>=1:
			new_data = np.zeros([data_shape[0], data_shape[1], data_shape[2]+y*2, data_shape[3]+x*2])
			for i in range(data.shape[1]):
				data = self.shiftProjection(data,-x_shifts[i],-y_shifts[i], i)

			if x == 0:
				new_data[:,:,y:-y,:] = data
			elif y == 0:
				new_data[:,:,:,x+clip_edges:-x-clip_edges] = data[:,:,:,clip_edges:-clip_edges]
			else:
				new_data[:,:,y:-y,x+clip_edges:-x-clip_edges] = data[:,:,:,clip_edges:-clip_edges]

			for i in range(data.shape[1]):
				data = self.shiftProjection(data,x_shifts[i],y_shifts[i], i)

		elif len(data_shape) == 4 and clip_edges==0:
			new_data = np.zeros([data_shape[0], data_shape[1], data_shape[2]+y*2, data_shape[3]+x*2])
			for i in range(data.shape[1]):
				data = self.shiftProjection(data,-x_shifts[i],-y_shifts[i], i)

			if x == 0:
				new_data[:,:,y:-y,:] = data
			elif y == 0:
				new_data[:,:,:,x:-x] = data
			else:
				new_data[:,:,y:-y,x:-x] = data

			for i in range(data.shape[1]):
				data = self.shiftProjection(data,x_shifts[i],y_shifts[i], i)

		else: 
			print("data not in [elment,projection,y,x] format")
			return
		# elif len(data_shape) == 3:
		#     new_data = np.zeros([data_shape[0], data_shape[1]+y*2, data_shape[2]+x*2])
		#     if x == 0:
		#         new_data[:,y:-y,:] = data
		#     elif y == 0:
		#         new_data[:,:,x:-x] = data
		#     else:
		#         new_data[:,y:-y,x:-x] = data

		# elif len(data_shape) == 2: 
		#     new_data = np.zeros([data_shape[1]+y*2, data_shape[2]+x*2])
		#     if x == 0:
		#         new_data[y:-y,:] = data
		#     elif y == 0:
		#         new_data[:,x:-x] = data
		#     else:
		#         new_data[:,y:-y,x:-x] = data
		# else: 
		#     print("incompatible data shape")
		return new_data

	def remove_hotspots(self, data, element):
		imgs = data[element]
		max_val = np.max(imgs)
		for i in range(imgs.shape[0]):
			img = imgs[i]
			img[img > 0.9*max_val] = 0.9*max_val
			data[element,i] = img
		return data

	def fill_void(self,data, element):
		imgs = data[element]

		for i in range(imgs.shape[0]):
			img = imgs[i]
			mask = self.create_mask(img)
			mask123 = np.logical_not(mask)*0.123456
			img_masked = img*mask+mask123
			local_max = img_masked.max()
			tru0_mask = img_masked == 0
			void_fill = tru0_mask*local_max
			filled = void_fill+img

			#get mask for current image
			#for pixel in pixels in mask, if 0, set to max
			# img[img > 0.95*max_val] = 0
			data[element,i] = filled
		return data

	def create_mask(self, data, mask_thresh=None, scale=.8):
		# Remove nan values
		mask_nan = np.isfinite(data)
		data[~np.isfinite(data)] = 0
		#     data /= data.max()
		# Median filter with disk structuring element to preserve cell edges.
		data = ndi.median_filter(data, size=int(data.size ** .5 * .05), mode='nearest')
		#     data = rank.median(data, disk(int(size**.5*.05)))
		# Threshold
		if mask_thresh == None:
			mask_thresh = np.nanmean(data) * scale / np.nanmax(data)
		mask = np.isfinite(data)
		mask[data / np.nanmax(data) < mask_thresh] = False
		# Remove small spots
		mask = remove_small_objects(mask, data.size // 100)
		# Remove small holes
		mask = ndi.binary_fill_holes(mask)
		return mask * mask_nan

	def remove_hotpixels(self, data, element):
		imgs = data[element]
		max_val = np.max(imgs)
		for i in range(imgs.shape[0]):
			img = imgs[i]
			img[img > 0.95*max_val] = 0
			data[element,i] = img
		return data

	def remove_empty_columns(self,data, element):
		imgs = data[element]
		num_projections = imgs.shape[0]
		num_cols = imgs.shape[2]
		for i in range(num_projections):
			for j in range(num_cols):
				if len(np.unique(imgs[i,:,j])) <= 2:
					data[:,i,:,j] = np.zeros_like(data[:,i,:,j])
		return data

	def remove_empty_rows(self,data, element):
		imgs = data[element]
		num_projections = imgs.shape[0]
		num_rows = imgs.shape[1]
		for i in range(num_projections):
			for j in range(num_rows):
				if len(np.unique(imgs[i,j])) <= 2:
					data[:,i,j] = np.zeros_like(data[:,i,j])
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
		temp_data = np.zeros([num_elements,num_projections, y_size, x_size])
		frame_height = data.shape[2]
		for i in range(num_projections):
			for j in range(num_elements):
				y0 = int(round(y_pos))
				y1 = int(round(y0+y_size))
				x0 = int(round(x_pos))
				x1 = int(round(x_pos) + x_size)
				temp_data[j,i,:,:] = data[j, i, frame_height-y1:frame_height-y0, x0:x1]
		print("done")
		data = temp_data
		return data

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

		x_start = int(round(x_pos))
		x_end = int(round(x_pos) + x_size)
		y_end = data.shape[2] - int(round(abs(y_pos)))
		y_start = data.shape[2] -int(round(abs(y_pos)) + y_size)
		data[element,projection, y_start:y_end, x_start:x_end] = noise_generator
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

	def invert(self, data, element):
		#set padding equal to max first

		projection_stack = data[element]
		num_projections = data.shape[1]
		mean_edge = 0
		for i in range(num_projections):
			col_sum = np.sum(projection_stack[0], axis=0)
			mus_loc = col_sum[::-1]
			left_end = next((i for i, x in enumerate(col_sum) if x), None)
			right_end = next((i for i, x in enumerate(mus_loc) if x), None)
			mean_left = col_sum[left_end]/projection_stack.shape[1]
			mean_right = col_sum[right_end]/projection_stack.shape[1]
			if mean_edge < mean_left:
				mean_edge = mean_left
			if mean_edge < mean_right:
				mean_edge = mean_right

		# mask = [projection_stack == 0][0]*mean_edge
		max_val = projection_stack.max()
		mask = [projection_stack == 0][0]*max_val
		data[element] = abs(projection_stack+mask-max_val)
		# data[element] = projection_stack+mask		
		return data

	def cumulative_distribution(self, image, nbins=2**16):
		hist, bin_centers = np.histogram(image, nbins)
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