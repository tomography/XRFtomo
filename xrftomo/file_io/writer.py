#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""
Module for importing raw data files.
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
from PyQt5.QtWidgets import *
import tomopy
import os
import numpy as np
from skimage import io

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
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("rotation axis, " + str(centers[2]) + "\n")
			for i in range(num_files):
				# file.writelines(fnames[i] + ", " + str(x_shift[i]) + ", " + str(y_shift[i]) + "\n")
				file.writelines("{}, {}, {} \n".format(fnames[i], str(x_shift[i]), str(y_shift[i])))
			file.close()
			return

		except IOError:
			print("choose file please")
		except Exception as e:
			print(e)

	def save_scatter_plot(self, fig):
		try:
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError	
			if str(savedir).rfind(".png") == -1:
				savedir = str(savedir) + ".png"
			print(str(savedir))
			fig.savefig(savedir)
		except IOError:
			print("enter file name")
		except Exception as e:
			print(e)

	def save_thetas(self, fnames, thetas):
		num_files = len(fnames)
		try:
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("file names, " + "thetas" + "\n")
			for i in range(num_files):
				file.writelines(fnames[i] + ", " + str(thetas[i]) + "\n")
			file.close()
			return
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)
	def save_projections(self, fnames, data, element_names):
		'''
		save projections as tiffs
		'''
		try:
			savedir = QFileDialog.getExistingDirectory()
			if savedir == "":
				raise IOError

			for j in range(data.shape[0]):			#elemen t index
				path = savedir + "/" + element_names[j]
				os.makedirs(path)
				for i in range(data.shape[1]):		#angle index
					img = data[j, i, :, :]
					img = img.astype(np.float32)
					# temp.save(path+"/"+element_names[j]+"_"+str(i)+'_'+fnames[0].split(".")[0]+".tiff")
					io.imsave(path+"/"+element_names[j]+"_"+str(i)+'_'+fnames[i].split(".")[0]+".tiff", img)
			return
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)

	def save_reconstruction(self, recon, savedir = None, index=-1):
		try:
			if savedir == "":
				raise IOError
			if savedir == None:
				savedir = QFileDialog.getSaveFileName()[0]
			if index == -1:
				recon = tomopy.circ_mask(recon, axis=0)
				io.imsave(savedir+".tiff",recon)
			if index != -1:
				recon = tomopy.circ_mask(recon, axis=0)
				indx = "0000"
				recon_index = indx[:-len(str(index))]+str(index)
				io.imsave(savedir+"_"+str(recon_index)+".tiff", recon[0])
			return
		except IOError:
			print("type the header name")
		except: 
			print("Something went horribly wrong.")

	def save_recon_2npy(self,recon, savedir=None, index=-1):
		try:
			if savedir == "":
				raise IOError
			if savedir == None:
				savedir = QFileDialog.getSaveFileName()[0]
			if index == -1:
				recon = tomopy.circ_mask(recon, axis=0)
				np.save(savedir, recon)
			return
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)
	def save_recon_array_2npy(self, recon_array, savedir=None, index=-1):
		try:
			if savedir == "":
				raise IOError
			if savedir == None:
				savedir = QFileDialog.getSaveFileName()[0]
			if index == -1:
				np.save(savedir, recon_array)
			return
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)


	def save_sinogram(self, sinodata):
		'''
		saves sinogram or array of sinograms for each row
		'''
		try:
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			os.makedirs(savedir)
			# temp_img = Image.fromarray(sinodata.astype(np.float32))
			# temp_img.save(savedir + "/" + "sinogram.tiff")
			io.imsave(savedir + "/" + "sinogram.tiff", sinodata)
			return
			
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)

	def save_sinogram2(self, data, element_names):
		'''
		saves sinogram or array of sinograms for each row
		'''
		try:
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			os.makedirs(savedir)
			num_elements = data.shape[0]
			num_projections = data.shape[1]
			sinogramData = np.sum(data, axis=2)
			sinogramData[np.isinf(sinogramData)] = 0.001

			for i in range(num_elements):
				element = element_names[i]
				# temp_img = Image.fromarray(sinogramData[i].astype(np.float32))
				# temp_img.save(savedir + "/"+element+"_sinogram.tiff")
				io.imsave(savedir + "/"+element+"_sinogram.tiff", sinogramData[i])
			return

		except IOError:
				print("ERROR saving sinogram stack")
		except Exception as e:
			print(e)

		except IOError:
				print("ERROR saving sinogram stack")
		except Exception as e:
			print(e)

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
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			np.savetxt(savedir+"_elements",elements, delimiter = ",", fmt="%s")
			np.save(savedir+"_thetas",thetas)
			np.save(savedir,data)
			return

		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)

	def save_correlation_analysis(self, elements, rMat):
		num_elements = len(elements)
		try:
			savedir = QFileDialog.getSaveFileName()[0]
			if savedir == "":
				raise IOError

			if str(savedir).rfind(".txt") == -1:
				savedir = str(savedir) + ".txt"
			print(str(savedir))
			file = open(savedir, "w")
			file.writelines("elements, " + (', '.join(elements))+ "\n")
			for i in range(num_elements):
				file.writelines(str(elements[i]) + ", " + str(list(rMat[i]))[1:-1] + "\n")
			file.close()
			return
		except IOError:
			print("type the header name")
		except Exception as e:
			print(e)