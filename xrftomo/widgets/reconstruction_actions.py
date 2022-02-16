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
import tomopy
import os
# from matplotlib.pyplot import *
import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure




class ReconstructionActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')
	fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

	def __init__(self):
		super(ReconstructionActions, self).__init__()
		self.writer = xrftomo.SaveOptions()

	def reconstruct(self, data, element, center, method, beta, delta, iters, thetas, guess=None):
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
			recon = tomopy.recon(recData, thetas * np.pi / 180, algorithm='mlem', center=recCenter, num_iter=1, init_recon=guess, accelerated=False, device='cpu')
		elif method == 1:
			recon= tomopy.recon(recData, thetas * np.pi / 180, algorithm='gridrec',center=recCenter, init_recon=guess)
			recon= recon/1.49
		elif method == 2:
			recon= tomopy.recon(recData, thetas * np.pi / 180, algorithm='art', num_iter=iters)
			recon= recon/1.49
		elif method == 3:
			recon= tomopy.recon(recData, thetas * np.pi / 180, algorithm='pml_hybrid', center=recCenter, reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)
		elif method == 4:
			recon = tomopy.recon(recData, thetas * np.pi / 180, algorithm='pml_quad', center=recCenter, reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)
		elif method == 5:
			recon= tomopy.recon(recData, thetas * np.pi / 180, algorithm='fbp')
		elif method == 6:
			recon= tomopy.recon(recData, thetas * np.pi / 180, algorithm='sirt', num_iter=iters)
		elif method == 7:
			recon = tomopy.recon(recData, thetas * np.pi / 180, algorithm='tv', center=recCenter, reg_par=np.array([beta, delta], dtype=np.float32), num_iter=iters)
		recon[recon<0] = 0
		#tomopy.remove_nan() does not remove inf values
		recon = tomopy.remove_nan(recon)

		if np.isinf(recon).max():
			print("WARNING: inf values found in reconstruction, consider reconstructing with less iterations")
			print("inf values replaced with 0.001")
			recon[recon == np.inf] = 0.001

		return recon

	def reconstructAll(self, data, element_names, center, method, beta, delta, iters, thetas,start_idx):
		print("This will take a while")
		save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
		num_elements = data.shape[0]
		for i in range(num_elements):
			print("running reconstruction for:", element_names[i])
			savepath = save_path+'/'+element_names[i]
			savedir = savepath+'/'+element_names[i]
			os.makedirs(savepath)
			num_xsections = data.shape[2]
			recons = np.zeros((data.shape[2], data.shape[3], data.shape[3]))  # empty array of size [y, x,x]
			xsection = np.zeros((1, data.shape[1], 1, data.shape[3]))  # empty array size [1(element), frames, 1(y), x]
			for l in range(num_xsections):
				j = num_xsections - l - 1
				xsection[0, :, 0] = data[i, :, j]
				guess = self.reconstruct(xsection, 0, center, method, beta, delta, 5, thetas, 0, False, None)
				for k in range(5, iters):
					guess = self.reconstruct(xsection, 0, center, method, beta, delta, 1, thetas, 0, False,guess)
					recons[i] = guess[0]
					print("reconstructing row {} on iteration{}".format(l, k))
				self.writer.save_reconstruction(guess, savedir, start_idx + l)

		return np.array(recons)

	def assessRecon(self,recon, data, thetas,show_plots):
		#TODO: make sure cros-section index does not exceed the data height
		#get index where projection angle is zero
		zero_index = np.where(abs(thetas)==abs(thetas).min())[0][0]
		num_slices = recon.shape[0]
		width = recon.shape[1]
		reprojection = np.zeros([num_slices, width])

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

	def equalize_recon(self,recon):
		# Equalization
		global_mean = np.mean(recon)
		num_recons = recon.shape[0]
		for i in range(num_recons):
			local_mean = np.mean(recon[i])
			coeff = global_mean/local_mean
			recon[i] = recon[i]*coeff
			img = recon[i]
			# data[element,i] = exposure.equalize_hist(img)
			img *= 1/img.max()
			recon[i] = exposure.equalize_adapthist(img)
		return recon

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

	def reconMultiply(self):
		'''
		multiply reconstruction by 10
		'''
		self.recon = self.recon * 10
		return self.recon

	def reconDivide(self, recon):
		'''
		divide reconstuction by 10
		'''
		self.recon = recon / 10
		return self.recon
