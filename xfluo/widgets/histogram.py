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
from PyQt5.QtCore import pyqtSignal
import pyqtgraph

class HistogramWidget(pyqtgraph.GraphicsLayoutWidget):
    shiftSig = pyqtSignal(str, name='sliderChangedSig')
    keyPressSig = pyqtSignal(str, name= 'keyPressSig')

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.hotSpotNumb = 0
        self.xSize = 10
        self.ySize = 10
        self.x_pos = 5
        self.y_pos = -5
        self.keylist = []
        self.initUI()

    def initUI(self):
        self.p1 = self.addPlot(enableMouse = False)
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(-90)
        self.projView.iniX = 0
        self.projView.iniY = -10
        self.ROI = pyqtgraph.ROI([self.projView.iniX, self.projView.iniY], [10, 10])
        # self.cross_h = p1.pyqtgraph.PlotItem.addLine(x=10, y=10, z=0)
        self.p1.addItem(self.projView)
        self.p1.addItem(self.ROI)
        self.cross_v = self.p1.addLine(x=10)
        self.cross_h = self.p1.addLine(y=-10)
        self.p1.scene().sigMouseMoved.connect(self.mouseMoved)
        self.p1.scene().sigMouseClicked.connect(self.mouseClick)
        self.p1.setMouseEnabled(x=False, y=False)

    def mouseMoved(self, evt):
        self.moving_x = self.p1.vb.mapSceneToView(evt).x()
        self.moving_y = self.p1.vb.mapSceneToView(evt).y()

    def mouseClick(self, evt):
        self.x_pos = int(round(self.moving_x))
        self.y_pos = int(round(self.moving_y))
        self.ROI.setPos([self.x_pos-self.xSize/2,self.y_pos-self.ySize/2])

    def mouseReleaseEvent(self, ev):
        x_pos = int(round(self.moving_x))
        y_pos = int(round(self.moving_y))
        frame_height = self.projView.width()
        frame_width = self.projView.height()
        self.x_pos, self.y_pos = self.update_roi(x_pos, y_pos, self.xSize, self.ySize, frame_height, frame_width)

        if ev.button() == 1:
            self.ROI.setPos([self.x_pos-self.xSize/2,self.y_pos-self.ySize/2])

        if ev.button() == 2: 
            self.p1.items[3].setValue(self.x_pos)
            self.p1.items[4].setValue(self.y_pos)

    def update_roi(self, x_pos, y_pos, x_size, y_size, frame_height, frame_width):
        print(x_pos, y_pos, x_pos-x_size/2, y_pos-y_size/2)

        max_y = frame_height
        max_x = frame_width

        roi_left =x_pos-x_size/2
        roi_right = x_pos+x_size/2
        roi_top = y_pos+y_size/2
        roi_bottom = y_pos-y_size/2

        ## if way far left
        if roi_left <= 0 :
            print("case 1")
            x_pos = x_size/2

        ## if way far right
        if roi_right>= max_x:
            print("case 2")
            x_pos = max_x - x_size/2

        ## if way far above
        if roi_top >= 0 :
            print("case 3")
            y_pos = -y_size/2

        ## if way far below
        if roi_bottom <= -max_y:
            print("case 4")
            y_pos = -max_y + y_size/2

        return x_pos, y_pos

    def wheelEvent(self, ev):
        pass

    def keyPressEvent(self, ev):
        self.firstrelease = True
        astr = ev.key()
        self.keylist.append(astr)

    def keyReleaseEvent(self, ev):
        if self.firstrelease == True:
            self.processMultipleKeys(self.keylist)

        self.firstrelease = False
        del self.keylist[-1]

    def processMultipleKeys(self, keyspressed):
        if len(keyspressed) ==1:
            if keyspressed[0]== QtCore.Qt.Key_Left:
                self.shiftSig.emit('left')
            if keyspressed[0] == QtCore.Qt.Key_Right:
                self.shiftSig.emit('right')
            if keyspressed[0] == QtCore.Qt.Key_Up:
                self.shiftSig.emit('up')
            if keyspressed[0] == QtCore.Qt.Key_Down:
                self.shiftSig.emit('down')
            if keyspressed[0] == QtCore.Qt.Key_N:
                self.keyPressSig.emit('Next')
            if keyspressed[0] == QtCore.Qt.Key_S:
                self.keyPressSig.emit('Skip')
            if keyspressed[0] == QtCore.Qt.Key_Delete:
                self.shiftSig.emit('Delete')

        if len(keyspressed) == 2:
            if keyspressed[0] == QtCore.Qt.Key_Shift and keyspressed[1] == QtCore.Qt.Key_Left:
                self.shiftSig.emit('shiftLeft')
            if keyspressed[0] == QtCore.Qt.Key_Shift and keyspressed[1] == QtCore.Qt.Key_Right:
                self.shiftSig.emit('shiftRight')
            if keyspressed[0] == QtCore.Qt.Key_Shift and keyspressed[1] == QtCore.Qt.Key_Up:
                self.shiftSig.emit('shiftUp')
            if keyspressed[0] == QtCore.Qt.Key_Shift and keyspressed[1] == QtCore.Qt.Key_Down:
                self.shiftSig.emit('shiftDown')

