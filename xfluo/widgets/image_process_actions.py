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

class ImageProcessActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')

	def __init__(self):
		super(ImageProcessActions, self).__init__()
	
	def shiftProjectionUp(self, data, index):
		data[:,index] = np.roll(data[:, index], -1, axis=1)
		self.dataSig.emit(data)

	def shiftProjectionDown(self, data, index):
		data[:,index] = np.roll(data[:,index],1,axis=1)
		self.dataSig.emit(data)

	def shiftProjectionLeft(self, data, index):
		data[:,index] = np.roll(data[:,index],-1)
		self.dataSig.emit(data)

	def shiftProjectionRight(self, data, index):
		data[:,index] = np.roll(data[:,index],1)
		self.dataSig.emit(data)

	def shiftDataUp(self, data, thetas):
		for i in range(len(thetas)):
			data[:,i] = np.roll(data[:,i],-1,axis=1)
		self.dataSig.emit(data)

	def shiftDataDown(self, data, thetas):
		for i in range(len(thetas)):
			data[:,i] = np.roll(data[:,i],1,axis=1)
		self.dataSig.emit(data)

	def shiftDataLeft(self, data):
		data = np.roll(data,-1)
		self.dataSig.emit(data)

	def shiftDataRight(self, data):
		data = np.roll(data,1)
		self.dataSig.emit(data)

	def normalize(self, data, element):
		normData = data[element, :, :, :]
		for i in range((normData.shape[0])):
			temp = normData[i, :, :]
			tempMax = temp.max()
			tempMin = temp.min()
			temp = (temp - tempMin) / tempMax * 10000
			data[element, i, :, :] = temp	
		self.dataSig.emit(data)

	def cut(self, data, img, x_pos, y_pos, x_size, y_size):
		num_elements = data.shape[0]
		num_projections = data.shape[1]
		temp_data = zeros([num_elements,num_projections, img.shape[0], img.shape[1]])
		
		for i in range(num_projections):
			for j in range(num_elements):
				temp_data[j,i,:,:] = data[j, i,
					int(round(abs(y_pos)) - y_size/2):int(round(abs(y_pos)) + y_size/2),
					int(round(x_pos) - x_size/2):int(round(x_pos) + x_size/2)]
		print("done")

		self.data = temp_data
		self.dataSig.emit(self.data)
		return self.data

	def gauss33(self):
		result = self.gauss2D(shape=(3, 3), sigma=1.3)
		print(result)
		return result

	def gauss55(self):
		result = self.gauss2D(shape=(5, 5), sigma=1.3)
		print(result)
		return result

	def gauss2D(self, shape=(3, 3), sigma=0.5):
		"""s
		2D gaussian mask - should give the same result as MATLAB's
		fspecial('gaussian',[shape],[sigma])
		"""
		m, n = [(ss - 1.) / 2. for ss in shape]
		y, x = np.ogrid[-m:m + 1, -n:n + 1]
		h = np.exp(-(x * x + y * y) / (2. * sigma * sigma))
		h[h < np.finfo(h.dtype).eps * h.max()] = 0
		sumh = h.sum()
		if sumh != 0:
			h /= sumh
		return h

	def copy_background(self, img):
		self.meanNoise = np.mean(img)
		self.stdNoise = np.std(img)
		return self.meanNoise, self.stdNoise

	def paste_background(self, data, element, projection, x_pos, y_pos, x_size, y_size, img):
		frame_boundary = img >=0
		noise_generator = np.random.normal(self.meanNoise, self.stdNoise, (y_size, x_size))*frame_boundary

		data[element,projection,
			int(round(abs(y_pos)) - y_size/2):int(round(abs(y_pos)) + y_size/2),
			int(round(x_pos) - x_size/2):int(round(x_pos) + x_size/2)] = noise_generator

		self.dataSig.emit(data)

	def exclude_projection(self, projection, data, thetas):
		num_projections = len(thetas)
		data = np.delete(data, projection, 1)
		thetas = np.delete(thetas, projection, 0)
		
		if projection>0:
			projection -= 1
			num_projections -=1
		else:
			num_projections -= 1

		self.dataSig.emit(data)
		return projection, data, thetas
					
	def noise_analysis(self, img):
		meanNoise, stdNoise = self.copy_background(img)
		flattened = img.reshape(np.size(img))
		noise_generator1 = np.random.normal(meanNoise, stdNoise, np.size(flattened)).clip(min=0)
		noise_generator = np.random.normal(meanNoise, stdNoise, np.shape(img)).clip(min=0)

		figure()
		plt.plot(np.array(np.ones(np.size(flattened), dtype=int)*meanNoise))
		plt.plot(flattened)
		plt.plot(noise_generator1)
		plt.legend(['Average Noise','Noise','Generated Noise'])

		figure()
		plt.imshow(noise_generator, cmap=gray(), interpolation='nearest')
		show()

	def saveHotspot(self):
		# if self.hotSpotNumb < self.data.shape[0]:
		# self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = self.projView.iniY
		# self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = self.projView.iniX
		# self.hotSpotNumb += 1
		# if self.hotSpotNumb < self.data.shape[0]:
		# self.projView.setImage(self.data[self.hotSpotNumb, :, :])
		pass

	def skipHotspot(self):

		# self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = 0
		# self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = 0
		# if self.hotSpotNumb < self.data.shape[0] - 1:
		#     self.hotSpotNumb += 1
		#     self.projView.setImage(self.data[self.hotSpotNumb, :, :])
		pass