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

from PyQt5 import QtCore, QtWidgets


class ReconstructionControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ReconstructionControlsWidget, self).__init__()

        self.initUI()

    def initUI(self):
        self.combo = QtWidgets.QComboBox(self)
        self.method = QtWidgets.QComboBox(self)
        self.btn = QtWidgets.QPushButton('Click2')
        self.save = QtWidgets.QPushButton("Save tiff files")
        self.save.setHidden(True)
        self.btn.setText("Sinogram")
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLineEdit("0")
        self.lbl = QtWidgets.QLabel()
        self.cbox = QtWidgets.QCheckBox("")
        self.lbl2 = QtWidgets.QLabel("Center")
        self.lbl.setText("")

        self.threshLbl = QtWidgets.QLabel("threshold")
        self.threshLe = QtWidgets.QLineEdit("")
        self.threshBtn = QtWidgets.QPushButton("Apply")

        centerBox = QtWidgets.QHBoxLayout()
        centerBox.addWidget(self.cbox)
        centerBox.addWidget(self.lbl2)
        centerBox.addWidget(self.lcd)
        self.lcd.setEnabled(False)
        self.methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad"]

        self.mulBtn = QtWidgets.QPushButton("x 10")
        self.divBtn = QtWidgets.QPushButton("/ 10")
        mdBox = QtWidgets.QHBoxLayout()
        mdBox.addWidget(self.mulBtn)
        mdBox.addWidget(self.divBtn)

        self.maxLbl = QtWidgets.QLabel("Max")
        self.minLbl = QtWidgets.QLabel("Min")
        self.maxText = QtWidgets.QLineEdit()
        self.minText = QtWidgets.QLineEdit()

        maxBox = QtWidgets.QHBoxLayout()
        minBox = QtWidgets.QHBoxLayout()
        maxBox.addWidget(self.maxLbl)
        maxBox.addWidget(self.maxText)
        minBox.addWidget(self.minLbl)
        minBox.addWidget(self.minText)

        self.betaName = QtWidgets.QLabel("Beta")
        self.deltaName = QtWidgets.QLabel("Delta")
        self.itersName = QtWidgets.QLabel("Iteration")
        self.beta = QtWidgets.QLineEdit("1")
        self.delta = QtWidgets.QLineEdit("0.01")
        self.iters = QtWidgets.QLineEdit("10")

        betaBox = QtWidgets.QHBoxLayout()
        deltaBox = QtWidgets.QHBoxLayout()
        itersBox = QtWidgets.QHBoxLayout()
        threshBox = QtWidgets.QHBoxLayout()
        betaBox.addWidget(self.betaName)
        betaBox.addWidget(self.beta)
        deltaBox.addWidget(self.deltaName)
        deltaBox.addWidget(self.delta)
        itersBox.addWidget(self.itersName)
        itersBox.addWidget(self.iters)
        threshBox.addWidget(self.threshLbl)
        threshBox.addWidget(self.threshLe)
        threshBox.addWidget(self.threshBtn)

        for k in range(len(self.methodname)):
            self.method.addItem(self.methodname[k])
        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.combo)
        vb.addWidget(self.method)
        vb.addWidget(self.btn)
        vb.addWidget(self.save)
        vb.addLayout(centerBox)
        vb.addLayout(threshBox)
        vb.addWidget(self.sld)
        vb.addWidget(self.lbl)
        vb.addLayout(mdBox)
        vb.addLayout(maxBox)
        vb.addLayout(minBox)
        vb.addLayout(itersBox)
        vb.addLayout(betaBox)
        vb.addLayout(deltaBox)
        self.setLayout(vb)