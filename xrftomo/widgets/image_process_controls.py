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


from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *

class ImageProcessControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ImageProcessControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.xSize = 10
        self.ySize = 10
        button1size = 270       #long button (1 column)
        button2size = 143     #mid button (2 column)
        button33size = 98
        button3size = 93      #small button (almost third)
        button4size = 79     #textbox size (less than a third)

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll.setWidgetResizable(True)
        self.populate_scroll_area()

        self.combo1 = QtWidgets.QComboBox()
        self.combo1.setFixedWidth(button1size)
        self.combo2 = QtWidgets.QComboBox()
        self.combo2.setFixedWidth(button1size)
        vb1 = QtWidgets.QVBoxLayout() #spacer
        vb5 = QtWidgets.QVBoxLayout()
        vb5.addWidget(self.combo1)
        vb5.addWidget(self.combo2)
        vb5.addLayout(vb1)
        vb5.addWidget(self.scroll)
        self.setLayout(vb5)
        self.setMaximumWidth(290)


        #__________Popup window for reshape button__________
        self.reshape_options = QtWidgets.QWidget()
        self.reshape_options.resize(275,300)
        self.reshape_options.setWindowTitle('data upsample settings')

        xUpsample_label = QtWidgets.QLabel("x upsample multiplier")
        yUpsample_label = QtWidgets.QLabel("y upsample multiplier ")

        self.xUpsample_text = QtWidgets.QLineEdit("1")
        self.yUpsample_text = QtWidgets.QLineEdit("1")
        self.run_reshape = QtWidgets.QPushButton("reshape")

        hb21 = QtWidgets.QHBoxLayout()
        hb21.addWidget(xUpsample_label)
        hb21.addWidget(self.xUpsample_text)

        hb22 = QtWidgets.QHBoxLayout()
        hb22.addWidget(yUpsample_label)
        hb22.addWidget(self.yUpsample_text)

        vb20 = QtWidgets.QVBoxLayout()
        vb20.addLayout(hb21)
        vb20.addLayout(hb22)
        vb20.addWidget(self.run_reshape)

        self.reshape_options.setLayout(vb20)

        #__________Popup window for pading button__________
        self.padding_options = QtWidgets.QWidget()
        self.padding_options.resize(275,300)
        self.padding_options.setWindowTitle('padding options')

        pad_x_label = QtWidgets.QLabel("x padding")
        pad_y_label = QtWidgets.QLabel("y padding")
        clip_label =  QtWidgets.QLabel("data edge clip amount")

        self.pad_x = QtWidgets.QLineEdit("0")
        self.pad_y = QtWidgets.QLineEdit("0")
        self.clip_x = QtWidgets.QLineEdit("0")
        self.run_padding = QtWidgets.QPushButton("apply padding")

        hb31 = QtWidgets.QHBoxLayout()
        hb31.addWidget(pad_x_label)
        hb31.addWidget(self.pad_x)

        hb32 = QtWidgets.QHBoxLayout()
        hb32.addWidget(pad_y_label)
        hb32.addWidget(self.pad_y)

        hb33 = QtWidgets.QHBoxLayout()
        hb33.addWidget(clip_label)
        hb33.addWidget(self.clip_x)

        vb30 = QtWidgets.QVBoxLayout()
        vb30.addLayout(hb31)
        vb30.addLayout(hb32)
        vb30.addLayout(hb33)
        vb30.addWidget(self.run_padding)

        self.padding_options.setLayout(vb30)


    def populate_scroll_area(self):
        widgetsizes = [240,115, 50]
        item_dict = {} #[type(button, file, path, dropdown), descriptions[idx], choices[idx],defaults[idx]]
        item_dict["downsample"] = [["button"], "downsample by 2x", None, None]
        item_dict["invert"] = [["button"], "invert 2d array", None, None]
        item_dict["cropBtn"] = [["button"], "crop to ROI", None, None]
        item_dict["padBtn"] = [["button"], "add 0 pixels ro edge of image", None, None]
        item_dict["deleteProjection"] = [["button"], "exclude form analysis", None, None]
        item_dict["rm_hotspot"] = [["button"], "remove hotspot", None, None]
        item_dict["normalize"] = [["button"], "normalize from sinogram", None, None]
        item_dict["mask"] = [["button","linedit"], "binary thresholding for alignment purposes", None, None]

        v_box = QVBoxLayout()
        for i, key in enumerate(item_dict.keys()):
            widget_items = item_dict[key][0]
            attrs = item_dict[key]
            widgetsize = widgetsizes[len(widget_items)-1]

            line_num = "line_{}".format(i)
            setattr(self, line_num, QHBoxLayout())
            line = self.__dict__[line_num]

            for widget in widget_items:
                if widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    line.addWidget(object)

                elif widget == "linedit":
                    name = key+"_lndt"
                    setattr(self, name, QLineEdit("10"))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    line.addWidget(object)
            v_box.addLayout(line)

        self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        v_box.setSpacing(0)
        v_box.setContentsMargins(0, 0, 0, 0)
        self.scroll_widget.setLayout(v_box)
        self.scroll.setWidget(self.scroll_widget)
        return

    def validate_reshape_parameters(self):
        valid = True
        try: #check value >1 and is int
            x_upsample = self.xUpsample_text.text()
            if x_upsample == "":
                self.xUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                x_upsample = float(self.xUpsample_text.text())
                if x_upsample%1 == 0 and x_upsample >= 1:
                    x_upsample = int(x_upsample)
                    self.xUpsample_text.setText(str(x_upsample))
                    self.xUpsample_text.setStyleSheet('* {background-color: }')
                elif x_upsample%1 != 0:
                    self.xUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    self.xUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.xUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')

        try: #check value >1 and is int
            y_upsample = self.yUpsample_text.text()
            if y_upsample == "":
                self.yUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                y_upsample = float(self.yUpsample_text.text())
                if y_upsample%1 == 0 and y_upsample >= 1:
                    y_upsample = int(y_upsample)
                    self.yUpsample_text.setText(str(y_upsample))
                    self.yUpsample_text.setStyleSheet('* {background-color: }')
                elif y_upsample%1 != 0:
                    self.yUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    self.yUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.yUpsample_text.setStyleSheet('* {background-color: rgb(255,200,200) }')

        return valid


    def validate_padding_parameters(self):
        valid = True
        try: #check value >1 and is int
            pad_x = self.pad_x.text()
            if pad_x == "":
                self.pad_x.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                pad_x = float(self.pad_x.text())
                if pad_x%1 == 0 and pad_x >= 0:
                    pad_x = int(pad_x)
                    self.pad_x.setText(str(pad_x))
                    self.pad_x.setStyleSheet('* {background-color: }')
                elif pad_x%1 != 0:
                    self.pad_x.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    self.pad_x.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')
        try: #check y_pad value
            pad_y = self.pad_y.text()
            if pad_y == "":
                self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                pad_y = float(self.pad_y.text())
                if pad_y%1 == 0 and pad_y >= 0:
                    pad_y = int(pad_y)
                    self.pad_y.setText(str(pad_y))
                    self.pad_y.setStyleSheet('* {background-color: }')
                elif pad_y%1 != 0:
                    self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')

        try: #check y_pad value
            clip_x = self.clip_x.text()
            if pad_y == "":
                self.clip_x.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                clip_x = float(self.clip_x.text())
                if clip_x%1 == 0 and clip_x >= 0:
                    clip_x = int(clip_x)
                    self.clip_x.setText(str(clip_x))
                    self.clip_x.setStyleSheet('* {background-color: }')
                elif clip_x%1 != 0:
                    self.clip_x.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    self.pad_y.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.clip_x.setStyleSheet('* {background-color: rgb(255,200,200) }')


        return valid

