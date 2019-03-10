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


from PyQt5 import QtWidgets

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

        self.xUpBtn = QtWidgets.QPushButton("x: +")
        self.xUpBtn.setMaximumWidth(button4size)
        self.xUpBtn.setMinimumWidth(button4size)
        self.xUpBtn.clicked.connect(self.xUp)
        self.xDownBtn = QtWidgets.QPushButton("x: -")
        self.xDownBtn.setMaximumWidth(button4size)
        self.xDownBtn.setMinimumWidth(button4size)
        self.xDownBtn.clicked.connect(self.xDown)
        self.yUpBtn = QtWidgets.QPushButton("y: +")
        self.yUpBtn.setMaximumWidth(button4size)
        self.yUpBtn.setMinimumWidth(button4size)
        self.yUpBtn.clicked.connect(self.yUp)
        self.yDownBtn = QtWidgets.QPushButton("y: -")
        self.yDownBtn.setMaximumWidth(button4size)
        self.yDownBtn.setMinimumWidth(button4size)
        self.yDownBtn.clicked.connect(self.yDown)
        # self.bgBtn = QtWidgets.QPushButton("Bg Value")
        # self.bgBtn.setMaximumWidth(button2size)
        # self.bgBtn.setMinimumWidth(button2size)
        # self.delHotspotBtn = QtWidgets.QPushButton("patch HS")
        # self.delHotspotBtn.setMaximumWidth(button2size)
        # self.delHotspotBtn.setMinimumWidth(button2size)
        self.normalizeBtn = QtWidgets.QPushButton("Normalize")
        self.normalizeBtn.setMaximumWidth(button2size)
        self.normalizeBtn.setMinimumWidth(button2size)
        self.cutBtn = QtWidgets.QPushButton("Cut")
        self.cutBtn.setMaximumWidth(button2size)
        self.cutBtn.setMinimumWidth(button2size)
        self.gaussian33Btn = QtWidgets.QPushButton("3*3 gauss")
        self.gaussian33Btn.setMaximumWidth(button2size)
        self.gaussian33Btn.setMinimumWidth(button2size)
        self.gaussian55Btn = QtWidgets.QPushButton("5*5 gauss")
        self.gaussian55Btn.setMaximumWidth(button2size)
        self.gaussian55Btn.setMinimumWidth(button2size)
        self.captureBackground = QtWidgets.QPushButton("copy Bg")
        self.captureBackground.setMaximumWidth(button2size)
        self.captureBackground.setMinimumWidth(button2size)
        self.setBackground = QtWidgets.QPushButton("Set Bg")
        self.setBackground.setMaximumWidth(button2size)
        self.setBackground.setMinimumWidth(button2size)
        self.deleteProjection = QtWidgets.QPushButton("Delete Frame")
        self.deleteProjection.setMaximumWidth(button2size)
        self.deleteProjection.setMinimumWidth(button2size)
        self.testButton = QtWidgets.QPushButton("test btn")
        self.testButton.setMaximumWidth(button2size)
        self.testButton.setMinimumWidth(button2size)

        self.xSizeLbl = QtWidgets.QLabel("x Size")
        self.xSizeLbl.setMaximumWidth(button4size)
        self.xSizeLbl.setMinimumWidth(button4size)
        self.ySizeLbl = QtWidgets.QLabel("y Size")
        self.ySizeLbl.setMaximumWidth(button4size)
        self.ySizeLbl.setMinimumWidth(button4size)
        self.xSizeTxt = QtWidgets.QLineEdit(str(self.xSize))
        self.xSizeTxt.setMaximumWidth(button4size)
        self.xSizeTxt.setMinimumWidth(button4size)
        self.ySizeTxt = QtWidgets.QLineEdit(str(self.ySize))
        self.ySizeTxt.setMaximumWidth(button4size)
        self.ySizeTxt.setMinimumWidth(button4size)
        self.combo1 = QtWidgets.QComboBox()
        self.combo1.setMaximumWidth(button1size)
        self.combo1.setMinimumWidth(button1size)
        self.combo2 = QtWidgets.QComboBox()
        self.combo2.setMaximumWidth(button1size)
        self.combo2.setMinimumWidth(button1size)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.xSizeLbl)
        hb1.addWidget(self.xUpBtn)
        hb1.addWidget(self.xDownBtn)
        hb1.addWidget(self.xSizeTxt)
        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.ySizeLbl)
        hb2.addWidget(self.yUpBtn)
        hb2.addWidget(self.yDownBtn)
        hb2.addWidget(self.ySizeTxt)

        # hb9 = QtWidgets.QHBoxLayout()
        # hb9.addWidget(self.bgBtn)
        # hb9.addWidget(self.delHotspotBtn)
        hb10 = QtWidgets.QHBoxLayout()
        hb10.addWidget(self.normalizeBtn)
        hb10.addWidget(self.cutBtn)
        hb11 = QtWidgets.QHBoxLayout()
        hb11.addWidget(self.gaussian33Btn)
        hb11.addWidget(self.gaussian55Btn)
        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(self.captureBackground)
        hb12.addWidget(self.setBackground)
        hb13 = QtWidgets.QHBoxLayout()
        hb13.addWidget(self.deleteProjection)
        hb13.addWidget(self.testButton)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)


        vb4 = QtWidgets.QVBoxLayout()
        # vb4.addLayout(hb9)
        vb4.addLayout(hb10)
        vb4.addLayout(hb11)
        vb4.addLayout(hb12)
        vb4.addLayout(hb13)

        vb5 = QtWidgets.QVBoxLayout()
        vb5.addWidget(self.combo1)
        vb5.addWidget(self.combo2)
        vb5.addLayout(vb1)
        vb5.addLayout(vb4)

        self.setLayout(vb5)

    def changeXSize(self):
        self.xSize = int(self.xSizeTxt.text())

    def changeYSize(self):
        self.ySize = int(self.ySizeTxt.text())

    def xUp(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize += 2
        self.xSizeTxt.setText(str(self.xSize))

    def xDown(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize -= 2
        self.xSizeTxt.setText(str(self.xSize))

    def yUp(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize += 2
        self.ySizeTxt.setText(str(self.ySize))

    def yDown(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize -= 2
        self.ySizeTxt.setText(str(self.ySize))
