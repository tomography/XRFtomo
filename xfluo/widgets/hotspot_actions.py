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
from scipy import ndimage, optimize, signal

class HotspotActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')
	sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')

	def __init__(self):
		super(HotspotActions, self).__init__()
		self.hotSpotNumb = 0

	# def saveHotSpotPos(self):
	#     # self.projView.view.hotSpotNumb=0
	#     self.projViewElement = self.projViewControl.combo.currentIndex()
	#     self.projView.view.data = self.data[self.projViewElement, :, :, :]
	#     self.projView.view.posMat = zeros(
	#         [5, self.data.shape[1], 2])  ## Later change 5 -> how many data are in the combo box.
	#     self.projView.view.projView.setImage(self.data[self.projViewElement, 0, :, :])


	def hotspot2line(self, element, boxSize, hs_group, posMat, data):
		'''
		save the position of hotspots
		and align hotspots by fixing hotspots in one position
		'''

		num_projections = data.shape[1]
		boxSize2 = int(boxSize / 2)
		hs_x_pos = zeros(num_projections, dtype=np.int)
		hs_y_pos = zeros(num_projections, dtype=np.int)
		hs_array = zeros([num_projections, boxSize, boxSize], dtype=np.int)
		xshift = zeros(num_projections, dtype=np.int)
		yshift = zeros(num_projections, dtype=np.int)
		p1 = [100, 100, int(data.shape[3] / 2)]

		for i in arange(num_projections):
			hs_x_pos[i] = int(round(posMat[hs_group, i, 0]))
			hs_y_pos[i] = int(abs(round(posMat[hs_group, i, 1])))

			if hs_x_pos[i] != 0 and hs_y_pos[i] != 0:
				if hs_y_pos[i] < boxSize2:	# if ROI is past top edge of projection
					hs_y_pos[i] = boxSize2
				if hs_y_pos[i] > data.shape[2] - boxSize2: # if ROI is past top bottom of projection
					hs_y_pos[i] = data.shape[2] - boxSize2
				if hs_x_pos[i] < boxSize2:	# if ROI is past left edge of projection
					hs_x_pos[i] = boxSize2
				if hs_x_pos[i] > data.shape[3] - boxSize2: # if ROI is past right edge of projection
					hs_x_pos[i] = data.shape[3] - boxSize2
				hs_array[i, :, :] = data[element, i,
									hs_y_pos[i] - boxSize2:hs_y_pos[i] + boxSize2,
									hs_x_pos[i] - boxSize2:hs_x_pos[i] + boxSize2]

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
				print(hs_x_pos[i], hs_y_pos[i])
				img = hs_array[i, :, :]
				a, x, y, b, c = self.fitgaussian(img)
				hotSpotY[i] = x
				hotSpotX[i] = y
				yshift_tmp = int(round(boxSize2 - hotSpotY[i]))
				xshift_tmp = int(round(boxSize2 - hotSpotX[i]))
				new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], xshift_tmp, axis=1)
				new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], yshift_tmp, axis=0)
				add = 0

		add2 = 0
		for j in arange(num_projections):

			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				yyshift_tmp = int(round(boxSize2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
				xxshift_tmp = int(round(boxSize2 - hotSpotX[j] - hs_x_pos[j] + hs_x_pos[firstPosOfHotSpot]))
				data[:, j, :, :] = np.roll(np.roll(data[:, j, :, :], xxshift_tmp, axis=2), yyshift_tmp, axis=1)

			if hs_x_pos[j] == 0:
				xxshift_tmp = 0
			if hs_y_pos[j] == 0:
				yyshift_tmp = 0

			xshift[j] += xxshift_tmp
			yshift[j] += yyshift_tmp

		p1[2] = hs_x_pos[0]

		print("align done")

	def fitgaussian(self, data):
		"""Returns (height, x, y, width_x, width_y)
		the gaussian parameters of a 2D distribution found by a fit"""
		params = self.moments(data)
		errorfunction = lambda p: ravel(self.gaussian(*p)(*indices(data.shape)) - data)
		p, success = optimize.leastsq(errorfunction, params)
		return p

	def moments(self, data):
		"""Returns (height, x, y, width_x, width_y)
		the gaussian parameters of a 2D distribution by calculating its
		moments """
		total = data.sum()
		X, Y = indices(data.shape)
		x = (X * data).sum() / total
		y = (Y * data).sum() / total
		col = data[:, int(y)]
		width_x = sqrt(abs((arange(col.size) - y) ** 2 * col).sum() / col.sum())
		row = data[int(x), :]
		width_y = sqrt(abs((arange(row.size) - x) ** 2 * row).sum() / row.sum())
		height = data.max()
		return height, x, y, width_x, width_y

	def gaussian(self, height, center_x, center_y, width_x, width_y):
		"""Returns a gaussian function with the given parameters"""
		width_x = float(width_x)
		width_y = float(width_y)
		return lambda x, y: height * exp(-(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

	# def hotspot2sine(self, hs_group):

	# 	'''
	# 	save the position of hotspots
	# 	and align by both x and y directions (self.alignHotSpotPos3_4)
	# 	'''

	# 	num_projections = data.shape[1]
	# 	boxSize2 = int(boxSize / 2)
	# 	hs_x_pos = zeros(num_projections, dtype=np.int)
	# 	hs_y_pos = zeros(num_projections, dtype=np.int)
	# 	hs_array = zeros([num_projections, boxSize, boxSize], dtype=np.int)

	# 	for i in arange(num_projections):
	# 		hs_x_pos[i] = int(round(posMat[hs_group, i, 0]))
	# 		hs_y_pos[i] = int(abs(round(posMat[hs_group, i, 1])))

	# 		if hs_x_pos[i] != 0 and hs_y_pos[i] != 0:
	# 			if hs_y_pos[i] < boxSize2:	# if ROI is past top edge of projection
	# 				hs_y_pos[i] = boxSize2
	# 			if hs_y_pos[i] > data.shape[2] - boxSize2: # if ROI is past top bottom of projection
	# 				hs_y_pos[i] = data.shape[2] - boxSize2
	# 			if hs_x_pos[i] < boxSize2:	# if ROI is past left edge of projection
	# 				hs_x_pos[i] = boxSize2
	# 			if hs_x_pos[i] > data.shape[3] - boxSize2: # if ROI is past right edge of projection
	# 				hs_x_pos[i] = data.shape[3] - boxSize2
	# 			hs_array[i, :, :] = data[element, i,
	# 								hs_y_pos[i] - boxSize2:hs_y_pos[i] + boxSize2,
	# 								hs_x_pos[i] - boxSize2:hs_x_pos[i] + boxSize2]


	    # self.hotSpotX = zeros(self.projections)
	    # self.hotSpotY = zeros(self.projections)
	    # self.newBoxPos = zeros(self.boxPos.shape)
	    # self.newBoxPos[...] = self.boxPos[...]
	    # ### need to change x and y's
	    # firstPosOfHotSpot = 0
	    # add = 1
	    # for i in arange(self.projections):
	    #     if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
	    #         firstPosOfHotSpot += add
	    #     if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
	    #         print(hs_x_pos[i], hs_y_pos[i]
	    #         img = self.boxPos[i, :, :]
	    #         print(img.shape
	    #         a, x, y, b, c = self.fitgaussian(img)
	    #         self.hotSpotY[i] = x
	    #         self.hotSpotX[i] = y
	    #         yshift = int(round(boxSize2 - self.hotSpotY[i]))
	    #         xshift = int(round(boxSize2 - self.hotSpotX[i]))
	    #         self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
	    #         self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
	    #         ##                  subplot(211)
	    #         ##                  plt.imshow(self.boxPos[i,:,:])
	    #         ##                  subplot(212)
	    #         ##                  plt.imshow(self.newBoxPos[i,:,:])
	    #         ##                  show()
	    #         add = 0

	    # for j in arange(self.projections):

	    #     if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
	    #         yyshift = int(round(boxSize2 - self.hotSpotY[j]))
	    #         xxshift = int(round(boxSize2 - self.hotSpotX[j]))

	    #     ##                        for l in arange(self.data.shape[0]):
	    #     ##                              if yyshift>0:
	    #     ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
	    #     ##                              if yyshift<0:
	    #     ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
	    #     ##                              if xxshift>0:
	    #     ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
	    #     ##                              if xxshift<0:
	    #     ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
	    #     if hs_x_pos[j] == 0:
	    #         xxshift = 0
	    #     if hs_y_pos[j] == 0:
	    #         yyshift = 0

	    #     self.xshift[j] += xxshift
	    #     self.yshift[j] += yyshift

	    # add2 = 0

	    # global hotspotXPos, hotspotYPos
	    # hotspotXPos = zeros(self.projections)
	    # hotspotYPos = zeros(self.projections)
	    # for i in arange(self.projections):
	    #     hotspotYPos[i] = int(round(hs_y_pos[i]))
	    #     hotspotXPos[i] = int(round(hs_x_pos[i]))
	    # self.hotspotProj = np.where(hotspotXPos != 0)[0]
	    # print(self.hotspotProj
	    # ## temp

	    # ## xfit
	    # print(self.hotspotProj
	    # global a1, b4
	    # a1 = self.theta
	    # b4 = self.hotspotProj
	    # theta = self.theta[self.hotspotProj]
	    # print("theta", theta
	    # self.com = hotspotXPos[self.hotspotProj]
	    # if self.projViewControl.combo2.currentIndex() == 0:
	    #     self.fitCenterOfMass(x=theta)
	    # else:
	    #     self.fitCenterOfMass2(x=theta)
	    # self.alignCenterOfMass2()

	    # ## yfit
	    # for i in self.hotspotProj:
	    #     self.yshift[i] += int(hotspotYPos[self.hotspotProj[0]]) - int(hotspotYPos[i])
	    #     self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)
	    #     print(int(hotspotYPos[0]) - int(hotspotYPos[i])

	    # self.recon.sld.setValue(self.p1[2])
	    # print("align done"



	def setY(self):

		# '''
		# loads variables for aligning hotspots in y direction only
		# '''



		# boxSize2 = self.boxSize / 2
		# hs_x_pos = zeros(self.projections)
		# hs_y_pos = zeros(self.projections)
		# self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
		# hs_group = self.projViewControl.combo2.currentIndex()
		# for i in arange(self.projections):

		# 	hs_y_pos[i] = int(round(self.projView.view.posMat[hs_group, i, 0]))
		# 	hs_x_pos[i] = int(round(self.projView.view.posMat[hs_group, i, 1]))

		# 	if hs_x_pos[i] != 0 and hs_y_pos[i] != 0:
		# 		if hs_y_pos[i] < boxSize2:
		# 			hs_y_pos[i] = boxSize2
		# 		if hs_y_pos[i] > self.projView.view.data.shape[1] - boxSize2:
		# 			hs_y_pos[i] = self.projView.view.data.shape[1] - boxSize2
		# 		if hs_x_pos[i] < boxSize2:
		# 			hs_x_pos[i] = boxSize2
		# 		if hs_x_pos[i] > self.projView.view.data.shape[2] - boxSize2:
		# 			hs_x_pos[i] = self.projView.view.data.shape[2] - boxSize2
		# 		# self.boxPos[i,:,:]=self.projView.data[i,hs_x_pos[i]-boxSize2:hs_x_pos[i]+boxSize2,hs_y_pos[i]-boxSize2:hs_y_pos[i]+boxSize2]
		# 		self.boxPos[i, :, :] = self.projView.view.data[i,
		# 							hs_y_pos[i] - boxSize2:hs_y_pos[i] + boxSize2,
		# 							hs_x_pos[i] - boxSize2:hs_x_pos[i] + boxSize2]
		# print(self.boxPos.shape
		# print(hs_x_pos, hs_y_pos

		# self.alignHotSpotY_next()

		pass

	def clrHotspot(self):
		# self.projView.view.posMat[...] = zeros_like(self.projView.view.posMat)

		pass








	# def alignHotSpotY_next(self):
	#     '''
	#     save the position of hotspots
	#     and align by only in y directions.
	#     '''
	#     self.hotSpotX = zeros(self.projections)
	#     self.hotSpotY = zeros(self.projections)
	#     self.newBoxPos = zeros(self.boxPos.shape)
	#     self.newBoxPos[...] = self.boxPos[...]
	#     ### need to change x and y's
	#     firstPosOfHotSpot = 0
	#     add = 1
	#     for i in arange(self.projections):
	#         if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
	#             firstPosOfHotSpot += add
	#         if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
	#             print(hs_x_pos[i], hs_y_pos[i]
	#             img = self.boxPos[i, :, :]
	#             print(img.shape
	#             a, x, y, b, c = self.fitgaussian(img)
	#             self.hotSpotY[i] = x
	#             self.hotSpotX[i] = y
	#             yshift = int(round(boxSize2 - self.hotSpotY[i]))
	#             xshift = int(round(boxSize2 - self.hotSpotX[i]))
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
	#             ##                  subplot(211)
	#             ##                  plt.imshow(self.boxPos[i,:,:])
	#             ##                  subplot(212)
	#             ##                  plt.imshow(self.newBoxPos[i,:,:])
	#             ##                  show()
	#             add = 0

	#     add2 = 0
	#     for j in arange(self.projections):

	#         if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
	#             yyshift = int(round(boxSize2 - self.hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))

	#             print(yyshift
	#             self.data[:, j, :, :] = np.roll(self.data[:, j, :, :],
	#                                             yyshift, axis=1)
	#         ##                        for l in arange(self.data.shape[0]):
	#         ##                              if yyshift>0:
	#         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
	#         ##                              if yyshift<0:
	#         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
	#         ##                              if xxshift>0:
	#         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
	#         ##                              if xxshift<0:
	#         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2

	#         if hs_y_pos[j] == 0:
	#             yyshift = 0

	#         self.yshift[j] += yyshift

	#     print("align done"







	# def alignHotSpotPos3_3(self):
	#     '''
	#     align hotspots by fixing hotspots in one position
	#     '''
	#     self.hotSpotX = zeros(self.projections)
	#     self.hotSpotY = zeros(self.projections)
	#     self.newBoxPos = zeros(self.boxPos.shape)
	#     self.newBoxPos[...] = self.boxPos[...]
	#     ### need to change x and y's
	#     firstPosOfHotSpot = 0
	#     add = 1
	#     for i in arange(self.projections):
	#         if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
	#             firstPosOfHotSpot += add
	#         if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
	#             print(hs_x_pos[i], hs_y_pos[i]
	#             img = self.boxPos[i, :, :]
	#             print(img.shape
	#             a, x, y, b, c = self.fitgaussian(img)
	#             self.hotSpotY[i] = x
	#             self.hotSpotX[i] = y
	#             yshift = int(round(boxSize2 - self.hotSpotY[i]))
	#             xshift = int(round(boxSize2 - self.hotSpotX[i]))
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
	#             ##                  subplot(211)
	#             ##                  plt.imshow(self.boxPos[i,:,:])
	#             ##                  subplot(212)
	#             ##                  plt.imshow(self.newBoxPos[i,:,:])
	#             ##                  show()
	#             add = 0

	#     add2 = 0
	#     for j in arange(self.projections):

	#         if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
	#             yyshift = int(round(boxSize2 - self.hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
	#             xxshift = int(round(boxSize2 - self.hotSpotX[j] - hs_x_pos[j] + hs_x_pos[firstPosOfHotSpot]))
	#             print(xxshift, yyshift
	#             self.data[:, j, :, :] = np.roll(np.roll(self.data[:, j, :, :], xxshift, axis=2),
	#                                             yyshift, axis=1)
	#         ##                        for l in arange(self.data.shape[0]):
	#         ##                              if yyshift>0:
	#         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
	#         ##                              if yyshift<0:
	#         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
	#         ##                              if xxshift>0:
	#         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
	#         ##                              if xxshift<0:
	#         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
	#         if hs_x_pos[j] == 0:
	#             xxshift = 0
	#         if hs_y_pos[j] == 0:
	#             yyshift = 0

	#         self.xshift[j] += xxshift
	#         self.yshift[j] += yyshift

	#     self.p1[2] = hs_x_pos[0]

	#     print("align done"





	# def alignHotSpotPos3_4(self):
	#     '''
	#     align hotspots by fixing hotspots by fitting in a sine curve
	#     '''
	#     self.hotSpotX = zeros(self.projections)
	#     self.hotSpotY = zeros(self.projections)
	#     self.newBoxPos = zeros(self.boxPos.shape)
	#     self.newBoxPos[...] = self.boxPos[...]
	#     ### need to change x and y's
	#     firstPosOfHotSpot = 0
	#     add = 1
	#     for i in arange(self.projections):
	#         if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
	#             firstPosOfHotSpot += add
	#         if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
	#             print(hs_x_pos[i], hs_y_pos[i]
	#             img = self.boxPos[i, :, :]
	#             print(img.shape
	#             a, x, y, b, c = self.fitgaussian(img)
	#             self.hotSpotY[i] = x
	#             self.hotSpotX[i] = y
	#             yshift = int(round(boxSize2 - self.hotSpotY[i]))
	#             xshift = int(round(boxSize2 - self.hotSpotX[i]))
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
	#             ##                  subplot(211)
	#             ##                  plt.imshow(self.boxPos[i,:,:])
	#             ##                  subplot(212)
	#             ##                  plt.imshow(self.newBoxPos[i,:,:])
	#             ##                  show()
	#             add = 0

	#     for j in arange(self.projections):

	#         if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
	#             yyshift = int(round(boxSize2 - self.hotSpotY[j]))
	#             xxshift = int(round(boxSize2 - self.hotSpotX[j]))

	#         ##                        for l in arange(self.data.shape[0]):
	#         ##                              if yyshift>0:
	#         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
	#         ##                              if yyshift<0:
	#         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
	#         ##                              if xxshift>0:
	#         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
	#         ##                              if xxshift<0:
	#         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
	#         if hs_x_pos[j] == 0:
	#             xxshift = 0
	#         if hs_y_pos[j] == 0:
	#             yyshift = 0

	#         self.xshift[j] += xxshift
	#         self.yshift[j] += yyshift

	#     add2 = 0

	#     global hotspotXPos, hotspotYPos
	#     hotspotXPos = zeros(self.projections)
	#     hotspotYPos = zeros(self.projections)
	#     for i in arange(self.projections):
	#         hotspotYPos[i] = int(round(hs_y_pos[i]))
	#         hotspotXPos[i] = int(round(hs_x_pos[i]))
	#     self.hotspotProj = np.where(hotspotXPos != 0)[0]
	#     print(self.hotspotProj
	#     ## temp

	#     ## xfit
	#     print(self.hotspotProj
	#     global a1, b4
	#     a1 = self.theta
	#     b4 = self.hotspotProj
	#     theta = self.theta[self.hotspotProj]
	#     print("theta", theta
	#     self.com = hotspotXPos[self.hotspotProj]
	#     if self.projViewControl.combo2.currentIndex() == 0:
	#         self.fitCenterOfMass(x=theta)
	#     else:
	#         self.fitCenterOfMass2(x=theta)
	#     self.alignCenterOfMass2()

	#     ## yfit
	#     for i in self.hotspotProj:
	#         self.yshift[i] += int(hotspotYPos[self.hotspotProj[0]]) - int(hotspotYPos[i])
	#         self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)
	#         print(int(hotspotYPos[0]) - int(hotspotYPos[i])

	#     self.recon.sld.setValue(self.p1[2])
	#     print("align done"





	# def alignHotSpotY_next(self):
	#     '''
	#     save the position of hotspots
	#     and align by only in y directions.
	#     '''
	#     self.hotSpotX = zeros(self.projections)
	#     self.hotSpotY = zeros(self.projections)
	#     self.newBoxPos = zeros(self.boxPos.shape)
	#     self.newBoxPos[...] = self.boxPos[...]
	#     ### need to change x and y's
	#     firstPosOfHotSpot = 0
	#     add = 1
	#     for i in arange(self.projections):
	#         if hs_x_pos[i] == 0 and hs_y_pos[i] == 0:
	#             firstPosOfHotSpot += add
	#         if hs_x_pos[i] != 0 or hs_y_pos[i] != 0:
	#             print(hs_x_pos[i], hs_y_pos[i]
	#             img = self.boxPos[i, :, :]
	#             print(img.shape
	#             a, x, y, b, c = self.fitgaussian(img)
	#             self.hotSpotY[i] = x
	#             self.hotSpotX[i] = y
	#             yshift = int(round(boxSize2 - self.hotSpotY[i]))
	#             xshift = int(round(boxSize2 - self.hotSpotX[i]))
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
	#             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
	#             ##                  subplot(211)
	#             ##                  plt.imshow(self.boxPos[i,:,:])
	#             ##                  subplot(212)
	#             ##                  plt.imshow(self.newBoxPos[i,:,:])
	#             ##                  show()
	#             add = 0

	#     add2 = 0
	#     for j in arange(self.projections):

	#         if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
	#             yyshift = int(round(boxSize2 - self.hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))

	#             print(yyshift
	#             self.data[:, j, :, :] = np.roll(self.data[:, j, :, :],
	#                                             yyshift, axis=1)
	#         ##                        for l in arange(self.data.shape[0]):
	#         ##                              if yyshift>0:
	#         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
	#         ##                              if yyshift<0:
	#         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
	#         ##                              if xxshift>0:
	#         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
	#         ##                              if xxshift<0:
	#         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2

	#         if hs_y_pos[j] == 0:
	#             yyshift = 0

	#         self.yshift[j] += yyshift

	#     print("align done"