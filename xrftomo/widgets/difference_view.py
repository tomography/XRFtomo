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
import xrftomo

class differenceView(pyqtgraph.GraphicsLayoutWidget):
    keyPressSig = pyqtSignal(str, name= 'keyPressSig')

    def __init__(self):
    # def __init__(self, parent):
        super(differenceView, self).__init__()
        self.keylist = []
        self.initUI()

    def initUI(self):
        custom_vb = xrftomo.CustomViewBox()
        self.p1 = self.addPlot(viewBox = custom_vb, enableMouse = False)
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(-90)
        self.p1.addItem(self.projView)
        self.p1.vb = custom_vb

        # position = [0.0, 0.25, 0.5, 0.75, 1.0]
        # colors = [[0, 0, 0, 255], [0, 0, 256, 255], [256, 0, 0, 255], [242, 125, 0, 255], [253, 207, 88, 255]]
        # bi_polar_color_map = pyqtgraph.ColorMap(position, colors)
        # lookup_table = bi_polar_color_map.getLookupTable(0.0, 1.0, 256)
        # self.projView.setLookupTable(lookup_table)
        # self.projView.setLevels([0, 5])

    def wheelEvent(self, ev):
        #empty function, but leave it as it overrides some other unwanted functionality.
        pass

    def keyPressEvent(self, ev):
        self.firstrelease = True
        astr = ev.key()
        self.keylist.append(astr)

    def keyReleaseEvent(self, ev):
        if self.firstrelease == True:
            self.processMultipleKeys(self.keylist)

        self.firstrelease = False

        try:    #complains about an index error for some reason.
            del self.keylist[-1]
        except:
            pass
        return

    def processMultipleKeys(self, keyspressed):
        if len(keyspressed) ==1:
            if keyspressed[0]== QtCore.Qt.Key_Left:
                self.keyPressSig.emit('left')
            if keyspressed[0] == QtCore.Qt.Key_Right:
                self.keyPressSig.emit('right')
            if keyspressed[0] == QtCore.Qt.Key_Up:
                self.keyPressSig.emit('up')
            if keyspressed[0] == QtCore.Qt.Key_Down:
                self.keyPressSig.emit('down')
            if keyspressed[0] == QtCore.Qt.Key_A:
                self.keyPressSig.emit('A')
            if keyspressed[0] == QtCore.Qt.Key_D:
                self.keyPressSig.emit('D')
        if len(keyspressed) >=2:
            self.keylist = []
            return
