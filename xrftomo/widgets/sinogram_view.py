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


from PyQt5 import QtCore
import pyqtgraph
from PyQt5.QtCore import pyqtSignal
from matplotlib.figure import Figure


class SinogramView(pyqtgraph.GraphicsLayoutWidget):
    keyPressSig = pyqtSignal(int, int, name= 'keyPressSig')

    def __init__(self):
        super(SinogramView, self).__init__()
        self.keylist = []
        self.hotSpotNumb = 0
        self.initUI()

    def initUI(self):
        self.p1 = self.addPlot()
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(0)
        self.p1.addItem(self.projView)
        self.p1.items[0].scene().sigMouseMoved.connect(self.mouseMoved)
        self.p1.items[0].scene().sigMouseClicked.connect(self.mouseClick)
        self.p1.setMouseEnabled(x=False, y=False)
        self.show()
        self.moving_x = 0
        self.moving_y = 0


    def mouseMoved(self, evt):
        try:
            self.moving_x = self.projView.mapFromDevice(evt).x()
            self.moving_y = self.projView.mapFromDevice(evt).y()
        except:
            "TODO: error when incorrect PV loaded or when only single angle information is available. "
            print("WARNING: single column for sinogram. Load more projections with unique angles. ")

    def mouseClick(self, evt):
        self.x_pos = int(round(self.moving_x))
        self.y_pos = int(round(self.moving_y))

    def mouseReleaseEvent(self, ev):
        self.x_pos = int(self.moving_x)
        self.y_pos = int(self.moving_y)

    def wheelEvent(self, ev):
        '''
        keep this here. It overrides the built in wheel event in order to keep the mouse wheel disabled.
        '''
        pass

    def keyPressEvent(self, ev):
        self.firstrelease = True
        astr = ev.key()
        self.keylist.append(astr)
        return

    def keyReleaseEvent(self, ev):
        try:
            if self.firstrelease == True:
                self.processMultipleKeys(self.keylist)
        except:
            pass
        self.firstrelease = False
        try:
            del self.keylist[-1]
        except:
            pass

    def processMultipleKeys(self, keyspressed):
        if len(keyspressed) ==1:

            if keyspressed[0] == QtCore.Qt.Key_Up:
                col_number = int(self.x_pos/10)
                self.keyPressSig.emit(1, col_number)

            if keyspressed[0] == QtCore.Qt.Key_Down:
                col_number = int(self.x_pos/10)
                self.keyPressSig.emit(-1, col_number)
 
