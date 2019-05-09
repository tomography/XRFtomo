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
from xfluo.file_io.reader import *


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
        #self.auto_detector_tag = self.parent.params.detector_tag
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

        dirLabel = QtWidgets.QLabel('Directory:')
        self.dirLineEdit = QtWidgets.QLineEdit(self.auto_input_path)
        self.dirLineEdit.returnPressed.connect(self.onLoadDirectory)
        self.extLineEdit = QtWidgets.QLineEdit('*.h5')
        self.extLineEdit.setMaximumSize(50, 30)
        self.extLineEdit.returnPressed.connect(self.onLoadDirectory)
        self.dirBrowseBtn = QtWidgets.QPushButton('Browse')
        self.dirBrowseBtn.clicked.connect(self.onDirBrowse)
        
        self.thetaOptions = ['2xfm:m53.VAL', '2xfm:m36.VAL','2xfm:m58.VAL', '9idbTAU:SM:ST:ActPos']
        thetaCompleter = QtWidgets.QCompleter(self.thetaOptions)
        thetaLabel = QtWidgets.QLabel('Theta PV:')
        thetaLabel.setFixedWidth(90)
        self.thetaLineEdit = QtWidgets.QLineEdit(self.auto_theta_pv)
        self.thetaLineEdit.setCompleter(thetaCompleter)
        self.thetaLineEdit.textChanged.connect(self.onThetaPVChange)
        self.thetaLineEdit.returnPressed.connect(self.onThetaUpdate)
        self.thetaLineEdit.setFixedWidth(122.5)
        
        imageTag_label = QtWidgets.QLabel('Image tag:')
        imageTag_label.setFixedWidth(90)
        self.imageTag = QtWidgets.QComboBox()
        # self.imageTag.currentIndexChanged.connect(self.getDataTag)
        self.imageTag.setFixedWidth(122.5)
        
        dataTag_label = QtWidgets.QLabel('')
        dataTag_label.setFixedWidth(90)
        self.dataTag = QtWidgets.QComboBox()
        # self.dataTag.currentIndexChanged.connect(self.getDataTag)
        self.dataTag.setFixedWidth(122.5)
        
        elementTag_label = QtWidgets.QLabel('Elements:')
        elementTag_label.setFixedWidth(90)
        self.elementTag = QtWidgets.QComboBox()
        self.elementTag.currentIndexChanged.connect(self.getElementList)
        self.elementTag.setFixedWidth(122.5)
        
        operator_label = QtWidgets.QLabel('Math operator:')
        operator_label.setFixedWidth(90)
        self.operator_option = QtWidgets.QComboBox()
        operators = ['/', '+', '-', '*',]
        self.operator_option.currentIndexChanged.connect(self.operator)
        self.operator_option.setFixedWidth(122.5)
        for k in arange(len(operators)):
            self.operator_option.addItem(operators[k])

        scalar_label = QtWidgets.QLabel('Detector:')
        scalar_label.setFixedWidth(90)
        self.scalar_option = QtWidgets.QComboBox()
        self.elementTag.currentIndexChanged.connect(self.getscalars)
        self.scalar_option.setFixedWidth(122.5)

        self.saveDataBtn = QtWidgets.QPushButton('Save to Memory')
        # self.saveDataBtn.clicked.connect(self.onSaveDataInMemory)
        # self.saveDataBtn.setEnabled(False)
        
        message_label = QtWidgets.QLabel('Messages:')
        self.message = QtWidgets.QTextEdit()
        self.message.setReadOnly(True)
        self.message.setMaximumHeight(20)
        self.message.setText('')

        hBox1 = QtWidgets.QHBoxLayout()
        hBox1.addWidget(thetaLabel)
        hBox1.addWidget(self.thetaLineEdit)
        hBox1.setAlignment(QtCore.Qt.AlignLeft)

        hBox2 = QtWidgets.QHBoxLayout()
        hBox2.addWidget(imageTag_label)
        hBox2.addWidget(self.imageTag)
        hBox2.setAlignment(QtCore.Qt.AlignLeft)
        
        hBox3 = QtWidgets.QHBoxLayout()
        hBox3.addWidget(dataTag_label)
        hBox3.addWidget(self.dataTag)
        hBox3.setAlignment(QtCore.Qt.AlignLeft)
        
        hBox4 = QtWidgets.QHBoxLayout()
        hBox4.addWidget(elementTag_label)
        hBox4.addWidget(self.elementTag)
        hBox4.setAlignment(QtCore.Qt.AlignLeft)
        
        hBox5 = QtWidgets.QHBoxLayout()
        hBox5.addWidget(operator_label)
        hBox5.addWidget(self.operator_option)
        hBox5.setAlignment(QtCore.Qt.AlignLeft)
        
        hBox6 = QtWidgets.QHBoxLayout()
        hBox6.addWidget(scalar_label)
        hBox6.addWidget(self.scalar_option)
        hBox6.setAlignment(QtCore.Qt.AlignLeft)
        
        hBox7 = QtWidgets.QHBoxLayout()
        hBox7.addWidget(self.saveDataBtn)
        
        vBox1 = QtWidgets.QVBoxLayout()
        vBox1.addLayout(hBox1)
        vBox1.addLayout(hBox2)
        vBox1.addLayout(hBox3)
        vBox1.addLayout(hBox4)
        vBox1.addLayout(hBox5)
        vBox1.addLayout(hBox6)
        vBox1.addLayout(hBox7)
        
        layout0 = QtWidgets.QHBoxLayout()
        layout0.addWidget(dirLabel)
        layout0.addWidget(self.dirLineEdit)
        layout0.addWidget(self.extLineEdit)
        layout0.addWidget(self.dirBrowseBtn)
        
        layout1 = QtWidgets.QHBoxLayout()
        layout1.addLayout(vBox1)
        layout1.addWidget(self.fileTableView)
        layout1.addWidget(self.elementTableView)
        
        layout2 = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(message_label)
        layout2.addWidget(self.message)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(layout0)
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)
        self.setLayout(mainLayout)

        try:
            self.onLoadDirectory()
        except:
            print("Invalid directory or file; Try a new folder or remove problematic files.")
        self.onThetaUpdate()
        

    def operator(self):
        pass

    def getscalars(self):  #use Detector instead of scaler on the gui
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
        self.version = 0
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
        
        # for new HDF files
        if self.version == 1:
            self.message.setText('exchange_0: '+ self.img['exchange_0']['description'][0].decode('utf-8')
                                  + '; exchange_1: '+ self.img['exchange_1']['description'][0].decode('utf-8')
                                  + '; exchang_2: '+ self.img['exchange_2']['description'][0].decode('utf-8')
                                  + '; exchange_3: '+ self.img['exchange_3']['description'][0].decode('utf-8')
                                  )
            self.thetaLineEdit.setEnabled(False)
            self.dataTag.setEnabled(False)
            self.elementTag.setEnabled(False)

            if 'MAPS' in self.imgTags:
                self.imgTags.remove('MAPS')
            #if 'exchange_0' in self.imgTags:
                #self.imgTags.remove('exchange_0')

            for i in self.imgTags:
                self.imageTag.addItem(i)
            
            if 'exchange' in self.imgTags:
                indx = self.imgTags.index('exchange')
                self.imageTag.setCurrentIndex(indx)
            else: 

                try:
                    indx = self.imgTags.index(self.auto_image_tag)
                except:
                    indx = 0
                self.imageTag.setCurrentIndex(indx)
                

        if self.version == 0:
            self.message.clear()
            self.thetaLineEdit.setEnabled(True)
            self.dataTag.setEnabled(True)
            self.elementTag.setEnabled(True)
            self.operator_option.setEnabled(False)
            self.scalar_option.setEnabled(False)

            for i in range(len(self.imgTags)):
                self.imageTag.addItem(self.imgTags[i])
            if self.auto_image_tag in self.imgTags:
                indx = self.imgTags.index(self.auto_image_tag)
            else:
                indx = self.imgTags.index("MAPS")
            self.imageTag.setCurrentIndex(indx)

    def getDataTag(self):  #no name on the GUI; the one below image tag
        # for new HDF files        
        if self.version == 1:
            indx = self.imageTag.currentIndex()
            if indx == -1:
                return
            
            # self.dataTag.clear()
            self.dataTag.addItem('data')
            self.parent.params.image_tag = self.imageTag.currentText()
            self.parent.params.data_tag = self.dataTag
            self.elementTag.clear()
            self.elementTag.addItem('data_names')
            self.parent.params.elementTag = self.elementTag
            # for exchange_0
            if self.imageTag.currentText() == 'exchange_0':
                self.scalar_option.clear()
                self.operator_option.setEnabled(False)
                self.scalar_option.setEnabled(False)
            else:
                self.operator_option.setEnabled(True)
                self.scalar_option.setEnabled(True)
                self.scalar_options = {}
                scalar_list = list(self.img['exchange_1']['scaler_names'])
                scalar_list = [scalar_list[i].decode() for i in range(len(scalar_list))]
                self.scalar_option.clear()
                
                for i in range(len(scalar_list)):
                    self.scalar_option.addItem(scalar_list[i])

        if self.version == 0:
            # for old 2IDE HDF files with "exchange"
            if self.imageTag.currentText() == 'exchange':
                self.message.setText('exchange: Fitted normalized by DS-IC')
                self.dataTag.clear()
                self.dataTag.addItem('images')
                self.elementTag.clear()
                self.elementTag.addItem('images_names')
                self.thetaLineEdit.setEnabled(True)
                self.dataTag.setEnabled(False)
                self.elementTag.setEnabled(False)
                self.operator_option.setEnabled(False)
                self.scalar_option.clear()
                self.scalar_option.setEnabled(False)
            # for old 2IDE HDF files without "exchange"    
            else: 
                # for read 
                self.message.clear()
                self.dataTags = {}
                self.elementTags = {}
                self.scalar_options = {}

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

                    if self.auto_element_tag in self.dataTags:
                        self.elementTag.setCurrentText(self.auto_element_tag)
                except KeyError:
                    pass

                try:
                    indx2 = self.dataTags[indx].index(self.auto_data_tag)
                    self.dataTag.setCurrentIndex(indx2)
                    indx3 = self.elementTags[indx].index(self.auto_element_tag)
                    self.elementTag.setCurrentIndex(indx3)
                except ValueError:
                    pass
                
                scalar_list = list(self.img['MAPS']['scaler_names'])
                scalar_list = [scalar_list[i].decode() for i in range(len(scalar_list))]
                self.scalar_option.clear()
                
                for i in range(len(scalar_list)):
                    self.scalar_option.addItem(scalar_list[i])
                    
                self.parent.params.image_tag = self.imageTag.currentText()
                self.parent.params.data_tag = self.dataTag.currentText()
                #self.parent.params.detector_tag = self.scaler_option.currentText()
                
                self.thetaLineEdit.setEnabled(True)
                self.dataTag.setEnabled(True)
                self.elementTag.setEnabled(True)
                self.operator_option.setEnabled(True)
                self.scalar_option.setEnabled(True)
                
    def getElementList(self):
        if self.version == 0:   #legacy data
            fpath = self.fileTableModel.getFirstCheckedFilePath()
            image_tag = self.imageTag.currentText()
            element_tag = self.elementTag.currentText()
            self.parent.params.element_tag = element_tag
            self.parent.params.data_tag = self.dataTag.currentText()
            self.elementTableModel.loadElementNames(fpath, image_tag, element_tag)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))   

        if self.version == 1:   #9idbdata
            fpath = self.fileTableModel.getFirstCheckedFilePath()
            image_tag = self.imageTag.currentText()
            element_tag = self.elementTag.currentText()
            self.parent.params.element_tag = self.imageTag.currentText()
            self.parent.params.data_tag = self.dataTag.currentText()
            self.elementTableModel.loadElementNames(fpath, image_tag, element_tag)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))
            
        # if self.version == 2:   #2ide data


    def checkVersion(self):
        #temporary definition of 'version'
        exchange_bool = list(self.img)
        self.version = 'exchange_1' in exchange_bool
        return self.version

    def onThetaUpdate(self):
        # version defines file format and how to read thetas from it.
        path_files = self.fileTableModel.getAllFiles()
        #get path_files list
        thetaPV = self.thetaLineEdit.text()
        thetas = load_thetas(path_files, self.imageTag.currentText(), self.version, thetaPV)

        self.parent.params.theta_pv = thetaPV
        self.parent.params.input_path = self.dirLineEdit.text()
        self.fileTableModel.update_thetas(thetas)
        if self.parent.params.sorted_angles == True:
            self.fileTableView.sortByColumn(1, 0)
        return

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


        element_index = [elements.index(j) for j in self.use_elements]
        self.parent.params.selected_elements = str(element_index)

        self.data = xfluo.read_mic_xrf(path_files, element_index, img_tag, data_tag, element_tag)
        return self.data, self.use_elements, self.use_thetas, use_files
