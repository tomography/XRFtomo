# #########################################################################
# Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2018. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################


from PyQt5 import QtWidgets, QtCore

class ImageProcessControlsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ImageProcessControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.xSize = 10
        self.ySize = 10
        button1size = 250       #long button (1 column)
        button2size = 122.5     #mid button (2 column)
        button3size = 73.3      #small button (almost third)
        button4size = 58.75     #textbox size (less than a third)

        self.combo1 = QtWidgets.QComboBox()
        self.combo1.setFixedWidth(button1size)
        self.combo2 = QtWidgets.QComboBox()
        self.combo2.setFixedWidth(button1size)
        self.combo3 = QtWidgets.QComboBox(self)
        self.combo3.setFixedWidth(button2size)

        self.xSizeLbl = QtWidgets.QLabel("x Size")
        self.xSizeLbl.setFixedWidth(button4size)
        self.ySizeLbl = QtWidgets.QLabel("y Size")
        self.ySizeLbl.setFixedWidth(button4size)
        self.xSizeTxt = QtWidgets.QLineEdit(str(self.xSize))
        self.xSizeTxt.setFixedWidth(button4size)
        self.xSizeTxt.textChanged.connect(self.xTxtChange)
        self.ySizeTxt = QtWidgets.QLineEdit(str(self.ySize))
        self.ySizeTxt.setFixedWidth(button4size)
        self.ySizeTxt.textChanged.connect(self.yTxtChange)

        self.aspectChkbx = QtWidgets.QCheckBox("Aspect ratio locked")

        self.x_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.x_sld.setFixedWidth(button2size)
        self.x_sld.setValue(self.xSize)
        self.x_sld.setRange(2, 10)
        self.x_sld.valueChanged.connect(self.xSldChange)
        self.y_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.y_sld.setFixedWidth(button2size)
        self.y_sld.setValue(self.xSize)
        self.y_sld.setRange(2, 10)
        self.y_sld.valueChanged.connect(self.ySldChange)

        self.normalizeBtn = QtWidgets.QPushButton("Normalize")
        self.normalizeBtn.setFixedWidth(button2size)
        self.cropBtn = QtWidgets.QPushButton("Crop")
        self.cropBtn.setFixedWidth(button2size)
        self.captureBackground = QtWidgets.QPushButton("copy Bg")
        self.captureBackground.setFixedWidth(button2size)
        self.setBackground = QtWidgets.QPushButton("Set Bg")
        self.setBackground.setFixedWidth(button2size)
        self.deleteProjection = QtWidgets.QPushButton("Delete Frame")
        self.deleteProjection.setFixedWidth(button2size)
        self.testButton = QtWidgets.QPushButton("test btn")
        self.testButton.setFixedWidth(button2size)
        self.testButton.setVisible(False)


        for i in range(5):
            self.combo3.addItem(str(i + 1))
        self.btn1 = QtWidgets.QPushButton("fit to a line")
        self.btn1.setFixedWidth(button2size)
        self.btn2 = QtWidgets.QPushButton("fit to sine curve")
        self.btn2.setFixedWidth(button2size)
        self.btn3 = QtWidgets.QPushButton("set y")
        self.btn3.setFixedWidth(button2size)
        self.btn4 = QtWidgets.QPushButton("Clear data")
        self.btn4.setFixedWidth(button2size)
        self.lbl3 = QtWidgets.QLabel("hotspot group#")
        self.lbl3.setFixedWidth(button2size)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.xSizeLbl)
        hb1.addWidget(self.x_sld)
        hb1.addWidget(self.xSizeTxt)
        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.ySizeLbl)
        hb2.addWidget(self.y_sld)
        hb2.addWidget(self.ySizeTxt)


        hb3 = QtWidgets.QHBoxLayout()
        hb3.addWidget(self.lbl3)
        hb3.addWidget(self.combo3)
        hb4 = QtWidgets.QHBoxLayout()
        hb4.addWidget(self.btn1)
        hb4.addWidget(self.btn2)        
        hb5 = QtWidgets.QHBoxLayout()
        hb5.addWidget(self.btn3)
        hb5.addWidget(self.btn4)

        hb10 = QtWidgets.QHBoxLayout()
        hb10.addWidget(self.normalizeBtn)
        hb10.addWidget(self.cropBtn)
        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(self.captureBackground)
        hb12.addWidget(self.setBackground)
        hb13 = QtWidgets.QHBoxLayout()
        hb13.addWidget(self.deleteProjection)
        hb13.addWidget(self.testButton)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)
        vb1.addWidget(self.aspectChkbx)

        vb2 = QtWidgets.QVBoxLayout()
        vb2.addLayout(hb3)
        vb2.addLayout(hb4)
        vb2.addLayout(hb5)

        vb4 = QtWidgets.QVBoxLayout()
        vb4.addLayout(hb10)
        # vb4xSldChange.addLayout(hb11)
        vb4.addLayout(hb12)
        vb4.addLayout(hb13)

        vb5 = QtWidgets.QVBoxLayout()
        vb5.addWidget(self.combo1)
        vb5.addWidget(self.combo2)
        vb5.addLayout(vb1)
        vb5.addLayout(vb4)
        vb5.addLayout(vb2)

        # vb5.addWidget(self.histogramButton)

        self.setLayout(vb5)

    def xTxtChange(self):
        try:
            self.xSize = int(self.xSizeTxt.text())
        except ValueError:
            print('integer values only')
        self.x_sld.setValue(self.xSize)

    def yTxtChange(self):
        try:
            self.ySize = int(self.ySizeTxt.text())
        except ValueError:
            print('integer values only')
        self.y_sld.setValue(self.ySize)

    def xSldChange(self):
        self.xSize = self.x_sld.value()
        self.xSizeTxt.setText(str(self.xSize))

    def ySldChange(self):
        self.ySize = self.y_sld.value()
        self.ySizeTxt.setText(str(self.ySize))