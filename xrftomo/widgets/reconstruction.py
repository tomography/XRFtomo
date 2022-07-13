# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.           #
#                                                                         #
#                       Software Name: XRFtomo                            #
#                                                                         #
#                   By: Argonne National Laboratory                       #
#                                                                         #
#                       OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#                                                                         #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the           #
#    distribution.                                                        #
#                                                                         #
# 3. Neither the name of the copyright holder nor the names of its        #
#    contributors may be used to endorse or promote products derived      #
#    from this software without specific prior written permission.        #
#                                                                         #
#                               DISCLAIMER                                #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT    #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT     #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    #
###########################################################################


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import xrftomo
import pyqtgraph
import numpy as np
import scipy.ndimage
import os
import shutil

from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure, draw, pause, close
import time


class ReconstructionWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, name='elementChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    reconChangedSig = pyqtSignal(np.ndarray, name='reconChangedSig')
    reconArrChangedSig = pyqtSignal(dict, name='reconArrChangedSig')

    def __init__(self):
        super(ReconstructionWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl = xrftomo.ReconstructionControlsWidget()
        self.ReconView = xrftomo.ReconView(self)
        self.actions = xrftomo.ReconstructionActions()
        self.actions2 = xrftomo.ImageProcessActions()
        self.writer = xrftomo.SaveOptions()

        self.file_name_title = QtWidgets.QLabel("_")
        lbl1 = QtWidgets.QLabel("x pos:")
        self.lbl2 = QtWidgets.QLabel("")
        lbl3 = QtWidgets.QLabel("y pos:")
        self.lbl4 = QtWidgets.QLabel("")
        lbl5 = QtWidgets.QLabel("Slice")
        lbl6 = QtWidgets.QLabel("value:")
        self.lbl7 = QtWidgets.QLabel("")

        self.ReconView.mouseMoveSig.connect(self.updatePanel)
        #get pixel value from Histogram widget's projview

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.ReconView.projView)

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.recon_set.currentIndexChanged.connect(self.recon_combobox_changed)
        self.ViewControl.btn.clicked.connect(self.reconstruct_params)
        # self.ViewControl.equalizeBtn.clicked.connect(self.equalize_params)
        self.ViewControl.rmHotspotBtn.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.setThreshBtn.clicked.connect(self.set_thresh_params)


        # self.ViewControl.btn2.clicked.connect(self.reconstruct_all_params)
        # self.ViewControl.recon2npy.clicked.connect(self.reconstruct_all_npy_params)
        self.ViewControl.mulBtn.clicked.connect(self.call_reconMultiply)
        self.ViewControl.divBtn.clicked.connect(self.call_reconDivide)
        self.ViewControl.end_indx.editingFinished.connect(self.update_y_range)
        self.ViewControl.start_indx.editingFinished.connect(self.update_y_range)
        self.ViewControl.mid_indx.editingFinished.connect(self.update_middle_index)
        self.ViewControl.recon_stats.clicked.connect(self.get_recon_stats)
        self.sld.valueChanged.connect(self.update_recon_image)

        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.recon = None
        self.recon_dict = {}
        self.data = None
        self.data_original = None

        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl1)
        hb0.addWidget(self.lbl2)
        hb0.addWidget(lbl3)
        hb0.addWidget(self.lbl4)
        hb0.addWidget(lbl6)
        hb0.addWidget(self.lbl7)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(lbl5)
        hb1.addWidget(self.lcd)
        hb1.addWidget(self.sld)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.file_name_title)
        vb1.addLayout(hb0)
        vb1.addWidget(self.ReconView)
        vb1.addLayout(hb1)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.ViewControl)
        hb2.addLayout(vb1)
        hb2.addWidget(self.hist, 10)

        self.setLayout(hb2)

    def updatePanel(self,x,y):
        self.lbl2.setText(str(x))
        self.lbl4.setText(str(y))
        try:
            pixel_val = round(self.view.projView.image[abs(y)-1,x],4)
            self.lbl7.setText(str(pixel_val))
        except:
            self.lbl7.setText("")

    def showReconstruct(self):
        '''
        load window for reconstruction window
        '''
        self.write = xrftomo.SaveOptions()
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.y_range = self.data.shape[2]

        self.ViewControl.combo1.clear()
        self.ViewControl.method.clear()
        self.ViewControl.recon_set.clear()
        self.ViewControl.recon_set.disconnect()
        methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad", "fbp", "sirt", "tv"]
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)
        for k in range(len(methodname)):
            self.ViewControl.method.addItem(methodname[k])
        for l in self.elements:
            self.ViewControl.recon_set.addItem(l)
            self.recon_dict[l] = np.zeros((self.y_range,self.data.shape[3],self.data.shape[3]))

        self.ViewControl.recon_set.currentIndexChanged.connect(self.recon_combobox_changed)
        self.elementChanged()
        #TODO: recon_array will need to update with any changes to data dimensions as well as re-initialization

        # self.ViewControl.centerTextBox.setText(str(self.centers[2]))
        self.ViewControl.mulBtn.setEnabled(False)
        self.ViewControl.divBtn.setEnabled(False)
        self.ViewControl.end_indx.setText((str(self.data.shape[2])))
        self.ViewControl.mid_indx.setText((str(self.data.shape[2]//2)))

        self.sld.setRange(0, self.y_range - 1)
        self.lcd.display(0)
        return

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.updateElementSlot(element)
        self.updateReconSlot(element)
        self.elementChangedSig.emit(element)

    def updateReconSlot(self,element):
        element = self.ViewControl.combo1.currentIndex()
        self.ViewControl.recon_set.setCurrentIndex(element)

    def call_reconMultiply(self):
        '''
        multiply reconstruction by 10
        '''
        self.recon = self.actions.reconMultiply(self.recon)
        self.update_recon_image()

    def call_reconDivide(self):
        '''
        divide reconstuction by 10
        '''
        self.recon = self.actions.reconDivide(self.recon)
        self.update_recon_image()

    def ySizeChanged(self, ySize):
        self.ViewControl.start_indx.setText('0')
        self.ViewControl.end_indx.setText(str(ySize))
        self.ViewControl.mid_indx.setText(str(ySize//2))
        self.sld.setValue(0)
        self.sld.setMaximum(ySize)
        for key in self.recon_dict.keys():
            self.recon_dict[key] = np.zeros((ySize,self.data.shape[3],self.data.shape[3]))
        return

    def xSizeChanged(self, xSize):
        for key in self.recon_dict.keys():
            self.recon_dict[key] = np.zeros((self.data.shape[2],xSize,xSize))
        return

    def update_y_range(self):
        start_indx = int(self.ViewControl.start_indx.text())
        end_indx = int(self.ViewControl.end_indx.text())
        if end_indx >self.data.shape[2]:
            end_indx = self.data.shape[2]
            self.ViewControl.end_indx.setText(str(end_indx))
        if end_indx <= 0:
            end_indx = self.data.shape[2]
            self.ViewControl.end_indx.setText(str(end_indx))
        if start_indx >=end_indx:
            self.ViewControl.start_indx.setText(str(end_indx-1))
        if start_indx < 0:
            self.ViewControl.start_indx.setText(str(0))
        self.update_middle_index()

        self.sld.setRange(0, end_indx-start_indx - 1)
        self.sld.setValue(0)
        self.lcd.display(0)

    def update_middle_index(self):
        start_indx = int(self.ViewControl.start_indx.text())
        end_indx = int(self.ViewControl.end_indx.text())
        mid_indx = int(self.ViewControl.mid_indx.text())
        if mid_indx == -1:
            mid_indx = end_indx//2
        if mid_indx > end_indx:
            mid_indx = end_indx
            self.ViewControl.mid_indx.setText(str(mid_indx))
        if mid_indx < start_indx:
            mid_indx = start_indx
            self.ViewControl.mid_indx.setText(str(mid_indx))

    def get_recon_stats(self):
        element = self.elements[self.ViewControl.combo1.currentIndex()]

        #TODO: get curent reconstruction from recon_dict
        recon = self.recon_dict[element]
        zero_index = np.where(abs(self.thetas) == abs(self.thetas).min())[0][0]
        middle_index = self.sld.value()
        row_index = int(eval(self.ViewControl.start_indx.text())) + middle_index
        data = self.data[self.elements.index(element)][zero_index]
        data = np.flipud(data)[row_index]
        err, mse = self.actions.recon_stats(recon, middle_index, data, True)
        return

    # def toggle_middle_index(self):
    #     if self.ViewControl.recon_stats.isChecked():
    #         self.ViewControl.mid_indx.setEnabled(True)
    #     else:
    #         self.ViewControl.mid_indx.setEnabled(False)


    def rm_hotspot_params(self):
        recon = self.recon
        recon = self.actions.remove_hotspots(recon)
        self.update_recon_image()

    def set_thresh_params(self):
        recon = self.recon
        threshold = float(self.ViewControl.lThresh.text())
        recon = self.actions.setThreshold(threshold,recon)
        self.update_recon_image()

    def update_recon_dict(self, recon):
        elem = self.ViewControl.combo1.currentText()
        #recon could be a partial reconstruction, account for this by indexing the Y range as well
        ymin = int(eval(self.ViewControl.start_indx.text()))
        ymax = int(eval(self.ViewControl.end_indx.text()))
        try:
            self.recon_dict[elem][ymin:ymax,:] = recon
        except ValueError:
            self.recon_dict[elem] = recon
            print("array shape missmatch. array_dict possibly updated elsewhere ")
        return

    def recon_combobox_changed(self):
        elem = self.ViewControl.recon_set.currentText()
        element = self.ViewControl.recon_set.currentIndex()
        self.updateElementSlot(element)
        self.elementChangedSig.emit(element)
        try:
            recon = self.recon_dict[elem]
            self.recon = recon
            self.update_recon_image()
        except KeyError:
            print("KeyError")
            #TODO: "loading data twice results in this error, figure out how to re-initialize recon_dict"

    def update_recon_image(self):
        index = self.sld.value()
        self.lcd.display(index)

        try:
            self.ViewControl.maxText.setText(str(self.recon[index, :, :].max()))
            self.ViewControl.minText.setText(str(self.recon[index, :, :].min()))
            self.ReconView.projView.setImage(self.recon[index, :, :])
        except:
            print("run reconstruction first")

    def recon_set_changed(self):
        element = self.ViewControl.recon_set.currentIndex()
        self.updateElementSlot(element)
        self.elementChangedSig.emit(element)

    def updateElementSlot(self, element):
        self.ViewControl.combo1.setCurrentIndex(element)

    def reconstruct_params(self):
        element = self.ViewControl.combo1.currentIndex()
        center = np.array(float(self.data.shape[3]), dtype=np.float32)/2
        method = self.ViewControl.method.currentIndex()
        beta = float(self.ViewControl.beta.text())
        delta = float(self.ViewControl.delta.text())
        iters = int(self.ViewControl.iters.text())
        thetas = self.thetas
        end_indx = int(self.data.shape[2] - eval(self.ViewControl.start_indx.text()))
        start_indx = int(self.data.shape[2] - eval(self.ViewControl.end_indx.text()))
        mid_indx = int(self.data.shape[2] - eval(self.ViewControl.mid_indx.text())) -start_indx - 1

        data = self.data[:,:,start_indx:end_indx,:]
        show_stats = self.ViewControl.recon_stats.isChecked()
        num_xsections = data.shape[2]
        recons = np.zeros((data.shape[2], data.shape[3], data.shape[3]))  # empty array of size [y, x,x]
        xsection = np.zeros((1, data.shape[1], 1, data.shape[3]))  # empty array size [1(element), frames, 1(y), x]
        recon_dict = self.recon_dict.copy()
        if self.ViewControl.recon_save.isChecked():
            try: #promps for directory and subdir folder
                # save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
                save_path = '/Users/marinf/Downloads/test_recon'
                if save_path == "":
                    raise IOError
                if save_path == None:
                    return
            except IOError:
                print("type the header name")
                return
            except:
                print("Unknown error in reconstruct_params()")
                return

        if self.ViewControl.recon_all.isChecked():
            #element is an index, so get list of indices.
            num_elements = self.ViewControl.combo1.count()
            elements = [i for i in range(num_elements)]
        else:
            elements = [self.ViewControl.combo1.currentIndex()]

        for element in elements:
            self.ViewControl.combo1.setCurrentIndex(element)    #required to properly update recon_dict
            recons = np.zeros((data.shape[2], data.shape[3], data.shape[3]))  # empty array of size [y, x,x]
            if self.ViewControl.recon_save.isChecked():
                #get list of element names from list of elemnt indices
                element_names = [self.ViewControl.combo1.itemText(idx) for idx in elements]
                print("running reconstruction for:", element_names[element])
                savepath = save_path + '/' + element_names[element]
                savedir = savepath + '/' + element_names[element]

                if os.path.exists(savepath):
                    shutil.rmtree(savepath)
                os.makedirs(savepath)

            start_idx = int(eval(self.ViewControl.start_indx.text()))
            print("working fine")
            for i in range(num_xsections):
                j = num_xsections - i - 1
                xsection[0, :, 0] = data[element, :, j]
                cent = center

                if method!= 1:  #all methods other than gridrec
                    recon = self.actions.reconstruct(xsection, 0, cent, 1, beta, delta, 5, thetas, None)
                    for k in range(5, iters):
                        recon = self.actions.reconstruct(xsection, 0, cent, method, beta, delta, 1, thetas, recon)
                        print("reconstructing row {}/{} on iteration{}".format(i+1,num_xsections,k))

                else:        #gridrec
                    recon = self.actions.reconstruct(xsection, 0, cent, method, beta, delta, 1, thetas, None)
                    print("reconstructing row{}/{}".format(i+1, num_xsections))

                recons[i] = recon[0]
                if self.ViewControl.recon_save.isChecked():
                    self.writer.save_reconstruction(recon, savedir, start_idx+i)
                err, mse = self.actions.assessRecon(recon, xsection[0,:,0], thetas, show_plots=False)
                print(mse)

            #TODO: Update recon_dict and recon display.
            recon_dict[self.ViewControl.combo1.itemText(element)] = np.array(recons)
            self.recon = np.array(recons)

        self.ViewControl.mulBtn.setEnabled(True)
        self.ViewControl.divBtn.setEnabled(True)
        self.update_recon_image()
        self.update_recon_dict(self.recon)
        self.reconChangedSig.emit(self.recon)
        self.reconArrChangedSig.emit(recon_dict)
        return

    def reconstruct_all_params(self):
        #figure out how to get a list of all selected elements
        num_elements = self.ViewControl.combo1.count()
        element_names = [self.ViewControl.combo1.itemText(i) for i in range(num_elements)]
        # box_checked = self.ViewControl.cbox.isChecked()
        center = np.array(float(self.data.shape[3]), dtype=np.float32)/2
        method = self.ViewControl.method.currentIndex()
        beta = float(self.ViewControl.beta.text())
        delta = float(self.ViewControl.delta.text())
        iters = int(self.ViewControl.iters.text())
        thetas = self.thetas
        end_indx = int(self.data.shape[2] - eval(self.ViewControl.start_indx.text()))
        start_indx = int(self.data.shape[2] - eval(self.ViewControl.end_indx.text()))
        mid_indx = int(self.data.shape[2] - eval(self.ViewControl.mid_indx.text()))
        data = self.data[:,:,start_indx:end_indx,:]

        self.recon = self.actions.reconstructAll(data, element_names, center, method, beta, delta, iters, thetas,start_indx)
        self.ViewControl.mulBtn.setEnabled(True)
        self.ViewControl.divBtn.setEnabled(True)
        self.update_recon_image()
        self.reconChangedSig.emit(self.recon)
        return