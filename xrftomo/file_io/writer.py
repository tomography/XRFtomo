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
import dxfile.dxtomo as dx

class SaveOptions(object):
	def save_alignemnt_information(self,fnames, x_shift, y_shift, centers):
		'''
		3D array [projection, x, y]
		fnames 
		'''
		num_files = len(x_shift)
		x_shift = list(x_shift)
		y_shift = list(y_shift)
		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("rotation axis, " + str(centers[2]) + "\n")
			for i in arange(num_files):
				# file.writelines(fnames[i] + ", " + str(x_shift[i]) + ", " + str(y_shift[i]) + "\n")
				file.writelines("{}, {}, {} \n".format(fnames[i], str(x_shift[i]), str(y_shift[i])))
			file.close()
			return

		except IOError:
			print("choose file please")
		except:
			print("Something went horribly wrong.")

	def save_thetas(self, fnames, thetas):
		num_files = len(fnames)
		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("file names, " + "thetas" + "\n")
			for i in arange(num_files):
				file.writelines(fnames[i] + ", " + str(thetas[i]) + "\n")
			file.close()
			return
		except IOError:
			print("type the header name")
		except:
			print("Something went horribly wrong.")

	def save_projections(self, fnames, data, element_names):
		'''
		save projections as tiffs
		'''
		try:
			savedir = QtGui.QFileDialog.getExistingDirectory()
			if savedir == "":
				raise IOError

			for j in arange(data.shape[0]):			#elemen t index
				path = savedir + "/" + element_names[j]
				os.makedirs(path)
				for i in arange(data.shape[1]):		#angle index
					temp_img = data[j, i, :, :]
					temp = Image.fromarray(temp_img.astype(np.float32))
					temp.save(path+"/"+element_names[j]+"_"+str(i)+'_'+fnames[0].split(".")[0]+".tif")
			return
		except IOError:
			print("type the header name")
		except: 
			print("Something went horribly wrong.")

	def save_reconstruction(self, recon, savedir=None):
		try:
			if savedir == "":
				raise IOError
			if savedir == None:
				savedir = QtGui.QFileDialog.getSaveFileName()[0]
			recon = tomopy.circ_mask(recon, axis=0)
			dxchange.writer.write_tiff_stack(recon, fname=savedir)
			return
		except IOError:
			print("type the header name")
		except: 
			print("Something went horribly wrong.")

	def save_sinogram(self, sinodata):
		'''
		saves sinogram or array of sinograms for each row
		'''
		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			os.makedirs(savedir)
			temp_img = Image.fromarray(sinodata.astype(np.float32))
			temp_img.save(savedir + "/" + "sinogram.tif")
			return
			
		except IOError:
			print("type the header name")
		except: 
			print("Something went horribly wrong.")

	def save_sinogram2(self, data, element_names):
		'''
		saves sinogram or array of sinograms for each row
		'''
		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			os.makedirs(savedir)
			num_elements = data.shape[0]
			num_projections = data.shape[1]
			sinogramData = np.sum(data, axis=2)
			sinogramData[isinf(sinogramData)] = 0.001

			for i in range(num_elements):
				element = element_names[i]
				temp_img = Image.fromarray(sinogramData[i].astype(np.float32))
				temp_img.save(savedir + "/"+element+"_sinogram.tif")
			return

		except IOError:
				print("ERROR saving sinogram stack")
		except: 
			print("Something went horribly wrong.")

	def save_dxhdf(self, data, element_names, thetas):
		'''
		saves all selected information to a new data exchange hdf5 file following the 
		dxfile definition at http://dxfile.readthedocs.io/

		uncomment import dxfile.dxtomo as dx

		'''
		try:
			fname = QtGui.QFileDialog.getSaveFileName()[0]
			if fname == "":
				raise IOError

			experimenter_affiliation="Argonne National Laboratory" 
			instrument_name="2-ID-E XRF"  
			sample_name = "test data set"

			# Open DataExchange file
			f = dx.File(fname, mode='w')
			 
			# Write the Data Exchange HDF5 file.
			f.add_entry(dx.Entry.experimenter(affiliation={'value': experimenter_affiliation}))
			f.add_entry(dx.Entry.instrument(name={'value': instrument_name}))
			f.add_entry(dx.Entry.sample(name={'value': sample_name}))

			f.add_entry(dx.Entry.data(data={'value': data, 'units':'ug/cm^2'}))
			f.add_entry(dx.Entry.data(theta={'value': thetas, 'units':'degrees'}))

			# file_names = [x.encode('utf-8') for x in file_names]
			# f.add_entry(dx.Entry.data(fnames={'value': file_names, 'units':'none'}))

			element_names = [x.encode('utf-8') for x in element_names]
			f.add_entry(dx.Entry.data(elements={'value': element_names, 'units':'none'}))

			f.close()

		except IOError:
				print("ERROR saving sinogram stack")
		except: 
			print("Something went horribly wrong.")
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

	def save_numpy_array(self, data, thetas, elements):

		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			np.savetxt(savedir+"_elements",elements, delimiter = ",", fmt="%s")
			np.save(savedir+"_thetas",thetas)
			np.save(savedir,data)
			return

		except IOError:
			print("type the header name")
		except: 
			print("Something went horribly wrong.")


	def save_correlation_analysis(self, elements, rMat):
		num_elements = len(elements)
		try:
			savedir = QtGui.QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("elements, " + (', '.join(elements))+ "\n")
			for i in arange(num_elements):
				file.writelines(str(elements[i]) + ", " + str(list(rMat[i]))[1:-1] + "\n")
			file.close()
			return
		except IOError:
			print("type the header name")
		except:
			print("Something went horribly wrong.")