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
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
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

	def background_value(self):
		element = self.control.combo1.currentIndex()
		projection = self.view.sld.value()
		iniX = self.view.view.p1.items[1].pos()[0]
		iniY = self.view.view.p1.items[1].pos()[1]
		xSize = self.control.xSize
		ySize = self.control.ySize
		ystart = int(abs(round(iniY)) - ySize)
		yend = int(abs(round(iniY)))
		xstart= int(round(iniX))
		xend = int(round(iniX))+int(np.floor(xSize))
		img = self.widget.data[element,projection, ystart: yend, xstart: xend]

		self.bg = np.average(img)
		print(self.bg)

	def patch_hotspot(self):
		element = self.control.combo1.currentIndex()
		projection = self.view.sld.value()
		iniX = self.view.view.p1.items[1].pos()[0]
		iniY = self.view.view.p1.items[1].pos()[1]
		xSize = self.control.xSize
		ySize = self.control.ySize
		ystart = int(abs(round(iniY)) - ySize)
		yend = int(abs(round(iniY)))
		xstart= int(round(iniX))
		xend = int(round(iniX))+int(np.floor(xSize))

		img = self.widget.data[element,projection, ystart: yend, xstart: xend]
		self.widget.data[element,projection, ystart: yend, xstart: xend] = ones(img.shape, dtype = img.dtype) * self.bg
		self.view.view.projView.setImage(self.widget.data[element,projection,:,:])

	def normalize(self):
		element = self.control.combo1.currentIndex()
		projection = self.view.sld.value()
		normData = self.widget.data[element, :, :, :]
		for i in range((normData.shape[0])):
			temp = normData[i, :, :]
			tempMax = temp.max()
			tempMin = temp.min()
			temp = (temp - tempMin) / tempMax * 10000
			self.widget.data[element, i, :, :] = temp	

	def cut(self):
		element = self.control.combo1.currentIndex()
		projection = self.view.sld.value()
		iniX = self.view.view.p1.items[1].pos()[0]
		iniY = self.view.view.p1.items[1].pos()[1]
		xSize = self.control.xSize
		ySize = self.control.ySize
		ystart = int(abs(round(iniY)) - ySize)
		yend = int(abs(round(iniY)))
		xstart= int(round(iniX))
		xend = int(round(iniX))+int(np.floor(xSize))

		num_elements = self.control.combo1.count()
		num_projections = self.widget.data.shape[1]
		img = self.widget.data[element,projection, ystart: yend, xstart: xend]
		temp_data = zeros([num_elements,num_projections, img.shape[0], img.shape[1]])
		
		for i in range(num_projections):
			for j in range(num_elements):
				temp_data[j,i,:,:] = self.widget.data[j, i, ystart: yend, xstart: xend]
		print("done")

		self.widget.data = temp_data
		self.view.view.projView.setImage(self.widget.data[element,projection,:,:])