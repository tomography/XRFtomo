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
        
        # Modify these selection settings
        self.fileTableView.setSelectionMode(QAbstractItemView.ContiguousSelection)  # Allows range selection
        self.fileTableView.setSelectionBehavior(QAbstractItemView.SelectRows)  # Selects entire rows
        self.fileTableView.setDragEnabled(False)  # Prevent drag and drop
        self.fileTableView.setAcceptDrops(False)
        
        self.fileTableView.setSortingEnabled(True)
        self.fileTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fileTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileTableView.customContextMenuRequested.connect(self.onFileTableContextMenu)
        self.fileTableView.setEditTriggers(QAbstractItemView.DoubleClicked | 
                                         QAbstractItemView.EditKeyPressed |
                                         QAbstractItemView.AnyKeyPressed)

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
        item_dict["data_menu"] = [["label","menu","selected_label"], "", None, None]
        item_dict["element_menu"] = [["label","menu","selected_label"], "", None, None]
        item_dict["scaler_menu"] = [["label","menu","selected_label"], "", None, None]
        item_dict["theta_menu"] = [["label","menu","selected_label"], "", None, None]
        item_dict["saveDataBtn"] = [["button"], "", None, None]

        vb_files = QVBoxLayout()
        widgetsizes = [240, 115, 50]
        for i, key in enumerate(item_dict.keys()):
            widget_items = item_dict[key][0]
            attrs = item_dict[key]
            widgetsize = widgetsizes[len(widget_items)-1]
            
            # Create a vertical layout for each menu group
            if "menu" in widget_items:
                # Create vertical layout for menu + selected label
                menu_layout = QVBoxLayout()
                
                # Create horizontal layout for label + menu
                line_num = "line_{}".format(i)
                setattr(self, line_num, QHBoxLayout())
                line = self.__dict__[line_num]
                
                for widget in widget_items:
                    if widget == "label":
                        # Create label for the combo box
                        name = key.split("_")[0]+"_tag"
                        setattr(self, name, QLabel(name))
                        object = self.__dict__[name]
                        object.setFixedWidth(widgetsize)
                        object.setToolTip(attrs[1])
                        line.addWidget(object)

                    elif widget == "menu":
                        # Use tree combo box for better positioning control
                        tree_combo = self.create_tree_combo_box(key, self)  # Pass self as parent
                        setattr(self, key, tree_combo)
                        object = self.__dict__[key]
                        line.addWidget(object)

                    elif widget == "selected_label":
                        # Create label to show selected item
                        name = key.split("_")[0] + "_selected"
                        setattr(self, name, QLabel("No selection"))
                        object = self.__dict__[name]
                        object.setFixedWidth(widgetsize)
                        object.setStyleSheet("color: blue; font-style: italic;")
                        # Add to vertical layout instead of horizontal
                        menu_layout.addLayout(line)
                        menu_layout.addWidget(object)
                        vb_files.addLayout(menu_layout)
                        break  # Exit the widget loop since we've handled the group

                    elif widget == "button":
                        setattr(self, key, QPushButton(key))
                        object = self.__dict__[key]
                        object.setFixedWidth(widgetsize)
                        object.setText("save data to memory")
                        line.addWidget(object)
                        vb_files.addLayout(line)
                    else:
                        pass
            else:
                # Handle non-menu items (like buttons) normally
                line_num = "line_{}".format(i)
                setattr(self, line_num, QHBoxLayout())
                line = self.__dict__[line_num]
                
                for widget in widget_items:
                    if widget == "button":
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
        """Show menus with proper positioning"""
        if not self.data_menu.isVisible():
            self.data_menu.setHidden(False)
            # Force menu to recalculate position before showing
            self.data_menu.adjustSize()
            self.data_menu.show()
        if not self.element_menu.isVisible():
            self.element_menu.setHidden(False)
            self.element_menu.adjustSize()
            self.element_menu.show()
        if not self.scaler_menu.isVisible():
            self.scaler_menu.setHidden(False)
            self.scaler_menu.adjustSize()
            self.scaler_menu.show()
        if not self.theta_menu.isVisible():
            self.theta_menu.setHidden(False)
            self.theta_menu.adjustSize()
            self.theta_menu.show()
        return

    def fix_menu_positioning(self, menu):
        """
        Fix menu positioning issues by ensuring proper geometry and style application
        """
        # Force immediate style update
        menu.style().unpolish(menu)
        menu.style().polish(menu)
        
        # Force geometry recalculation
        menu.adjustSize()
        
        # Ensure all submenus also have proper positioning
        for action in menu.actions():
            if action.menu():
                submenu = action.menu()
                # Reset submenu positioning completely
                submenu.setStyleSheet("""
                    QMenu {
                        margin: 0px;
                        padding: 0px;
                        border: 1px solid #c0c0c0;
                    }
                    QMenu::item {
                        padding: 4px 8px;
                        border: none;
                    }
                    QMenu::item:selected {
                        background-color: #0078d4;
                        color: white;
                    }
                    QMenu::separator {
                        height: 1px;
                        background: #c0c0c0;
                        margin: 2px 0px;
                    }
                """)
                
                # Force complete recalculation
                submenu.adjustSize()
                submenu.updateGeometry()
                
                # Force submenu to recalculate its position by temporarily hiding
                submenu.hide()
                submenu.show()

    def onLoadDirectory(self, fnames=None, path=None):
        try:
            self.data_menu.clear()
            self.element_menu.clear()
            self.scaler_menu.clear()
            self.theta_menu.clear()
            ext = self.extLineEdit.text()
        except Exception as error:
            print("onLoadDirectory Error: ",error)

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
        just_names = [os.path.basename(fname) for fname in fnames]
        self.fileTableModel.update_fnames(just_names)
        self.fileTableModel.setAllChecked(True)

        if "h5" in ext:
            try:
                # NEW APPROACH: Use tree combo boxes for better positioning
                self.img = h5py.File(fnames[0], "r")
                
                # Populate tree combo boxes with H5 structure
                self.data_menu.populate_from_h5(self.img, self.update_data_tag)
                self.element_menu.populate_from_h5(self.img, self.update_element_tag)
                self.scaler_menu.populate_from_h5(self.img, self.update_scaler_tag)
                self.theta_menu.populate_from_h5(self.img, self.update_theta_tag)
                
                # Set initial placeholder text after populating
                self.data_menu.setCurrentText("Select data...")
                self.element_menu.setCurrentText("Select element...")
                self.scaler_menu.setCurrentText("Select scaler...")
                self.theta_menu.setCurrentText("Select theta...")
                
                # Ensure the placeholder text is displayed
                self.data_menu.setEditable(False)
                self.element_menu.setEditable(False)
                self.scaler_menu.setEditable(False)
                self.theta_menu.setEditable(False)

                tags_exist = self.check_auto_tags()
                if tags_exist:
                    # Set the auto tags if they exist
                    self.data_menu.setCurrentText(self.auto_data_tag)
                    self.element_menu.setCurrentText(self.auto_element_tag)
                    self.scaler_menu.setCurrentText(self.auto_scaler_tag)
                    self.theta_menu.setCurrentText(self.auto_theta_tag)
                    
                    # Set the full paths as properties
                    self.data_menu.setProperty("full_path", self.auto_data_tag)
                    self.element_menu.setProperty("full_path", self.auto_element_tag)
                    self.scaler_menu.setProperty("full_path", self.auto_scaler_tag)
                    self.theta_menu.setProperty("full_path", self.auto_theta_tag)
                    
                    # Update the selected labels
                    self.data_selected.setText(self.auto_data_tag)
                    self.element_selected.setText(self.auto_element_tag)
                    self.scaler_selected.setText(self.auto_scaler_tag)
                    self.theta_selected.setText(self.auto_theta_tag)
                    
                    self.element_tag_changed()
                    self.scaler_tag_changed()
                    # self.theta_tag_changed()
                else:
                    return
            except:
                print("problem")
                return
            

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
        try_idxs = [663, 657, 691, 663]
        for idx in try_idxs:
            thetas = self.reader.load_thetas(files=path_files, theta_tag="dummy", idx=idx)
            uniques = len(set(thetas))
            errflag = len(path_files)/uniques > 3
            try:
                if max(thetas)<=360 and min(thetas)>=-360 and not errflag: #thetas valid if at least more than one unique value per every 3 files and range is within +-360
                    self.fileTableModel.update_thetas(thetas)
                    self.fileTableView.sortByColumn(1, 0)
                    success = True
                    break
            except:
                print("thetas is None")
        return success
    def check_auto_tags(self):
        data_tag_exists = self.auto_data_tag in self.img
        element_tag_exists = self.auto_element_tag in self.img
        scaler_tag_exists = self.auto_scaler_tag in self.img

        if data_tag_exists and element_tag_exists and scaler_tag_exists:
            return True
        else:
            default = list(self.img.keys())[0]
            self.data_menu.setCurrentText(default)
            self.element_menu.setCurrentText(default)
            self.scaler_menu.setCurrentText(default)
            self.theta_menu.setCurrentText(default)
            return False

    def populate_unified_menu(self, h5_obj, existing_menu, callback_func, max_depth=5):
        """
        Populate an existing QMenu with nested dropdown menus from H5 file structure
        
        Parameters:
        -----------
        h5_obj : h5py.File or h5py.Group
            The H5 object to traverse
        existing_menu : QMenu
            The existing menu to populate
        callback_func : function
            Function to call when menu item is selected
        max_depth : int
            Maximum depth for nested menus (prevents infinite recursion)
        """
        # Clear existing menu items
        existing_menu.clear()
        
        def populate_menu_recursive(obj, parent_menu, current_depth=0):
            if current_depth >= max_depth:
                return
                
            for key in obj.keys():
                if isinstance(obj[key], h5py.Group):
                    # Create submenu for groups
                    submenu = parent_menu.addMenu(key)
                    # Override submenu positioning behavior
                    submenu.setStyleSheet("""
                        QMenu {
                            margin: 0px;
                            padding: 0px;
                            border: 1px solid #c0c0c0;
                        }
                        QMenu::item {
                            padding: 4px 8px;
                            border: none;
                        }
                        QMenu::item:selected {
                            background-color: #0078d4;
                            color: white;
                        }
                        QMenu::separator {
                            height: 1px;
                            background: #c0c0c0;
                            margin: 2px 0px;
                        }
                    """)
                    
                    # Connect submenu's aboutToShow to ensure proper positioning
                    submenu.aboutToShow.connect(lambda sm=submenu: self.ensure_submenu_position(sm))
                    
                    populate_menu_recursive(obj[key], submenu, current_depth + 1)
                elif isinstance(obj[key], h5py.Dataset):
                    # Create action for datasets
                    action = QAction(key, self)
                    parent_menu.addAction(action)
                    action.triggered.connect(callback_func)
                    
        populate_menu_recursive(h5_obj, existing_menu)
        
        # Force menu to recalculate its geometry after population
        existing_menu.adjustSize()

    def ensure_submenu_position(self, submenu):
        """
        Ensure submenu appears in the correct position relative to its parent
        """
        # Force submenu to recalculate its position
        submenu.adjustSize()
        submenu.updateGeometry()
        
        # Force immediate style update
        submenu.style().unpolish(submenu)
        submenu.style().polish(submenu)
        
        # Try to force proper positioning by temporarily hiding and showing
        submenu.hide()
        submenu.show()

    def create_tree_combo_box(self, title, parent_widget=None):
        """
        Create a QComboBox with a tree model for better positioning control
        """
        from PyQt5.QtWidgets import QComboBox, QTreeView
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        from PyQt5.QtCore import Qt
        
        class TreeComboBox(QComboBox):
            def __init__(self, title, parent=None, parent_widget=None):
                super().__init__(parent)
                self.setWindowTitle(title)
                self.setObjectName(title)  # Set object name for identification
                self.parent_widget = parent_widget  # Store reference to parent widget
                self.setFixedSize(240, 35)
                
                # Override the combo box's showPopup behavior
                self._popup_open = False
                
                # Create tree view
                self.tree_view = QTreeView()
                self.tree_view.setHeaderHidden(True)
                self.tree_view.setRootIsDecorated(True)
                self.tree_view.setAlternatingRowColors(False)
                self.tree_view.setIndentation(20)
                self.tree_view.setExpandsOnDoubleClick(True)
                self.tree_view.setItemsExpandable(True)
                self.tree_view.setSortingEnabled(False)
                
                # Override mouse press event to prevent combo box from closing
                self.tree_view.mousePressEvent = self.tree_mouse_press_event
                
                # Enable hover expansion
                self.tree_view.setMouseTracking(True)
                self.tree_view.installEventFilter(self)
                
                # Set the tree view as the popup
                self.setView(self.tree_view)
                
                # Override the combo box's popup behavior
                self._custom_popup = None
                
                # Set initial placeholder text
                self.setCurrentText("Select...")
                
                # Style the combo box
                self.setStyleSheet("""
                    QComboBox {
                        border: 1px solid #c0c0c0;
                        border-radius: 3px;
                        padding: 4px 8px;
                        background: white;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #666;
                        margin-right: 5px;
                    }
                    QComboBox QAbstractItemView {
                        border: 1px solid #c0c0c0;
                        selection-background-color: #0078d4;
                        selection-color: white;
                    }
                """)
                
                # Connect signals for proper tree behavior
                self.tree_view.clicked.connect(self.on_item_clicked)
                self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
                self.tree_view.expanded.connect(self.on_item_expanded)
                
            def on_item_clicked(self, index):
                """Handle item selection - only select on double click"""
                # Prevent combo box from closing when clicking on folders
                item = self.model().itemFromIndex(index)
                if item and item.hasChildren():
                    # This is a folder, don't close the popup
                    return
                # For leaf nodes, let the double-click handler take care of it
            
            def on_item_double_clicked(self, index):
                """Handle double-click selection"""
                item = self.model().itemFromIndex(index)
                if item and not item.hasChildren():
                    # This is a leaf node (dataset), select it
                    # Remove the icon from the text
                    text = item.text().replace("📄 ", "").replace("📁 ", "")
                    
                    # Find and store the full path
                    full_path = self.find_item_path(item, item.text())
                    if full_path:
                        self.setProperty("full_path", full_path)
                    
                    # Update the corresponding label to show selected item
                    self.update_selected_label(text)
                    
                    # Call the callback function directly
                    if hasattr(self, 'callback_func'):
                        # Create a mock sender object with the full path
                        class MockSender:
                            def __init__(self, path):
                                self.path = path
                            def property(self, prop):
                                if prop == "full_path":
                                    return self.path
                                return None
                        
                        mock_sender = MockSender(full_path)
                        # Temporarily replace sender in callback
                        original_sender = getattr(self.callback_func, '__self__', None)
                        if original_sender:
                            original_sender.sender = lambda: mock_sender
                            self.callback_func()
                            original_sender.sender = lambda: original_sender
                    
                    # Hide the popup
                    self.hidePopup()
            
            def on_item_expanded(self, index):
                """Handle item expansion - keep popup open"""
                # Keep the popup open when expanding items
                pass
            

            
            def showPopup(self):
                """Override to use custom popup behavior"""
                if not self._popup_open:
                    # Create custom popup
                    from PyQt5.QtWidgets import QFrame
                    from PyQt5.QtCore import Qt
                    
                    self._custom_popup = QFrame(self, Qt.Popup)
                    self._custom_popup.setFrameStyle(QFrame.Box)
                    
                    # Create layout for the popup
                    from PyQt5.QtWidgets import QVBoxLayout
                    layout = QVBoxLayout(self._custom_popup)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(self.tree_view)
                    
                    # Position the popup
                    popup_rect = self.rect()
                    popup_pos = self.mapToGlobal(popup_rect.bottomLeft())
                    self._custom_popup.move(popup_pos)
                    
                    # Set size
                    self._custom_popup.resize(240, 200)
                    
                    # Show the popup
                    self._custom_popup.show()
                    self._popup_open = True
            
            def hidePopup(self):
                """Override to hide custom popup"""
                if self._custom_popup:
                    self._custom_popup.hide()
                    self._custom_popup = None
                self._popup_open = False
            
            def mousePressEvent(self, event):
                """Override to prevent closing when clicking on folders"""
                if self._popup_open:
                    # If popup is open, don't handle the click at combo box level
                    event.ignore()
                    return
                super().mousePressEvent(event)
            
            def tree_mouse_press_event(self, event):
                """Custom mouse press event for tree view"""
                from PyQt5.QtCore import Qt
                
                # Get the item under the mouse
                pos = event.pos()
                index = self.tree_view.indexAt(pos)
                
                if index.isValid():
                    item = self.model().itemFromIndex(index)
                    if item and item.hasChildren():
                        # This is a folder, toggle expansion
                        if self.tree_view.isExpanded(index):
                            self.tree_view.collapse(index)
                        else:
                            self.tree_view.expand(index)
                        # Don't let the combo box close
                        event.accept()
                        return
                
                # For leaf nodes or invalid clicks, let the default behavior handle it
                QTreeView.mousePressEvent(self.tree_view, event)
            
            def keyPressEvent(self, event):
                """Override key press to prevent closing on Enter/Space"""
                if self._popup_open:
                    # Don't close popup on key presses when it's open
                    event.ignore()
                    return
                super().keyPressEvent(event)
            
            def populate_from_h5(self, h5_obj, callback_func, max_depth=5):
                """Populate the tree from H5 object"""
                model = QStandardItemModel()
                
                def add_items_recursive(obj, parent_item, current_path="", current_depth=0):
                    if current_depth >= max_depth:
                        return
                        
                    for key in obj.keys():
                        full_path = f"{current_path}/{key}" if current_path else key
                        
                        if isinstance(obj[key], h5py.Group):
                            # Create group item
                            group_item = QStandardItem("📁 " + key)  # Folder icon
                            group_item.setEditable(False)
                            group_item.setData(full_path, Qt.UserRole)  # Store full path
                            parent_item.appendRow(group_item)
                            add_items_recursive(obj[key], group_item, full_path, current_depth + 1)
                        elif isinstance(obj[key], h5py.Dataset):
                            # Create dataset item
                            dataset_item = QStandardItem("📄 " + key)  # File icon
                            dataset_item.setEditable(False)
                            dataset_item.setData(full_path, Qt.UserRole)  # Store full path
                            parent_item.appendRow(dataset_item)
                
                add_items_recursive(h5_obj, model.invisibleRootItem())
                self.setModel(model)
                
                # Also set the model for the tree view
                self.tree_view.setModel(model)
                
                # Clear the current text to prevent showing the first item
                self.setCurrentText("")
                
                # Store callback for later use
                self.callback_func = callback_func
                

            
            def update_selected_label(self, text):
                """Update the corresponding selected label"""
                # Find the corresponding label based on the combo box name
                combo_name = self.objectName()
                if not combo_name:
                    # Try to get name from parent
                    combo_name = self.parent_widget.objectName() if self.parent_widget else ""
                
                # Map combo box names to label names
                label_map = {
                    "data_menu": "data_selected",
                    "element_menu": "element_selected", 
                    "scaler_menu": "scaler_selected",
                    "theta_menu": "theta_selected"
                }
                
                label_name = label_map.get(combo_name)
                if label_name and hasattr(self.parent_widget, label_name):
                    label = getattr(self.parent_widget, label_name)
                    label.setText(text)
            
            def find_item_path(self, item, target_text):
                """Recursively find item with target text and call callback"""
                # Remove icons from item text for comparison
                item_text = item.text().replace("📄 ", "").replace("📁 ", "")
                if item_text == target_text:
                    full_path = item.data(Qt.UserRole)
                    if full_path and hasattr(self, 'callback_func'):
                        # Create a mock sender object with the full path
                        class MockSender:
                            def __init__(self, path):
                                self.path = path
                            def property(self, prop):
                                if prop == "full_path":
                                    return self.path
                                return None
                        
                        mock_sender = MockSender(full_path)
                        # Temporarily replace sender in callback
                        original_sender = getattr(self.callback_func, '__self__', None)
                        if original_sender:
                            original_sender.sender = lambda: mock_sender
                            self.callback_func()
                            original_sender.sender = lambda: original_sender
                    return True
                
                for row in range(item.rowCount()):
                    child = item.child(row)
                    if self.find_item_path(child, target_text):
                        return True
                return False
        
        return TreeComboBox(title, parent_widget, parent_widget)

    def create_unified_menu(self, h5_obj, menu_title, callback_func, max_depth=5):
        """
        Unified function to create nested dropdown menus from H5 file structure
        
        Parameters:
        -----------
        h5_obj : h5py.File or h5py.Group
            The H5 object to traverse
        menu_title : str
            Title for the menu
        callback_func : function
            Function to call when menu item is selected
        max_depth : int
            Maximum depth for nested menus (prevents infinite recursion)
            
        Returns:
        --------
        QMenu : The created menu
        """
        menu = QMenu(menu_title, self)
        menu.setObjectName(f"{menu_title}_menu")
        
        def populate_menu_recursive(obj, parent_menu, current_depth=0):
            if current_depth >= max_depth:
                return
                
            for key in obj.keys():
                if isinstance(obj[key], h5py.Group):
                    # Create submenu for groups
                    submenu = parent_menu.addMenu(key)
                    populate_menu_recursive(obj[key], submenu, current_depth + 1)
                elif isinstance(obj[key], h5py.Dataset):
                    # Create action for datasets
                    action = QAction(key, self)
                    parent_menu.addAction(action)
                    action.triggered.connect(callback_func)
                    
        populate_menu_recursive(h5_obj, menu)
        return menu

    def populate_smart_menu(self, h5_obj, existing_menu, callback_func, filter_func=None):
        """
        Populate an existing QMenu with smart filtering and path tracking
        
        Parameters:
        -----------
        h5_obj : h5py.File or h5py.Group
            The H5 object to traverse
        existing_menu : QMenu
            The existing menu to populate
        callback_func : function
            Function to call when menu item is selected
        filter_func : function, optional
            Function to filter which items to include
        """
        # Clear existing menu items
        existing_menu.clear()
        
        def populate_with_paths(obj, parent_menu, current_path=""):
            for key in obj.keys():
                full_path = f"{current_path}/{key}" if current_path else key
                
                # Apply filter if provided
                if filter_func and not filter_func(key, obj[key], full_path):
                    continue
                    
                if isinstance(obj[key], h5py.Group):
                    submenu = parent_menu.addMenu(key)
                    submenu.setProperty("full_path", full_path)
                    populate_with_paths(obj[key], submenu, full_path)
                elif isinstance(obj[key], h5py.Dataset):
                    action = QAction(key, self)
                    action.setProperty("full_path", full_path)
                    parent_menu.addAction(action)
                    action.triggered.connect(callback_func)
                    
        populate_with_paths(h5_obj, existing_menu)

    def create_smart_menu(self, h5_obj, menu_title, callback_func, filter_func=None):
        """
        Smart menu generator with filtering and path tracking
        
        Parameters:
        -----------
        h5_obj : h5py.File or h5py.Group
            The H5 object to traverse
        menu_title : str
            Title for the menu
        callback_func : function
            Function to call when menu item is selected
        filter_func : function, optional
            Function to filter which items to include
            
        Returns:
        --------
        QMenu : The created menu
        """
        menu = QMenu(menu_title, self)
        menu.setObjectName(f"{menu_title}_menu")
        
        def populate_with_paths(obj, parent_menu, current_path=""):
            for key in obj.keys():
                full_path = f"{current_path}/{key}" if current_path else key
                
                # Apply filter if provided
                if filter_func and not filter_func(key, obj[key], full_path):
                    continue
                    
                if isinstance(obj[key], h5py.Group):
                    submenu = parent_menu.addMenu(key)
                    submenu.setProperty("full_path", full_path)
                    populate_with_paths(obj[key], submenu, full_path)
                elif isinstance(obj[key], h5py.Dataset):
                    action = QAction(key, self)
                    action.setProperty("full_path", full_path)
                    parent_menu.addAction(action)
                    action.triggered.connect(callback_func)
                    
        populate_with_paths(h5_obj, menu)
        return menu

    def populate_data_menu(self, obj, menu):
        """Legacy function - now uses unified approach"""
        return self.create_unified_menu(obj, "data", self.update_data_tag)

    def populate_element_menu(self, obj, menu):
        """Legacy function - now uses unified approach"""
        return self.create_unified_menu(obj, "element", self.update_element_tag)

    def populate_scaler_menu(self, obj, menu):
        """Legacy function - now uses unified approach"""
        return self.create_unified_menu(obj, "scaler", self.update_scaler_tag)

    def populate_theta_menu(self, obj, menu):
        """Legacy function - now uses unified approach"""
        return self.create_unified_menu(obj, "theta", self.update_theta_tag)

    def update_data_tag(self):
        """Update data tag using combo box selection"""
        sender = self.sender()
        if hasattr(sender, 'property') and sender.property("full_path"):
            # Use the stored full path if available
            full_path = sender.property("full_path")
            self.data_menu.setCurrentText(full_path.split('/')[-1])  # Show just the filename
            # Store the full path for later use
            self.data_menu.setProperty("full_path", full_path)
        else:
            # Fallback for legacy compatibility
            selected_text = self.data_menu.currentText()
            self.data_menu.setProperty("full_path", selected_text)

    def update_element_tag(self):
        """Update element tag using combo box selection"""
        sender = self.sender()
        if hasattr(sender, 'property') and sender.property("full_path"):
            # Use the stored full path if available
            full_path = sender.property("full_path")
            self.element_menu.setCurrentText(full_path.split('/')[-1])  # Show just the filename
            # Store the full path for later use
            self.element_menu.setProperty("full_path", full_path)
        else:
            # Fallback for legacy compatibility
            selected_text = self.element_menu.currentText()
            self.element_menu.setProperty("full_path", selected_text)
        
        self.element_tag_changed()

    def update_scaler_tag(self):
        """Update scaler tag using combo box selection"""
        sender = self.sender()
        if hasattr(sender, 'property') and sender.property("full_path"):
            # Use the stored full path if available
            full_path = sender.property("full_path")
            self.scaler_menu.setCurrentText(full_path.split('/')[-1])  # Show just the filename
            # Store the full path for later use
            self.scaler_menu.setProperty("full_path", full_path)
        else:
            # Fallback for legacy compatibility
            selected_text = self.scaler_menu.currentText()
            self.scaler_menu.setProperty("full_path", selected_text)
        
        self.scaler_tag_changed()

    def update_theta_tag(self):
        """Update theta tag using combo box selection"""
        sender = self.sender()
        if hasattr(sender, 'property') and sender.property("full_path"):
            # Use the stored full path if available
            full_path = sender.property("full_path")
            self.theta_menu.setCurrentText(full_path.split('/')[-1])  # Show just the filename
            # Store the full path for later use
            self.theta_menu.setProperty("full_path", full_path)
            
            # Handle theta-specific logic
            try:
                dataset = self.img[full_path]
                dataset = np.array(dataset).astype('U13')
                self.create_table(dataset)
            except:
                print("Error loading theta dataset")
        else:
            # Fallback for legacy compatibility
            selected_text = self.theta_menu.currentText()
            self.theta_menu.setProperty("full_path", selected_text)
        
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
        current_theta_path = self.theta_menu.property("full_path") or self.theta_menu.currentText()
        theta_tag = "{}/{}".format(current_theta_path, self.tablewidget.currentItem().text())
        theta_tag = theta_tag.strip(",")
        self.theta_menu.setCurrentText(theta_tag.split('/')[-1])
        self.theta_menu.setProperty("full_path", theta_tag)
        self.theta_tag_changed()
        self.tablewidget.close()


    def getElements(self):
        element_tag = self.element_menu.property("full_path") or self.element_menu.currentText()
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
            element_tag = self.element_menu.property("full_path") or self.element_menu.currentText()
            element_list = list(self.img[element_tag])
            elements = [x.decode("utf-8") for x in element_list]
            self.elementTableModel.loadElementNames(elements)
            self.elementTableModel.setAllChecked(False)
            self.elementTableModel.setChecked(self.auto_selected_elements, (True))
        except:
            print("invalid tag option")

        thetas_loaded = self.try_theta()
        if not thetas_loaded:
            self.theta_tag_changed()
        return

    def scaler_tag_changed(self):
        try:
            scaler_tag = self.scaler_menu.property("full_path") or self.scaler_menu.currentText()
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
            theta_tag = self.theta_menu.property("full_path") or self.theta_menu.currentText()

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
            rows = sorted(set(i.row() for i in self.fileTableView.selectionModel().selection().indexes()))
            menu = QMenu()
            check_action = menu.addAction("Check")
            uncheck_action = menu.addAction("Uncheck")
            edit_action = menu.addAction("Edit Theta")
            
            # Add extrapolate action if multiple rows are selected
            extrapolate_action = None
            if len(rows) > 1:
                extrapolate_action = menu.addAction("Extrapolate Thetas")
            
            action = menu.exec_(self.fileTableView.mapToGlobal(pos))
            if action == check_action or action == uncheck_action:
                self.fileTableModel.setChecked(rows, (check_action == action))
            elif action == edit_action:
                self.editTheta(rows[0])
            elif extrapolate_action and action == extrapolate_action:
                self.extrapolateThetas(rows)

    def extrapolateThetas(self, rows):
        """Handle extrapolation of theta values for selected rows"""
        if len(rows) < 2:
            return
            
        # Get first and last selected rows
        start_idx = rows[0]
        end_idx = rows[-1]
        
        # Ask user for start and end theta values
        start_theta, ok1 = QInputDialog.getDouble(
            self, 
            'Start Theta',
            'Enter starting theta value:',
            self.fileTableModel.arrayData[start_idx].theta,
            -360,
            360,
            2
        )
        
        if not ok1:
            return
        else: 
            self.fileTableModel.arrayData[start_idx].theta = start_theta

            
        end_theta, ok2 = QInputDialog.getDouble(
            self, 
            'End Theta',
            'Enter ending theta value:',
            self.fileTableModel.arrayData[end_idx].theta,
            -360,
            360,
            2
        )
        
        if not ok2:
            return
        else: 
            self.fileTableModel.arrayData[end_idx].theta = end_theta
        
        # Update start and end values and perform extrapolation
        self.fileTableModel.extrapolate_thetas(start_idx, end_idx)

    def editTheta(self, row):
        """Handle editing of theta value"""
        current_theta = self.fileTableModel.arrayData[row].theta
        new_theta, ok = QInputDialog.getDouble(
            self, 
            'Edit Theta',
            'Enter new theta value:',
            current_theta,
            -360,
            360,
            2
        )
        if ok:
            index = self.fileTableModel.index(row, self.fileTableModel.COL_THETA)
            self.fileTableModel.setData(index, new_theta, Qt.EditRole)

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
        element_tag = self.element_menu.property("full_path") or self.element_menu.currentText()
        scaler_tag = self.scaler_menu.property("full_path") or self.scaler_menu.currentText()
        data_tag = self.data_menu.property("full_path") or self.data_menu.currentText()
        k = np.arange(len(files))
        l = np.arange(len(elements))
        s = np.arange(len(scalers))
        files = [files[j] for j in k if files_bool[j]==True]
        path_files = [self.fileTableModel.directory + s for s in files]
        thetas = np.asarray([thetas[j] for j in k if files_bool[j]==True])
        elements = [elements[j] for j in l if elements_bool[j]==True]
        scalers = [scalers[j] for j in s if scalers_bool[j]==True]
        # elements.append("us_ic")
        #update auto-load parameters
        self.parent.params.input_path = self.dirLineEdit.text()
        self.parent.params.file_extension = self.extLineEdit.text()
        self.parent.params.theta_tag = self.theta_menu.property("full_path") or self.theta_menu.currentText()
        self.parent.params.data_tag = self.data_menu.property("full_path") or self.data_menu.currentText()
        self.parent.params.element_tag = self.element_menu.property("full_path") or self.element_menu.currentText()
        self.parent.params.selected_elements = str(list(np.where(elements_bool)[0]))
        self.parent.params.scaler_tag = self.scaler_menu.property("full_path") or self.scaler_menu.currentText()
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

    def create_h5_tree_widget(self, h5_obj, title="H5 Structure"):
        """
        Create a tree widget to display H5 file structure
        
        Parameters:
        -----------
        h5_obj : h5py.File or h5py.Group
            The H5 object to traverse
        title : str
            Title for the tree widget
            
        Returns:
        --------
        QTreeWidget : The created tree widget
        """
        from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
        
        tree = QTreeWidget()
        tree.setHeaderLabel(title)
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Name", "Type"])
        
        def populate_tree(obj, parent_item, current_path=""):
            for key in obj.keys():
                full_path = f"{current_path}/{key}" if current_path else key
                
                if isinstance(obj[key], h5py.Group):
                    # Create group item
                    group_item = QTreeWidgetItem(parent_item)
                    group_item.setText(0, key)
                    group_item.setText(1, "Group")
                    group_item.setData(0, Qt.UserRole, full_path)
                    group_item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                    
                    # Recursively populate group
                    populate_tree(obj[key], group_item, full_path)
                    
                elif isinstance(obj[key], h5py.Dataset):
                    # Create dataset item
                    dataset_item = QTreeWidgetItem(parent_item)
                    dataset_item.setText(0, key)
                    dataset_item.setText(1, f"Dataset ({obj[key].shape})")
                    dataset_item.setData(0, Qt.UserRole, full_path)
                    dataset_item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
        
        populate_tree(h5_obj, tree.invisibleRootItem())
        tree.expandAll()
        
        # Connect double-click signal
        tree.itemDoubleClicked.connect(self.on_tree_item_selected)
        
        return tree
    
    def on_tree_item_selected(self, item, column):
        """Handle tree item selection"""
        full_path = item.data(0, Qt.UserRole)
        item_type = item.text(1)
        
        if "Dataset" in item_type:
            # Determine which menu this should update based on context
            # You could add a property to the tree widget to indicate the target menu
            print(f"Selected dataset: {full_path}")
            # self.update_data_tag_from_path(full_path)

