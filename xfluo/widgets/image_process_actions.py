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

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt


class ImageProcessActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')
	thetaSig = pyqtSignal(np.ndarray, name='thetaSig')
	
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

		data = temp_data
		self.dataSig.emit(data)
		return data

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
		self.thetaSig.emit(thetas)
		# return projection, data, thetas
		return
		
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

	def bounding_analysis(self, projection):
		bounds = self.find_bounds(projection, 20)
		rowsum = np.sum(projection, axis=0)/projection.shape[0]
		colsum = np.sum(projection, axis=1)/projection.shape[1]

		fig = plt.figure(figsize=(5,5.5))
		#ax1, ax2, ax3 = top right, middle
		ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
		ax2 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
		ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2, sharey=ax2, sharex=ax1)
		ax1.get_xaxis().set_visible(False)
		# ax1.get_yaxis().set_visible(False)
		#ax2.get_xaxis().set_visible(False)
		ax2.get_yaxis().set_visible(False)

		ax1.plot(rowsum)
		ax1.axvline(bounds[0], c='r')
		ax1.axvline(bounds[1], c='r')
		ax3.imshow(projection)
		ax3.set_aspect(aspect=projection.shape[1] / projection.shape[0])
		ax3.axvline(bounds[0], c='r')
		ax3.axvline(bounds[1], c='r')
		ax3.axhline(bounds[2], c='r')
		ax3.axhline(bounds[3], c='r')
		ax2.plot(colsum, np.arange(projection.shape[0]))
		ax2.axhline(bounds[2], c='r')
		ax2.axhline(bounds[3], c='r')

		# fig2 = plt.figure(figsize=(5,5.5))
		#
		# downx = 10
		# downy = 100
		# proj = self.rebin(projection, downx,downy)
		# rowsum = np.sum(proj, axis=0)/proj.shape[0]
		# colsum = np.sum(proj, axis=1)/proj.shape[1]
		#
		#
		# #ax1, ax2, ax3 = top right, middle
		# ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
		# ax2 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
		# ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2, sharey=ax2, sharex=ax1)
		# ax1.get_xaxis().set_visible(False)
		# # ax1.get_yaxis().set_visible(False)
		# #ax2.get_xaxis().set_visible(False)
		# ax2.get_yaxis().set_visible(False)
		#
		# ax1.plot(rowsum)
		# ax1.axvline(bounds[0], c='r')
		# ax1.axvline(bounds[1], c='r')
		# ax3.imshow(proj)
		# ax3.set_aspect(aspect=proj.shape[1] / proj.shape[0])
		# ax3.axvline(bounds[0], c='r')
		# ax3.axvline(bounds[1], c='r')
		# ax3.axhline(bounds[2], c='r')
		# ax3.axhline(bounds[3], c='r')
		# ax2.plot(colsum, np.arange(proj.shape[0]))
		# ax2.axhline(bounds[2], c='r')
		# ax2.axhline(bounds[3], c='r')
		#
		#
		# plt.tight_layout()
		#
		#
		#
		# plt.show()
		return fig

	def rebin(self, projection, x=100, y=100):

		numrows=projection.shape[0]
		numcols=projection.shape[1]
		newrows= round(numrows/round(numrows*(y/100)))
		newcols= round(numcols/round(numcols*(x/100)))

		projection = projection[::newrows, ::newcols].repeat(newcols, axis=1).repeat(newrows,axis=0)[:numrows, :numcols]

		# projection = projection[::newrows, :].repeat(newrows, axis=0)[:numrows, :]

		return projection


	def find_bounds(self, projection, coeff):
		bounds = {}
		bounds[0] = [] #x_left
		bounds[1] = [] #x_right
		bounds[2] = [] #y_top
		bounds[3] = [] #y_bottom
		
		col_sum = np.sum(projection, axis=0)/projection.shape[0]
		row_sum = np.sum(projection, axis=1)/projection.shape[1]
		noise_col = np.sort(col_sum[col_sum > 0])[:1]
		noise_row = np.sort(row_sum[row_sum > 0])[:1]

		if noise_col <= noise_row:
			noise = noise_col
		else:
			noise = noise_row

		upper_thresh_col = np.median(col_sum)
		diffcol = upper_thresh_col - noise
		y_thresh = diffcol*coeff/100 + noise

		upper_thresh_row = np.median(row_sum)
		diffrow = upper_thresh_row - noise
		x_thresh = diffrow*coeff/100 + noise

		for j in range(len(col_sum)):
			if col_sum[j] >= y_thresh:
				bounds[0].append(j)
				break
		for j in range(len(col_sum)):
			if col_sum[len(col_sum)-j-1] >= y_thresh:
				bounds[1].append(len(col_sum)-j-1)
				break
		for j in range(len(row_sum)):
			if row_sum[len(row_sum)-j-1] >= x_thresh:
				bounds[2].append(len(row_sum)-j-1)
				break
		for j in range(len(row_sum)):
			if row_sum[j] >= x_thresh:
				bounds[3].append(j)
				break
		return bounds  

	def save_bound_anlysis(self,data,element,thetas):
		save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
		num_projections = data.shape[1]

		for i in range(num_projections):
			projection = data[element,i,:,:]
			projection = self.rebin(projection,10,100)
			fig = self.bounding_analysis(projection)
			angle = str(thetas[i])
			fig.axes[2].set_title(angle)
			fig.savefig(save_path+'/'+angle+'.png')
		return


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
