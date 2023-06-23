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
from PyQt5.QtCore import pyqtSignal
import xrftomo
import os
import matplotlib.pyplot as plt
from scipy.fftpack import fftshift, ifftshift, fft, ifft, fft2, ifft2
from scipy import interpolate
import numpy as np
import subprocess
from skimage import exposure

#TODO: add multiple viewing angles for reconstruction.
class LaminographyActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')
	fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

	def __init__(self):
		super(LaminographyActions, self).__init__()
		self.writer = xrftomo.SaveOptions()

	def reconstruct(self, data, element, center, tiltangle, method, thetas, search_width, recon_option):
		'''
		load data for reconstruction and load variables for reconstruction
		make it sure that data doesn't have infinity or nan as one of
		entries
		'''
		recData = data[element, :, :, :]
		recData[recData == np.inf] = True
		recData[np.isnan(recData)] = True
		recCenter = np.array(center, dtype=np.float32)

		if method == 0:
			recon = self.lam(data, thetas, tiltangle, interpolation="nearest_neighbor")

		elif method == 1:
			pass
			# os.system("echo Hello from the other side!")
			# "tomocupy recon_steps " \
			# "--file-name {} " \
			# "--lamino-angle 18.25 " \
			# "--center-search-width 50 " \
			# "--rotation-axis 151 " \
			# "--reconstruction-type full " \
			# "--fbp-filter shepp " \
			# "--minus-log False".format(fname)
			# result = subprocess.run(["ls", "-l"])
			recon = None

		if np.isinf(recon).max():
			print("WARNING: inf values found in reconstruction, consider reconstructing with less iterations")
			print("inf values replaced with 0.001")
			recon[recon == np.inf] = 0.001

		return recon

	def assessRecon(self,recon, data, thetas,show_plots=False):
		#TODO: make sure cros-section index does not exceed the data height
		#get index where projection angle is zero
		zero_index = np.where(abs(thetas)==abs(thetas).min())[0][0]
		num_slices = recon.shape[0]
		width = recon.shape[1]
		reprojection = np.zeros([num_slices, width])
		projection = np.zeros([num_slices, width])

		# get recon reporjection for slice i and take the difference with data projection (at angle ~=0).
		for i in range(num_slices):
			reprojection[i] = np.sum(recon[i], axis=0)
			#if data is empty at angle zero, disregard set tmp to zero array
			if data[zero_index].max() == 0:
				#TODO: local porjection referenced before assignment
				projection[i] = np.zeros(width)
			else:
				projection = data[zero_index]
				reprojection = np.sum(recon[0], axis=0)

		#normslize projections against corss section height so plot fits, only used for plotting puposess.

		norm_proj = projection/projection.max()*recon.shape[1]
		norm_repr = reprojection/projection.max()*recon.shape[1]
		sf = np.round(norm_repr.max()/norm_proj.max(),4)
		#difference between reporjection and original projection at angle == 0
		# err = projection - reprojection
		err = norm_proj - norm_repr
		#mean squared error
		mse = (np.square(err)).mean(axis=None)
		if show_plots:

			figA = plt.figure()
			plt.imshow(recon[0], origin='lower'), plt.plot(norm_proj), plt.plot(norm_repr)
			plt.legend(('projection', 'reprojection'), loc=1)
			plt.title("MSE:{}\nScale Factor: {}".format(np.round(mse, 4),sf))
			figA.show()

		return err, mse

	def recon_stats(self,recon, middle_index, projection, show_plots = False):
		# TODO: make sure cros-section index does not exceed the data height
		# get index where projection angle is zero
		num_slices = recon.shape[0]
		width = recon.shape[1]

		# get recon reporjection for slice i and take the difference with data projection (at angle ~=0).
		reprojection = np.zeros((num_slices, width))
		reprojection = np.sum(recon, axis=1)
		# reprojection = np.flipud(reprojection)
		# normslize projections against corss section height so plot fits, only used for plotting puposess.


		#TODO: normalize all to 1 to make mse calculation more fair and not dependant on the recon width.
		if projection.max() > reprojection[middle_index].max():
			plot_proj = projection / projection.max() * recon.shape[1]
			plot_repr = reprojection[middle_index] / reprojection[middle_index].max() * recon.shape[1]
			norm_proj = projection / projection.max()
			norm_repr = reprojection[middle_index] / projection.max()

		else:
			plot_proj = projection / projection.max() * recon.shape[1]
			plot_repr = reprojection[middle_index] / reprojection[middle_index].max() * recon.shape[1]
			norm_proj = projection / reprojection[middle_index].max()
			norm_repr = reprojection[middle_index] / reprojection[middle_index].max()

		sf = np.round(norm_repr.max() / norm_proj.max(), 4)
		# difference between reporjection and original projection at angle == 0
		# err = projection - reprojection
		err = (norm_proj - norm_repr)*100
		# mean squared error
		mse = (np.square(err)).mean(axis=None)
		if show_plots:
			figA = plt.figure()
			plt.imshow(np.flipud(recon[middle_index]), origin='lower'), plt.plot(plot_proj), plt.plot(plot_repr)
			plt.legend(('projection', 'reprojection'), loc=1)
			plt.title("MSE:{}\nScale Factor: {}".format(np.round(mse, 4), sf))
			figA.show()

		return err, mse

	def setThreshold(self,threshold,recon):
		for i in range(recon.shape[0]):
			img = recon[i]
			img[img <= threshold] = 0
			recon[i] = img
		return recon

	def remove_hotspots(self, recon):
		max_val = np.max(recon)
		for i in range(recon.shape[0]):
			img = recon[i]
			img[img > 0.5*max_val] = 0.5*max_val
			recon[i] = img
		return recon

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

	def lam(self, stack, thetas, tiltangle, interpolation="nearest_neighbor"):
		# stack[theta,y,x]
		stack = self.filter(stack)
		theta = np.deg2rad(thetas)
		tiltangle = np.deg2rad(tiltangle)

		n = stack.shape[2]
		nz = stack.shape[1]
		M = stack.shape[0]
		reconstructed = np.zeros((nz, n, n))

		for itheta in range(M):
			data = stack[itheta]


			[Z, X, Y] = np.mgrid[0:nz, 0:n, 0:n]
			zpr = Z-nz/2
			ypr = Y-n/2
			xpr = X-n/2

			# Rotation Ry x Rz - backprojection (works for the tube tiltangle = 0)
			# u = xpr*np.cos(theta[itheta])*np.cos(tiltangle) + ypr*np.sin(theta[itheta])*np.cos(tiltangle) - zpr*np.sin(tiltangle) + n/2
			# v = xpr*np.cos(theta[itheta])*np.sin(tiltangle) + ypr*np.sin(theta[itheta])*np.sin(tiltangle) + zpr*np.cos(tiltangle) + nz/2

			# Backprojection Rotation Rz(-theta) x Ry(-fi)
			# u = xpr*np.cos(theta[itheta])*np.cos(tiltangle) + ypr*np.sin(theta[itheta]) - zpr*np.cos(theta[itheta])*np.sin(tiltangle) + n/2
			# v = xpr*np.sin(tiltangle) + zpr*np.cos(tiltangle) + nz/2

			# # Geometry from the paper
			# u = xpr * np.cos(theta[itheta]) + ypr * np.sin(theta[itheta]) + n/2
			# v = xpr * np.cos(tiltangle) * np.sin(theta[itheta]) - ypr * np.cos(tiltangle) * np.cos(
			#     theta[itheta]) + zpr * np.sin(tiltangle) + nz/2

			# victor Geometry
			# u = xpr * np.cos(theta[itheta]) + ypr * np.sin(theta[itheta]) + n/2
			# v = xpr * np.cos(tiltangle) * np.sin(theta[itheta]) + ypr * np.cos(tiltangle) * np.cos(
			#     theta[itheta]) + zpr * np.sin(tiltangle) + nz/2

			#cos(o)  -sin(o)
			#sin(a)sin(o) cos(a) sin(a)cos(o)
			# u = xpr * np.cos(theta[itheta]) - zpr * np.sin(theta[itheta]) + n/2
			# v = xpr * np.sin(tiltangle) * np.sin(theta[itheta]) - ypr * np.cos(tiltangle)  \
			#     + zpr * np.sin(tiltangle)*np.cos(theta[itheta]) + nz/2

			# sin(a)sin(o) cos(a) sin(a)cos(o)
			#cos(a)sin(o) -sin(a) cos(a)cos(o)
			# u = xpr * np.sin(tiltangle) * np.sin(theta[itheta]) - ypr * np.cos(tiltangle)  \
			#     + zpr * np.sin(tiltangle)*np.cos(theta[itheta]) + n/2
			# v = xpr * np.cos(tiltangle) * np.sin(theta[itheta]) - ypr * np.sin(tiltangle) \
			#     + zpr * np.cos(tiltangle) * np.cos(theta[itheta]) + nz/2

			#cos(o)  -sin(o)
			#cos(a)sin(o) -sin(a) cos(a)cos(o)
			# u = xpr * np.cos(theta[itheta]) - zpr * np.sin(theta[itheta]) + n/2
			# v = xpr * np.cos(tiltangle) * np.sin(theta[itheta]) - ypr * np.sin(tiltangle) \
			#     + zpr * np.cos(tiltangle) * np.cos(theta[itheta]) + nz/2

			#THISSSSS
			u = xpr * np.cos(theta[itheta]) + ypr * np.sin(theta[itheta]) + n/2
			v = -xpr * np.cos(tiltangle) * np.sin(theta[itheta]) + ypr * np.cos(tiltangle) * np.cos(
				theta[itheta]) + zpr * np.sin(tiltangle) + nz/2

			if interpolation == 'nearest_neighbor':
				# Nearest neighbor
				reconstructed += data[
					((((v > 0) & (v < nz)) * v)).astype(np.int),
					((((u > 0) & (u < n)) * u)).astype(np.int)]
			elif interpolation == 'cubic':
				# Cubic interpolation
				[gY, gX] = np.mgrid[0:nz, 0:n]
				reconstructed += interpolate.griddata((gY.ravel(), gX.ravel()), data.ravel(), ((v, u)), method='cubic', fill_value=0.0)

			elif interpolation == "linear":
				# linear interpolation
				[gY, gX] = np.mgrid[0:nz, 0:n]
				reconstructed += interpolate.griddata((gY.ravel(), gX.ravel()), data.ravel(), ((v, u)), method='linear', fill_value=0.0)
			else:
				pass

		return reconstructed


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
