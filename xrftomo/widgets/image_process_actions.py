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
from scipy.fftpack import fftshift, fft2, ifft2
import matplotlib.pyplot as plt


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

	def normalize(self, data, sino):
		intensities = np.sum(sino, axis=1)          #1D array;
		max_intensity = np.max(intensities)       #float val
		intensities = max_intensity/intensities   #normalization factor
		plt.figure()
		plt.plot(intensities)
		plt.show()

		for i in range(data.shape[0]):      #apply for all elements
			data[i] = intensities[:,None,None]*data[i]
		return data


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

	def remove_hotspot_old(self, data, element):
		imgs = data[element].copy()
		max_val = np.max(imgs)
		std_imgs = np.std(imgs)
		imgs[imgs>15*std_imgs] = std_imgs
		data[element] = imgs

		dif = data[element] - imgs
		if dif.max() == 0:
			imgs[imgs>0.98*max_val] = 0.98*max_val
			data[element] = imgs

		return data

	def filter(self, data, bpfilter=3):
		center = data.shape[1] / 2
		n = data.shape[-1]
		ne = 3 * n // 2  # padding
		t = np.fft.rfftfreq(ne).astype('float32')

		if bpfilter == 2:
			# ramp filter
			f = fftshift(abs(np.mgrid[-1:1:2 / n])).reshape(1, -1)

			for i in range(data.shape[0]):
				data[i] = np.real(np.ifft2(fft2(data[i]) * f))

		elif bpfilter == 3:
			# Shepp-Logan filter
			f = fftshift(abs(np.mgrid[-1:1:2 / n])).reshape(1, -1)
			w = 2 * np.pi * f
			f[1:] = f[1:] * np.sin(w[1:] / 2) / (w[1:] / 2)
			for i in range(data.shape[0]):
				data[i] = np.real(ifft2(fft2(data[i]) * f))

		elif bpfilter == 4:
			w = t  # ramp filter
			tmp = np.pad(data, ((0, 0), (0, 0), (ne // 2 - n // 2, ne // 2 - n // 2)), mode='edge')
			w = w * np.exp(-2 * np.pi * 1j * t)  # center fix
			tmp = np.fft.irfft(w * np.fft.rfft(tmp, axis=2), axis=2).astype('float32')
			# TODO: cannot broadcast input array from shape [r,y,x-1] to [r,y,x]
			try:
				data[:] = tmp[:, :, ne // 2 - n // 2:ne // 2 + n // 2]
			except:
				data[:] = tmp[:, :, ne // 2 - n // 2:ne // 2 + n // 2 + 1]

		return data

	def remove_hotspots_new(self, data, element):
		imgs = data[element]
		max_val = np.max(imgs)
		std_imgs = np.std(imgs)
		imgs[imgs>15*std_imgs] = std_imgs
		data[element] = imgs
		return data

	def remove_hotspot_blend(self, data, element, reference_projection=None):
		"""
		Remove hotspots by replacing them with a blend (median) of surrounding pixels.
		Uses local adaptive detection to identify hotspots of various sizes by detecting
		sudden jumps in pixel values compared to their local neighborhood.
		Uses a reference projection (typically the current image) to calibrate detection thresholds.
		
		Parameters:
		-----------
		data : ndarray
			4D xrf dataset ndarray [elements, projections, y, x]
		element : int
			element index to process
		reference_projection : int, optional
			Index of projection to use as reference for calibrating hotspot detection.
			If None, uses the projection with the highest maximum value.
			
		Returns:
		--------
		data : ndarray
			Modified data array with hotspots replaced
		"""
		imgs = data[element].copy()
		num_projections = imgs.shape[0]
		
		# Helper function to compute median of surrounding pixels excluding NaN
		def median_ignore_nan(window):
			"""Compute median of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 0:
				return np.median(valid_values)
			else:
				return np.nan
		
		def mean_ignore_nan(window):
			"""Compute mean of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 0:
				return np.mean(valid_values)
			else:
				return np.nan
		
		def std_ignore_nan(window):
			"""Compute std of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 1:
				return np.std(valid_values)
			else:
				return 0.0
		
		# Helper function to compute median excluding center pixel
		def median_exclude_center(window):
			"""Compute median excluding center pixel."""
			center_idx = window.size // 2
			window_flat = window.flatten()
			# Exclude center pixel
			neighbors = np.concatenate([window_flat[:center_idx], window_flat[center_idx+1:]])
			valid_values = neighbors[~np.isnan(neighbors)]
			if len(valid_values) > 0:
				return np.median(valid_values)
			else:
				return np.nan
		
		def std_exclude_center(window):
			"""Compute std excluding center pixel."""
			center_idx = window.size // 2
			window_flat = window.flatten()
			# Exclude center pixel
			neighbors = np.concatenate([window_flat[:center_idx], window_flat[center_idx+1:]])
			valid_values = neighbors[~np.isnan(neighbors)]
			if len(valid_values) > 1:
				return np.std(valid_values)
			else:
				return 0.0
		
		# Step 0: Analyze reference projection to calibrate thresholds
		# If no reference provided, use projection with highest max value
		if reference_projection is None:
			max_vals = [np.max(imgs[i]) for i in range(num_projections)]
			reference_projection = np.argmax(max_vals)
		
		# Ensure reference_projection is within valid range
		reference_projection = max(0, min(reference_projection, num_projections - 1))
		ref_img = imgs[reference_projection].copy()
		
		# Analyze reference image to find obvious hotspots and calibrate intensity thresholds only
		# Note: Size detection (kernel sizes, expansion) remains adaptive per projection
		print(f"Analyzing reference projection {reference_projection} for hotspot intensity calibration...")
		
		# Compute local statistics for reference image
		ref_local_median = ndi.generic_filter(ref_img, median_exclude_center, size=5, mode='nearest')
		ref_local_std = ndi.generic_filter(ref_img, std_exclude_center, size=5, mode='nearest')
		ref_local_std = np.maximum(ref_local_std, 1e-10)
		
		# Compute z-scores for reference image
		ref_z_scores = (ref_img - ref_local_median) / ref_local_std
		
		# Find obvious hotspots in reference (use moderate threshold to catch clear hotspots only)
		# This is only for calibration, not for final detection
		ref_hotspot_mask = ref_z_scores > 4.0  # Moderate threshold to catch obvious hotspots
		
		# Also check gradient for obvious hotspots
		ref_grad_y = ndi.sobel(ref_img, axis=0, mode='nearest')
		ref_grad_x = ndi.sobel(ref_img, axis=1, mode='nearest')
		ref_grad_magnitude = np.sqrt(ref_grad_x**2 + ref_grad_y**2)
		ref_grad_normalized = ref_grad_magnitude / (ref_local_median + 1e-10)
		
		# Combine detection criteria for reference (only obvious hotspots)
		ref_hotspot_mask = ref_hotspot_mask | ((ref_grad_normalized > 0.4) & (ref_z_scores > 3.5))
		
		# Calculate reference statistics from detected hotspots
		# Use median or higher percentiles to avoid being too aggressive
		if np.any(ref_hotspot_mask):
			ref_hotspot_z_scores = ref_z_scores[ref_hotspot_mask]
			ref_hotspot_gradients = ref_grad_normalized[ref_hotspot_mask]
			ref_abs_diffs = (ref_img[ref_hotspot_mask] - ref_local_median[ref_hotspot_mask])
			
			# Use median (50th percentile) or higher percentiles for calibration
			# This ensures we're using the typical hotspot intensity, not the weakest ones
			calibrated_z_min = np.percentile(ref_hotspot_z_scores, 50) if len(ref_hotspot_z_scores) > 0 else 4.0
			calibrated_z_med = np.percentile(ref_hotspot_z_scores, 30) if len(ref_hotspot_z_scores) > 0 else 3.0
			calibrated_grad_min = np.percentile(ref_hotspot_gradients, 50) if len(ref_hotspot_gradients) > 0 else 0.4
			
			# Compute relative absolute difference thresholds
			ref_abs_diff_ratios = ref_abs_diffs / (ref_local_median[ref_hotspot_mask] + 1e-10)
			calibrated_abs_diff_min = np.percentile(ref_abs_diff_ratios, 50) if len(ref_abs_diff_ratios) > 0 else 0.4
			
			# Ensure minimum thresholds to avoid being too aggressive
			calibrated_z_min = max(3.5, calibrated_z_min)
			calibrated_z_med = max(2.5, calibrated_z_med)
			calibrated_grad_min = max(0.3, calibrated_grad_min)
			calibrated_abs_diff_min = max(0.3, calibrated_abs_diff_min)
			
			print(f"  Detected {np.sum(ref_hotspot_mask)} obvious hotspot pixels in reference projection")
			print(f"  Calibrated intensity thresholds: z_min={calibrated_z_min:.2f}, z_med={calibrated_z_med:.2f}, "
				  f"grad={calibrated_grad_min:.2f}, abs_diff={calibrated_abs_diff_min:.2f}")
		else:
			# No obvious hotspots found, use conservative default thresholds
			calibrated_z_min = 4.0
			calibrated_z_med = 3.0
			calibrated_grad_min = 0.4
			calibrated_abs_diff_min = 0.4
			print(f"  No obvious hotspots found in reference, using conservative default thresholds")
		
		# Process each projection separately
		for proj_idx in range(num_projections):
			img = imgs[proj_idx].copy()
			max_val_before = np.max(img)
			
			# Start with calibrated intensity thresholds from reference projection
			# Use calibrated values directly (they're already conservative)
			# Note: Size-based detection (kernel sizes, expansion) adapts per projection
			z_score_threshold_high = calibrated_z_min  # Use calibrated value directly
			z_score_threshold_medium = calibrated_z_med  # Use calibrated value directly
			z_score_threshold_very_high = max(calibrated_z_min * 1.3, 4.5)  # Slightly higher for very high z-scores
			gradient_threshold = calibrated_grad_min  # Use calibrated value directly
			absolute_diff_factor = calibrated_abs_diff_min  # Use calibrated value directly
			
			# Iteratively process until max value decreases or no more hotspots found
			max_iterations = 3
			for iteration in range(max_iterations):
				# Step 1: Detect hotspots using local adaptive thresholds
				# Use multiple kernel sizes to detect hotspots of different sizes
				hotspot_mask = np.zeros(img.shape, dtype=bool)
				
				# Try different kernel sizes to detect various hotspot sizes
				for kernel_size in [3, 5, 7, 11]:
					# Compute local statistics excluding center pixel for more accurate detection
					local_median = ndi.generic_filter(img, median_exclude_center, size=kernel_size, mode='nearest')
					local_std = ndi.generic_filter(img, std_exclude_center, size=kernel_size, mode='nearest')
					
					# Avoid division by zero
					local_std = np.maximum(local_std, 1e-10)
					
					# Compute how many standard deviations each pixel is above its local median
					z_score = (img - local_median) / local_std
					
					# Detect sudden jumps: pixels significantly higher than local neighborhood
					# Use more aggressive adaptive threshold
					local_hotspot = z_score > z_score_threshold_high
					
					# Also check absolute difference: sudden jumps should be significant
					absolute_diff = img - local_median
					# Use a threshold that's adaptive to local scale (more aggressive)
					min_absolute_diff = np.maximum(local_median * absolute_diff_factor, local_std * 2.0)
					local_hotspot = local_hotspot | (absolute_diff > min_absolute_diff)
					
					# Combine with gradient-based detection for sudden jumps
					# Compute gradient magnitude
					grad_y = ndi.sobel(img, axis=0, mode='nearest')
					grad_x = ndi.sobel(img, axis=1, mode='nearest')
					grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
					
					# Normalize gradient by local median to detect relative jumps
					grad_normalized = grad_magnitude / (local_median + 1e-10)
					high_gradient = grad_normalized > gradient_threshold
					
					# Hotspot if: (high z-score OR high absolute difference) AND high gradient
					# This catches sudden jumps in values
					# Also catch pixels with very high z-score even without gradient (for isolated hotspots)
					local_hotspot = local_hotspot | (high_gradient & (z_score > z_score_threshold_medium)) | (z_score > z_score_threshold_very_high)
					
					# Also detect pixels that are significantly above the maximum of their neighbors
					# This catches cases where hotspots are in high-value regions
					# Use calibrated thresholds to avoid being too aggressive
					max_neighbor = ndi.maximum_filter(img, size=kernel_size, mode='nearest')
					# If pixel is significantly higher than median, it's suspicious
					# Use more conservative thresholds
					high_relative_to_max = (img > local_median * 2.0) & (img > max_neighbor * 0.98)
					local_hotspot = local_hotspot | (high_relative_to_max & (z_score > z_score_threshold_medium))
					
					# Combine detections from different kernel sizes
					hotspot_mask = hotspot_mask | local_hotspot
				
				# Step 2: Expand hotspot regions to include adjacent high-value pixels
				# This handles cases where hotspots span multiple pixels
				# Iteratively expand to include pixels that are significantly higher than
				# the non-hotspot neighborhood
				for expand_iter in range(3):  # Allow up to 3 iterations of expansion
					if not np.any(hotspot_mask):
						break
					
					# Create a mask excluding hotspots
					non_hotspot_img = img.copy()
					non_hotspot_img[hotspot_mask] = np.nan
					
					# Compute local median of non-hotspot pixels
					local_median_safe = ndi.generic_filter(
						non_hotspot_img, 
						median_ignore_nan, 
						size=5, 
						mode='nearest'
					)
					local_std_safe = ndi.generic_filter(
						non_hotspot_img, 
						std_ignore_nan, 
						size=5, 
						mode='nearest'
					)
					local_std_safe = np.maximum(local_std_safe, 1e-10)
					
					# Find pixels adjacent to hotspots that are also suspicious
					# Dilate hotspot mask to get adjacent pixels
					dilated_mask = ndi.binary_dilation(hotspot_mask, structure=np.ones((3, 3)))
					adjacent_pixels = dilated_mask & ~hotspot_mask
					
					if not np.any(adjacent_pixels):
						break
					
					# Check if adjacent pixels are significantly higher than local median
					# Use calibrated threshold for expansion, with slight reduction per iteration
					z_score_threshold_adjacent = max(2.0, z_score_threshold_medium - (iteration * 0.2))
					z_score_adjacent = (img - local_median_safe) / local_std_safe
					suspicious_adjacent = adjacent_pixels & (z_score_adjacent > z_score_threshold_adjacent)
					suspicious_adjacent = suspicious_adjacent & (img > local_median_safe + 2.0 * local_std_safe)
					
					# Add suspicious adjacent pixels to hotspot mask
					if np.any(suspicious_adjacent):
						hotspot_mask = hotspot_mask | suspicious_adjacent
					else:
						break  # No more expansion needed
				
				# Step 3: Replace hotspots with blended values
				if not np.any(hotspot_mask):
					# No hotspots found in this iteration, check if we should continue
					break
				
				# Create a temporary image with hotspots masked out for better blending
				temp_img = img.copy()
				temp_img[hotspot_mask] = np.nan
				
				# Use a larger kernel for blending (7x7) to get better representation
				# of surrounding pixels, especially for larger hotspots
				blended_img = ndi.generic_filter(
					temp_img, 
					median_ignore_nan, 
					size=7, 
					mode='nearest'
				)
				
				# Fallback: if median filter resulted in NaN, use mean of surrounding pixels
				nan_mask = np.isnan(blended_img) & hotspot_mask
				if np.any(nan_mask):
					mean_blended = ndi.generic_filter(
						temp_img, 
						mean_ignore_nan, 
						size=7, 
						mode='nearest'
					)
					blended_img[nan_mask] = mean_blended[nan_mask]
				
				# Final fallback: if still NaN, use the original image's local mean
				nan_mask = np.isnan(blended_img) & hotspot_mask
				if np.any(nan_mask):
					mean_val_local = ndi.uniform_filter(img, size=7, mode='nearest')
					blended_img[nan_mask] = mean_val_local[nan_mask]
				
				# Replace only the hotspot pixels with the blended values
				img[hotspot_mask] = blended_img[hotspot_mask]
				
				# Check if max value decreased
				max_val_after = np.max(img)
				if max_val_after < max_val_before:
					# Successfully reduced max value, update max_val_before for next iteration
					max_val_before = max_val_after
					# If still hotspots exist, continue with current thresholds
					if iteration < max_iterations - 1:
						continue
					else:
						break
				else:
					# Max value didn't decrease, make thresholds slightly more aggressive
					if iteration < max_iterations - 1:
						# Make thresholds slightly more aggressive for next iteration
						# Use conservative minimums to avoid being too aggressive
						z_score_threshold_high = max(2.5, z_score_threshold_high - 0.3)
						z_score_threshold_medium = max(2.0, z_score_threshold_medium - 0.2)
						z_score_threshold_very_high = max(3.5, z_score_threshold_very_high - 0.5)
						gradient_threshold = max(0.25, gradient_threshold - 0.03)
						absolute_diff_factor = max(0.25, absolute_diff_factor - 0.03)
						# Continue with more aggressive thresholds
						continue
					else:
						# Last iteration, force detection of maximum pixel
						# Find the maximum pixel and its neighbors
						max_pixel_idx = np.unravel_index(np.argmax(img), img.shape)
						# Create a small mask around maximum pixel
						y_max, x_max = max_pixel_idx
						y_min = max(0, y_max - 2)
						y_max_bound = min(img.shape[0], y_max + 3)
						x_min = max(0, x_max - 2)
						x_max_bound = min(img.shape[1], x_max + 3)
						
						# Create a mask for this region
						force_mask = np.zeros(img.shape, dtype=bool)
						force_mask[y_min:y_max_bound, x_min:x_max_bound] = True
						
						# Recompute blended image for this region
						temp_img_force = img.copy()
						temp_img_force[force_mask] = np.nan
						blended_img_force = ndi.generic_filter(
							temp_img_force, 
							median_ignore_nan, 
							size=7, 
							mode='nearest'
						)
						
						# Fallback to mean if needed
						nan_mask_force = np.isnan(blended_img_force) & force_mask
						if np.any(nan_mask_force):
							mean_blended_force = ndi.generic_filter(
								temp_img_force, 
								mean_ignore_nan, 
								size=7, 
								mode='nearest'
							)
							blended_img_force[nan_mask_force] = mean_blended_force[nan_mask_force]
						
						# Replace the maximum pixel region
						img[force_mask] = blended_img_force[force_mask]
			
			# Update the projection
			imgs[proj_idx] = img
		
		# Assign back to data
		data[element] = imgs
		
		return data

	def remove_hotspot_roi(self, data, element, projection, x_pos, y_pos, x_size, y_size):
		"""
		Remove hotspots within a specific ROI for a single projection.
		Uses local adaptive detection to identify hotspots by detecting sudden jumps
		in pixel values compared to their local neighborhood within the ROI.
		
		Parameters:
		-----------
		data : ndarray
			4D xrf dataset ndarray [elements, projections, y, x]
		element : int
			element index to process
		projection : int
			projection index to process
		x_pos : int
			ROI x coordinate (left edge)
		y_pos : int
			ROI y coordinate (top edge)
		x_size : int
			ROI width in pixels
		y_size : int
			ROI height in pixels
			
		Returns:
		--------
		data : ndarray
			Modified data array with hotspots replaced only in the specified ROI
		"""
		# Extract the full projection image
		img = data[element, projection].copy()
		frame_height = img.shape[0]
		
		# Convert ROI coordinates to array indices
		# Note: ROI coordinates may be in image view coordinates
		y_end = int(round(frame_height - y_pos))
		y_start = int(round(frame_height - y_pos - y_size))
		x_start = int(round(x_pos))
		x_end = int(round(x_pos + x_size))
		
		# Ensure coordinates are within bounds
		y_start = max(0, y_start)
		y_end = min(frame_height, y_end)
		x_start = max(0, x_start)
		x_end = min(img.shape[1], x_end)
		
		# Extract ROI
		roi = img[y_start:y_end, x_start:x_end].copy()
		
		if roi.size == 0:
			print("Warning: ROI is empty, no processing performed")
			return data
		
		print(f"Processing ROI hotspots: projection {projection}, ROI shape {roi.shape}")
		
		# Helper functions for ROI processing
		def median_ignore_nan(window):
			"""Compute median of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 0:
				return np.median(valid_values)
			else:
				return np.nan
		
		def mean_ignore_nan(window):
			"""Compute mean of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 0:
				return np.mean(valid_values)
			else:
				return np.nan
		
		def std_ignore_nan(window):
			"""Compute std of window, ignoring NaN values."""
			window_flat = window.flatten()
			valid_values = window_flat[~np.isnan(window_flat)]
			if len(valid_values) > 1:
				return np.std(valid_values)
			else:
				return 0.0
		
		def median_exclude_center(window):
			"""Compute median excluding center pixel."""
			center_idx = window.size // 2
			window_flat = window.flatten()
			neighbors = np.concatenate([window_flat[:center_idx], window_flat[center_idx+1:]])
			valid_values = neighbors[~np.isnan(neighbors)]
			if len(valid_values) > 0:
				return np.median(valid_values)
			else:
				return np.nan
		
		def std_exclude_center(window):
			"""Compute std excluding center pixel."""
			center_idx = window.size // 2
			window_flat = window.flatten()
			neighbors = np.concatenate([window_flat[:center_idx], window_flat[center_idx+1:]])
			valid_values = neighbors[~np.isnan(neighbors)]
			if len(valid_values) > 1:
				return np.std(valid_values)
			else:
				return 0.0
		
		# Calibrate thresholds from ROI statistics
		# Use conservative thresholds for ROI processing
		max_val_before = np.max(roi)
		
		# Set conservative initial thresholds
		z_score_threshold_high = 3.5
		z_score_threshold_medium = 2.5
		z_score_threshold_very_high = 5.0
		gradient_threshold = 0.35
		absolute_diff_factor = 0.35
		
		# Iteratively process ROI until max value decreases or no more hotspots found
		max_iterations = 3
		for iteration in range(max_iterations):
			# Detect hotspots using local adaptive thresholds
			hotspot_mask = np.zeros(roi.shape, dtype=bool)
			
			# Try different kernel sizes to detect various hotspot sizes
			# Use smaller kernel sizes for ROI since the region is smaller
			kernel_sizes = [3, 5]
			if min(roi.shape) > 15:
				kernel_sizes.append(7)
			
			for kernel_size in kernel_sizes:
				# Skip if kernel is too large for ROI
				if kernel_size > min(roi.shape):
					continue
				
				# Compute local statistics excluding center pixel
				local_median = ndi.generic_filter(roi, median_exclude_center, size=kernel_size, mode='nearest')
				local_std = ndi.generic_filter(roi, std_exclude_center, size=kernel_size, mode='nearest')
				local_std = np.maximum(local_std, 1e-10)
				
				# Compute z-scores
				z_score = (roi - local_median) / local_std
				
				# Detect sudden jumps
				local_hotspot = z_score > z_score_threshold_high
				
				# Check absolute difference
				absolute_diff = roi - local_median
				min_absolute_diff = np.maximum(local_median * absolute_diff_factor, local_std * 2.0)
				local_hotspot = local_hotspot | (absolute_diff > min_absolute_diff)
				
				# Gradient-based detection
				grad_y = ndi.sobel(roi, axis=0, mode='nearest')
				grad_x = ndi.sobel(roi, axis=1, mode='nearest')
				grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
				grad_normalized = grad_magnitude / (local_median + 1e-10)
				high_gradient = grad_normalized > gradient_threshold
				
				# Combine detection criteria
				local_hotspot = local_hotspot | (high_gradient & (z_score > z_score_threshold_medium)) | (z_score > z_score_threshold_very_high)
				
				# Combine detections from different kernel sizes
				hotspot_mask = hotspot_mask | local_hotspot
			
			# Expand hotspot regions to include adjacent high-value pixels
			for expand_iter in range(2):  # Fewer expansions for ROI
				if not np.any(hotspot_mask):
					break
				
				# Create a mask excluding hotspots
				non_hotspot_roi = roi.copy()
				non_hotspot_roi[hotspot_mask] = np.nan
				
				# Compute local median of non-hotspot pixels
				local_median_safe = ndi.generic_filter(
					non_hotspot_roi, 
					median_ignore_nan, 
					size=5, 
					mode='nearest'
				)
				local_std_safe = ndi.generic_filter(
					non_hotspot_roi, 
					std_ignore_nan, 
					size=5, 
					mode='nearest'
				)
				local_std_safe = np.maximum(local_std_safe, 1e-10)
				
				# Find adjacent pixels
				dilated_mask = ndi.binary_dilation(hotspot_mask, structure=np.ones((3, 3)))
				adjacent_pixels = dilated_mask & ~hotspot_mask
				
				if not np.any(adjacent_pixels):
					break
				
				# Check if adjacent pixels are suspicious
				z_score_threshold_adjacent = max(2.0, z_score_threshold_medium - (expand_iter * 0.2))
				z_score_adjacent = (roi - local_median_safe) / local_std_safe
				suspicious_adjacent = adjacent_pixels & (z_score_adjacent > z_score_threshold_adjacent)
				suspicious_adjacent = suspicious_adjacent & (roi > local_median_safe + 2.0 * local_std_safe)
				
				if np.any(suspicious_adjacent):
					hotspot_mask = hotspot_mask | suspicious_adjacent
				else:
					break
			
			# Replace hotspots with blended values
			if not np.any(hotspot_mask):
				break
			
			# Create temporary ROI with hotspots masked out
			temp_roi = roi.copy()
			temp_roi[hotspot_mask] = np.nan
			
			# Use median filter for blending
			blend_kernel_size = min(7, min(roi.shape) // 2 * 2 - 1) if min(roi.shape) > 7 else 3
			blended_roi = ndi.generic_filter(
				temp_roi, 
				median_ignore_nan, 
				size=blend_kernel_size, 
				mode='nearest'
			)
			
			# Fallback to mean if needed
			nan_mask = np.isnan(blended_roi) & hotspot_mask
			if np.any(nan_mask):
				mean_blended = ndi.generic_filter(
					temp_roi, 
					mean_ignore_nan, 
					size=blend_kernel_size, 
					mode='nearest'
				)
				blended_roi[nan_mask] = mean_blended[nan_mask]
			
			# Final fallback
			nan_mask = np.isnan(blended_roi) & hotspot_mask
			if np.any(nan_mask):
				mean_val_local = ndi.uniform_filter(roi, size=blend_kernel_size, mode='nearest')
				blended_roi[nan_mask] = mean_val_local[nan_mask]
			
			# Replace hotspot pixels
			roi[hotspot_mask] = blended_roi[hotspot_mask]
			
			# Check if max value decreased
			max_val_after = np.max(roi)
			num_hotspots = np.sum(hotspot_mask)
			print(f"  Iteration {iteration + 1}: Found {num_hotspots} hotspot pixels, "
				  f"max value: {max_val_before:.1f} -> {max_val_after:.1f}")
			
			if max_val_after < max_val_before:
				max_val_before = max_val_after
				if iteration < max_iterations - 1:
					continue
				else:
					break
			else:
				# Make thresholds slightly more aggressive
				if iteration < max_iterations - 1:
					z_score_threshold_high = max(2.5, z_score_threshold_high - 0.3)
					z_score_threshold_medium = max(2.0, z_score_threshold_medium - 0.2)
					z_score_threshold_very_high = max(3.5, z_score_threshold_very_high - 0.5)
					gradient_threshold = max(0.25, gradient_threshold - 0.03)
					absolute_diff_factor = max(0.25, absolute_diff_factor - 0.03)
					continue
				else:
					# Last iteration: force removal of maximum pixel
					max_pixel_idx = np.unravel_index(np.argmax(roi), roi.shape)
					y_max, x_max = max_pixel_idx
					y_min = max(0, y_max - 2)
					y_max_bound = min(roi.shape[0], y_max + 3)
					x_min = max(0, x_max - 2)
					x_max_bound = min(roi.shape[1], x_max + 3)
					
					force_mask = np.zeros(roi.shape, dtype=bool)
					force_mask[y_min:y_max_bound, x_min:x_max_bound] = True
					
					temp_roi_force = roi.copy()
					temp_roi_force[force_mask] = np.nan
					blended_roi_force = ndi.generic_filter(
						temp_roi_force, 
						median_ignore_nan, 
						size=blend_kernel_size, 
						mode='nearest'
					)
					
					nan_mask_force = np.isnan(blended_roi_force) & force_mask
					if np.any(nan_mask_force):
						mean_blended_force = ndi.generic_filter(
							temp_roi_force, 
							mean_ignore_nan, 
							size=blend_kernel_size, 
							mode='nearest'
						)
						blended_roi_force[nan_mask_force] = mean_blended_force[nan_mask_force]
					
					roi[force_mask] = blended_roi_force[force_mask]
					print(f"  Forced removal of maximum pixel region")
		
		# Update the ROI in the original data
		img[y_start:y_end, x_start:x_end] = roi
		data[element, projection] = img
		
		print(f"ROI hotspot removal complete")
		return data

	def mask_data(self, data, element, threshold):
		img = data[element, :, :, :]
		num_projections = data.shape[1]

		for i in range(num_projections):
			img[i] = img[i] ** 2
			tsh = np.mean(img[i]) * threshold / 100
			img[i][img[i] < tsh] = 0
			img[i][img[i] > tsh] = 255

		return img

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