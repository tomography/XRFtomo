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
import xrftomo
class ReconstructionControlsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ReconstructionControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)

        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.setFixedWidth(button1size)

        self.populate_scroll_area()
        self.remove_artifact_scroll_area()
        self.rotate_volume_area()

        self.middle_row_lbl.setVisible(False)
        self.middle_row_lbl.setVisible(False)
        self.beta_lbl.setVisible(False)
        self.delta_lbl.setVisible(False)
        self.lower_thresh_lbl.setVisible(False)
        self.beta.setVisible(False)
        self.delta.setVisible(False)
        self.lower_thresh.setVisible(False)

        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.combo1)
        vb.addWidget(self.recon_scroll)

        self.setLayout(vb)
        self.setMaximumWidth(290)
    def populate_scroll_area(self):
        button1size = 250       #long button (1 column)
        button2size = 115     #mid button (2 column)

        self.recon_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.recon_scroll.setWidgetResizable(True)
        item_dict = {} #[type(button, file, path, dropdown), descriptions[idx], choices[idx],defaults[idx]]
        item_dict["method"] = ["dropdown", "reconstruction methods"]
        item_dict["top_row"] = ["label", "index of top cross section to reconstruct"]
        item_dict["middle_row"] = ["label", "index of top middle cross section to reconstruct"]
        item_dict["bottom_row"] = ["label", "index of lower middle cross section to reconstruct"]
        item_dict["iterations"] = ["label", "number of reconsturction iteration"]
        item_dict["recon_all"] = ["checkbox", "reconstruct all loaded elements"]
        item_dict["recon_save"] = ["checkbox", "reconstruct and save simultaneously"]
        item_dict["beta"] = ["label", "mlem parameter"]
        item_dict["delta"] = ["label", "mlem parameter"]
        item_dict["lower_thresh"] = ["label", "cut-off display value"]
        item_dict["reconstruct"] = ["button", "run reconstruction"]
        item_dict["recon_stats"] = ["button", "show reconstruction statisticks"]
        item_dict["remove_hotspot"] = ["button", "remove hotspots from reconstruction"]
        item_dict["remove_artifact"] = ["button", "remove line artifacts"]
        item_dict["rotate_volume"] = ["button", "opens tool in separate window to rotate reconstructed volume"]


        vb_recon = QVBoxLayout()
        for key in item_dict.keys():
            widget_type = item_dict[key][0]
            attrs = item_dict[key]
            if widget_type == "dropdown":
                setattr(self, key, QComboBox())
                self.__dict__[key].setFixedWidth(button1size)
                vb_recon.addWidget(self.__dict__[key])
            elif widget_type == "label":
                line = QHBoxLayout()
                lbl = key + "_lbl"
                setattr(self, lbl, QLabel(key))
                setattr(self, key, QLineEdit(""))
                self.__dict__[lbl].setFixedWidth(button2size)
                self.__dict__[key].setFixedWidth(button2size)
                line.addWidget(self.__dict__[lbl])
                line.addWidget(self.__dict__[key])
                vb_recon.addLayout(line)
            if widget_type == "checkbox":
                setattr(self, key, QCheckBox(attrs[1]))
                self.__dict__[key].setFixedWidth(button1size)
                vb_recon.addWidget(self.__dict__[key])
            elif widget_type == "button":
                setattr(self, key, QPushButton(key))
                self.__dict__[key].setFixedWidth(button1size)
                vb_recon.addWidget(self.__dict__[key])
                self.__dict__[key].setToolTip(attrs[1])

        self.recon_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_recon.setSpacing(0)
        vb_recon.setContentsMargins(0, 0, 0, 0)
        self.recon_scroll_widget.setLayout(vb_recon)
        self.recon_scroll.setWidget(self.recon_scroll_widget)

        self.top_row.setText("0")
        self.bottom_row.setText("0")
        self.middle_row.setText("-1")
        self.iterations.setText("10")
        self.beta.setText("1")
        self.delta.setText("0.01")
        self.lower_thresh.setText("0.0")
        return

    def remove_artifact_scroll_area(self):

        #__________Popup window for PIRT button__________
        self.artifact_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.artifact_scroll.setWidgetResizable(True)
        self.artifact_parameters = QtWidgets.QWidget()
        self.artifact_parameters.resize(240,100)
        self.artifact_parameters.setWindowTitle('artifact removal parameters')
        widgetsizes = [300, 135, 75]
        artifact_dict = {}
        artifact_dict["ar_diameter"] = [["label", "linedit"], "diameter in percent of overall reconstruction width",None, "34"]
        artifact_dict["ar_threshold"] = [["label", "linedit"], "threshold used to mask line 'features' in fourier space.", None, "75"]
        artifact_dict["run_ar"] = [["button"], "run line artifact removal", None, False]

        artifact_v_box = QVBoxLayout()
        for i, key in enumerate(artifact_dict.keys()):
            widget_items = artifact_dict[key][0]
            attrs = artifact_dict[key]
            widgetsize = widgetsizes[len(widget_items) - 1]

            artifact_line_num = "artifact_line_{}".format(i)
            setattr(self, artifact_line_num, QHBoxLayout())
            artifact_line = self.__dict__[artifact_line_num]

            for widget in widget_items:
                if widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    artifact_line.addWidget(object)
                elif widget == "linedit":
                    setattr(self, key, QLineEdit(attrs[3]))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    artifact_line.addWidget(object)
                elif widget == "label":
                    name = key + "_lbl"
                    setattr(self, name, QLabel(key))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    artifact_line.addWidget(object)
            artifact_v_box.addLayout(artifact_line)

        self.artifact_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        artifact_v_box.setSpacing(0)
        artifact_v_box.setContentsMargins(0, 0, 0, 0)
        self.artifact_scroll_widget.setLayout(artifact_v_box)
        self.artifact_scroll.setWidget(self.artifact_scroll_widget)
        self.artifact_parameters.setLayout(artifact_v_box)

    def rotate_volume_area(self):

        #__________Popup window for PIRT button__________
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
                    object.setRange(-90, 90)
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
