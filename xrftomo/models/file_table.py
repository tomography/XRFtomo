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

"""
Subclasses the h5py module for interacting with Data Exchange files.
"""


from PyQt5 import QtCore
import os

__author__ = "Arthur T. Glowacki"
__copyright__ = "Copyright (c) 2018-19, UChicago Argonne, LLC."
__version__ = "0.0.1"
__docformat__ = 'restructuredtext en'
__all__ = ['TableArrayItem', 'FileTableModel']

class TableArrayItem:
    def __init__(self, fname):
        self.filename = fname
        self.theta = 0.0
        self.use = True


class FileTableModel(QtCore.QAbstractTableModel):

    """
    Interact with Data Exchange files.

    Methods
    -------
    data(self, index, role)
        Helper function for ....

    loadDirectory(self, directoryName, ext='*.h5*')
        This method is used to ....

    """

    def __init__(self, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arrayData = [] # list of TableArrayItem's
        self.directory = ''
        self.columns = ['Filename', 'Theta']
        self.COL_FILE = 0
        self.COL_THETA = 1
        self.COL_USE = 2
        self.idx = 0

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
        if index.column() == self.COL_FILE:
            flags |= QtCore.Qt.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            rows = len(self.arrayData)
            if rows > 0 and index.row() < rows:
                self.arrayData[index.row()].use = bool(value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role == QtCore.Qt.CheckStateRole and index.column() == self.COL_FILE:
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
            if index.column() == self.COL_FILE:
                return QtCore.QVariant(self.arrayData[index.row()].filename)
            elif index.column() == self.COL_THETA:
                return QtCore.QVariant(self.arrayData[index.row()].theta)
        else:
            return QtCore.QVariant()

    def loadDirectory(self, directoryName, ext='*.h5*'):
        self.directory = directoryName
        topLeft = self.index(0, 0)
        self.layoutAboutToBeChanged.emit()
        all_files = [x for x in os.listdir(directoryName)]
        fileNames = [x for x in all_files if x.split(".")[-1] == ext.split(".")[-1]]

        # TODO: filter files begining with "._"
        with_ = [x for x in fileNames if x.startswith(".")]
        without_ = [x for x in fileNames if x not in with_]
        fileNames = without_

        # fileNames = [os.path.basename(x) for x in glob(directoryName+'/'+ext)]
        fileNames = sorted(fileNames)
        self.arrayData = []
        for i in range(len(fileNames)):
            self.arrayData += [TableArrayItem(fileNames[i])]
        bottomRight = self.index(len(self.arrayData), len(self.columns))
        self.layoutChanged.emit()
        self.dataChanged.emit(topLeft, bottomRight)

    def update_thetas(self, thetas):
        topLeft = self.index(0, self.COL_THETA)
        bottomRight = self.index(len(self.arrayData), self.COL_THETA)
        try:
            for i in range(len(self.arrayData)):
                self.arrayData[i].theta = thetas[i]
        except:
            print("something is off here")
        self.dataChanged.emit(topLeft, bottomRight)
        return 
        
    def getFirstCheckedFilePath(self):
        for i in range(len(self.arrayData)):
            if self.arrayData[i].use is True:
                return self.directory+'/'+self.arrayData[i].filename
        return None

    def getAllFiles(self):
        path_files = []
        for i in range(len(self.arrayData)):
            if self.arrayData[i].use is True:
                path_files.append(self.directory+'/'+self.arrayData[i].filename)
        return path_files

    def setChecked(self, rows, value):
        for i in rows:
            self.setData(self.index(i, self.COL_FILE), value, QtCore.Qt.CheckStateRole)

    def setAllChecked(self, value):
        for i in range(len(self.arrayData)):
            self.setData(self.index(i, self.COL_FILE), value, QtCore.Qt.CheckStateRole)

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        # self.arrayData = sorted(self.arrayData, key=operator.itemgetter(col))
        if col == self.COL_FILE:
            self.arrayData = sorted(self.arrayData, key=lambda tableitem: tableitem.filename)
        if col == self.COL_THETA:
            self.arrayData = sorted(self.arrayData, key=lambda tableitem: tableitem.theta)
        if order == QtCore.Qt.DescendingOrder:
            self.arrayData.reverse()
        self.layoutChanged.emit()
