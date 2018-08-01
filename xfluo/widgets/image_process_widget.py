'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.

Copyright 2016. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.

Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.

    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

from PyQt5 import QtWidgets
from widgets.image_and_histogram_widget import ImageAndHistogramWidget


class ImageProcessWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ImageProcessWidget, self).__init__()

        self.initUI()

    def initUI(self):
        self.xSize = 20
        self.ySize = 20

        self.bgBtn = QtWidgets.QPushButton("Bg Value")
        self.delHotspotBtn = QtWidgets.QPushButton("Delete HS")
        self.normalizeBtn = QtWidgets.QPushButton("Normalize")
        self.cutBtn = QtWidgets.QPushButton("Cut")
        self.gaussian33Btn = QtWidgets.QPushButton("3*3 gauss")
        self.gaussian55Btn = QtWidgets.QPushButton("5*5 gauss")
        self.xUpBtn = QtWidgets.QPushButton("x: +")
        self.xUpBtn.clicked.connect(self.xUp)
        self.xDownBtn = QtWidgets.QPushButton("x: -")
        self.xDownBtn.clicked.connect(self.xDown)
        self.yUpBtn = QtWidgets.QPushButton("y: +")
        self.yUpBtn.clicked.connect(self.yUp)
        self.yDownBtn = QtWidgets.QPushButton("y: -")
        self.yDownBtn.clicked.connect(self.yDown)

        self.xSizeLbl = QtWidgets.QLabel("x Size")
        self.ySizeLbl = QtWidgets.QLabel("y Size")

        self.xSizeTxt = QtWidgets.QLineEdit(str(self.xSize))
        self.ySizeTxt = QtWidgets.QLineEdit(str(self.ySize))

        self.combo1 = QtWidgets.QComboBox()
        self.combo2 = QtWidgets.QComboBox()

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.xUpBtn)
        hb1.addWidget(self.xDownBtn)
        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.xSizeLbl)
        hb2.addWidget(self.xSizeTxt)
        hb3 = QtWidgets.QHBoxLayout()
        hb3.addWidget(self.yUpBtn)
        hb3.addWidget(self.yDownBtn)
        hb4 = QtWidgets.QHBoxLayout()
        hb4.addWidget(self.ySizeLbl)
        hb4.addWidget(self.ySizeTxt)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)
        vb2 = QtWidgets.QVBoxLayout()
        vb2.addLayout(hb3)
        vb2.addLayout(hb4)
        xSG = QtWidgets.QGroupBox("x Size")
        xSG.setLayout(vb1)
        ySG = QtWidgets.QGroupBox("y Size")
        ySG.setLayout(vb2)
        vb3 = QtWidgets.QVBoxLayout()
        vb3.addWidget(self.combo1)
        vb3.addWidget(self.combo2)
        vb3.addWidget(xSG)
        vb3.addWidget(ySG)

        hb6 = QtWidgets.QHBoxLayout()
        hb6.addWidget(self.bgBtn, stretch=0)
        hb6.addWidget(self.delHotspotBtn, stretch=0)

        hb7 = QtWidgets.QHBoxLayout()
        hb7.addWidget(self.normalizeBtn, stretch=0)
        hb7.addWidget(self.cutBtn, stretch=0)

        hb8 = QtWidgets.QHBoxLayout()
        hb8.addWidget(self.gaussian33Btn, stretch=0)
        hb8.addWidget(self.gaussian55Btn, stretch=0)

        vb3.addLayout(hb6)
        vb3.addLayout(hb7)
        vb3.addLayout(hb8)

        self.imgAndHistoWidget = ImageAndHistogramWidget()
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addLayout(vb3)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)

    def changeXSize(self):
        self.xSize = int(self.xSizeTxt.text())

    def changeYSize(self):
        self.ySize = int(self.ySizeTxt.text())

    def xUp(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize += 1
        self.xSizeTxt.setText(str(self.xSize))

    def xDown(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize -= 1
        self.xSizeTxt.setText(str(self.xSize))

    def yUp(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize += 1
        self.ySizeTxt.setText(str(self.ySize))

    def yDown(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize -= 1
        self.ySizeTxt.setText(str(self.ySize))
