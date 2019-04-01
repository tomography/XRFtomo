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

from PyQt5 import QtWidgets, QtCore, QtGui
# from models.file_table_model import FileTableModel
# from models.element_table_model import ElementTableModel
import xfluo
import h5py
from pylab import *

# from file_io.reader import read_projection


class FileTableWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(FileTableWidget, self).__init__()
        self.parent = parent
        self._num_cols = 4
        self._num_row = 4
        self.auto_theta_pv = self.parent.params.theta_pv
        self.auto_input_path = self.parent.params.input_path
        self.auto_image_tag = self.parent.params.image_tag
        self.auto_data_tag = self.parent.params.data_tag
        self.auto_element_tag = self.parent.params.element_tag
        self.auto_sorted_angles = self.parent.params.sorted_angles
        self.auto_selected_elements = eval(self.parent.params.selected_elements)
        self.initUI()

    def initUI(self):
        self.fileTableModel = xfluo.FileTableModel()
        self.fileTableView = QtWidgets.QTableView()
        self.fileTableView.setModel(self.fileTableModel)
        self.fileTableView.setSortingEnabled(True)
        self.fileTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.fileTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.fileTableView.customContextMenuRequested.connect(self.onFileTableContextMenu)

        self.elementTableModel = xfluo.ElementTableModel()
        self.elementTableView = QtWidgets.QTableView()
        self.elementTableView.setModel(self.elementTableModel)
        self.elementTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.elementTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.elementTableView.customContextMenuRequested.connect(self.onElementTableContextMenu)

        dirLabel = QtWidgets.QLabel('Directory')
        self.dirLineEdit = QtWidgets.QLineEdit(self.auto_input_path)
        self.dirLineEdit.returnPressed.connect(self.onLoadDirectory)
        self.extLineEdit = QtWidgets.QLineEdit('*.h5')
        self.extLineEdit.setMaximumSize(50, 30)
        self.extLineEdit.returnPressed.connect(self.onLoadDirectory)
        self.dirBrowseBtn = QtWidgets.QPushButton('Browse')
        self.dirBrowseBtn.clicked.connect(self.onDirBrowse)
        self.thetaOptions = ['2xfm:m53.VAL', '2xfm:m36.VAL','2xfm:m58.VAL']
        thetaCompleter = QtWidgets.QCompleter(self.thetaOptions)
        thetaLabel = QtWidgets.QLabel('Theta PV')
        self.thetaLineEdit = QtWidgets.QLineEdit(self.auto_theta_pv)
        self.thetaLineEdit.setCompleter(thetaCompleter)
        self.thetaLineEdit.textChanged.connect(self.onThetaPVChange)
        self.thetaLineEdit.returnPressed.connect(self.onThetaUpdate)
        imageTag_label = QtWidgets.QLabel('Image Tag:')
        self.imageTag = QtWidgets.QComboBox()
        self.imageTag.currentIndexChanged.connect(self.getDataTag)
        dataTag_label = QtWidgets.QLabel('Data Tag:')
        self.dataTag = QtWidgets.QComboBox()
        elementTag_label = QtWidgets.QLabel('Element Tag:')
        self.elementTag = QtWidgets.QComboBox()
        self.elementTag.currentIndexChanged.connect(self.getElementList)
        operator_label = QtWidgets.QLabel('Operator:')
        self.operator_option = QtWidgets.QComboBox()
        operators = ['+', '-', '*', '/']
        self.operator_option.currentIndexChanged.connect(self.operator)
        for k in arange(len(operators)):
            self.operator_option.addItem(operators[k])

        scalar_label = QtWidgets.QLabel('scalar names:')
        self.scalar_option = QtWidgets.QComboBox()
        self.scalar_option.setMaximumWidth(250)
        self.elementTag.currentIndexChanged.connect(self.getscalars)

        # self.thetaUpdatehBtn = QtWidgets.QPushButton('Update')
        # self.thetaUpdatehBtn.clicked.connect(self.onThetaUpdate)
        self.saveDataBtn = QtWidgets.QPushButton('Save to Memory')
        # self.saveDataBtn.clicked.connect(self.onSaveDataInMemory)
        try:
            self.onLoadDirectory()
        except:
            print("invalid directory or file, try new folder or remove problematic file")
        self.onThetaUpdate()
        # self.saveDataBtn.setEnabled(False)

        hBox0 = QtWidgets.QHBoxLayout()
        hBox0.addWidget(dirLabel)
        hBox0.addWidget(self.dirLineEdit)
        hBox0.addWidget(self.extLineEdit)
        hBox0.addWidget(self.dirBrowseBtn)

        hBox1 = QtWidgets.QHBoxLayout()
        hBox1.addWidget(thetaLabel)
        hBox1.addWidget(self.thetaLineEdit)
        hBox1.addWidget(self.saveDataBtn)


        hBox2 = QtWidgets.QHBoxLayout()
        hBox2.addWidget(imageTag_label)
        hBox2.addWidget(self.imageTag)
        hBox2.addWidget(dataTag_label)
        hBox2.addWidget(self.dataTag)
        hBox2.addWidget(elementTag_label)
        hBox2.addWidget(self.elementTag)
        hBox2.addWidget(operator_label)
        hBox2.addWidget(self.operator_option)
        hBox2.addWidget(scalar_label)
        hBox2.addWidget(self.scalar_option)

        vBox = QtWidgets.QVBoxLayout()
        vBox.addLayout(hBox0)
        vBox.addLayout(hBox1)
        vBox.addLayout(hBox2)
        vBox.addWidget(self.fileTableView)
        vBox.addWidget(self.elementTableView)
        self.setLayout(vBox)


    def operator(self):
        pass

    def getscalars(self):
        pass

    def onThetaPVChange(self):
        self.parent.params.theta_pv =  self.thetaLineEdit.text()

    def onDirBrowse(self):
        try:
            folderName = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
            self.dirLineEdit.setText(folderName)
            self.parent.params.input_path = self.dirLineEdit.text()
            self.onLoadDirectory()
        except:
            print("select directory")

    def onLoadDirectory(self):
        self.parent.params.input_path = self.dirLineEdit.text()
        self.fileTableModel.loadDirectory(self.dirLineEdit.text(), self.extLineEdit.text())
        self.fileTableModel.setAllChecked(True)
        try:
            self.imageTag.clear()
            self.getImgTags()
            self.getDataTag()
            self.getElementList()
            self.onThetaUpdate()
        except KeyError:
            pass


    def getImgTags(self):
        fpath = self.fileTableModel.getFirstCheckedFilePath()
        self.img = h5py.File(fpath,"r")
        self.imgTags = list(self.img.keys())
        self.version = self.checkVersion()
        if self.version:
            self.thetaLineEdit.setEnabled(False)
            self.dataTag.setEnabled(False)
            self.elementTag.setEnabled(False)
            self.operator_option.setEnabled(True)
            self.scalar_option.setEnabled(True)
            self.scalar_options = {}
            scalar_list = list(self.img['exchange_1']['scaler_names'])
            scalar_list = [scalar_list[i].decode() for i in range(len(scalar_list))]
            self.scalar_option.clear()

            if 'MAPS' in self.imgTags:
                self.imgTags.remove('MAPS')
            if 'exchange_0' in self.imgTags:
                self.imgTags.remove('exchange_0')

            for i in range(len(scalar_list)):
                 self.scalar_option.addItem(scalar_list[i])
            for i in range(len(self.imgTags)):
                self.imageTag.addItem(self.imgTags[i])

            indx = self.imgTags.index(self.auto_image_tag)
            self.imageTag.setCurrentIndex(indx)

        else:
            self.thetaLineEdit.setEnabled(True)
            self.dataTag.setEnabled(True)
            self.elementTag.setEnabled(True)
            self.operator_option.setEnabled(False)
            self.scalar_option.setEnabled(False)

            for i in range(len(self.imgTags)):
                self.imageTag.addItem(self.imgTags[i])
            indx = self.imgTags.index(self.auto_image_tag)
            self.imageTag.setCurrentIndex(indx)

    def getDataTag(self):
        if self.version:
            indx = self.imageTag.currentIndex()
            if indx == -1:
                return
            
            self.dataTag.clear()
            self.dataTag.addItem('images')
            self.parent.params.image_tag = self.imageTag.currentText()
            self.parent.params.data_tag = self.dataTag
            self.elementTag.clear()
            self.elementTag.addItem('image_names')
            self.parent.params.elementTag = self.elementTag


        else: 
            self.dataTags = {}
            self.elementTags = {}

            for i in range(len(self.imgTags)):
                self.dataTags[i] = list(self.img[self.imgTags[i]])
                self.elementTags[i] = list(self.img[self.imgTags[i]])
                indx = self.imageTag.currentIndex()
                if indx == -1:
                    return
            try:
                self.dataTag.clear()
                self.elementTag.clear()
                for i in range(len(self.dataTags[indx])):
                    self.dataTag.addItem(self.dataTags[indx][i])
                    self.elementTag.addItem(self.dataTags[indx][i])
            except KeyError:        #This error happens when resetting image tags as a result of reloading the same dataset
                pass

            try:
                indx2 = self.dataTags[indx].index(self.auto_data_tag)
                self.dataTag.setCurrentIndex(indx2)
                indx3 = self.elementTags[indx].index(self.auto_element_tag)
                self.elementTag.setCurrentIndex(indx3)
            except ValueError:
                pass
            self.parent.params.image_tag = self.imageTag.currentText()
            self.parent.params.data_tag = self.dataTag.currentText()

    def getElementList(self):

        if self.version:
            fpath = self.fileTableModel.getFirstCheckedFilePath()
            image_tag = self.imageTag.currentText()
            element_tag = self.elementTag.currentText()
            self.parent.params.element_tag = self.imageTag.currentText()
            self.parent.params.data_tag = self.dataTag
            self.elementTableModel.loadElementNames(fpath, image_tag, element_tag)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))
            
        else:
            fpath = self.fileTableModel.getFirstCheckedFilePath()
            image_tag = self.imageTag.currentText()
            element_tag = self.elementTag.currentText()
            self.parent.params.element_tag = element_tag
            self.parent.params.data_tag = self.dataTag.currentText()
            self.elementTableModel.loadElementNames(fpath, image_tag, element_tag)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))

    def checkVersion(self):
        echange_bool = list(self.img)
        version_bool =  'exchange_1' in echange_bool
        return version_bool

    def onThetaUpdate(self):
        if self.version:
            self.fileTableModel.loadThetas2(self.imageTag.currentText())
            if self.parent.params.sorted_angles == True:
                self.fileTableView.sortByColumn(1, 0)
            self.parent.params.input_path = self.dirLineEdit.text()

        else:
            self.fileTableModel.loadThetas(self.thetaLineEdit.text())
            if self.parent.params.sorted_angles == True:
                self.fileTableView.sortByColumn(1, 0)
            self.parent.params.theta_pv = self.thetaLineEdit.text()
            self.parent.params.input_path = self.dirLineEdit.text()

    def onFileTableContextMenu(self, pos):
        if self.fileTableView.selectionModel().selection().indexes():
            rows = []
            for i in self.fileTableView.selectionModel().selection().indexes():
                rows += [i.row()]
            menu = QtGui.QMenu()
            check_action = menu.addAction("Check")
            uncheck_action = menu.addAction("Uncheck")
            action = menu.exec_(self.fileTableView.mapToGlobal(pos))
            if action == check_action or action == uncheck_action:
                self.fileTableModel.setChecked(rows, (check_action == action))

    def onElementTableContextMenu(self, pos):
        if self.elementTableView.selectionModel().selection().indexes():
            rows = []
            for i in self.elementTableView.selectionModel().selection().indexes():
                rows += [i.row()]
            menu = QtGui.QMenu()
            check_action = menu.addAction("Check")
            uncheck_action = menu.addAction("Uncheck")
            action = menu.exec_(self.elementTableView.mapToGlobal(pos))
            if action == check_action or action == uncheck_action:
                self.elementTableModel.setChecked(rows, (check_action == action))

    def onSaveDataInMemory(self):

        files = [i.filename for i in self.fileTableModel.arrayData]
        path_files = [self.fileTableModel.directory + '/' + s for s in files]
        thetas = [i.theta for i in self.fileTableModel.arrayData]
        elements = [i.element_name for i in self.elementTableModel.arrayData]
        use = [i.use for i in self.fileTableModel.arrayData]
        use2 = [i.use for i in self.elementTableModel.arrayData]
        img_tag = self.imageTag.currentText()
        data_tag = self.dataTag.currentText()
        element_tag = self.elementTag.currentText()

        k = arange(len(files))
        l = arange(len(elements))
        use_files =[files[j] for j in k if use[j]==True]
        self.use_thetas = np.asarray([thetas[j] for j in k if use[j]==True])
        self.use_elements = [elements[j] for j in l if use2[j]==True]

        if self.version:
            theta_index = None
        else:
            theta_index = int(self.fileTableModel.idx[0])
        element_index = [elements.index(j) for j in self.use_elements]
        self.parent.params.selected_elements = str(element_index)

        self.data = xfluo.convert_to_array(path_files, element_index, theta_index, img_tag, data_tag, element_tag)
        return self.data, self.use_elements, self.use_thetas, use_files
