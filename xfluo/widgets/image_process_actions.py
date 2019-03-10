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
	# YsizeSig = pyqtSignal(int, name='YsizeSig')

	def __init__(self, parent):
		super(ImageProcessActions, self).__init__()
		self.widget = parent
		self.control = self.widget.ViewControl
		self.view = self.widget.imgAndHistoWidget
	
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
			self.data[self.element, i, :, :] = temp	
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

		# self.x = xSize
		# self.y = ySize

		self.dataSig.emit(data)
		self.YsizeSig.emit(y_size)

	def gauss33(self):
		result = self.gauss2D(shape=(3, 3), sigma=1.3)
		print(result)
		return result

	def gauss55(self):
		result = self.gauss2D(shape=(5, 5), sigma=1.3)
		print(result)
		return result

	def gauss2D(self, shape=(3, 3), sigma=0.5):
		"""
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

	def copy_background(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]
		self.meanNoise = np.mean(self.img)
		self.stdNoise = np.std(self.img)

		return self.meanNoise, self.stdNoise

	def set_background(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]

		frame_boundary = self.img >=0
		noise_generator = np.random.normal(self.meanNoise, self.stdNoise, 
			(self.control.ySize, self.control.xSize))*frame_boundary

		self.widget.data[self.element,self.projection,
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)] = noise_generator

		self.view.view.projView.setImage(self.widget.data[self.element, self.projection, :, :])
		self.sync_data()

	def exclude_projection(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.thetas = self.widget.thetas
		num_projections = len(self.thetas)
		# self.widget.data = np.delete(self.widget.data,self.projection,1)
		self.thetas = np.delete(self.thetas, self.projection, 0)

		# self.files = np.delete(self.files,projection,0)               #remove one projection from every channel
		if self.projection>0:
			self.projection -= 1
			num_projections -=1
		else:
			num_projections -= 1

		self.view.sld.setRange(0, num_projections -1)
		self.view.lcd.display(self.thetas[self.projection])
		self.view.sld.setValue(self.projection)
		self.view.view.projView.setImage(self.widget.data[self.element, self.projection, :, :])

		self.widget.parent.hotspotWidget.imgAndHistoWidget.sld.setRange(0, num_projections -1)
		self.widget.parent.hotspotWidget.imgAndHistoWidget.lcd.display(self.thetas[self.projection])
		self.widget.parent.hotspotWidget.imgAndHistoWidget.sld.setValue(self.projection)
		self.widget.parent.hotspotWidget.imgAndHistoWidget.view.projView.setImage(self.widget.data[self.element, self.projection, :, :])
		
		self.sync_data()
			
	def noise_analysis(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]

		meanNoise, stdNoise = self.copy_background()
		flattened = self.img.reshape(np.size(self.img))
		noise_generator1 = np.random.normal(meanNoise, stdNoise, np.size(flattened)).clip(min=0)
		noise_generator = np.random.normal(meanNoise, stdNoise, np.shape(self.img)).clip(min=0)

		figure()
		plt.plot(np.array(np.ones(np.size(flattened), dtype=int)*meanNoise))
		plt.plot(flattened)
		plt.plot(noise_generator1)
		plt.legend(['Average Noise','Noise','Generated Noise'])

		figure()
		plt.imshow(noise_generator, cmap=gray(), interpolation='nearest')
		show()

	def sync_data(self, data):
		# self.widget.parent.fileTableWidget.data = self.widget.data
		try: 
			print("trying theta sync...")
			self.widget.thetas  = self.thetas
			self.widget.parent.hotspotWidget.thetas = self.thetas	
			self.widget.imageProcessLCDValueChanged()
			self.widget.parent.hotspotWidget.hotSpotLCDValueChanged()
		except Exception as e:
			print(e)

		try:
			self.widget.parent.hotspotWidget.data = self.widget.data
			self.widget.parent.hotspotWidget.hotSpotProjChanged()
			self.widget.parent.sinogramWidget.data = self.widget.data
			self.widget.parent.sinogramWidget.sinogram()
			self.widget.imgProcessProjChanged()
		except Exception as e:
			print(e)
