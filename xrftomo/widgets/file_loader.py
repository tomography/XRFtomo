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


from PyQt5 import QtWidgets, QtCore, QtGui
import xrftomo
import h5py
import numpy as np
import os
from xrftomo.file_io.reader import *

class FileTableWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(FileTableWidget, self).__init__()
        self.parent = parent
        self._num_cols = 4
        self._num_row = 4
        self.auto_load_settings = eval(self.parent.params.load_settings)
        self.auto_theta_pv = self.parent.params.theta_pv
        self.auto_input_path = self.parent.params.input_path
        self.auto_image_tag = self.parent.params.image_tag
        self.auto_data_tag = self.parent.params.data_tag
        self.auto_element_tag = self.parent.params.element_tag
        self.auto_quant_tag = self.parent.params.quant_tag
        self.auto_scaler_tag = self.parent.params.scaler_tag
        #self.auto_detector_tag = self.parent.params.detector_tag
        self.auto_sorted_angles = self.parent.params.sorted_angles
        self.auto_selected_elements = eval(self.parent.params.selected_elements)
        self.initUI()

    def initUI(self):
        self.fileTableModel = xrftomo.FileTableModel()
        self.fileTableView = QtWidgets.QTableView()
        self.fileTableView.setModel(self.fileTableModel)
        self.fileTableView.setSortingEnabled(True)
        self.fileTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.fileTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.fileTableView.customContextMenuRequested.connect(self.onFileTableContextMenu)

        self.elementTableModel = xrftomo.ElementTableModel()
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
        # self.dirBrowseBtn = QtWidgets.QPushButton('Browse')
        # self.dirBrowseBtn.clicked.connect(self.onDirBrowse)

        self.thetaOptions = ['2xfm:m53.VAL', '2xfm:m36.VAL','2xfm:m58.VAL', '9idbTAU:SM:ST:ActPos']
        thetaCompleter = QtWidgets.QCompleter(self.thetaOptions)
        self.thetaLabel = QtWidgets.QLabel('Theta PV:')
        self.thetaLabel.setFixedWidth(90)
        self.thetaLabel.setVisible(False)
        self.thetaLineEdit = QtWidgets.QLineEdit(self.auto_theta_pv)
        self.thetaLineEdit.setCompleter(thetaCompleter)
        # self.thetaLineEdit.textChanged.connect(self.onThetaPVChange)
        self.thetaLineEdit.returnPressed.connect(self.onThetaUpdate)
        self.thetaLineEdit.setFixedWidth(122.5)
        self.thetaLineEdit.setVisible(False)


        imageTag_label = QtWidgets.QLabel('image tag:')
        imageTag_label.setFixedWidth(90)
        self.imageTag = QtWidgets.QComboBox()
        self.imageTag.activated.connect(self.getDataTag)
        self.imageTag.activated.connect(self.setup_element_list)
        self.imageTag.setFixedWidth(122.5)

        dataTag_label = QtWidgets.QLabel('data tag')
        dataTag_label.setFixedWidth(90)
        self.dataTag = QtWidgets.QComboBox()
        # self.dataTag.currentIndexChanged.connect(self.getDataTag)
        self.dataTag.currentIndexChanged.connect(self.setup_element_list)
        self.dataTag.setFixedWidth(122.5)

        self.elementTag_label = QtWidgets.QLabel('Elements:')
        self.elementTag_label.setFixedWidth(90)

        self.elementTag = QtWidgets.QComboBox()
        self.elementTag.currentIndexChanged.connect(self.element_tag_changed)
        self.elementTag.setFixedWidth(122.5)

        quant_label = QtWidgets.QLabel('quant options:')
        quant_label.setFixedWidth(90)
        self.quantTag = QtWidgets.QComboBox()
        # self.scalerTag.currentIndexChanged.connect(self.getScalerOptions)
        self.quantTag.setFixedWidth(122.5)

        scaler_label = QtWidgets.QLabel('Normalize by:')
        scaler_label.setFixedWidth(90)
        self.scalerTag = QtWidgets.QComboBox()
        self.scalerTag.currentIndexChanged.connect(self.setup_scaler_list)
        # self.imageTag.activated.connect(self.setup_scaler_list())

        self.scalerTag.setFixedWidth(122.5)

        self.saveDataBtn = QtWidgets.QPushButton('Save to Memory')
        # self.saveDataBtn.clicked.connect(self.onSaveDataInMemory)
        # self.saveDataBtn.setEnabled(False)
        self.saveDataBtn.setFixedWidth(220.5)

        message_label = QtWidgets.QLabel('Messages:')
        self.message = QtWidgets.QTextEdit()
        self.message.setReadOnly(True)
        self.message.setMaximumHeight(20)
        self.message.setText('')

        hBox1 = QtWidgets.QHBoxLayout()
        hBox1.addWidget(self.thetaLabel)
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
        hBox4.addWidget(self.elementTag_label)
        hBox4.addWidget(self.elementTag)
        hBox4.setAlignment(QtCore.Qt.AlignLeft)

        hBox5 = QtWidgets.QHBoxLayout()
        hBox5.addWidget(quant_label)
        hBox5.addWidget(self.quantTag)
        hBox5.setAlignment(QtCore.Qt.AlignLeft)

        hBox6 = QtWidgets.QHBoxLayout()
        hBox6.addWidget(scaler_label)
        hBox6.addWidget(self.scalerTag)
        hBox6.setAlignment(QtCore.Qt.AlignLeft)

        hBox7 = QtWidgets.QHBoxLayout()
        hBox7.addWidget(self.saveDataBtn)
        hBox7.setAlignment(QtCore.Qt.AlignLeft)

        vBox1 = QtWidgets.QVBoxLayout()
        vBox1.addLayout(hBox1)
        vBox1.addLayout(hBox2)
        vBox1.addLayout(hBox3)
        vBox1.addLayout(hBox4)
        vBox1.addLayout(hBox5)
        vBox1.addLayout(hBox6)
        vBox1.addLayout(hBox7)
        # vBox1.setFixedWidth(275)

        layout0 = QtWidgets.QHBoxLayout()
        layout0.addWidget(dirLabel)
        layout0.addWidget(self.dirLineEdit)
        layout0.addWidget(self.extLineEdit)
        # layout0.addWidget(self.dirBrowseBtn)

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
        # self.dataTag.currentIndexChanged.connect(self.getElementList)

        try:
            self.onLoadDirectory()
        except:
            print("Invalid directory or file; Try a new folder or remove problematic files.")
        self.onThetaUpdate()





    def onLoadDirectory(self, files = None):
        self.version = 0

        #specify file extension by 'majority rule' for a given directory
        if files == None:
            try:
                filenames = os.listdir(self.dirLineEdit.text())


            except FileNotFoundError:
                self.message.setText("directory probably not mounted")
                return
            extension_list = ["."+ x.split(".")[-1] for x in filenames]
            unique_ext = list(set(extension_list))
            counter = 0
            for i in unique_ext:
                tmp_counter = 0
                for j in extension_list:
                    tmp_counter += i == j
                if tmp_counter > counter:
                    dominant_ext = i
                    counter = tmp_counter
                    self.extLineEdit.setText("*"+dominant_ext)
                    ext = dominant_ext
        else:
            ext = "*."+ files[0].split(".")[-1]
            self.extLineEdit.setText(ext)


        #TODO: get filetablemodel to accept only the selected files and not all files in the directory.
        self.fileTableModel.loadDirectory(self.dirLineEdit.text(), self.extLineEdit.text())
        fpath = self.fileTableModel.getFirstCheckedFilePath()

        if fpath == None:
            self.message.setText('Invalid directory')
            return
        self.fileTableModel.setAllChecked(True)

        if ext == '*.h5' or ext == '.h5':
            try:
                self.imageTag.clear()
                self.getImgTags()
                self.getDataTag()
                self.setup_element_list()
                self.setup_quant_list()
                self.setup_scaler_list()
                self.onThetaUpdate()

                try: #set auto_load options here:

                    img_indx = self.imgTags.index(self.auto_image_tag)
                    self.imageTag.setCurrentIndex(img_indx)

                    data_indx = self.dataTags.index(self.auto_data_tag)
                    self.dataTag.setCurrentIndex(data_indx)

                    elem_indx = self.elementTags[self.imageTag.currentIndex()].index(self.auto_element_tag)
                    self.elementTag.setCurrentIndex(elem_indx)
                    self.element_tag = self.elementTag.currentText()
                    self.element_tag_changed()

                    quant_indx = self.quantTags.index(self.auto_quant_tag)
                    self.quantTag.setCurrentIndex(quant_indx)

                    scaler_indx = self.scalerTags.index(self.auto_scaler_tag)
                    self.scalerTag.setCurrentIndex(scaler_indx)

                except:
                    pass
                self.imageTag.currentIndexChanged.connect(self.setup_element_list)
                self.elementTag.currentIndexChanged.connect(self.element_tag_changed)
                # self.scalerTag.currentIndexChanged.connect(self.scaler_tag_changed)

            except KeyError:
                pass

        if ext == '*.tiff' or ext == ".tiff" or ext == ".tif" or ext == "*.tif":
            # TODO: when loading from filemenu, check only files which were selected
            if not self.elementTableModel.arrayData == []:

                for i in range(1,len(self.elementTableModel.arrayData)):
                    self.elementTableModel.arrayData.pop()
                self.elementTableModel.arrayData[0].element_name = "Channel_1"
                self.elementTableModel.arrayData[0].use = True
            else:
                pass

            self.imageTag.setEnabled(False)
            self.dataTag.setEnabled(False)
            self.scalerTag.setEnabled(False)
            self.message.setText("Load angle information using txt or csv file")
            pass
        return

    def getImgTags(self):
        fpath = self.fileTableModel.getFirstCheckedFilePath()
        self.img = h5py.File(fpath,"r")
        tmpTags = list(self.img.keys())
        self.imgTags =  list(filter(lambda k: 'version' not in k, tmpTags))
        self.version = self.checkVersion()
        self.description = []

        # for new HDF files
        if self.version == 1:
            try:
                self.message.setText('exchange_0: '+ self.img['exchange_0']['description'][0].decode('utf-8')
                                      + '; exchange_1: '+ self.img['exchange_1']['description'][0].decode('utf-8')
                                      + '; exchang_2: '+ self.img['exchange_2']['description'][0].decode('utf-8')
                                      + '; exchange_3: '+ self.img['exchange_3']['description'][0].decode('utf-8')
                                      )
            except:
                self.message.setText("no description available")
            self.thetaLineEdit.setEnabled(False)
            self.dataTag.setEnabled(False)

            if 'MAPS' in self.imgTags:
                self.imgTags.remove('MAPS')

            try:

                for i in self.img:
                    if i !='MAPS':
                        self.description.append(self.img[i]['description'][0].decode('utf-8'))

                for i in self.description:
                    self.imageTag.addItem(i)

            except:

                for i in self.imgTags:
                    self.imageTag.addItem(i)

        if self.version == 0:
            self.message.clear()
            # self.thetaLineEdit.setEnabled(True)
            self.dataTag.setEnabled(True)
            # self.scalerTag.setEnabled(True)

            for i in range(len(self.imgTags)):
                self.imageTag.addItem(self.imgTags[i])

            # if 'exchange' in self.imgTags and 'MAPS' in self.imgTags:
            #     self.imgTags.remove('MAPS')


            indx = 0
            self.imageTag.setCurrentIndex(indx)

            # else:
            #     indx = self.imgTags.index("MAPS")
            # self.imageTag.setCurrentIndex(indx)

    def getDataTag(self):  #no name on the GUI; the one below image tag
        # for new HDF files
        if self.version == 1:
            indx = self.imageTag.currentIndex()
            if indx == -1:
                return

            self.dataTag.clear()
            self.dataTag.addItem('data')

        if self.version == 0:
            self.message.clear()
            self.dataTags = []
            self.dataTags = list(self.img[self.imgTags[self.imageTag.currentIndex()]])
            indx = self.imageTag.currentIndex()
            if indx == -1:
                return

            # #filtering  drop-down menu to inlcude only relevant entries.
            temp_tags1 = list(filter(lambda k: not 'names' in k, self.dataTags))
            temp_tags1 = list(filter(lambda k: not 'units' in k, temp_tags1))
            temp_tags1 = list(filter(lambda k: not 'axis' in k, temp_tags1))
            temp_tags1 = list(filter(lambda k: not 'quant' in k, temp_tags1))
            # temp_tags2 = list(filter(lambda k: 'scalers' in k, self.dataTags[indx]))
            self.dataTags = temp_tags1
            try:
                self.dataTag.disconnect()
            except TypeError:
                pass
            self.dataTag.clear()
            for i in range(len(self.dataTags)):
                self.dataTag.addItem(self.dataTags[i])
                self.dataTag.setCurrentIndex(0)
            self.dataTag.setEnabled(True)

    def getElements(self):
        img_tag = self.imageTag.currentText()
        element_tag = self.elementTag.currentText()
        element_list = list(self.img[img_tag][element_tag])
        element_list = [x.decode("utf-8") for x in element_list]
        element_idxs = []
        element_names = []
        for i in range(len(element_list)):
            if self.elementTableModel.arrayData[i].use:
                element_names.append(self.elementTableModel.arrayData[i].element_name)
                element_idxs.append(i)

        return element_names, element_idxs


    def element_tag_changed(self):
        fpath = self.fileTableModel.getFirstCheckedFilePath()
        image_tag = self.imgTags[self.imageTag.currentIndex()]
        self.element_tag = self.elementTag.currentText()
        self.elementTableModel.loadElementNames(fpath, image_tag, self.element_tag)
        self.elementTableModel.setAllChecked(False)
        self.elementTableModel.setChecked(self.auto_selected_elements, (True))
        return

    def setup_element_list(self):
        fpath = self.fileTableModel.getFirstCheckedFilePath()
        image_tag = self.imageTag.currentText()
        self.message.clear()
        self.elementTags = {}
        num_image_tags = len(self.imgTags)
        for i in range(num_image_tags):      #get element tags
            self.elementTags[i] = list(self.img[self.imgTags[i]])
            self.elementTags[i] = list(filter(lambda k: 'names' in k, self.elementTags[i]))
            self.elementTags[i] = list(filter(lambda k: 'quant' not in k, self.elementTags[i]))
        try:
            self.elementTag.disconnect()
        except TypeError:
            pass
        self.elementTag.clear()
        img_indx = self.imageTag.currentIndex()
        if img_indx == -1:
            return
        for i in range(len(self.elementTags[img_indx])):
            self.elementTag.addItem(self.elementTags[img_indx][i])
        self.elementTag.setCurrentIndex(0)
        self.element_tag = self.elementTag.currentText()

        self.elementTableModel.loadElementNames(fpath, image_tag, self.element_tag)
        self.elementTableModel.setAllChecked(False)
        self.elementTableModel.setChecked(self.auto_selected_elements, (True))

    def setup_quant_list(self):
        self.quantTag.clear()
        quant_indx = self.imageTag.currentIndex()
        if quant_indx == -1:
            return
        try:
            # #filtering  drop-down menu to inlcude only relevant entries.
            img_tag = self.imgTags[quant_indx]
            self.quantTags = list(self.img[img_tag])
            self.quantTags = list(filter(lambda k: 'quant' in k, self.quantTags))
            self.quantTags = list(filter(lambda k: 'names' not in k, self.quantTags))
            self.quantTags.insert(0,"None")
        except:
            print("no qaunts found")
            return
        try:
            for i in range(len(self.quantTags)):
                self.quantTag.addItem(self.quantTags[i])
            self.quantTag.setCurrentIndex(0)
        except:
            return
        return

    def setup_scaler_list(self):
        self.message.clear()
        tmpscalerTags = {}
        num_image_tags = len(self.imgTags)
        for i in range(num_image_tags):      #get scaler tags
            tmpscalerTags[i] = list(self.img[self.imgTags[i]])
            tmpscalerTags[i] = list(filter(lambda k: 'scaler' in k, tmpscalerTags[i]))
            tmpscalerTags[i] = list(filter(lambda k: 'names'  in k, tmpscalerTags[i]))
        try:
            self.scalerTag.disconnect()
        except TypeError:
            pass

        self.scalerTag.clear()
        scaler_indx = self.imageTag.currentIndex()
        if scaler_indx == -1:
            return
        try:
            # #filtering  drop-down menu to inlcude only relevant entries.
            img_tag = self.imgTags[scaler_indx]
            scaler_tag = tmpscalerTags[scaler_indx][0]
            self.scalerTags = list(self.img[img_tag][scaler_tag])
            self.scalerTags = [x.decode("utf-8") for x in self.scalerTags]
            self.scalerTags.insert(0, "None")
        except:
            print("no scalers found")
            return
        try:
            for i in range(len(self.scalerTags)):
                self.scalerTag.addItem(self.scalerTags[i])
            self.scalerTag.setCurrentIndex(0)
            self.scaler_tag = self.scalerTag.currentText()
        except:
            return
        return

    def normalizeData(self, data, scalers, quants):
        #normalize
        num_files = data.shape[1]
        num_elements= data.shape[0]
        for i in range(num_elements):
            for j in range(num_files):
                data[i,j] = data[i,j]/quants[i,j]
            data[i] = data[i]/scalers
        data[np.isnan(data)] = 0.0001
        data[data == np.inf] = 0.0001
        # for i in range(num_elements):
        #     norm_median = np.median(data[i, :, :, :])
        #     norm_mean = np.mean(data[i, :, :, :])
        #     norm_std = np.std(data[i, :, :, :])
        #     elem_max = np.max(data[i, :, :, :])
        #     norm_max = 3*norm_std + norm_mean
        #     for j in range(num_files):
        #         median_arr = np.ones_like(data[i,j])*norm_mean
        #         data[i,j] = [data[i,j] <= norm_max]*data[i,j,:,:]
        #         data[i,j] = data[i,j] + [data[i,j] == 1]*np.ones_like(data[i,j])*norm_max
        return data

    def checkVersion(self):
        #temporary definition of 'version'
        exchange_bool = list(self.img)

        try:
            theta_exists = self.img[list(self.img)[0]]["theta"][()]
            self.version = 1
        except:
            print("checking file version... No version info available")
            self.version = 0

        # if self.parent.forceLegacy.isChecked():
        #     self.version=0

        #Temporary hardcode version to 0 (legacy import mode)
        #self.version = 0

        # TODO: the auto_load_settings line will override non-legacy version, not good.
        # if self.auto_load_settings[0]:
        #     self.version = 0
        # try:
            # TODO: there may no longer be a legacy checkbox
            # if self.parent.legacy_chbx.isChecked():
            #     self.version = 0
            # if not self.parent.legacy_chbx.isChecked():
            #     self.version = 1
        # except:
        #     #checkboxes not yet defined
        #     pass
        return self.version

    def onThetaUpdate(self):
        # version defines file format and how to read thetas from it.
        path_files = self.fileTableModel.getAllFiles()
        #get path_files list
        thetaPV = self.thetaLineEdit.text()
        #TODO: check to see if thetas is available under exchange tag, if not, load in
        #legacy mode or just check under MAPS, or throw a warning (prompt user to enable
        #debug tools and enter PV otherweise load thetas file.
        try:
            thetas = load_thetas(path_files, self.imgTags[self.imageTag.currentIndex()], self.version, thetaPV)
        except:
            thetas=[]
            self.message.setText("directory probably not mounted.")
        if len(thetas) == 0:
            for i in self.thetaOptions:
                try:
                    thetas = load_thetas(path_files, self.imgTags[self.imageTag.currentIndex()], self.version, i)
                except:
                    print("trying theta PV {}".format(i))
                if len(thetas) >0:
                    if len(set(thetas)) > 1:
                        self.thetaLineEdit.setText(i)
                        break
                else:
                    thetas = np.ones(len(path_files))

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

    def reset_widgets(self):
        self.parent.imageProcessWidget.sld.setValue(0)
        self.parent.reconstructionWidget.sld.setValue(0)
        self.parent.reconstructionWidget.recon = []
        self.parent.sinogramWidget.sld.setValue(0)

    def onSaveDataInMemory(self):
        files = [i.filename for i in self.fileTableModel.arrayData]
        if len(files) == 0:
            self.message.setText('Directory probably not mounted')
            return [], [] , [], []
        thetas = [i.theta for i in self.fileTableModel.arrayData]
        elements = [i.element_name for i in self.elementTableModel.arrayData]
        files_bool = [i.use for i in self.fileTableModel.arrayData]
        elements_bool = [i.use for i in self.elementTableModel.arrayData]

        hdf_tag = self.imgTags[self.imageTag.currentIndex()]
        data_tag = self.dataTag.currentText()
        element_tag = self.element_tag
        quant_tag = self.quantTag.currentText()
        scaler_tag = self.scalerTag.currentText()

        k = np.arange(len(files))
        l = np.arange(len(elements))

        files = [files[j] for j in k if files_bool[j]==True]


        
        path_files = [self.fileTableModel.directory + '/' + s for s in files]


        thetas = np.asarray([thetas[j] for j in k if files_bool[j]==True])
        elements = [elements[j] for j in l if elements_bool[j]==True]

        #update auto-load parameters
        self.parent.params.input_path = self.dirLineEdit.text()
        self.parent.params.theta_pv = self.thetaLineEdit.text()
        self.parent.params.image_tag = self.imgTags[self.imageTag.currentIndex()]
        self.parent.params.data_tag = self.dataTag.currentText()
        self.parent.params.element_tag = element_tag
        self.parent.params.quant_tag = quant_tag
        self.parent.params.scaler_tag = scaler_tag
        self.parent.params.selected_elements = str(list(np.where(elements_bool)[0]))
        #self.parent.params.detector_tag = self.scaler_option.currentText()

        if len(elements) == 0:
            self.message.setText('no element selected.')
            return [], [] , [], []
        else:
            self.message.setText('loading files...')
        if all(x==thetas[0] for x in thetas):           #check if all values in thetas are the same: no theta info.
            self.message.setText('WARNING: No unique angle information. Double check Theta PV or current directory')
            # return [], [] , [], []

        self.parent.clear_all()
        try:
            scaler_exists = self.img[self.imageTag.currentText()]["scalers"]
            quant_tag = self.quantTag.currentText()
            scaler_tag = "scalers"
            scaler_idx = self.scalerTag.currentIndex()-1
            if scaler_idx<-1:
                scaler_idx = -1
        except:
            print("no 'scaler' tag found")
            scaler_tag = None
            quant_tag = None
            scaler_idx=-1

        # try:
        # data, scalers = xrftomo.read_mic_xrf(path_files, elements, hdf_tag, data_tag, element_tag, scaler_name)
        try:
            data, quants, scalers = xrftomo.read_mic_xrf(path_files, elements, hdf_tag, data_tag, element_tag, quant_tag, scaler_tag, scaler_idx)
        except:
            self.message.setText("invalid image/data/element tag combination. Load failed")
            return [], [], [], []

        if data is None or scalers is None:
            return [], [], [], []
        if self.scalerTag.currentText() != 'None':
            scaler_idx = self.scalerTag.currentIndex()-1
            quant_option = self.quantTag.currentText()
            elements, element_idxs = self.getElements()
            data = self.normalizeData(data, scalers, quants)
        self.message.setText('finished loading')

        data[np.isnan(data)] = 0.0001
        data[data == np.inf] = 0.0001

        return data, elements, thetas, files

