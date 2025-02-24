# #########################################################################
# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.           #
#                                                                         #
#                       Software Name: XRFtomo                            #
#                                                                         #
#                   By: Argonne National Laboratory                       #
#                                                                         #
#                       OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#                                                                         #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the           #
#    distribution.                                                        #
#                                                                         #
# 3. Neither the name of the copyright holder nor the names of its        #
#    contributors may be used to endorse or promote products derived      #
#    from this software without specific prior written permission.        #
#                                                                         #
#                               DISCLAIMER                                #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT    #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT     #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    #
###########################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from PyQt5 import QtCore
import h5py

__author__ = "Arthur T. Glowacki"
__copyright__ = "Copyright (c) 2018-19, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'
__all__ = ['ElementTableModel']


class TableArrayItem:
    def __init__(self, name):
        self.element_name = name
        self.use = True


class ElementTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arrayData = []
        self.columns = ['Element Map']
        self.COL_MAP = 0

    def rowCount(self, parent):
        return len(self.arrayData)

    def columnCount(self, parent):
        return len(self.columns)
    # fdc 04/30/2019 commented to fix compile error. Please defing int = ...
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.columns[section]

    def flags(self, index):
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if index.column() == self.COL_MAP:
            flags |= QtCore.Qt.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            rows = len(self.arrayData)
            if rows > 0 and index.row() < rows:
                self.arrayData[index.row()].use = bool(value)
                return True
        return False

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role == QtCore.Qt.CheckStateRole and index.column() == self.COL_MAP:
            if len(self.arrayData) > 0:
                if self.arrayData[index.row()].use is True:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
            else:
                return QtCore.Qt.Unchecked
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if len(self.arrayData) > 0:
            return QtCore.QVariant(self.arrayData[index.row()].element_name)
        else:
            return QtCore.QVariant()

    def loadElementNames(self, elements):
        self.arrayData = []
        topLeft = self.index(0, 0)
        self.layoutAboutToBeChanged.emit()
        for element in elements:
            self.arrayData += [TableArrayItem(element)]
        bottomRight = self.index(len(self.arrayData), len(self.columns))
        self.layoutChanged.emit()
        self.dataChanged.emit(topLeft, bottomRight)

    def setChecked(self, rows, value):
        for i in rows:
            self.setData(self.index(i, self.COL_MAP), value, QtCore.Qt.CheckStateRole)

    def setAllChecked(self, value):
        for i in range(len(self.arrayData)):
            self.setData(self.index(i, self.COL_MAP), value, QtCore.Qt.CheckStateRole)

