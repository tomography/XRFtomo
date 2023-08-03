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
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import xrftomo
import pyqtgraph
import numpy as np
import scipy.ndimage
import os
import h5py
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
        self.ViewControl.elem.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.method.currentIndexChanged.connect(self.method_changed)
        self.ViewControl.browse.setText(truncated_dir)
        self.ViewControl.browse.clicked.connect(self.file_browse)
        self.ViewControl.generate.clicked.connect(self.generate_structure)
        self.ViewControl.show_ops.clicked.connect(self.show_options)
        self.ViewControl.rmHotspotBtn.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.recon_stats.clicked.connect(self.get_recon_stats)
        self.sld.valueChanged.connect(self.update_recon_image)
        self.ViewControl.rec_btn.clicked.connect(self.reconstruct_params)

        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.recon = None
        self.recon_dict = {}
        self.data = None
        self.data_original = None
        self.method_changed()
        self.show_options()


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


    def show_options(self):
        if self.ViewControl.show_ops.isChecked() and self.ViewControl.show_ops.isVisible():
            self.ViewControl.show_ops.setText("show less")
            for child in self.ViewControl.scroll.children():
                child.setVisible(False)

        elif not self.ViewControl.show_ops.isChecked() and self.ViewControl.show_ops.isVisible():
            self.ViewControl.show_ops.setText("show more")
            for child in self.ViewControl.scroll.children():
                child.setVisible(True)

    def method_changed(self):
        if self.ViewControl.method.currentIndex() == 0:
            self.ViewControl.scroll.setVisible(False)
            self.ViewControl.scroll2.setVisible(True)
            self.ViewControl.browse.setVisible(False)
            self.ViewControl.generate.setVisible(False)
            self.ViewControl.generate_lbl.setVisible(False)
            self.ViewControl.browse_lbl.setVisible(False)
            self.ViewControl.show_ops.setVisible(False)

        elif self.ViewControl.method.currentIndex() == 1:
            self.ViewControl.scroll.setVisible(True)
            self.ViewControl.scroll2.setVisible(False)
            self.ViewControl.browse.setVisible(True)
            self.ViewControl.generate.setVisible(True)
            self.ViewControl.generate_lbl.setVisible(True)
            self.ViewControl.browse_lbl.setVisible(True)
            self.ViewControl.show_ops.setVisible(True)
        else:
            pass
        return
    def file_browse(self):
        try:  # promps for directory and subdir folder
            if os.path.exists(self.h5_dir):
                save_path = QFileDialog.getExistingDirectory(self, "Open Folder", self.h5_dir)
            else:
                save_path = QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
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

    def generate_structure(self):
        parent_dir = self.h5_dir
        rec = "tomocupy_rec"
        data = "tomocupy_data"

        # Paths
        path_rec = os.path.join(parent_dir, rec)
        path_data = os.path.join(parent_dir, data)

        try:
            os.makedirs(path_rec, exist_ok=True)
            os.makedirs(path_data, exist_ok=True)
            print("Directory '%s' created successfully" % rec)
            print("Directory '%s' created successfully" % data)
        except OSError as error:
            print("Directory '%s' created successfully" % rec)
            print("Directory '%s' created successfully" % data)
            return

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

        if self.parent.tcp_installed:
            self.ViewControl.__dict__["reconstruction-type"].item3.setChecked(True)
            self.ViewControl.__dict__["lamino-angle"].item2.setText("18.25")
            self.ViewControl.__dict__["lamino-angle"].item3.setChecked(True)
            self.ViewControl.__dict__["rotation-axis"].item2.setText(str(self.data.shape[3]//2))
            self.ViewControl.__dict__["rotation-axis"].item3.setChecked(True)
            self.ViewControl.__dict__["lamino-search-width"].item2.setText("20")
            self.ViewControl.__dict__["lamino-search-width"].item3.setChecked(True)
            self.ViewControl.__dict__["fbp-filter"].item2.setCurrentIndex(1)
            self.ViewControl.__dict__["fbp-filter"].item3.setChecked(True)
            self.ViewControl.__dict__["minus-log"].item2.setText("False")
            self.ViewControl.__dict__["minus-log"].item3.setChecked(True)
            self.ViewControl.__dict__["file-name"].item2.setText("")
            self.ViewControl.__dict__["file-name"].item3.setChecked(True)
        else:
            self.ViewControl.method.clear()
            self.ViewControl.method.addItem("lamni-fbp(cpu)")
            self.ViewControl.__dict__["fbp-filter"].item2.setCurrentIndex(1)
            self.ViewControl.__dict__["fbp-filter"].item3.setChecked(True)
            self.ViewControl.__dict__["lamino-angle"].item2.setText("18.25")
            self.ViewControl.__dict__["lamino-angle"].item3.setChecked(True)
            self.ViewControl.__dict__["rotation-axis"].item2.setText(str(self.data.shape[3]//2))
            self.ViewControl.__dict__["rotation-axis"].item3.setChecked(True)


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
        try:
            self.recon_dict[elem]= recon
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
        lami_angle = 90 - eval(self.ViewControl.__dict__["lamino-angle"].item2.text())
        center_axis = eval(self.ViewControl.__dict__["rotation-axis"].item2.text())
        parent_dir = self.h5_dir
        data = self.data.copy()
        recon_dict = self.recon_dict.copy()
        command_string = self.get_command_string()

        if not self.check_savepath_exists():
            print("save path invalid or insufficient permissions")
            return

        if self.ViewControl.recon_all.isChecked():
            num_elements = self.ViewControl.elem.count()
            elements = [i for i in range(num_elements)]

        for element_idx in elements:
            element = self.parent.elements[element_idx]
            #TODO: edit file-name to match current element.h5 file path.
            # self.ViewControl.__dict__["file-name"].item2.setText("")
            self.ViewControl.elem.setCurrentIndex(element_idx)    #required to properly update recon_dict
            recons = self.actions.reconstruct(data, element_idx, element, lami_angle, center_axis, method, thetas, parent_dir=parent_dir, command_string=command_string)
            recon_dict[self.ViewControl.elem.itemText(element_idx)] = np.array(recons),
            self.recon = np.array(recons)

        self.update_recon_image()
        self.update_recon_dict(self.recon)
        self.reconChangedSig.emit(self.recon)
        self.reconArrChangedSig.emit(recon_dict)
        return

    def get_command_string(self):
        options = []
        values = []
        command = "tomocupy recon_steps"

        for line in self.ViewControl.line_names:
            line_object = self.ViewControl.__dict__[line]
            if line_object.item3.isChecked():
                options.append(line)
                command += " --{}".format(line)
                if isinstance(line_object.item2, QComboBox):
                    value = line_object.item2.currentText()
                    values.append(value)
                    command += " {}".format(value)
                elif isinstance(line_object.item2, QLineEdit):
                    value = line_object.item2.text()
                    values.append(value)
                    command += " {}".format(value)

        return command

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
            if not os.path.exists(self.h5_dir+"/tomocupy_rec/"):
                os.mkdir(self.h5_dir+"/tomocupy_rec/")
            if not os.path.exists(self.h5_dir+"/tomocupy_data/"):
                os.mkdir(self.h5_dir + "/tomocupy_data/")
        else:
            return False
        return True