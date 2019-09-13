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
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENTn SHALL UChicago    #
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
		self.x_shifts = None
		self.y_shifts = None
		self.centers = None

	def hotspot2line(self, element, boxSize, hs_group, posMat, data):
		'''
		save the position of hotspots
		and align hotspots by fixing hotspots in one position
		'''
		self.posMat = posMat
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, boxSize, hs_group, self.posMat, data)
#****************
		num_projections = data.shape[1]
		boxSize2 = int(boxSize / 2)
		for j in arange(num_projections):

			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				yyshift = int(round(boxSize2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
				xxshift = int(round(boxSize2 - hotSpotX[j] - hs_x_pos[j] + hs_x_pos[firstPosOfHotSpot]))
				data[:, j, :, :] = np.roll(np.roll(data[:, j, :, :], xxshift, axis=2), yyshift, axis=1)

			if hs_x_pos[j] == 0:
				xxshift = 0
			if hs_y_pos[j] == 0:
				yyshift = 0

			self.x_shifts[j] += xxshift
			self.y_shifts[j] += yyshift

		self.centers[2] = hs_x_pos[0]

		print("align done")
		return self.x_shifts, self.y_shifts, self.centers

	def hotspot2sine(self, element, boxSize, hs_group, posMat, data, theta):
		'''
		save the position of hotspots
		and align by both x and y directions (self.alignHotSpotPos3_4)
		'''
		self.posMat = posMat
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, boxSize, hs_group, self.posMat, data)
#****************
		num_projections = data.shape[1]
		boxSize2 = int(boxSize / 2)
		theta  = np.asarray(theta)
		for j in arange(num_projections):

			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				xxshift = int(round(boxSize2 - hotSpotX[j]))
				yyshift = int(round(boxSize2 - hotSpotY[j]))
			if hs_x_pos[j] == 0:
				xxshift = 0
			if hs_y_pos[j] == 0:
				yyshift = 0

			self.x_shifts[j] += xxshift
			self.y_shifts[j] += yyshift

		hotspotXPos = zeros(num_projections, dtype=np.int)
		hotspotYPos = zeros(num_projections, dtype=np.int)
		for i in arange(num_projections):
			hotspotYPos[i] = int(round(hs_y_pos[i]))
			hotspotXPos[i] = int(round(hs_x_pos[i]))
		hotspotProj = np.where(hotspotXPos != 0)[0]
		print(hotspotProj)

		theta_tmp = theta[hotspotProj]
		com = hotspotXPos[hotspotProj]

		if hs_group == 0:
			self.fitCenterOfMass(com, x=theta_tmp)
		else:
			self.fitCenterOfMass2(com, self.centers, x=theta_tmp)
		self.alignCenterOfMass2(hotspotProj, data)

		## yfit
		for i in hotspotProj:
			self.y_shifts[i] += int(hotspotYPos[hotspotProj[0]]) - int(hotspotYPos[i])
			data[:, i, :, :] = np.roll(data[:, i, :, :], self.y_shifts[i], axis=1)
			print(int(hotspotYPos[0]) - int(hotspotYPos[i]))

		#update reconstruction slider value
		# self.recon.sld.setValue(self.centers[2])

		print("align done")
		self.centers = list(np.round(self.centers))
		return self.x_shifts, self.y_shifts, self.centers
		

	def setY(self, element, boxSize, hs_group, posMat, data):
		'''
		loads variables for aligning hotspots in y direction only
		'''
		self.posMat = posMat
		hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data = self.alignment_parameters(element, boxSize, hs_group, self.posMat, data)
#****************
		num_projections = data.shape[1]
		boxSize2 = int(boxSize / 2)
		for j in arange(num_projections):
			if hs_x_pos[j] != 0 and hs_y_pos[j] != 0:
				yyshift = int(round(boxSize2 - hotSpotY[j] - hs_y_pos[j] + hs_y_pos[firstPosOfHotSpot]))
				data[:, j, :, :] = np.roll(data[:, j, :, :], yyshift, axis=1)
			if hs_y_pos[j] == 0:
				yyshift = 0

			self.y_shifts[j] += yyshift

		print("align done")
		self.centers = list(np.round(self.centers))
		return self.x_shifts, self.y_shifts, self.centers



	def alignment_parameters(self, element, boxSize, hs_group, posMat, data):
		self.posMat = posMat
		num_projections = data.shape[1]
		boxSize2 = int(boxSize / 2)
		hs_x_pos = zeros(num_projections, dtype=np.int)
		hs_y_pos = zeros(num_projections, dtype=np.int)
		hs_array = zeros([num_projections, boxSize, boxSize], dtype=np.int)

		for i in arange(num_projections):
			hs_x_pos[i] = int(round(self.posMat[hs_group, i, 0]))
			hs_y_pos[i] = int(abs(round(self.posMat[hs_group, i, 1])))

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
				img = hs_array[i, :, :]
				print(img.sum(), i)
				a, x, y, b, c = self.fitgaussian(img)
				hotSpotY[i] = x
				hotSpotX[i] = y
				yshift_tmp = int(round(boxSize2 - hotSpotY[i]))
				xshift_tmp = int(round(boxSize2 - hotSpotX[i]))
				new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], xshift_tmp, axis=1)
				new_hs_array[i, :, :] = np.roll(new_hs_array[i, :, :], yshift_tmp, axis=0)
				add = 0

		return hs_x_pos, hs_y_pos, firstPosOfHotSpot, hotSpotX, hotSpotY, data

	def fitCenterOfMass(self, com, x):
		fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
		errfunc = lambda p, x, y: fitfunc(p, x) - y
		p0 = [100, 100, 100]
		self.centers, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
		self.centerOfMassDiff = fitfunc(p0, x) - com
		print(self.centerOfMassDiff)

	def fitCenterOfMass2(self, com, x):
		fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + self.centers[2]
		errfunc = lambda p, x, y: fitfunc(p, x) - y
		p0 = [100, 100]
		p2, success = optimize.leastsq(errfunc, np.asarray(p0), args=(x, com))
		self.centerOfMassDiff = fitfunc(p2, x) - com
		print(self.centerOfMassDiff)

	def alignCenterOfMass2(self, hotspotProj, data):
		j = 0
		for i in hotspotProj:
			self.x_shifts[i] += int(self.centerOfMassDiff[j])

			data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(self.x_shifts[i])), axis=2)
			j += 1

		#set some label to be show that the alignment has completed. perhaps print this in a logbox
		# self.lbl.setText("Alignment has been completed")
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
		#TODO: sometimes data == 0 causing division by error.
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

	def clrHotspot(self, posMat):
		posMat[...] = zeros_like(posMat)
		return posMat
