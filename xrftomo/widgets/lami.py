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
from PyQt5.QtWidgets import QFileDialog, QComboBox, QLineEdit
from PyQt5.QtCore import pyqtSignal
import xrftomo
import pyqtgraph
import numpy as np
import scipy.ndimage
import os
import sys
import h5py
import shutil

from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure, draw, pause, close
import time

#TODO: add volume rotation option
#TODO: add crop option
# TODO: Run recons in separate thread
# TODO: change reconstruct and remove_artifact to "click to cancel" while thread is running.
#TODO: add ROI box or draggable ROI

class LaminographyWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, name='elementChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    reconChangedSig = pyqtSignal(np.ndarray, name='reconChangedSig')
    reconArrChangedSig = pyqtSignal(dict, name='reconArrChangedSig')

    def __init__(self, parent):
        super(LaminographyWidget, self).__init__()
        self.parent = parent
        self.initUI()
        sys.stdout = xrftomo.gui.Stream(newText=self.parent.onUpdateText)

    def initUI(self):
        self.ViewControl = xrftomo.LaminographyControlsWidget()
        self.ReconView = xrftomo.LamiView(self)
        self.actions = xrftomo.LaminographyActions()
        self.writer = xrftomo.SaveOptions(self)

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

        self.ViewControl.rotate_volume.clicked.connect(self.openEvent)
        self.ViewControl.elem.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.elem.currentIndexChanged.connect(self.recon_combobox_changed)
        self.ViewControl.method.currentIndexChanged.connect(self.method_changed)
        self.ViewControl.tomocupy_opts.browse.setText(truncated_dir)
        self.ViewControl.tomocupy_opts.browse.clicked.connect(self.file_browse)
        self.ViewControl.tomocupy_opts.generate.clicked.connect(self.generate_structure)
        # self.ViewControl.tomocupy_opts.show_ops.clicked.connect(self.show_options)
        self.ViewControl.rm_hotspot.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.recon_stats.clicked.connect(self.get_recon_stats)
        self.sld.valueChanged.connect(self.update_recon_image)
        self.ViewControl.reconstruct.clicked.connect(self.reconstruct_params)
        self.ViewControl.reset.clicked.connect(self.reset_recon_volume)
        self.ViewControl.apply.clicked.connect(self.apply_clicked)
        self.ViewControl.sld_rot_vol.sliderReleased.connect(self.update_vol_image)
        self.ViewControl.sld_rot_vol_ldt.returnPressed.connect(self.rot_vol_ldt_changed)
        self.ViewControl.sld_x.sliderReleased.connect(self.rot_vol_sld_changed)
        self.ViewControl.sld_y.sliderReleased.connect(self.rot_vol_sld_changed)
        self.ViewControl.sld_z.sliderReleased.connect(self.rot_vol_sld_changed)
        self.ViewControl.sld_x_ldt.returnPressed.connect(self.rot_vol_ldt_changed)
        self.ViewControl.sld_y_ldt.returnPressed.connect(self.rot_vol_ldt_changed)
        self.ViewControl.sld_z_ldt.returnPressed.connect(self.rot_vol_ldt_changed)
        self.ViewControl.circular_mask.clicked.connect(self.circular_mask_params)

        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.recon = None
        self.recon_dict = {}
        self.data = None
        self.data_original = None
        self.method_changed()

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

        # self.show_select_plus()
        return

    def openEvent(self):
        self.tmp_recon = np.copy(self.recon)
        self.reset_recon_volume()
        self.update_vol_image()
        self.ViewControl.rotate_volume_window.show()

    def reset_recon_volume(self):
        self.tmp_recon = np.copy(self.recon)
        self.ViewControl.sld_rot_vol.setRange(0,self.tmp_recon.shape[0])
        self.ViewControl.sld_x_ldt.setText(str(0))
        self.ViewControl.sld_y_ldt.setText(str(0))
        self.ViewControl.sld_z_ldt.setText(str(0))
        self.ViewControl.sld_rot_vol.setValue(0)
        self.ViewControl.sld_x.setValue(0)
        self.ViewControl.sld_y.setValue(0)
        self.ViewControl.sld_z.setValue(0)

    def rot_vol_sld_changed(self):
        x_deg = self.ViewControl.sld_x.value()/10
        y_deg = self.ViewControl.sld_y.value()/10
        z_deg = self.ViewControl.sld_z.value()/10
        self.ViewControl.sld_x_ldt.setText(str(x_deg))
        self.ViewControl.sld_y_ldt.setText(str(y_deg))
        self.ViewControl.sld_z_ldt.setText(str(z_deg))
        self.rotate_volume_params([x_deg,y_deg,z_deg])

    def rot_vol_ldt_changed(self):
        vol_ldt = self.ViewControl.sld_rot_vol_ldt.text()
        x_ldt = self.ViewControl.sld_x_ldt.text()
        y_ldt = self.ViewControl.sld_y_ldt.text()
        z_ldt = self.ViewControl.sld_z_ldt.text()
        try:
            vol_ldt = round(eval(vol_ldt),1)
            x_ldt = round(eval(x_ldt),1)
            y_ldt = round(eval(y_ldt),1)
            z_ldt = round(eval(z_ldt),1)
            if x_ldt < -90 or x_ldt > 90 or y_ldt < -90 or y_ldt > 90 or z_ldt < -90 or z_ldt > 90:
                print("invalid angle entered")
                return
        except:
            print("invalid angle entered")
            return

        
        self.ViewControl.sld_rot_vol.setValue(vol_ldt)
        self.ViewControl.sld_x.setValue(int(x_ldt*10))
        self.ViewControl.sld_y.setValue(int(y_ldt*10))
        self.ViewControl.sld_z.setValue(int(z_ldt*10))
        self.rot_vol_sld_changed()

    def rotate_volume_params(self, angles):
        try:
            recon = np.copy(self.recon)
            self.tmp_recon = self.actions.rotate_volume(recon, angles)
            self.ViewControl.sld_rot_vol.setRange(0, self.tmp_recon.shape[0])
            self.update_vol_image()
        except Exception as error:
            print(error)

    def apply_clicked(self):
        try:
            x_ldt = self.ViewControl.sld_x_ldt.text()
            y_ldt = self.ViewControl.sld_y_ldt.text()
            z_ldt = self.ViewControl.sld_z_ldt.text()
            try:
                x_ldt = round(eval(x_ldt),1)
                y_ldt = round(eval(y_ldt),1)
                z_ldt = round(eval(z_ldt),1)
                if x_ldt < -90 or x_ldt > 90 or y_ldt < -90 or y_ldt > 90 or z_ldt < -90 or z_ldt > 90:
                    print("invalid angle entered")
                    return
            except:
                print("invalid angle entered")
                return

            angles = [x_ldt,y_ldt,z_ldt]
            recon_dict = self.recon_dict
            for key in recon_dict:
                recon = recon_dict[key]
                self.recon_dict[key] = self.actions.rotate_volume(recon, angles)
            element = self.ViewControl.elem.currentText()
            self.recon = self.recon_dict[element]
            self.sld.setRange(self.recon.shape[0])
            self.update_recon_image()
            # self.update_vol_image()

        except Exception as error:
            print(error)
    def update_vol_image(self):
        idx = self.ViewControl.sld_rot_vol.value()
        try:
            self.ViewControl.sld_rot_vol.setRange(0, self.tmp_recon.shape[0])
            self.ViewControl.sld_rot_vol_ldt.setText(str(idx))
            self.ViewControl.volume_img.projView.setImage(self.tmp_recon[idx, :, :])
        except:
            print("run reconstruction first")

    def method_changed(self):
        #TODO: hide individual scroll areas not individual widgets
        # Check the actual method name instead of index to handle when some methods are not available
        current_method = self.ViewControl.method.currentText()
        
        if "cpu" in current_method.lower():
            self.ViewControl.cpu_opts.setHidden(False)
            self.ViewControl.tomocupy_opts.setHidden(True)
            self.ViewControl.pyxalign_opts.setHidden(True)
            
        elif "tomocupy" in current_method.lower():
            self.ViewControl.cpu_opts.setHidden(True)
            self.ViewControl.tomocupy_opts.setHidden(False)
            self.ViewControl.pyxalign_opts.setHidden(True)

        elif "pyxalign" in current_method.lower():
            self.ViewControl.cpu_opts.setHidden(True)
            self.ViewControl.tomocupy_opts.setHidden(True)
            self.ViewControl.pyxalign_opts.setHidden(False)

        else:
            pass
        return

    def option_checked(self, option):
        widx = self.__dict__["ViewControl"].tomocupy_opts.__dict__["line_{}".format(self.ViewControl.tomocupy_opts.line_names.index(option))].count()
        checked = self.__dict__["ViewControl"].tomocupy_opts.__dict__["line_{}".format(self.ViewControl.tomocupy_opts.line_names.index(option))].itemAt(
            widx - 1).widget().isChecked()
        return checked
    def set_option_checked(self,option, wgt):
        widx = wgt.__dict__["line_{}".format(wgt.line_names.index(option))].count()
        checked = wgt.__dict__["line_{}".format(wgt.line_names.index(option))].itemAt(widx - 1).widget().setChecked(True)
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
        rec = "tomocupy_data_rec"
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
        self.write = xrftomo.SaveOptions(self)
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.y_range = self.data.shape[2]

        self.ViewControl.elem.clear()
        for j in self.elements:
            self.ViewControl.elem.addItem(j)
            self.recon_dict[j] = np.zeros((self.y_range,self.data.shape[3],self.data.shape[3]))

        self.ViewControl.cpu_opts.__dict__["fbp-filter"].setCurrentIndex(1)
        self.set_option_checked("fbp-filter",self.ViewControl.cpu_opts)
        self.ViewControl.cpu_opts.__dict__["lamino-angle"].setText("18.25")
        self.set_option_checked("lamino-angle",self.ViewControl.cpu_opts)
        self.ViewControl.cpu_opts.__dict__["rotation-axis"].setText(str(self.data.shape[3] // 2))
        self.set_option_checked("rotation-axis",self.ViewControl.cpu_opts)

        if self.parent.tcp_installed:
            self.set_option_checked("reconstruction-type", self.ViewControl.tomocupy_opts)
            self.ViewControl.tomocupy_opts.__dict__["minus-log"].setText("False")
            self.set_option_checked("reconstruction-type", self.ViewControl.tomocupy_opts)
            self.ViewControl.tomocupy_opts.__dict__["file-name"].setText(self.h5_dir)
            self.set_option_checked("file-name", self.ViewControl.tomocupy_opts)
            self.ViewControl.tomocupy_opts.__dict__["lamino-search-width"].setText("20")
            self.set_option_checked("lamino-search-width", self.ViewControl.tomocupy_opts)
        # else:
        #     self.ViewControl.method.clear()
        #     self.ViewControl.method.addItem("lamni-fbp(cpu)")

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
        self.sld.setRange(0, self.data.shape[2])
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
        self.update_recon_dict(recon)

    def circular_mask_params(self):
        self.recon = self.actions.circular_mask(self.recon)
        self.update_recon_image()
        self.update_recon_dict(self.recon)

    def set_thresh_params(self):
        threshold = float(self.ViewControl.lThresh.text())
        self.recon = self.actions.setThreshold(threshold,self.recon)
        self.update_recon_image()
        self.update_recon_dict(self.recon)

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
        print("DEBUG: entering LaminographyWidget.reconstruct_params")

        elements = [self.ViewControl.elem.currentIndex()]
        method_name = self.ViewControl.method.currentText()
        thetas = self.thetas

        parent_dir = self.h5_dir
        data = self.data.copy()
        recon_dict = self.recon_dict.copy()

        if self.ViewControl.recon_save.isChecked():
            try: #promps for directory and subdir folder
                save_path = QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
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
            num_elements = self.ViewControl.elem.count()
            elements = [i for i in range(num_elements)]


        for element_idx in elements:
            element = self.parent.elements[element_idx]
            self.ViewControl.elem.setCurrentIndex(element_idx)  # required to properly update recon_dict
            empty_recon = np.zeros((data.shape[2], data.shape[3], data.shape[3]), dtype=np.float32)  # empty array of size [y, x,x]
            recon_dict[element] = empty_recon
            print("running reconstruction for:", element)
            if "cpu" in method_name.lower():
                lami_angle = 90 - eval(self.ViewControl.cpu_opts.__dict__["lamino-angle"].text())
                center_axis = eval(self.ViewControl.cpu_opts.__dict__["rotation-axis"].text())
                # Note: method parameter might be used by reconstruct_cpu for algo selection
                method_idx = 0  # CPU method
                recon = self.actions.reconstruct_cpu(data, element_idx, element, lami_angle, center_axis, method_idx, thetas, parent_dir=parent_dir)
                recon_dict[element] = np.array(recon)
                self.recon = np.array(recon)
            elif "tomocupy" in method_name.lower():
                if not self.check_savepath_exists():
                    print("save path invalid or insufficient permissions")
                    return
                element = self.parent.elements[element_idx]
                command_string = self.get_command_string(element)
                recon = self.actions.reconstruct_gpu(data, element_idx, element, thetas, parent_dir=parent_dir, command_string=command_string)
                recon_dict[element] = np.array(recon)
                self.recon = np.array(recon)                
                if recon is None:
                    return

            elif "pyxalign" in method_name.lower():
                # Temporary debug stop to ensure this branch is reached during debugging

                scan_numbers = [i.split("_")[1].split(".")[0] for i in self.parent.fnames]
                elements = self.parent.elements
                data_dict = {}
                primary_element = self.parent.elements[element_idx]
                for element in elements:
                    data_dict[element] = data[elements.index(element)]
                    #run_it(lamino_angle, results_folder, center_of_rotation, xrf_array_dict, scan_numbers, thetas, xrf_standard_data_dict, primary_channel
                results_folder = self.h5_dir + "/pyxalign_results"
                center = [data.shape[2] // 2, data.shape[3] // 2]
                file_paths = self.parent.fileTableWidget.fileTableModel.getAllFiles()
                recons, projections, shifts = self.actions.run_pyxalign(lamino_angle=20, results_folder=results_folder, center_of_rotation=center, xrf_array_dict=data_dict, scan_numbers=scan_numbers, thetas=thetas, primary_channel=primary_element, file_paths=file_paths)
                # recon_dict = recons
                # recon = recon_dict[primary_element]
                # self.recon = np.array(recon)
                # self.parent.update_data(data)
                return


            else:
                print(f"Invalid or unrecognized method: {method_name}")
                return
            if self.ViewControl.recon_save.isChecked():
                rec = {element: recon}
                self.writer.save_recon_stack(rec, savedir=save_path)



        self.update_recon_image()               #get single image from self.recon
        self.update_recon_dict(self.recon)      #put self.recon into self.recon_dict[element]
        self.reconChangedSig.emit(self.recon)   #signals to recon tab to update recon image
        self.reconArrChangedSig.emit(recon_dict) #signls to recon tab to update recon image
        return
    
    def reset_recons(self):
        elements = self.parent.elements
        for key in elements:
            self.recon_dict[key] = np.zeros_like(self.recon)
        self.recon = np.zeros_like(self.recon)
    def get_command_string(self, element):
        options = []
        values = []
        command = "tomocupy recon_steps"

        for line in self.ViewControl.tomocupy_opts.line_names:
            line_object = self.ViewControl.tomocupy_opts.__dict__[line]
            if self.option_checked(line):
                options.append(line)
                command += " --{}".format(line)
                if isinstance(line_object, QComboBox):
                    value = line_object.currentText()
                    values.append(value)
                    command += " {}".format(value)
                elif isinstance(line_object, QLineEdit):
                    value = line_object.text()
                    values.append(value)
                    command += " {}".format(value)
                if line == "file-name":
                    #TODO: full path is not specified here.
                    path = self.ViewControl.tomocupy_opts.__dict__["file-name"].text()
                    command += " "+path + "/tomocupy_data/{}.h5".format(element)
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