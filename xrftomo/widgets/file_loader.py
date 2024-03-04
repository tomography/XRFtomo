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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import xrftomo
import h5py
import numpy as np
import os
import sys

class FileTableWidget(QWidget):
    def __init__(self, parent):
        super(FileTableWidget, self).__init__()
        self.parent = parent
        self._num_cols = 4
        self._num_row = 4
        self.auto_load_settings = eval(self.parent.params.load_settings)
        self.auto_theta_tag = self.parent.params.theta_tag
        self.auto_input_path = self.parent.params.input_path
        self.auto_extension = self.parent.params.file_extension
        self.auto_element_tag = self.parent.params.element_tag
        self.auto_data_tag = self.parent.params.data_tag
        self.auto_scaler_tag = self.parent.params.scaler_tag
        self.auto_sorted_angles = self.parent.params.sorted_angles
        self.auto_selected_elements = eval(self.parent.params.selected_elements)
        self.auto_selected_scalers = eval(self.parent.params.selected_scalers)
        self.reader = self.parent.reader
        self.initUI()
        sys.stdout = xrftomo.gui.Stream(newText=self.parent.onUpdateText)

    def initUI(self):
        self.fileTableModel = xrftomo.FileTableModel()
        self.fileTableView = QTableView()
        self.fileTableView.setModel(self.fileTableModel)
        self.fileTableView.setSortingEnabled(True)
        self.fileTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fileTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileTableView.customContextMenuRequested.connect(self.onFileTableContextMenu)

        self.elementTableModel = xrftomo.ElementTableModel()
        self.elementTableView = QTableView()
        self.elementTableView.setModel(self.elementTableModel)
        self.elementTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.elementTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.elementTableView.customContextMenuRequested.connect(self.onElementTableContextMenu)

        self.scalerTableModel = xrftomo.ElementTableModel()
        self.scalerTableModel.columns = ['Scaler Map']
        self.scalerTableView = QTableView()
        self.scalerTableView.setModel(self.scalerTableModel)
        self.scalerTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scalerTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scalerTableView.customContextMenuRequested.connect(self.onScalerTableContextMenu)

        dirLabel = QLabel('Directory:')
        self.dirLineEdit = QLineEdit(self.auto_input_path)
        self.dirLineEdit.returnPressed.connect(self.onLoadDirectory)
        self.extLineEdit = QLineEdit(self.auto_extension)
        self.extLineEdit.setMaximumSize(50, 30)
        self.extLineEdit.returnPressed.connect(self.onLoadDirectory)


        self.populate_scroll_area()


        layout0 = QHBoxLayout()
        layout0.addWidget(dirLabel)
        layout0.addWidget(self.dirLineEdit)
        layout0.addWidget(self.extLineEdit)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.scroll)
        layout1.addWidget(self.fileTableView)
        layout1.addWidget(self.elementTableView)
        layout1.addWidget(self.scalerTableView)



        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout0)
        mainLayout.addLayout(layout1)

        self.setLayout(mainLayout)
        try:
            #TODO: get files and
            self.onLoadDirectory()
        except:
            print("Invalid directory or file; Try a new folder or remove problematic files.")

    def populate_scroll_area(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumWidth(290)

        item_dict = {}  # [type(button, file, path, dropdown), descriptions[idx], choices[idx],defaults[idx]]
        item_dict["data_menu"] = [["label","menu"], "", None, None]
        item_dict["element_menu"] = [["label","menu"], "", None, None]
        item_dict["scaler_menu"] = [["label","menu"], "", None, None]
        item_dict["theta_menu"] = [["label","menu"], "", None, None]
        item_dict["saveDataBtn"] = [["button"], "", None, None]

        vb_files = QVBoxLayout()
        widgetsizes = [240, 115, 50]
        for i, key in enumerate(item_dict.keys()):
            widget_items = item_dict[key][0]
            attrs = item_dict[key]
            widgetsize = widgetsizes[len(widget_items)-1]
            line_num = "line_{}".format(i)
            setattr(self, line_num, QHBoxLayout())
            line = self.__dict__[line_num]

            for widget in widget_items:
                if widget == "label":
                    name = key.split("_")[0]+"_tag"
                    setattr(self, name, QLabel(name))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    line.addWidget(object)

                elif widget == "menu":
                    setattr(self, key, QMenu(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.aboutToHide.connect(self.menu_event)
                    line.addWidget(object)

                elif widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText("save data to memory")
                    line.addWidget(object)
                else:
                    pass
            vb_files.addLayout(line)
        # vb_files.setSpacing(0)
        # vb_files.setContentsMargins(0, 0, 0, 0)
        self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        self.scroll_widget.setLayout(vb_files)
        self.scroll.setWidget(self.scroll_widget)

        return

    def menu_event(self):
        if not self.data_menu.isVisible():
            self.data_menu.setHidden(False)
            self.data_menu.show()
        if not self.element_menu.isVisible():
            self.element_menu.setHidden(False)
            self.element_menu.show()
        if not self.theta_menu.isVisible():
            self.theta_menu.setHidden(False)
            self.theta_menu.show()
        return

    def onLoadDirectory(self, fnames=None, path=None):
        try:
            self.data_menu.clear()
            self.element_menu.clear()
            self.theta_menu.clear()
            ext = self.extLineEdit.text()
        except Exception as error:
            print(error)

        if path == None:
            try:
                path = self.dirLineEdit.text()
            except:
                print('Invalid directory')
                return
        if fnames == None or fnames == []:
            try:
                fileNames = [x for x in os.listdir(path)]
                fileNames = [file for file in fileNames if file.split(".")[-1] == ext]
            except Exception as e:
                print(e)
                return

            # TODO: filter files begining with "._"
            with_ = [x for x in fileNames if x.startswith(".")]
            without_ = [x for x in fileNames if x not in with_]
            fnames = [path+"/"+file for file in without_]
            if fileNames == []:
                print("no valid files, check file extension")
                return

        self.fileTableModel.update_fnames(fnames)
        self.fileTableModel.setAllChecked(True)

        if "h5" in ext:
            try:

                self.img = h5py.File(fnames[0], "r")
                self.data_tag = self.data_menu.addMenu("data")
                self.data_tag.objectName = "data_tag"
                self.populate_data_menu(self.img, self.data_tag)
                self.data_tag.setTitle(self.auto_data_tag)

                self.element_tag = self.element_menu.addMenu("element")
                self.element_tag.objectName = "element_tag"
                self.populate_element_menu(self.img, self.element_tag)
                self.element_tag.setTitle(self.auto_element_tag)

                self.scaler_tag = self.element_menu.addMenu("scaler")
                self.scaler_tag.objectName = "scaler_tag"
                self.populate_scaler_menu(self.img, self.scaler_tag)
                self.scaler_tag.setTitle(self.auto_scaler_tag)

                self.theta_tag = self.theta_menu.addMenu("theta")
                self.populate_theta_menu(self.img, self.theta_tag)
                self.theta_tag.objectName = "theta_tag"
                self.theta_tag.setTitle(self.auto_theta_tag)

                tags_exist = self.check_auto_tags()
                if tags_exist:
                    pass
                else:
                    return

                self.element_tag_changed()
                self.scaler_tag_changed()
                try:
                    thetas_loaded = self.try_theta()
                except Exception as error:
                    print(error)

                if not thetas_loaded:
                    self.theta_tag_changed()


            except KeyError:
                pass

        if ext == '*.tiff' or ext == ".tiff" or ext == ".tif" or ext == "*.tif":
            # TODO: when loading from filemenu, check only files which were selected
            if not self.elementTableModel.arrayData == []:

                for i in range(1,len(self.elementTableModel.arrayData)):
                    self.elementTableModel.arrayData.pop()
                self.elementTableModel.arrayData[0].element_name = "Channel_1"
                self.elementTableModel.arrayData[0].use = True
            print("Load angle information using txt or csv file")
        return

    def try_theta(self):
        success = False
        path_files = self.fileTableModel.getAllFiles()
        thetas = self.reader.load_thetas(path_files, "dummy", 3)
        self.fileTableModel.update_thetas(thetas)
        self.fileTableView.sortByColumn(1, 0)
        try:
            if max(thetas) - min(thetas) > 5:
                success = True
        except:
            print("thetas is None")
        return success
    def check_auto_tags(self):
        data_tag_exists = self.auto_data_tag in self.img
        element_tag_exists = self.auto_element_tag in self.img
        scaler_tag_exists = self.auto_scaler_tag in self.img
        # theta_tag_exists = self.auto_theta_tag in self.img

        if data_tag_exists and element_tag_exists and scaler_tag_exists:
            return True
        else:
            default = list(self.img.keys())[0]
            self.data_tag.setTitle(default)
            self.element_tag.setTitle(default)
            self.scaler_tag.setTitle(default)
            self.theta_tag.setTitle(default)
            return False

    def populate_data_menu(self, obj, menu):
        keys = obj.keys()
        for key in keys:
            if isinstance(obj[key],h5py.Group):
                sub_menu = menu.addMenu(key)
                self.populate_data_menu(obj[key], sub_menu)
            elif isinstance(obj[key],h5py.Dataset):
                sub_action = QAction(key,self)
                menu.addAction(sub_action)
                sub_action.triggered.connect(self.update_data_tag)
        return menu

    def populate_element_menu(self, obj, menu):
        keys = obj.keys()
        for key in keys:
            if isinstance(obj[key],h5py.Group):
                sub_menu = menu.addMenu(key)
                self.populate_element_menu(obj[key], sub_menu)
            elif isinstance(obj[key],h5py.Dataset):
                sub_action = QAction(key,self)
                menu.addAction(sub_action)
                sub_action.triggered.connect(self.update_element_tag)
        return menu

    def populate_scaler_menu(self, obj, menu):
        keys = obj.keys()
        for key in keys:
            if isinstance(obj[key],h5py.Group):
                sub_menu = menu.addMenu(key)
                self.populate_scaler_menu(obj[key], sub_menu)
            elif isinstance(obj[key],h5py.Dataset):
                sub_action = QAction(key,self)
                menu.addAction(sub_action)
                sub_action.triggered.connect(self.update_scaler_tag)
        return menu

    def populate_theta_menu(self, obj, menu):
        keys = obj.keys()
        for key in keys:
            if isinstance(obj[key],h5py.Group):
                sub_menu = menu.addMenu(key)
                self.populate_theta_menu(obj[key], sub_menu)
            elif isinstance(obj[key],h5py.Dataset):
                sub_action = QAction(key,self)
                menu.addAction(sub_action)
                sub_action.triggered.connect(self.update_theta_tag)
        return menu

    def update_data_tag(self):
        self.data_tag.setTitle("data_tag")
        lvl0 = ""
        lvl1 = ""
        lvl2 = ""
        lvl3 = ""
        lvl4 = ""
        try:
            # hardcoding path to max depth of 4.
            lvl0 = self.sender().text()
            lvl1 = self.sender().associatedWidgets()[0].title()
            lvl2 = self.sender().associatedWidgets()[0].parent().title()
            lvl3 = self.sender().associatedWidgets()[0].parent().parent().title()
            lvl4 = self.sender().associatedWidgets()[0].parent().parent().parent().title()
        except:
            pass
        lvl_list = [lvl0, lvl1, lvl2, lvl3, lvl4]
        lvls = []
        for i in lvl_list:
            if i != "data_tag":
                lvls.insert(0, i)
            else:
                break
        self.data_tag.setTitle("/".join(lvls))
        self.data_menu.setFixedSize(123,25)
        self.data_menu.show()

    def update_element_tag(self):
        self.element_tag.setTitle("element_tag")
        lvl0 = ""
        lvl1 = ""
        lvl2 = ""
        lvl3 = ""
        lvl4 = ""
        try:
            #hardcoding path to max depth of 4.
            lvl0 = self.sender().text()
            lvl1 = self.sender().associatedWidgets()[0].title()
            lvl2 = self.sender().associatedWidgets()[0].parent().title()
            lvl3 = self.sender().associatedWidgets()[0].parent().parent().title()
            lvl4 = self.sender().associatedWidgets()[0].parent().parent().parent().title()
        except:
            pass
        lvl_list = [lvl0, lvl1, lvl2, lvl3, lvl4]
        lvls = []
        for i in lvl_list:
            if i != "element_tag":
                lvls.insert(0, i)
            else:
                break
        self.element_tag.setTitle("/".join(lvls))
        self.element_menu.setFixedSize(123,25)
        self.element_menu.show()
        self.element_tag_changed()

    def update_scaler_tag(self):
        self.scaler_tag.setTitle("scaler_tag")
        lvl0 = ""
        lvl1 = ""
        lvl2 = ""
        lvl3 = ""
        lvl4 = ""
        try:
            #hardcoding path to max depth of 4.
            lvl0 = self.sender().text()
            lvl1 = self.sender().associatedWidgets()[0].title()
            lvl2 = self.sender().associatedWidgets()[0].parent().title()
            lvl3 = self.sender().associatedWidgets()[0].parent().parent().title()
            lvl4 = self.sender().associatedWidgets()[0].parent().parent().parent().title()
        except:
            pass
        lvl_list = [lvl0, lvl1, lvl2, lvl3, lvl4]
        lvls = []
        for i in lvl_list:
            if i != "scaler_tag":
                lvls.insert(0, i)
            else:
                break
        self.scaler_tag.setTitle("/".join(lvls))
        self.scaler_menu.setFixedSize(123,25)
        self.scaler_menu.show()
        self.scaler_tag_changed()
    def update_theta_tag(self):
        self.theta_tag.setTitle("theta_tag")
        lvl0 = ""
        lvl1 = ""
        lvl2 = ""
        lvl3 = ""
        lvl4 = ""
        try:
            #hardcoding path to max depth of 4.
            lvl0 = self.sender().text()
            lvl1 = self.sender().associatedWidgets()[0].title()
            lvl2 = self.sender().associatedWidgets()[0].parent().title()
            lvl3 = self.sender().associatedWidgets()[0].parent().parent().title()
            lvl4 = self.sender().associatedWidgets()[0].parent().parent().parent().title()
        except:
            pass
        lvl_list = [lvl0, lvl1, lvl2, lvl3, lvl4]
        lvls = []
        for i in lvl_list:
            if i != "theta_tag":
                lvls.insert(0, i)
            else:
                break
        theta_tag = "/".join(lvls)
        theta_tag = theta_tag.strip(",")
        self.theta_tag.setTitle(theta_tag)
        #TODO: errors here when incompatible tags selected
        #TODO: clear menu items when loading new data
        dataset = self.img[self.theta_tag.title()]
        dataset = np.array(dataset).astype('U13')
        self.create_table(dataset)
        self.theta_menu.setFixedSize(123,25)
        self.theta_menu.show()
        self.theta_tag_changed()

    def create_table(self, dataset):
        self.tablewidget = QTableWidget()

        if dataset.ndim == 1:
            numcols = 1
            numrows = len(dataset)
            self.tablewidget.setColumnCount(numcols)
            self.tablewidget.setRowCount(numrows)
            for row in range(numrows):
                for column in range(numcols):
                    self.tablewidget.setItem(row, column, QTableWidgetItem((dataset[row])))
        elif dataset.ndim == 2:
            numcols = len(dataset[0])  # ( to get number of columns, count number of values in first row( first row is data[0]))
            numrows = len(dataset)
            self.tablewidget.setColumnCount(numcols)
            self.tablewidget.setRowCount(numrows)
            for row in range(numrows):
                for column in range(numcols):
                    self.tablewidget.setItem(row, column, QTableWidgetItem((dataset[row][column])))
        else:
            print("more than 2 dimensions")
            return
        self.tablewidget.show()
        self.tablewidget.itemDoubleClicked.connect(self.clicked_event)

    def clicked_event(self):
        current_row = self.tablewidget.currentRow()
        current_column = self.tablewidget.currentColumn()
        cell_value = self.tablewidget.item(current_row, current_column).text()
        theta_tag = "{}/{}".format(self.theta_tag.title(),self.tablewidget.currentItem().text())
        theta_tag = theta_tag.strip(",")
        self.theta_tag.setTitle(theta_tag)
        self.theta_tag_changed()
        self.tablewidget.close()


    def getElements(self):
        element_tag = self.element_tag
        element_list = list(self.img[element_tag])
        element_list = [x.decode("utf-8") for x in element_list]
        element_idxs = []
        element_names = []
        for i in range(len(element_list)):
            if self.elementTableModel.arrayData[i].use:
                element_names.append(self.elementTableModel.arrayData[i].element_name)
                element_idxs.append(i)
        return element_names, element_idxs

    def element_tag_changed(self):
        try:
            element_tag = self.element_tag.title()
            element_list = list(self.img[element_tag])
            elements = [x.decode("utf-8") for x in element_list]
            self.elementTableModel.loadElementNames(elements)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))
            print("")
        except:
            print("invalid tag option")
        return

    def scaler_tag_changed(self):
        try:
            scaler_tag = self.scaler_tag.title()
            scaler_list = list(self.img[scaler_tag])
            scalers = [x.decode("utf-8") for x in scaler_list]
            self.scalerTableModel.loadElementNames(scalers)
            self.scalerTableModel.setAllChecked(False)
            self.scalerTableModel.setChecked(self.auto_selected_scalers, (True))
            print("")
        except:
            print("invalid tag option")
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
        return data

    def theta_tag_changed(self):
        try:
            path_files = self.fileTableModel.getAllFiles()
            theta_tag = self.theta_tag.title()

            thetas = self.reader.load_thetas(path_files, theta_tag, 1)
            print("")
            self.fileTableModel.update_thetas(thetas)
            self.fileTableView.sortByColumn(1, 0)
        except:
            thetas=[]
            print("directory probably not mounted or incorrect theta tag")



        return

    def onFileTableContextMenu(self, pos):
        if self.fileTableView.selectionModel().selection().indexes():
            rows = []
            for i in self.fileTableView.selectionModel().selection().indexes():
                rows += [i.row()]
            menu = QMenu()
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
            menu = QMenu()
            check_action = menu.addAction("Check")
            uncheck_action = menu.addAction("Uncheck")
            action = menu.exec_(self.elementTableView.mapToGlobal(pos))
            if action == check_action or action == uncheck_action:
                self.elementTableModel.setChecked(rows, (check_action == action))

    def onScalerTableContextMenu(self, pos):
        if self.scalerTableView.selectionModel().selection().indexes():
            rows = []
            for i in self.scalerTableView.selectionModel().selection().indexes():
                rows += [i.row()]
            menu = QMenu()
            check_action = menu.addAction("Check")
            uncheck_action = menu.addAction("Uncheck")
            action = menu.exec_(self.scalerTableView.mapToGlobal(pos))
            if action == check_action or action == uncheck_action:
                self.scalerTableModel.setChecked(rows, (check_action == action))

    def reset_widgets(self):
        self.parent.imageProcessWidget.sld.setValue(0)
        self.parent.reconstructionWidget.sld.setValue(0)
        self.parent.reconstructionWidget.recon = []
        self.parent.sinogramWidget.sld.setValue(0)

    def onSaveDataInMemory(self):
        files = [i.filename for i in self.fileTableModel.arrayData]
        if len(files) == 0:
            print('Directory probably not mounted')
            return [], [] , [], []
        thetas = [i.theta for i in self.fileTableModel.arrayData]
        elements = [i.element_name for i in self.elementTableModel.arrayData]
        scalers = [i.element_name for i in self.scalerTableModel.arrayData]
        files_bool = [i.use for i in self.fileTableModel.arrayData]
        elements_bool = [i.use for i in self.elementTableModel.arrayData]
        scalers_bool = [i.use for i in self.scalerTableModel.arrayData]
        element_tag = self.element_tag.title()
        scaler_tag = self.scaler_tag.title()
        data_tag = self.data_tag.title()
        k = np.arange(len(files))
        l = np.arange(len(elements))
        files = [files[j] for j in k if files_bool[j]==True]
        path_files = [self.fileTableModel.directory + s for s in files]
        thetas = np.asarray([thetas[j] for j in k if files_bool[j]==True])
        elements = [elements[j] for j in l if elements_bool[j]==True]
        scalers = [scalers[j] for j in l if scalers_bool[j]==True]
        elements.append("us_ic")
        #update auto-load parameters
        self.parent.params.input_path = self.dirLineEdit.text()
        self.parent.params.file_extension = self.extLineEdit.text()
        self.parent.params.theta_tag = self.theta_tag.title()
        self.parent.params.data_tag = self.data_tag.title()
        self.parent.params.element_tag = self.element_tag.title()
        self.parent.params.selected_elements = str(list(np.where(elements_bool)[0]))
        self.parent.params.scaler_tag = self.scaler_tag.title()
        self.parent.params.selected_scalers = str(list(np.where(scalers_bool)[0]))

        if len(elements) == 0:
            print('no element selected.')
            return [], [] , [], []
        else:
            print('loading files...')
        if all(x==thetas[0] for x in thetas):           #check if all values in thetas are the same: no theta info.
            print('WARNING: No unique angle information. Double check Theta PV or current directory')
            # return [], [] , [], []

        self.parent.clear_all()
        try:
            #TODO: add file upload status: n / total files uploaded
            data = self.reader.read_mic_xrf(path_files, elements, data_tag, element_tag, scalers, scaler_tag)
        except:
            print("invalid image/data/element tag combination. Load failed")
            return [], [], [], []

        if data is None:
            return [], [], [], []
        print('finished loading')
        elements = elements+scalers
        return data, elements, thetas, files

