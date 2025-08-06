# #########################################################################
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


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import subprocess
import xrftomo

class LaminographyControlsWidget(QWidget):

    def __init__(self):
        super(LaminographyControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.button1size = 450       #long button (1 column)

        self.elem = QComboBox(self)
        self.elem.setFixedWidth(self.button1size)
        self.method = QComboBox(self)
        self.method.setFixedWidth(self.button1size)
        self.method.clear()
        self.method.addItem("lamni-fbp(cpu)")
        self.method.setCurrentIndex(0)
        self.recon_all = QCheckBox(self)
        self.recon_all.setText("reconstruct all")
        self.recon_all.setToolTip("reconstruct all loaded elements")
        self.recon_all.setChecked(False)
        self.recon_save = QCheckBox(self)
        self.recon_save.setToolTip("reconstruct and save simultaneously")
        self.recon_save.setChecked(False)
        self.recon_save.setText("reconstruct and save")
        self.reconstruct = QPushButton("reconstruct")
        self.recon_stats = QPushButton("recon stats")
        self.rm_hotspot = QPushButton("remove hotspot")
        self.rotate_volume = QPushButton("rotate volume")
        self.circular_mask = QPushButton("circular mask")


        self.cpu_opts = xrftomo.LaminographyCPU(self)
        self.tomocupy_opts = xrftomo.LaminographyTomocupy(self)
        self.pyxalign_opts = xrftomo.OptionsWidget()
        if self.tomocupy_opts is not None: 
            self.method.addItem("tomocupy(gpu)")
        if self.pyxalign_opts is not None:
            self.method.addItem("pyxalign(gpu)")
        vb = QVBoxLayout()
        vb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        vb.addWidget(self.elem)
        vb.addWidget(self.method)
        vb.addWidget(self.cpu_opts)
        vb.addWidget(self.tomocupy_opts)
        vb.addWidget(self.pyxalign_opts)
        vb.addWidget(self.recon_all)
        vb.addWidget(self.recon_save)
        vb.addWidget(self.reconstruct)
        vb.addWidget(self.recon_stats)
        vb.addWidget(self.rm_hotspot)
        vb.addWidget(self.circular_mask)
        self.setLayout(vb)
        self.setMaximumWidth(self.button1size)
        self.rotate_volume_area()

    def rotate_volume_area(self):
        #__________Popup window for rotate volume button__________
        self.rotate_volume_window = QtWidgets.QWidget()
        self.rotate_volume_window.resize(500,400)
        self.rotate_volume_window.setWindowTitle('rotate volume tool')
        widgetsizes = [300, 135, 75]
        volume_dict = {}
        volume_dict["volume_img"] = [["view"], "",None, None]
        volume_dict["sld_rot_vol"] = [["label", "slider", "linedit"], "current cross section",None, "0"]
        volume_dict["sld_x"] = [["label", "slider", "linedit"], "change x angle",None, "0"]
        volume_dict["sld_y"] = [["label", "slider", "linedit"], "change y angle.", None, "0"]
        volume_dict["sld_z"] = [["label", "slider", "linedit"], "change z angle", None, "0"]
        volume_dict["reset"] = [["button"], "reset view", None, None]
        volume_dict["apply"] = [["button"], "reset view", None, None]

        volume_v_box = QVBoxLayout()
        for i, key in enumerate(volume_dict.keys()):
            widget_items = volume_dict[key][0]
            attrs = volume_dict[key]
            widgetsize = widgetsizes[len(widget_items) - 1]

            line_num = "volume_line_{}".format(i)
            setattr(self, line_num, QHBoxLayout())
            volume_line = self.__dict__[line_num]

            for widget in widget_items:
                if widget == "view":
                    setattr(self, key, xrftomo.ReconView(self))
                    object = self.__dict__[key]
                    volume_line.addWidget(object)
                if widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    volume_line.addWidget(object)
                elif widget == "slider":
                    setattr(self, key, QSlider(QtCore.Qt.Horizontal, self))
                    object = self.__dict__[key]
                    object.setRange(-900, 900)
                    volume_line.addWidget(object)
                elif widget == "linedit":
                    name = key+"_ldt"
                    setattr(self, name, QLineEdit(attrs[3]))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    volume_line.addWidget(object)
                elif widget == "label":
                    name = key + "_lbl"
                    setattr(self, name, QLabel(key))
                    object = self.__dict__[name]
                    object.setFixedWidth(75)
                    object.setToolTip(attrs[1])
                    volume_line.addWidget(object)
            volume_v_box.addLayout(volume_line)

        volume_v_box.setSpacing(0)
        volume_v_box.setContentsMargins(0, 0, 0, 0)
        self.rotate_volume_window.setLayout(volume_v_box)
