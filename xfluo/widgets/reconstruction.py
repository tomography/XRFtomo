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
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, signal
# import tomopy

class ReconstructionWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, name='elementChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')

    def __init__(self):
        super(ReconstructionWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ReconstructionControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        self.imgAndHistoWidget.lbl5.setText(str('Slice'))
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)

    def showReconstruct(self, data, elements, fnames, thetas):
        '''
        load window for reconstruction window
        '''
        self.p1 = [100, 100, data.shape[3] / 2]
        self.fnames = fnames
        self.data = data
        self.y_range = self.data.shape[2]
        self.thetas = thetas
        self.ViewControl.combo1.clear()
        self.ViewControl.method.clear()
        methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad"]
        for j in elements:
            self.ViewControl.combo1.addItem(j)
        for k in arange(len(methodname)):
            self.ViewControl.method.addItem(methodname[k])

        self.actions = xfluo.ReconstructionActions()
        self.elementChanged()
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.centerTextBox.setText(str(self.p1[2]))
        self.ViewControl.btn.clicked.connect(self.reconstruct_params)
        self.ViewControl.save.clicked.connect(self.call_saveRecTiff)
        self.ViewControl.mulBtn.setEnabled(False)
        self.ViewControl.divBtn.setEnabled(False)
        self.ViewControl.mulBtn.clicked.connect(self.call_reconMultiply)
        self.ViewControl.divBtn.clicked.connect(self.call_reconDivide)
        self.ViewControl.cbox.clicked.connect(self.cboxClicked)
        self.ViewControl.threshBtn.clicked.connect(self.call_threshold)
        self.imgAndHistoWidget.sld.setRange(0, self.y_range - 1)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.update_recon_image)

    def call_threshold(self):
        '''
        set threshhold for reconstruction
        '''
        threshValue = float(self.ViewControl.threshLe.text())
        self.recon = self.actions.threshhold(self.recon, threshValue)

    def cboxClicked(self):
        if self.ViewControl.cbox.isChecked():
            self.ViewControl.centerTextBox.setEnabled(True)
        else:
            self.ViewControl.centerTextBox.setEnabled(False)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.updateElementSlot(element)
        self.elementChangedSig.emit(element)

    def updateElementSlot(self, element):
        self.ViewControl.combo1.setCurrentIndex(element)

    def call_reconMultiply(self):
        '''
        multiply reconstruction by 10
        '''
        self.recon = self.actions.reconMultiply(self.recon)
        self.update_recon_image()

    def call_reconDivide(self):
        '''
        divide reconstuction by 10
        '''
        self.recon = self.actions.reconDivide(self.recon)
        self.update_recon_image()

    def call_saveRecTiff(self):
        rec = self.recon
        self.actions.saveRecTiff(rec)

    def reconstruct_params(self):

        self.ViewControl.lbl.setText("Reconstruction is currently running")
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        box_checked = self.ViewControl.cbox.isChecked()
        center = np.array(float(self.ViewControl.centerTextBox.text()), dtype=float32)
        method = self.ViewControl.method.currentIndex()
        beta = float(self.ViewControl.beta.text())
        delta = float(self.ViewControl.delta.text())
        iters = int(self.ViewControl.iters.text())
        thetas = self.thetas

        self.recon = self.actions.reconstruct(data, element, box_checked, center, method, beta, delta, iters, thetas)
        self.ViewControl.mulBtn.setEnabled(True)
        self.ViewControl.divBtn.setEnabled(True)
        self.update_recon_image()
        self.ViewControl.lbl.setText("Done")
        self.ViewControl.save.setHidden(False)

    def update_recon_image(self):
        index = self.ViewControl.sld.value()
        try:
            self.ViewControl.maxText.setText(str(self.recon[index, :, :].max()))
            self.ViewControl.minText.setText(str(self.recon[index, :, :].min()))
            self.imgAndHistoWidget.view.projView.setImage(self.recon[index, :, :])
        except:
            print("run reconstruction first")




