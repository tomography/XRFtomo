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

class ImageProcessControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ImageProcessControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.xSize = 10
        self.ySize = 10
        button1size = 270       #long button (1 column)
        button2size = 142.5     #mid button (2 column)
        button33size = 98.3
        button3size = 93.3      #small button (almost third)
        button4size = 78.75     #textbox size (less than a third)

        self.combo1 = QtWidgets.QComboBox()
        self.combo1.setFixedWidth(button1size)
        self.combo2 = QtWidgets.QComboBox()
        self.combo2.setFixedWidth(button1size)
        # self.combo3 = QtWidgets.QComboBox(self)
        # self.combo3.setFixedWidth(button2size)

        self.padBtn = QtWidgets.QPushButton("pad edges")
        self.padBtn.setFixedWidth(button2size)
        self.cropBtn = QtWidgets.QPushButton("Crop")
        self.cropBtn.setFixedWidth(button2size)
        # self.filter_center = QtWidgets.QPushButton("filter")
        # self.filter_center.setFixedWidth(button2size)
        # self.setBackground = QtWidgets.QPushButton("Paste")
        # self.setBackground.setFixedWidth(button2size)
        self.deleteProjection = QtWidgets.QPushButton("remove img")
        self.deleteProjection.setFixedWidth(button2size)
        self.rm_hotspot = QtWidgets.QPushButton("Remove hotspot")
        self.rm_hotspot.setFixedWidth(button2size)
        self.downsample = QtWidgets.QPushButton("downsample")
        self.downsample.setFixedWidth(button2size)
        self.invert = QtWidgets.QPushButton("invert values")
        self.invert.setFixedWidth(button2size)

        self.invert.setVisible(False)

        hb10 = QtWidgets.QHBoxLayout()
        hb10.addWidget(self.downsample)
        hb10.addWidget(self.invert)

        hb11 = QtWidgets.QHBoxLayout()
        hb11.addWidget(self.cropBtn)
        hb11.addWidget(self.padBtn)

        # hb12 = QtWidgets.QHBoxLayout()
        # hb12.addWidget(self.filter_center)
        # hb12.addWidget(self.setBackground)

        hb13 = QtWidgets.QHBoxLayout()
        hb13.addWidget(self.deleteProjection)
        hb13.addWidget(self.rm_hotspot)

        vb1 = QtWidgets.QVBoxLayout()
        # vb1.addLayout(hb1)
        # vb1.addLayout(hb2)

        # vb2 = QtWidgets.QVBoxLayout()
        # vb2.addLayout(hb3)
        # vb2.addLayout(hb4)
        # vb2.addLayout(hb5)

        vb4 = QtWidgets.QVBoxLayout()
        vb4.addLayout(hb10)
        vb4.addLayout(hb11)
        # vb4.addLayout(hb12)
        vb4.addLayout(hb13)

        vb5 = QtWidgets.QVBoxLayout()
        vb5.addWidget(self.combo1)
        vb5.addWidget(self.combo2)
        vb5.addLayout(vb1)
        vb5.addLayout(vb4)
        # vb5.addLayout(vb2)
        self.setLayout(vb5)

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

