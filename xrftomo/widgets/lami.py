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


class LaminographyWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, name='elementChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    reconChangedSig = pyqtSignal(np.ndarray, name='reconChangedSig')
    reconArrChangedSig = pyqtSignal(dict, name='reconArrChangedSig')

    def __init__(self, parent):
        super(LaminographyWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.ViewControl = xrftomo.LaminographyControlsWidget()
        self.ReconView = xrftomo.LamiView(self)
        self.actions = xrftomo.LaminographyActions()
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
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.ReconView.projView)
        self.h5_dir = "/".join(self.parent.fileTableWidget.dirLineEdit.text().split("/")[:-1])+"/"
        truncated_dir = "~/"+"/".join(self.h5_dir.split("/")[-4:])
        self.ViewControl.browse.setText(truncated_dir)
        self.ViewControl.elem.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.browse.clicked.connect(self.file_browse)
        self.ViewControl.rmHotspotBtn.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.setThreshBtn.clicked.connect(self.set_thresh_params)
        self.ViewControl.recon_stats.clicked.connect(self.get_recon_stats)
        self.sld.valueChanged.connect(self.update_recon_image)
        self.ViewControl.rec_btn.clicked.connect(self.reconstruct_params)
        self.ViewControl.lami_angle.textChanged.connect(self.validate_params)
        self.ViewControl.axis_center.textChanged.connect(self.validate_params)
        self.ViewControl.center_search_width.textChanged.connect(self.validate_params)
        self.ViewControl.thresh.textChanged.connect(self.validate_params)

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

    def file_browse(self):
        try:  # promps for directory and subdir folder
            if os.path.exists(self.h5_dir):
                save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", self.h5_dir)
            else:
                save_path = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
            # save_path = '/Users/marinf/Downloads/test_recon'
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
        # print(save_path)
        self.h5_dir = save_path
        truncated_dir = "~/"+"/".join(self.h5_dir.split("/")[-4:])
        self.ViewControl.browse.setText(truncated_dir)


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

        self.ViewControl.elem.clear()
        for j in self.elements:
            self.ViewControl.elem.addItem(j)
            self.recon_dict[j] = np.zeros((self.y_range,self.data.shape[3],self.data.shape[3]))

        self.ViewControl.axis_center.setText(str(self.data.shape[3]//2))
        self.elementChanged()
        #TODO: recon_array will need to update with any changes to data dimensions as well as re-initialization

        self.sld.setRange(0, self.y_range - 1)
        self.lcd.display(0)
        return

    def elementChanged(self):
        element = self.ViewControl.elem.currentIndex()
        self.updateElementSlot(element)
        self.elementChangedSig.emit(element)


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

        self.sld.setRange(0, end_indx-start_indx - 1)
        self.sld.setValue(0)
        self.lcd.display(0)

    def get_recon_stats(self):
        element = self.elements[self.ViewControl.elem.currentIndex()]

        #TODO: get curent reconstruction from recon_dict
        recon = self.recon_dict[element]
        zero_index = np.where(abs(self.thetas) == abs(self.thetas).min())[0][0]
        middle_index = self.sld.value()
        row_index = int(eval(self.ViewControl.start_indx.text())) + middle_index
        data = self.data[self.elements.index(element)][zero_index]
        data = np.flipud(data)[row_index]
        err, mse = self.actions.recon_stats(recon, middle_index, data, True)
        return

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
        elem = self.ViewControl.elem.currentText()
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
        elem = self.ViewControl.elem.currentText()
        element = self.ViewControl.elem.currentIndex()
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



    def updateElementSlot(self, element):
        self.ViewControl.elem.setCurrentIndex(element)

    def reconstruct_params(self):
        #TODO: create temporary directory to save structured h5 data in if one is not specified

        elements = [self.ViewControl.elem.currentIndex()]
        method = self.ViewControl.method.currentIndex()
        thetas = self.thetas
        recon_option = self.ViewControl.recon_options.currentText()
        lami_angle = eval(self.ViewControl.lami_angle.text())
        axis_center = eval(self.ViewControl.axis_center.text())
        search_width = eval(self.ViewControl.center_search_width.text())
        minus_log = None
        filter_type = None
        fname = self.h5_dir


        lower_thresh = eval(self.ViewControl.thresh.text())
        data = self.data
        num_xsections = data.shape[2]
        recon_dict = self.recon_dict.copy()

        if not self.check_savepath_exists():
            print("save path invalid or insufficient permissions")
            return

        if self.ViewControl.recon_all.isChecked():
            #element is an index, so get list of indices.
            num_elements = self.ViewControl.elem.count()
            elements = [i for i in range(num_elements)]

        for element in elements:
            self.ViewControl.elem.setCurrentIndex(element)    #required to properly update recon_dict
            recons = np.zeros((data.shape[2], data.shape[3], data.shape[3]))  # empty array of size [y, x,x]
            print("working fine")
            for i in range(num_xsections):
                recons = self.actions.reconstruct(data, element, lami_angle, method, thetas, axis_center, fname=fname, rec_op=recon_option, search_width=search_width, recon_type=None, filter_type=filter_type, minus_log=minus_log)
            recon_dict[self.ViewControl.elem.itemText(element)] = np.array(recons)
            self.recon = np.array(recons)

        self.update_recon_image()
        self.update_recon_dict(self.recon)
        self.reconChangedSig.emit(self.recon)
        self.reconArrChangedSig.emit(recon_dict)
        return

    def validate_params(self,sender):
        valid = False
        try:
            val = eval(sender)
            if val >= 0:
                valid = True
                self.sender().setStyleSheet("background: white")
        except:
            print("invalid params")
            self.sender().setStyleSheet("background: lightsalmon")
        return valid

    def check_savepath_exists(self):
        if os.path.exists(self.h5_dir):
            if not os.path.exists(self.h5_dir+"/data/"):
                os.mkdir(self.h5_dir+"/data/")
            if not os.path.exists(self.h5_dir+"/lami_recons/"):
                os.mkdir(self.h5_dir + "/lami_recons/")
        else:
            return False
        return True