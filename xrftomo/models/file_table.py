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

        # fileNames = [os.path.basename(x) for x in glob(directoryName+'/'+ext)]
        fileNames = sorted(fileNames)
        self.arrayData = []
        for i in range(len(fileNames)):
            self.arrayData += [TableArrayItem(fileNames[i])]
        bottomRight = self.index(len(self.arrayData), len(self.columns))
        self.layoutChanged.emit()
        self.dataChanged.emit(topLeft, bottomRight)

    # def loadThetasLegacy(self, thetaPV):
    #     thetaBytes = thetaPV.encode('ascii')
    #     topLeft = self.index(0, self.COL_THETA)
    #     bottomRight = self.index(len(self.arrayData), self.COL_THETA)
    #     for i in range(len(self.arrayData)):
    #         try:
    #             hFile = h5py.File(self.directory+'/'+self.arrayData[i].filename)
    #             extra_pvs = hFile['/MAPS/extra_pvs']
    #             self.idx = np.where(extra_pvs[0] == thetaBytes)
    #             if len(self.idx[0]) > 0:
    #                 self.arrayData[i].theta = float(extra_pvs[1][self.idx[0][0]])
    #         except:
    #             pass
    #     self.dataChanged.emit(topLeft, bottomRight)
    
    # def loadThetas(self, img_tag):
    #     topLeft = self.index(0, self.COL_THETA)
    #     bottomRight = self.index(len(self.arrayData), self.COL_THETA)
    #     for i in range(len(self.arrayData)):
    #         try:
    #             hFile = h5py.File(self.directory+'/'+self.arrayData[i].filename)
    #             self.arrayData[i].theta = float(hFile[img_tag]['theta'].value)
    #         except:
    #             pass
    #     self.dataChanged.emit(topLeft, bottomRight)


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
