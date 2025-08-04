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
        # BREAKPOINT TEST: This should definitely stop
        print("DEBUG: LaminographyControlsWidget.__init__ called")
        # import pdb; pdb.set_trace()  # Uncomment to force breakpoint
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)

        self.elem = QComboBox(self)
        self.elem.setFixedWidth(button1size)
        self.method = QComboBox(self)
        self.method.setFixedWidth(button1size)


        

        self.populate_scroll_area()
        vb = QVBoxLayout()
        vb.addWidget(self.elem)
        vb.addWidget(self.method)
        vb.addWidget(self.lami_scroll)
        self.setLayout(vb)
        self.setMaximumWidth(290)
        self.rotate_volume_area()

    def populate_scroll_area(self):

        item_dict = {}
        item_dict["browse"] = [["label","path"], "location where data is stored", None, ""]
        item_dict["generate"] = [["label","button"], "generate folder structure in data path", None, None]
        item_dict["show_ops"] = [["checkbox"], "show additional options", None, False]
        item_dict["fbp-filter"] = [["label","dropdown"], "filter choice", ["ramp", "shepp"], "shepp"]
        item_dict["rotation-axis"] = [["label","linedit"], "rotation axis given by x-position", None, ""]
        item_dict["lamino-angle"] = [["label","linedit"], "laminography tilt angle", None, "18.25"]

        item_dict2 = {}
        item_dict2["recon_all"] = [["checkbox"], "reconstruct all loaded elements", None, False]
        item_dict2["recon_save"] = [["checkbox"], "reconstruct and save simultaneously", None, False]
        item_dict2["reconstruct"] = [["button"], "run reconstruction", None, None]
        item_dict2["recon_stats"] = [["button"], "show reconstruction statistics", None, None]
        item_dict2["rm_hotspot"] = [["button"], "laminography tilt angle", None, None]
        item_dict2["rotate_volume"] = [["button"], "opens tool in separate window to rotate reconstructed volume", None, None]
        item_dict2["circular_mask"] = [["button"], "remove volume outside cylinder", None, None]

     
        self.method.clear()
        self.method.addItems(["lamni-fbp(cpu)"])
        self.method.setCurrentIndex(0)
        widget_dict = item_dict | item_dict2

        self.lami_scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.lami_scroll.setWidgetResizable(True)
        #TODO: the dictionary pop function maks self forget that lami_scroll exists. fix
        vb_lami = self.create_widgets(widget_dict)
        self.lami_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_lami.setSpacing(0)
        vb_lami.setContentsMargins(0, 0, 0, 0)
        self.lami_scroll_widget.setLayout(vb_lami)
        self.lami_scroll.setWidget(self.lami_scroll_widget)

        self.show_ops.setCheckable(True)
        self.show_ops.setChecked(False)
        self.recon_all.setChecked(False)
        return

    def create_widgets(self,item_dict):
        widgetsizes = [240, 115, 50]
        vb_lami = QVBoxLayout()
        self.num_lines= len(item_dict.keys())
        self.line_names = []
        for i, key in enumerate(item_dict.keys()):
            widget_items = item_dict[key][0]
            attrs = item_dict[key]
            widgetsize = widgetsizes[len(widget_items)-1]

            self.line_names.append(key)

            line_num = "line_{}".format(i)
            setattr(self, line_num, QHBoxLayout())
            line = self.__dict__[line_num]

            for widget in widget_items:
                #TODO: add line number and extra button to each line
                if widget == "dropdown":
                    setattr(self, key, QComboBox())
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    options = attrs[2]
                    default = attrs[3]
                    for option in options:
                        object.addItem(option)
                    # Check if default value exists in options list
                    if default in options:
                        idx = options.index(default)
                        object.setCurrentIndex(idx)
                    else:
                        # If default is not in options, set to first option or 0
                        object.setCurrentIndex(0)
                    line.addWidget(object)

                elif widget == "label":
                    name = key+"_lbl"
                    setattr(self, name, QLabel())
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    object.setText(key)
                    line.addWidget(object)

                elif widget == "linedit":
                    setattr(self, key, QLineEdit())
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    line.addWidget(object)

                elif widget == "checkbox":
                    setattr(self, key, QCheckBox(attrs[1]))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setChecked(attrs[3])
                    line.addWidget(object)

                elif widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    line.addWidget(object)

                elif widget == "file":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    object.clicked.connect(self.get_file)
                    line.addWidget(object)

                elif widget == "path":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    object.clicked.connect(self.get_path)
                    line.addWidget(object)
                else:
                    print("invalid option")

            button_name = "btn_{}".format(i)
            setattr(self, button_name, QPushButton("+"))
            line_btn = self.__dict__[button_name]
            line_btn.setCheckable(True)
            line_btn.setObjectName(str(button_name))
            line_btn.setFixedWidth(25)
            line.addWidget(line_btn)
            vb_lami.addLayout(line)
        return vb_lami

    def get_file(self):
        try:
            sender = self.sender
            file = QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
            sender().setText(file)
        except:
            return

    def get_path(self):
        sender = self.sender
        path = QFileDialog.getExistingDirectory(self, "Open Directory", QtCore.QDir.currentPath())
        sender().setText(path)


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
