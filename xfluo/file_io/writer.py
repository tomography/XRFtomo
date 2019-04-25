#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""
Module for importing raw data files.
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
import dxchange
import string
from PyQt5 import QtGui
from pylab import *
import tomopy
import os
from PIL import Image


class SaveOptions(object):
	def save_alignemnt_information(self,fnames, x_shift, y_shift, centers):
		'''
		3D array [projection, x, y]
		fnames 
		'''
		num_files = len(x_shift)
		try:
			alignFileName = QtGui.QFileDialog.getSaveFileName()[0]
			if str(alignFileName).rfind(".txt") == -1:
				alignFileName = str(alignFileName) + ".txt"
			print(str(alignFileName))
			file = open(alignFileName, "w")
			file.writelines("rotation axis, " + str(centers[2]) + "\n")
			for i in arange(num_files):
				file.writelines(fnames[i] + ", " + str(x_shift[i]) + ", " + str(y_shift[i]) + "\n")
			file.close()
		except IOError:
			print("choose file please")

	def save_projections(self, fnames, data, element_names):
		'''
		save projections as tiffs
		'''
		savedir = QtGui.QFileDialog.getSaveFileName()[0]
		for j in arange(data.shape[0]):			#elemen t index
			path = savedir + "/" + element_names[j]
			try:
				os.makedirs(path)
			except e:
				print(e)
			for i in arange(data.shape[1]):		#angle index
				temp_img = data[j, i, :, :]
				temp = Image.fromarray(temp_img.astype(np.float32))
				temp.save(path+"/"+element_names[j]+"_"+fnames[i]+".tiff")

	def save_reconstruction(self, recon):
		try:
			global debugging
			savedir = str(QtGui.QFileDialog.getSaveFileName())

			if savedir == "":
				raise IndexError
			print(savedir)
			recon = tomopy.circ_mask(recon, axis=0)
			dxchange.writer.write_tiff_stack(recon, fname=savedir)
		except IndexError:
			print("type the header name")

	def save_sinogram(self, sinodata):
		'''
		saves sinogram or array of sinograms for each row
		'''
		j = Image.fromarray(sinodata.astype(np.float32))
		j.save("sinogram.tif")
		return
		
	def export_h5(self):

		#angle
		#x_shifts (pixels)
		#y_shifts (pixels)
		#hotspot_x [ lisr entry]
		#hotspor_y [ list entry]
		#centers
		#projections

		#row
		#sinogram (function of row)
		#reconstruction

		'''
		saves all selected information to a new or existing h5 file
		'''
		pass

	def save_center_position(self, angle, cen_pos):
		'''
		save center pixel position and possibly motor position as a 3D array
		in order to apply to raw data, first apply the shifts then apply/load 
		center position
		'''
		pass

	def save_motor_position(self, angle, x_pos, y_pos):
	# 	'''
	# 	save motor positions along with corresponding angle position
	# 	'''
		pass
