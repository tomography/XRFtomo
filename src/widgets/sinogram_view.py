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

from PyQt5 import QtCore
import pyqtgraph
import numpy as np


class SinogramView(pyqtgraph.GraphicsLayoutWidget):

    def __init__(self):
        super(SinogramView, self).__init__()

        self.initUI()
        self.hotSpotNumb = 0

    def initUI(self):
        self.show()
        self.p1 = self.addPlot()
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(-90)
        self.p1.addItem(self.projView)

    def keyPressEvent(self, ev):

        if ev.key() == QtCore.Qt.Key_Right:
            self.getMousePos()
            self.shiftnumb = 1
            self.shift()
            self.projView.setImage(self.copy)
            self.regShift[self.numb2] += self.shiftnumb

        if ev.key() == QtCore.Qt.Key_Left:
            self.getMousePos()
            self.shiftnumb = -1
            self.shift()
            self.projView.setImage(self.copy)
            self.regShift[self.numb2] += self.shiftnumb

    def getMousePos(self):
        numb = self.projView.iniY
        self.numb2 = int(numb / 10)

    def shift(self):
        self.copy = self.projData
        self.copy[self.numb2 * 10:self.numb2 * 10 + 10, :] = np.roll(self.copy[self.numb2 * 10:self.numb2 * 10 + 10, :], self.shiftnumb, axis=1)

    def getShape(self):
        self.regShift = np.zeros(self.projData.shape[0], dtype=int)