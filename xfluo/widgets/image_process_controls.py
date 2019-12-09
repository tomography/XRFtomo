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
        button33size = 78.3
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

        # self.normalizeBtn = QtWidgets.QPushButton("Normalize")
        # self.normalizeBtn.setFixedWidth(button33size)
        self.cropBtn = QtWidgets.QPushButton("Crop")
        self.cropBtn.setFixedWidth(button33size)
        self.captureBackground = QtWidgets.QPushButton("Copy Bg")
        self.captureBackground.setFixedWidth(button33size)
        self.setBackground = QtWidgets.QPushButton("Set Bg")
        self.setBackground.setFixedWidth(button33size)
        self.deleteProjection = QtWidgets.QPushButton("remove img")
        self.deleteProjection.setFixedWidth(button2size)
        # self.hist_equalize = QtWidgets.QPushButton("Equalize")
        # self.hist_equalize.setFixedWidth(button33size)
        self.rm_hotspot = QtWidgets.QPushButton("Remove hs")
        self.rm_hotspot.setFixedWidth(button2size)
        self.Equalize = QtWidgets.QPushButton("Equalize")
        self.Equalize.setFixedWidth(button33size)
        self.center = QtWidgets.QPushButton("Find center")
        self.center.setFixedWidth(button33size)
        self.rot_axis = QtWidgets.QPushButton("Set rot. axis")
        self.rot_axis.setFixedWidth(button33size)


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
        # hb10.addWidget(self.normalizeBtn)
        # hb10.addWidget(self.hist_equalize)
        hb10.addWidget(self.Equalize)
        hb10.addWidget(self.center)
        hb10.addWidget(self.rot_axis)


        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(self.cropBtn)
        hb12.addWidget(self.captureBackground)
        hb12.addWidget(self.setBackground)

        hb13 = QtWidgets.QHBoxLayout()
        hb13.addWidget(self.deleteProjection)
        hb13.addWidget(self.rm_hotspot)

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
        # vb4.addLayout(hb14)

        vb5 = QtWidgets.QVBoxLayout()
        vb5.addWidget(self.combo1)
        vb5.addWidget(self.combo2)
        vb5.addLayout(vb1)
        vb5.addLayout(vb4)
        vb5.addLayout(vb2)

        self.setLayout(vb5)


        #__________Popup window for center-find button__________   

        self.center_parameters = QtWidgets.QWidget()
        self.center_parameters.resize(275,300)
        self.center_parameters.setWindowTitle('center-finiding options')

        method = ["tomopy center-find", "Everett's center-find"]
        self.options = QtWidgets.QComboBox()
        self.options.setFixedWidth(button1size)

        self.move2center = QtWidgets.QPushButton("Move to center")
        self.move2center.setFixedWidth(button1size)

        for j in method:
            self.options.addItem(j)

        self.stack1 = QtWidgets.QWidget()
        self.stack2 = QtWidgets.QWidget()

        self.stack1UI()
        self.stack2UI()

        self.Stack = QtWidgets.QStackedWidget (self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.options)
        vbox.addWidget(self.Stack)
        vbox.addWidget(self.move2center)

        self.center_parameters.setLayout(vbox)
        self.options.currentIndexChanged.connect(self.display)

    def stack1UI(self):
        button1size = 250       #long button (1 column)
        button2size = 122.5     #mid button (2 column)
        button33size = 78.3
        button3size = 73.3      #small button (almost third)
        button4size = 58.75     #textbox size (less than a third)

        #options for tomopy center-finding algorithm
        slice_label = QtWidgets.QLabel("slice index")
        slice_label.setFixedWidth(button2size)
        self.slice_textbox = QtWidgets.QLineEdit("-1")
        self.slice_textbox.setFixedWidth(button2size)
        self.slice_textbox.returnPressed.connect(self.validate_parameters)

        init_label = QtWidgets.QLabel("init. guess for center")
        init_label.setFixedWidth(button2size)
        self.init_textbox = QtWidgets.QLineEdit(str("-1"))
        self.init_textbox.setFixedWidth(button2size)
        self.init_textbox.returnPressed.connect(self.validate_parameters)

        tol_label = QtWidgets.QLabel("sub-pix accuracy")
        tol_label.setFixedWidth(button2size)
        self.tol_textbox = QtWidgets.QLineEdit("0.5")
        self.tol_textbox.setFixedWidth(button2size)
        self.tol_textbox.returnPressed.connect(self.validate_parameters)

        self.mask_checkbox =QtWidgets.QCheckBox("mask")
        self.mask_checkbox.setChecked(False)
        self.mask_checkbox.setFixedWidth(button2size)
        self.mask_checkbox.stateChanged.connect(self.mask_enable)

        ratio_label = QtWidgets.QLabel("circular mask : recon. edge")
        ratio_label.setFixedWidth(button2size)
        self.ratio_textbox = QtWidgets.QLineEdit("1")
        self.ratio_textbox.setFixedWidth(button2size)
        self.ratio_textbox.returnPressed.connect(self.validate_parameters)

        self.find_center_1 = QtWidgets.QPushButton("Find rotation axis")
        self.find_center_1.setFixedWidth(button2size)
        self.center_1 = QtWidgets.QLabel("center: 0")
        self.center_1.setFixedWidth(button2size)

        hb01 = QtWidgets.QHBoxLayout()
        hb01.addWidget(slice_label)
        hb01.addWidget(self.slice_textbox)

        hb02 = QtWidgets.QHBoxLayout()
        hb02.addWidget(init_label)
        hb02.addWidget(self.init_textbox)

        hb03 = QtWidgets.QHBoxLayout()
        hb03.addWidget(tol_label)
        hb03.addWidget(self.tol_textbox)

        hb04 = QtWidgets.QHBoxLayout()
        hb04.addWidget(self.mask_checkbox)
        hb04.setAlignment(QtCore.Qt.AlignLeft)

        hb05 = QtWidgets.QHBoxLayout()
        hb05.addWidget(ratio_label)
        hb05.addWidget(self.ratio_textbox)

        hb06 = QtWidgets.QHBoxLayout()
        hb06.addWidget(self.find_center_1)
        hb06.addWidget(self.center_1)

        vb00 = QtWidgets.QVBoxLayout()
        vb00.addLayout(hb01)
        vb00.addLayout(hb02)
        vb00.addLayout(hb03)
        vb00.addLayout(hb04)
        vb00.addLayout(hb05)
        vb00.addLayout(hb06)

        self.stack1.setLayout(vb00)

    def stack2UI(self):
        button1size = 250       #long button (1 column)
        button2size = 122.5     #mid button (2 column)
        button33size = 78.3
        button3size = 73.3      #small button (almost third)
        button4size = 58.75     #textbox size (less than a third)

        modes = ["Mean","Median", "Local"]
        self.ave_mode = QtWidgets.QComboBox()
        self.ave_mode.setFixedWidth(button1size)

        for j in modes:
            self.ave_mode.addItem(j)

        limit_label = QtWidgets.QLabel("limit")
        limit_label.setFixedWidth(button2size)
        self.limit_textbox = QtWidgets.QLineEdit("-1")
        self.limit_textbox.setFixedWidth(button2size)
        self.limit_textbox.returnPressed.connect(self.validate_parameters)

        self.find_center_2 = QtWidgets.QPushButton("Find rotation axis.")
        self.find_center_2.setFixedWidth(button2size)
        self.center_2 = QtWidgets.QLabel("center: 0")
        self.center_2.setFixedWidth(button2size)

        hb11 = QtWidgets.QHBoxLayout()
        hb11.addWidget(limit_label)
        hb11.addWidget(self.limit_textbox)

        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(self.find_center_2)
        hb12.addWidget(self.center_2)

        vb10 = QtWidgets.QVBoxLayout()
        vb10.addLayout(hb11)
        vb10.addLayout(hb12)

        self.stack2.setLayout(vb10)

    def display(self,i):
        self.Stack.setCurrentIndex(i)


    def validate_parameters(self, init_center = None):
        valid = True
        if init_center == None:
            pass
        else:
            self.init_textbox.setText(str(init_center))
            return

        layout_stack = self.options.currentIndex()
        if layout_stack == 0: 

            try: #check slice index value
                slice_index = self.slice_textbox.text()
                if slice_index == "":
                    self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    slice_index = int(self.slice_textbox.text())
                    if slice_index%1 == 0 and slice_index >= 0:
                        slice_index = int(slice_index)
                        self.slice_textbox.setText(str(slice_index))
                        self.slice_textbox.setStyleSheet('* {background-color: }')
                    elif slice_index%1 != 0:
                        self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
                    else:
                        self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
            
            try: #check initial guess
                init_center = self.init_textbox.text()
                if init_center == "":
                    self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    init_center = int(self.init_textbox.text())
                    if init_center%1 == 0 and init_center >= 0:
                        init_center = int(init_center)
                        self.init_textbox.setText(str(init_center))
                        self.init_textbox.setStyleSheet('* {background-color: }')
                    elif init_center%1 != 0:
                        self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
                    else:
                        self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

            try: #check tolerance
                tol = self.tol_textbox.text()
                if tol == "":
                    self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    tol = float(self.tol_textbox.text())
                    if tol > 0:
                        tol = float(tol)
                        self.tol_textbox.setText(str(tol))
                        self.tol_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

            try: #check ratio
                mask_enabled = self.mask_checkbox.isChecked()
                ratio = self.ratio_textbox.text()
                if ratio == "" and mask_enabled:
                    self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    ratio = float(self.ratio_textbox.text())
                    if ratio > 0 and ratio <=1 and mask_enabled:
                        self.ratio_textbox.setText(str(ratio))
                        self.ratio_textbox.setStyleSheet('* {background-color: }')
                    elif not mask_enabled:
                        self.ratio_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        if layout_stack == 1:

            try: #check iters value
                limit = self.limit_textbox.text()
                if limit == "":
                    self.limit_textbox.setStyleSheet('* {background-color: }')
                else:
                    limit = float(self.limit_textbox.text())
                    if limit > 0:
                        self.limit_textbox.setText(str(limit))
                        self.limit_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.limit_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.limit_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        return valid

    def mask_enable(self):
        checked = self.mask_checkbox.isChecked()
        if checked:
            self.ratio_textbox.setEnabled(True)
        else:
            self.ratio_textbox.setEnabled(False)

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


