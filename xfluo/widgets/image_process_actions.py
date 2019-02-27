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
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt

class ImageProcessActions(QtWidgets.QWidget):
	def __init__(self, parent):
		super(ImageProcessActions, self).__init__()
		self.parent = parent
		self.widget = self.parent.imageProcessWidget
		self.control = self.widget.ViewControl
		self.view = self.widget.imgAndHistoWidget
	
	def shiftProjectionUp(self):
		projection_index = self.view.sld.value()
		self.widget.data[:,projection_index] = np.roll(self.widget.data[:,projection_index],-1,axis=1)
		self.widget.imgProcessProjChanged()

	def shiftProjectionDown(self):
		projection_index = self.view.sld.value() 
		self.widget.data[:,projection_index] = np.roll(self.widget.data[:,projection_index],1,axis=1)
		self.widget.imgProcessProjChanged()

	def shiftProjectionLeft(self):
		projection_index = self.view.sld.value() 
		self.widget.data[:,projection_index] = np.roll(self.widget.data[:,projection_index],-1)
		self.widget.imgProcessProjChanged()

	def shiftProjectionRight(self):
		projection_index = self.view.sld.value() 
		self.widget.data[:,projection_index] = np.roll(self.widget.data[:,projection_index],1)
		self.widget.imgProcessProjChanged()

	def shiftDataUp(self):
		self.thetas = self.widget.thetas
		for i in range(len(self.thetas)):
			self.widget.data[:,i] = np.roll(self.widget.data[:,i],-1,axis=1)
		self.widget.imgProcessProjChanged()

	def shiftDataDown(self):
		self.thetas = self.widget.thetas
		for i in range(len(self.thetas)):
			self.widget.data[:,i] = np.roll(self.widget.data[:,i],1,axis=1)
		self.widget.imgProcessProjChanged()

	def shiftDataLeft(self):
		self.widget.data = np.roll(self.widget.data,-1)
		self.widget.imgProcessProjChanged()

	def shiftDataRight(self):
		self.widget.data = np.roll(self.widget.data,1)
		self.widget.imgProcessProjChanged()

	def background_value(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]

		self.bg = np.average(self.img)
		print(self.bg)

	def patch_hotspot(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]

		patch = ones(self.img.shape, dtype = self.img.dtype) * self.bg

		self.widget.data[self.element,self.projection,
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)] = patch
		
		self.view.view.projView.setImage(self.widget.data[self.element, self.projection,:,:])

	def normalize(self):
		self.element = self.control.combo1.currentIndex()
		normData = self.widget.data[self.element, :, :, :]
		for i in range((normData.shape[0])):
			temp = normData[i, :, :]
			tempMax = temp.max()
			tempMin = temp.min()
			temp = (temp - tempMin) / tempMax * 10000
			self.widget.data[self.element, i, :, :] = temp	

	def cut(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]
		num_elements = self.control.combo1.count()
		num_projections = self.widget.data.shape[1]
		temp_data = zeros([num_elements,num_projections, self.img.shape[0], self.img.shape[1]])
		
		for i in range(num_projections):
			for j in range(num_elements):
				temp_data[j,i,:,:] = self.widget.data[j, i,
					int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
					int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
					int(round(self.view.view.x_pos) - self.control.xSize/2): 
					int(round(self.view.view.x_pos) + self.control.xSize/2)]
		print("done")

		self.widget.data = temp_data
		self.view.view.projView.setImage(self.widget.data[self.element, self.projection,:,:])

		# self.x = xSize
		# self.y = ySize
		# self.sino.sld.setRange(1, self.control.ySize)
		# self.sino.sld.setValue(1)
		# self.sino.lcd.display(1)

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

	def set_background(self):
		self.element = self.control.combo1.currentIndex()
		self.projection = self.view.sld.value()
		self.img = self.widget.data[self.element, self.projection, 
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)]

		frame_boundary = self.img > 0
		noise_generator = np.random.normal(self.meanNoise, self.stdNoise, 
			(self.control.ySize, self.control.xSize))*frame_boundary

		self.widget.data[self.element,self.projection,
			int(round(abs(self.view.view.y_pos)) - self.control.ySize/2):
			int(round(abs(self.view.view.y_pos)) + self.control.ySize/2),
			int(round(self.view.view.x_pos) - self.control.xSize/2): 
			int(round(self.view.view.x_pos) + self.control.xSize/2)] = noise_generator

		self.view.view.projView.setImage(self.widget.data[self.element, self.projection, :, :])
