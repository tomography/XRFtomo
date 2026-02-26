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
import numpy as np
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *


import xrftomo
import xrftomo.config as config
from scipy import stats
import matplotlib.pyplot as plt
from os.path import expanduser
from skimage import measure
from matplotlib.pyplot import *
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from skimage import io
import csv
import h5py
import os
import re
import subprocess
os.environ["QT_DEBUG_PLUGINS"] = "1"

STR_CONFIG_THETA_STRS = 'theta_pv_strs'


def _extract_scan_number(filename):
    """Extract scan number from filename stem only (preserves leading zeros)."""
    stem = os.path.splitext(filename)[0]
    digits = re.findall(r'\d+', stem)
    if digits:
        return digits[-1]
    if '_' in stem:
        part = stem.split('_')[-1]
        if part.isdigit():
            return part
    return ''


def _scan_numbers_match(scan_from_filename, scan_from_txt):
    """True if both refer to the same scan (10 matches 010; 10 does not match 10.5)."""
    a, b = str(scan_from_filename).strip(), str(scan_from_txt).strip()
    if a == b:
        return True
    try:
        fa, fb = float(a), float(b)
        return abs(fa - fb) < 1e-9
    except (ValueError, TypeError):
        return False


class MatchFilenamesThetasDialog(QDialog):
    """Popup table: column 0 = filenames, column 1 = scan#, rest = columns from loaded txt file."""

    def __init__(self, filenames, parent=None):
        super(MatchFilenamesThetasDialog, self).__init__(parent)
        self.filenames = list(filenames) if filenames else []
        self.txt_headers = []
        self.txt_rows = []
        self.scan_in_last_column = False
        self.column_header_overrides = {}
        self.PREDEFINED_HEADERS = ["x-shifts", "y-shifts", "theta"]
        self.setWindowTitle("Match filenames to thetas")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        row0 = QHBoxLayout()
        self.loadTxtBtn = QPushButton("Load txt file (comma-delimited)")
        self.loadTxtBtn.clicked.connect(self._load_txt)
        row0.addWidget(self.loadTxtBtn)
        row0.addWidget(QLabel("Scan # column:"))
        self.scanColCombo = QComboBox()
        self.scanColCombo.addItems(["First column", "Last column"])
        self.scanColCombo.currentIndexChanged.connect(self._on_scan_column_changed)
        row0.addWidget(self.scanColCombo)
        layout.addLayout(row0)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        hheader = self.table.horizontalHeader()
        hheader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        hheader.customContextMenuRequested.connect(self._on_header_context_menu)
        layout.addWidget(self.table)

        self.acceptBtn = QPushButton("Accept")
        self.acceptBtn.clicked.connect(self._on_accept)
        layout.addWidget(self.acceptBtn)

        self._build_table()

    def _on_scan_column_changed(self, index):
        self.scan_in_last_column = (index == 1)
        self._build_table()

    def _header_label_for_column(self, col_index):
        """Resolved header for column col_index (override or loaded)."""
        if col_index < 2:
            return ["Filename", "Scan #"][col_index]
        j = col_index - 2
        if j >= len(self.txt_headers):
            return ''
        return self.column_header_overrides.get(col_index) or self.txt_headers[j]

    def _refresh_header_labels(self):
        n_cols = self.table.columnCount()
        headers = [self._header_label_for_column(c) for c in range(n_cols)]
        self.table.setHorizontalHeaderLabels(headers)

    def _on_header_context_menu(self, pos):
        col = self.table.horizontalHeader().logicalIndexAt(pos)
        if col < 2:
            return
        menu = QMenu(self)
        for name in self.PREDEFINED_HEADERS:
            act = menu.addAction(name)
            act.triggered.connect(lambda checked, n=name, c=col: self._set_column_header(c, n))
        menu.addSeparator()
        clear_act = menu.addAction("Clear header")
        clear_act.triggered.connect(lambda checked, c=col: self._set_column_header(c, None))
        menu.exec_(self.table.horizontalHeader().mapToGlobal(pos))

    def _set_column_header(self, col_index, name):
        if name is not None:
            for other in list(self.column_header_overrides):
                if other != col_index and self.column_header_overrides.get(other) == name:
                    del self.column_header_overrides[other]
            self.column_header_overrides[col_index] = name
        else:
            self.column_header_overrides.pop(col_index, None)
        self._refresh_header_labels()

    def _column_index_for_header(self, label):
        for c in range(self.table.columnCount()):
            if self._header_label_for_column(c) == label:
                return c
        return None

    def _table_cell_text(self, row, col):
        item = self.table.item(row, col)
        return item.text().strip() if item else ''

    def _on_accept(self):
        theta_col = self._column_index_for_header("theta")
        if theta_col is None:
            QMessageBox.information(
                self, "Assign theta",
                "Assign \"theta\" to a column (right-click its header) before accepting."
            )
            return
        x_col = self._column_index_for_header("x-shifts")
        y_col = self._column_index_for_header("y-shifts")

        accepted = []
        shifts = []
        for row in range(self.table.rowCount()):
            fname = self._table_cell_text(row, 0)
            theta_val = self._table_cell_text(row, theta_col)
            if not theta_val:
                continue
            try:
                theta_float = float(theta_val)
            except ValueError:
                continue
            x_val = self._table_cell_text(row, x_col) if x_col is not None else ''
            y_val = self._table_cell_text(row, y_col) if y_col is not None else ''
            accepted.append((fname, theta_float))
            shifts.append({
                "filename": fname,
                "theta": theta_float,
                "x-shifts": x_val,
                "y-shifts": y_val,
            })

        if not accepted:
            QMessageBox.information(
                self, "No rows",
                "No rows have a theta value. Fill the theta column for at least one row."
            )
            return

        accepted.sort(key=lambda x: x[0])
        fnames = [a[0] for a in accepted]
        thetas_list = [float(a[1]) for a in accepted]

        main = self.parent()
        if main is None:
            self.reject()
            return
        main.fileTableWidget.fileTableModel.update_fnames(fnames)
        main.fileTableWidget.fileTableModel.update_thetas(thetas_list)
        main.fnames = list(fnames)
        main.thetas = np.array(thetas_list)
        main.shifts = shifts

        self.accept()

    def _build_table(self):
        scan_numbers = [_extract_scan_number(f) for f in self.filenames]
        n_extra = len(self.txt_headers)
        n_cols = 2 + n_extra
        self.table.setRowCount(len(self.filenames))
        self.table.setColumnCount(n_cols)
        headers = [self._header_label_for_column(c) for c in range(n_cols)]
        self.table.setHorizontalHeaderLabels(headers)

        for i, (fname, scan) in enumerate(zip(self.filenames, scan_numbers)):
            self.table.setItem(i, 0, QTableWidgetItem(fname))
            self.table.setItem(i, 1, QTableWidgetItem(scan))
            for j, h in enumerate(self.txt_headers):
                val = self._value_for_row(i, j)
                self.table.setItem(i, 2 + j, QTableWidgetItem(val))
        self.table.resizeColumnsToContents()

    def _value_for_row(self, file_index, col_index):
        """Find the txt row whose scan column matches this file's scan number; return the data value at col_index."""
        if col_index >= len(self.txt_headers) or not self.txt_rows:
            return ''
        scan = _extract_scan_number(self.filenames[file_index])
        for row in self.txt_rows:
            key = row[-1] if self.scan_in_last_column else (row[0] if row else '')
            if len(row) > 0 and _scan_numbers_match(scan, key):
                if self.scan_in_last_column:
                    if col_index < len(row) - 1:
                        return str(row[col_index]).strip()
                else:
                    if col_index + 1 < len(row):
                        return str(row[col_index + 1]).strip()
                return ''
        return ''

    def _load_txt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open comma-delimited txt", QtCore.QDir.currentPath(), "Text (*.txt);;All (*)"
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                rows = []
                for row in csv.reader(f):
                    row = [c.strip() for c in row]
                    if not row or all(not c for c in row):
                        continue
                    rows.append(row)
            if not rows:
                return
            first = rows[0]
            n_cols = max(len(r) for r in rows) if rows else 0
            n_data_cols = max(0, n_cols - 1)
            if self.scan_in_last_column:
                key_cell = first[-1].strip() if len(first) > 0 else ''
                has_header = key_cell != '' and not re.match(r'^-?\d*\.?\d+$', key_cell)
                if has_header:
                    self.txt_headers = [c.strip() for c in first[0:n_data_cols]]
                else:
                    self.txt_headers = [''] * n_data_cols
                self.txt_rows = list(rows[1:]) if has_header else list(rows)
            else:
                key_cell = first[0].strip() if len(first) > 0 else ''
                has_header = key_cell != '' and not re.match(r'^-?\d*\.?\d+$', key_cell)
                if has_header:
                    self.txt_headers = [c.strip() for c in first[1:n_data_cols + 1]]
                else:
                    self.txt_headers = [''] * n_data_cols
                self.txt_rows = list(rows[1:]) if has_header else list(rows)
            while len(self.txt_headers) < n_data_cols:
                self.txt_headers.append('')
            self.column_header_overrides.clear()
            self._build_table()
        except Exception as e:
            QMessageBox.warning(self, "Load error", "Could not load file: {}".format(e))


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))

class xrftomoGui(QMainWindow):
    newText = QtCore.pyqtSignal(str)

    def __init__(self, app, params):
        super(QMainWindow, self).__init__()
        self.params = params
        self.param_list = {}
        self.shifts = []
        self.app = app
        # self.get_values_from_params()
        self.initUI()
        sys.stdout = Stream(newText=self.onUpdateText)

    def initUI(self):
        try:
            import tomocupy
            self.tcp_installed = True
        except:
            self.tcp_installed = False
        
        try:
            from pyxalign import options as opts
            self.pyxalign_installed = True
        except:
            self.pyxalign_installed = False

        self.message_window = QtWidgets.QTextEdit("")
        self.message_window.setStyleSheet("background: beige; color: black")
        self.message_window.setReadOnly(True)
        self.message_window.setMinimumHeight(80)

        self.message_window.setMaximumHeight(300)

        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut('Ctrl+Q')

        closeAction = QAction('Quit', self)
        closeAction.triggered.connect(sys.exit)
        closeAction.setShortcut('Ctrl+X')

        openH5Action = QAction('open h5 files', self)
        openH5Action.triggered.connect(self.openH5)

        openCompleteH5Action = QAction('open structured h5 file', self)
        openCompleteH5Action.triggered.connect(self.open_complete_H5)

        openTiffAction = QAction('open tiff files', self)
        openTiffAction.triggered.connect(self.openTiffs)

        openStackAction = QAction('open tiff stack', self)
        openStackAction.triggered.connect(self.openStack)

        openThetaAction = QAction('open thetas file', self)
        openThetaAction.triggered.connect(self.openThetas)

        matchFilenamesThetasAction = QAction('match filenames to thetas', self)
        matchFilenamesThetasAction.triggered.connect(self.match_filenames_to_thetas)

        self.saveCorrAnalysisAction = QAction("Corelation Analysis", self)
        self.saveCorrAnalysisAction.triggered.connect(self.saveCorrAlsys)
        self.saveCorrAnalysisAction.setVisible(False)

        undoAction = QAction('Undo (Ctrl+Z)', self)
        undoAction.triggered.connect(self.undo)
        undoAction.setShortcut('Ctrl+Z')

        setAspectratio = QAction("lock aspect ratio",self)
        setAspectratio.setCheckable(True)
        setAspectratio.triggered.connect(self.toggle_aspect_ratio)

        self.debugMode = QAction("experimental",self)
        self.debugMode.setCheckable(True)
        self.debugMode.triggered.connect(self.toggleDebugMode)

        restoreAction = QAction("Restore", self)
        restoreAction.triggered.connect(self.restore)

        self.keyMapAction = QAction('key map settings', self)
        self.keyMapAction.triggered.connect(self.keyMapSettings)

        self.configAction = QAction('load configuration settings', self)
        self.configAction.triggered.connect(self.configSettings)

        self.softwareupdateAction = QAction('update software', self)
        self.softwareupdateAction.triggered.connect(self.update_software)
        ###
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()

        self.writer = xrftomo.SaveOptions(self)
        # self.reader = xrftomo.ReadOptions()
        self.fileTableWidget = xrftomo.FileTableWidget(self)
        self.imageProcessWidget = xrftomo.ImageProcessWidget(self)
        self.sinogramWidget = xrftomo.SinogramWidget(self)
        self.reconstructionWidget = xrftomo.ReconstructionWidget(self)
        self.laminographyWidget = xrftomo.LaminographyWidget(self)
        self.scatterWidget = xrftomo.ScatterView()
        self.scatterWidgetRecon = xrftomo.ScatterView()
        self.miniReconWidget = xrftomo.MiniReconView()

        #refresh UI
        self.imageProcessWidget.refreshSig.connect(self.refreshUI)

        #sinogram changed
        self.sinogramWidget.sinoChangedSig.connect(self.update_sino)

        #slider change
        self.imageProcessWidget.sliderChangedSig.connect(self.imageProcessWidget.updateSliderSlot)

        #element dropdown change
        self.imageProcessWidget.elementChangedSig.connect(self.sinogramWidget.updateElementSlot)
        self.sinogramWidget.elementChangedSig.connect(self.reconstructionWidget.updateElementSlot)
        self.reconstructionWidget.elementChangedSig.connect(self.laminographyWidget.updateElementSlot)
        self.laminographyWidget.elementChangedSig.connect(self.imageProcessWidget.updateElementSlot)

        # data update
        self.imageProcessWidget.dataChangedSig.connect(self.update_history)
        self.sinogramWidget.dataChangedSig.connect(self.update_history)

        # theta update
        self.imageProcessWidget.thetaChangedSig.connect(self.update_theta)
        self.imageProcessWidget.thetaChangedSig.connect(self.sinogramWidget.updateImgSldRange)

        #data dimensions changed
        self.imageProcessWidget.ySizeChangedSig.connect(self.sinogramWidget.ySizeChanged)
        self.imageProcessWidget.ySizeChangedSig.connect(self.reconstructionWidget.ySizeChanged)
        self.imageProcessWidget.xSizeChangedSig.connect(self.reconstructionWidget.xSizeChanged)
        self.imageProcessWidget.ySizeChangedSig.connect(self.laminographyWidget.ySizeChanged)
        self.imageProcessWidget.xSizeChangedSig.connect(self.laminographyWidget.xSizeChanged)
        self.imageProcessWidget.padSig.connect(self.update_padding)
        #alignment changed
        self.imageProcessWidget.alignmentChangedSig.connect(self.update_alignment)
        self.sinogramWidget.alignmentChangedSig.connect(self.update_alignment)
        self.sinogramWidget.restoreSig.connect(self.restore)

        #fnames changed 
        self.imageProcessWidget.fnamesChanged.connect(self.update_filenames)
        self.imageProcessWidget.fnamesChanged.connect(self.sinogramWidget.update_filenames)


        #update_reconstructed_data
        self.reconstructionWidget.reconChangedSig.connect(self.update_recon)
        self.reconstructionWidget.reconArrChangedSig.connect(self.update_recon_dict)
        self.laminographyWidget.reconChangedSig.connect(self.update_recon)
        self.laminographyWidget.reconArrChangedSig.connect(self.update_recon_dict)

        self.prevTab = 0
        self.TAB_FILE = 0
        self.TAB_IMAGE_PROC = 1
        self.TAB_SINOGRAM = 2
        self.TAB_RECONSTRUCTION = 3
        self.TAB_LAMINOGRAPHY = 4

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.fileTableWidget, 'Files')
        self.tab_widget.addTab(self.imageProcessWidget, "Pre Processing")
        self.tab_widget.addTab(self.sinogramWidget, "Alignment")
        self.tab_widget.addTab(self.reconstructionWidget, "Reconstruction")
        self.tab_widget.addTab(self.laminographyWidget, "Laminography")
        self.tab_widget.setTabEnabled(1,False)
        self.tab_widget.setTabEnabled(2,False)
        self.tab_widget.setTabEnabled(3,False)
        self.tab_widget.setTabEnabled(4,False)

        # self.tab_widget.currentChanged.connect(self.onTabChanged)
        #TODO: Run in separate thread
        # change save data to memory to "click to cancel" while thread is running.
        self.fileTableWidget.saveDataBtn.clicked.connect(self.updateImages)

        self.vl.addWidget(self.tab_widget)
        self.vl.addWidget(self.message_window)
        #self.vl.addWidget(self.createMessageWidget())

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        ## Top menu bar [file   Convert Option    Alignment   After saving in memory]
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        self.fileMenu = menubar.addMenu(' &File')
        self.fileMenu.addAction(openH5Action)
        self.fileMenu.addAction(openCompleteH5Action)
        self.fileMenu.addAction(openTiffAction)
        self.fileMenu.addAction(openStackAction)
        self.fileMenu.addAction(openThetaAction)
        self.fileMenu.addAction(matchFilenamesThetasAction)
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(closeAction)

        self.editMenu = menubar.addMenu(" &Edit")
        self.editMenu.addAction(undoAction)
        self.editMenu.addAction(restoreAction)
        self.editMenu.setDisabled(True)

        analysis = QMenu('Analysis', self)
        #TODO: find way to correlate elements without addind seaborn or new dependency
        # self.corrElemAction = QAction('Correlate Elements', self)
        # analysis.addAction(self.corrElemAction)
        # self.corrElemAction.triggered.connect(self.corrElem)
        # self.corrElemAction.setVisible(False)

        self.scatterPlotAction = QAction('Scatter Plot', self)
        analysis.addAction(self.scatterPlotAction)
        self.scatterPlotAction.triggered.connect(self.scatterPlot)
        self.scatterPlotAction.setVisible(False)

        self.scatterPlotReconAction = QAction('Scatter Plot Recon', self)
        analysis.addAction(self.scatterPlotReconAction)
        self.scatterPlotReconAction.triggered.connect(self.scatterPlotRecon)
        self.scatterPlotReconAction.setVisible(False)

        self.projWinAction = QAction('reprojection', self)
        analysis.addAction(self.projWinAction)
        self.projWinAction.triggered.connect(self.projWindow)

        self.pixelDistanceAction = QAction('spatial analysis', self)
        analysis.addAction(self.pixelDistanceAction)
        self.pixelDistanceAction.triggered.connect(self.pixDistanceWindow)
        self.pixelDistanceAction.setVisible(False)

        self.layerDensityAction = QAction('onion analysis', self)
        analysis.addAction(self.layerDensityAction)
        self.layerDensityAction.triggered.connect(self.onionWindow)
        self.layerDensityAction.setVisible(False)

        subPixShift = QMenu("shift step size", self)
        ag = QActionGroup(subPixShift)
        ag.setExclusive(True)
        self.subPix_1 = ag.addAction(QAction('1', subPixShift, checkable=True))
        subPixShift.addAction(self.subPix_1)
        self.subPix_1.setChecked(True)
        self.subPix_1.triggered.connect(self.subPixShiftChanged)

        self.subPix_05 = ag.addAction(QAction('2', subPixShift, checkable=True))
        subPixShift.addAction(self.subPix_05)
        self.subPix_05.triggered.connect(self.subPixShiftChanged)

        self.subPix_025 = ag.addAction(QAction('5', subPixShift, checkable=True))
        subPixShift.addAction(self.subPix_025)
        self.subPix_025.triggered.connect(self.subPixShiftChanged)

        self.subPix_01 = ag.addAction(QAction('10', subPixShift, checkable=True))
        subPixShift.addAction(self.subPix_01)
        self.subPix_01.triggered.connect(self.subPixShiftChanged)

        #
        # viewStatAct = QAction('View statusbar', self, checkable=True)
        # viewStatAct.setStatusTip('View statusbar')
        # viewStatAct.setChecked(True)
        # viewStatAct.triggered.connect(self.toggle_sps)

        self.toolsMenu = menubar.addMenu(" &Tools")
        self.toolsMenu.addMenu(analysis)
        self.toolsMenu.addMenu(subPixShift)
        self.toolsMenu.setDisabled(True)

        self.viewMenu = menubar.addMenu(" &View")
        self.viewMenu.addAction(setAspectratio)
        self.viewMenu.addAction(self.debugMode)
        self.viewMenu.setDisabled(True)

        projections_save = QMenu("Projections", self)
        ag = QActionGroup(projections_save)
        self.proj_stack = ag.addAction(QAction('proj.tiff', projections_save))
        projections_save.addAction(self.proj_stack)
        self.proj_stack.triggered.connect(self.save_proj_stack)
        self.proj_indiv = ag.addAction(QAction('projx.tiff', projections_save))
        projections_save.addAction(self.proj_indiv)
        self.proj_indiv.triggered.connect(self.save_proj_indiv)
        self.proj_npy = ag.addAction(QAction('proj.npy', projections_save))
        projections_save.addAction(self.proj_npy)
        self.proj_npy.triggered.connect(self.save_proj_npy)

        recon_save = QMenu("Reconstructions", self)
        ag = QActionGroup(recon_save)
        self.recon_stack = ag.addAction(QAction('recon.tiff', recon_save))
        recon_save.addAction(self.recon_stack)
        self.recon_stack.triggered.connect(self.save_recon_stack)
        self.recon_indiv = ag.addAction(QAction('reconx.tiff', recon_save))
        recon_save.addAction(self.recon_indiv)
        self.recon_indiv.triggered.connect(self.save_recon_indiv)
        self.recon_npy = ag.addAction(QAction('recon.npy', recon_save))
        recon_save.addAction(self.recon_npy)
        self.recon_npy.triggered.connect(self.save_recon_npy)

        sino_save = QMenu("Sinograms", self)
        ag = QActionGroup(sino_save)
        self.sino_stack = ag.addAction(QAction('sino.tiff', sino_save))
        sino_save.addAction(self.sino_stack)
        self.sino_stack.triggered.connect(self.save_sino_stack)
        self.sino_indiv = ag.addAction(QAction('sinox.tiff', sino_save))
        sino_save.addAction(self.sino_indiv)
        self.sino_indiv.triggered.connect(self.save_sino_indiv)
        self.sino_npy = ag.addAction(QAction('sino.npy', sino_save))
        sino_save.addAction(self.sino_npy)
        self.sino_npy.triggered.connect(self.save_sino_npy)

        align_save = QMenu("Alignment", self)
        ag = QActionGroup(align_save)
        self.align_npy = ag.addAction(QAction('align.npy', align_save))
        align_save.addAction(self.align_npy)
        self.align_npy.triggered.connect(self.save_align_npy)
        self.aling_txt = ag.addAction(QAction('align.txt', align_save))
        align_save.addAction(self.aling_txt)
        self.aling_txt.triggered.connect(self.save_align_txt)

        thetas_save = QMenu("thetas", self)
        ag = QActionGroup(align_save)
        self.thetas_npy = ag.addAction(QAction('thetas.npy', thetas_save))
        thetas_save.addAction(self.thetas_npy)
        self.thetas_npy.triggered.connect(self.save_thetas_npy)
        self.thetas_txt = ag.addAction(QAction('thetas.txt', thetas_save))
        thetas_save.addAction(self.thetas_txt)
        self.thetas_txt.triggered.connect(self.save_thetas_txt)

        h5_save = QMenu("hdf5", self)
        ag = QActionGroup(h5_save)
        self.all_hdf5 = ag.addAction(QAction('everything.h5', h5_save))
        h5_save.addAction(self.all_hdf5)
        self.all_hdf5.triggered.connect(self.save_hdf5)

        self.afterConversionMenu = menubar.addMenu(' &Save')
        self.afterConversionMenu.addMenu(projections_save)
        self.afterConversionMenu.addMenu(recon_save)
        self.afterConversionMenu.addMenu(sino_save)
        self.afterConversionMenu.addMenu(align_save)
        self.afterConversionMenu.addMenu(thetas_save)
        self.afterConversionMenu.addMenu(h5_save)
        # self.afterConversionMenu.addAction(self.saveThetasAction)
        # self.afterConversionMenu.addAction(self.saveToNumpyAction)
        # self.afterConversionMenu.addAction(self.saveCorrAnalysisAction)

        self.helpMenu = menubar.addMenu(' &Help')
        self.helpMenu.addAction(self.keyMapAction)
        self.helpMenu.addAction(self.configAction)
        self.helpMenu.addAction(self.softwareupdateAction)
        self.helpMenu.setVisible(False)

        self.afterConversionMenu.setDisabled(True)
        version = "1.1.0"
        add = 0
        if sys.platform == "win32":
            add = 50
        self.setGeometry(add, add, 1600 + add, 500 + add)
        self.setWindowTitle('XRFtomo v{}'.format(version))
        self.show()




        #_______________________Help/config_options______________________
        self.config_options = QtWidgets.QWidget()
        self.config_options.resize(300,400)
        self.config_options.setWindowTitle('config options')

        file_lbl = QtWidgets.QLabel("Files")
        self.directory_chbx = QtWidgets.QCheckBox("Load last directory")
        self.suffix_chbx = QtWidgets.QCheckBox("Load last suffix")
        self.thetaPV_chbx = QtWidgets.QCheckBox("Load last theta PV")
        self.image_tag_chbx = QtWidgets.QCheckBox("Load last image_tag")
        self.data_tag_chbx= QtWidgets.QCheckBox("Load last data_tag")
        self.elem_tag_chbx = QtWidgets.QCheckBox("Load last element tag")
        self.quant_chbx = QtWidgets.QCheckBox("Load last quant setting")
        self.normalize_chbx = QtWidgets.QCheckBox("Load last normalization")
        self.elememts_chbx = QtWidgets.QCheckBox("Load last element selection")
        self.files_chbx = QtWidgets.QCheckBox("Load last files selection")

        processing_lbl = QtWidgets.QLabel("pre-processing")
        self.crop_chbx = QtWidgets.QCheckBox("crop after aligning")
        self.padding_chbx = QtWidgets.QCheckBox("pad at startup")

        alignment_lbl = QtWidgets.QLabel("alignment")
        self.alingmen_chbx = QtWidgets.QCheckBox("Align at startup")

        recon_lbl = QtWidgets.QLabel("reconstruction")
        self.recon_chbx = QtWidgets.QCheckBox("reconstruct at startup")
        self.recon_all_chbx = QtWidgets.QCheckBox("reconstruct all?")
        self.recon_save_chbx = QtWidgets.QCheckBox("reconstruct and save?")
        self.recon_save_chbx = QtWidgets.QCheckBox("save simultaneously?")
        self.iter_align_param_chbx = QtWidgets.QCheckBox("load last iteration preferences")
        self.recon_method_chbx = QtWidgets.QCheckBox("Load last-used reconstruction method")

        self.toggleDebugMode(self.params.experimental)

        file_box = QtWidgets.QVBoxLayout()
        file_box.addWidget(file_lbl)
        file_box.addWidget(self.directory_chbx)
        file_box.addWidget(self.suffix_chbx)
        file_box.addWidget(self.thetaPV_chbx)
        file_box.addWidget(self.image_tag_chbx)
        file_box.addWidget(self.data_tag_chbx)
        file_box.addWidget(self.elem_tag_chbx)
        file_box.addWidget(self.quant_chbx)
        file_box.addWidget(self.normalize_chbx)
        file_box.addWidget(self.elememts_chbx)
        file_box.addWidget(self.files_chbx)

        processing_box = QtWidgets.QVBoxLayout()
        processing_box.addWidget(processing_lbl)
        processing_box.addWidget(self.crop_chbx)
        processing_box.addWidget(self.padding_chbx)

        alignment_box = QtWidgets.QVBoxLayout()
        alignment_box.addWidget(alignment_lbl)
        alignment_box.addWidget(self.alingmen_chbx)

        recon_box = QtWidgets.QVBoxLayout()
        recon_box.addWidget(recon_lbl)
        recon_box.addWidget(self.recon_chbx)
        recon_box.addWidget(self.recon_all_chbx)
        recon_box.addWidget(self.recon_save_chbx)
        recon_box.addWidget(self.recon_save_chbx)
        recon_box.addWidget(self.iter_align_param_chbx)
        recon_box.addWidget(self.recon_method_chbx)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(file_box)
        vbox.addLayout(processing_box)
        vbox.addLayout(alignment_box)
        vbox.addLayout(recon_box)

        self.config_options.setLayout(vbox)

        self.checkbox_states = eval(self.params.load_settings)
        counter = 0
        for child in self.config_options.children():
            if isinstance(child, QtWidgets.QCheckBox):
                try:
                    child.setChecked(self.checkbox_states[counter])
                except:
                    child.setChecked(False)
                    self.checkbox_states.append(False)
                child.stateChanged.connect(self.loadSettingsChanged)
                counter += 1
            else:
                pass

        #_______________________Help/keymap_options______________________
        self.keymap_options = QtWidgets.QWidget()
        self.keymap_options.resize(600,400)
        self.keymap_options.setWindowTitle('key map')
        text = QtWidgets.QLabel("Undo: \t\t Ctr+Z \t\t previous image: \t A \n\n" 
                    "shift image up: \t up \t\t next image: \t D \n\n" 
                    "shift image down: \t down  \t\t skip (hotspot): \t S \n\n"
                    "shift image left: \t left \t\t next (hotspot): \t N \n\n"
                    "shift image right: \t right  \n\n"
                    "shift stack up: \t Shift + up \n\n"
                    "shift stack down: \t Shift + down \n\n"
                    "shift stack left: \t Shift + left \n\n"
                    "shift stack right: \t Shift + right \n\n"
                    "exclude image: \t Delete \n\n"
                    "copy background: \t Ctrl + C \n\npaste background:  Ctrl + V"
                    )

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(text)
        self.keymap_options.setLayout(vbox)


        #_______________________ scatter plot window ______________________ win 1
        self.scatter_window = QtWidgets.QWidget()
        self.scatter_window.resize(1000,500)
        self.scatter_window.setWindowTitle('scatter')

        self.elem1_options = QtWidgets.QComboBox()
        self.elem1_options.setFixedWidth(100)
        self.elem2_options = QtWidgets.QComboBox()
        self.elem2_options.setFixedWidth(100)

        self.projection_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.projection_lcd = QtWidgets.QLCDNumber(self)
        projection_lbl = QtWidgets.QLabel("Projection index")
        # self.width_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        # self.width_lcd = QtWidgets.QLCDNumber(self)
        width_lbl = QtWidgets.QLabel("curve width")
        slope_lbl = QtWidgets.QLabel("Slope: ")
        self.slope_value = QtWidgets.QLineEdit("")

        self.apply_globally = QtWidgets.QPushButton("set red region to zero")

        ##_____ left blok: scatter view _____
        hboxA1 = QtWidgets.QHBoxLayout()
        hboxA1.addWidget(self.elem1_options)
        hboxA1.addWidget(self.elem2_options)
        hboxA1.addWidget(self.apply_globally)

        hboxA2 = QtWidgets.QHBoxLayout()
        hboxA2.addWidget(projection_lbl)
        hboxA2.addWidget(self.projection_lcd)
        hboxA2.addWidget(self.projection_sld)

        hboxA4 = QtWidgets.QHBoxLayout()
        hboxA4.addWidget(slope_lbl)
        hboxA4.addWidget(self.slope_value)

        vboxA1 = QtWidgets.QVBoxLayout()
        vboxA1.addWidget(self.scatterWidget)
        vboxA1.addLayout(hboxA1)
        vboxA1.addLayout(hboxA2)
        # vboxA1.addLayout(hboxA3)
        vboxA1.addLayout(hboxA4)

        ##_____ right block: recon_view _____
        self.recon_views = QtWidgets.QComboBox()
        views = ["recon #1", "recon #2", "difference:#2 - #1"]
        for k in range(len(views)):
            self.recon_views.addItem(views[k])

        self.recon_method = QtWidgets.QComboBox()
        methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad", "fbp", "sirt", "tv"]
        for k in range(len(methodname)):
            self.recon_method.addItem(methodname[k])

        self.recon_button = QtWidgets.QPushButton("reconstruct")
        self.recon_button.clicked.connect(self.updateMiniRecon)

        spacer = QtWidgets.QLabel("")

        hboxB1 = QtWidgets.QHBoxLayout()
        hboxB1.addWidget(self.recon_views)
        hboxB1.addWidget(self.recon_method)
        hboxB1.addWidget(self.recon_button)

        vboxB1 = QtWidgets.QVBoxLayout()
        vboxB1.addWidget(self.miniReconWidget)
        vboxB1.addLayout(hboxB1)
        vboxB1.addWidget(spacer)
        vboxB1.addWidget(spacer)
        vboxB1.addWidget(spacer)


        hboxC1 = QtWidgets.QHBoxLayout()
        hboxC1.addLayout(vboxA1)
        hboxC1.addLayout(vboxB1)

        self.scatter_window.setLayout(hboxC1)

        self.elem1_options.currentIndexChanged.connect(self.updateScatter)
        self.elem2_options.currentIndexChanged.connect(self.updateScatter)
        self.projection_sld.valueChanged.connect(self.updateScatter)
        # self.width_sld.valueChanged.connect(self.updateWidth)
        # self.width_sld.valueChanged.connect(self.updateInnerScatter)
        self.scatterWidget.mousePressSig.connect(self.updateInnerScatter)
        self.scatterWidget.roiDraggedSig.connect(self.updateInnerScatter)
        self.apply_globally.clicked.connect(self.sendData)
        self.slope_value.returnPressed.connect(self.slopeEntered)
        self.first_run = True


        #_______________________ scatter plot window Recon ______________________ win 2
        self.scatter_window_recon = QtWidgets.QWidget()
        self.scatter_window_recon.resize(1000,500)
        self.scatter_window_recon.setWindowTitle('scatter')

        self.elem1_options_recon = QtWidgets.QComboBox()
        self.elem1_options_recon.setFixedWidth(100)
        self.elem2_options_recon = QtWidgets.QComboBox()
        self.elem2_options_recon.setFixedWidth(100)

        self.recon_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.recon_lcd = QtWidgets.QLCDNumber(self)
        recon_lbl = QtWidgets.QLabel("Projection index")
        # self.width_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        # self.width_lcd = QtWidgets.QLCDNumber(self)
        width_lbl_recon = QtWidgets.QLabel("curve width")
        slope_lbl_recon = QtWidgets.QLabel("Slope: ")
        self.slope_value_recon = QtWidgets.QLineEdit("")



        self.apply_globally_recon = QtWidgets.QPushButton("set red region to zero")

        ##_____ left blok: scatter view _____
        hboxA1_recon = QtWidgets.QHBoxLayout()
        hboxA1_recon.addWidget(self.elem1_options_recon)
        hboxA1_recon.addWidget(self.elem2_options_recon)
        hboxA1_recon.addWidget(self.apply_globally_recon)

        hboxA2_recon = QtWidgets.QHBoxLayout()
        hboxA2_recon.addWidget(recon_lbl)
        hboxA2_recon.addWidget(self.recon_lcd)
        hboxA2_recon.addWidget(self.recon_sld)

        # hboxA3 = QtWidgets.QHBoxLayout()
        # hboxA3.addWidget(width_lbl)
        # hboxA3.addWidget(self.width_lcd)
        # hboxA3.addWidget(self.width_sld)

        hboxA4_recon = QtWidgets.QHBoxLayout()
        hboxA4_recon.addWidget(slope_lbl_recon)
        hboxA4_recon.addWidget(self.slope_value_recon)

        vboxA1_recon = QtWidgets.QVBoxLayout()
        vboxA1_recon.addWidget(self.scatterWidgetRecon)
        vboxA1_recon.addLayout(hboxA1_recon)
        vboxA1_recon.addLayout(hboxA2_recon)
        # vboxA1.addLayout(hboxA3)
        vboxA1_recon.addLayout(hboxA4_recon)



        hboxC1_recon = QtWidgets.QHBoxLayout()
        hboxC1_recon.addLayout(vboxA1_recon)

        self.scatter_window_recon.setLayout(hboxC1_recon)

        self.elem1_options_recon.currentIndexChanged.connect(self.updateScatterRecon)
        self.elem2_options_recon.currentIndexChanged.connect(self.updateScatterRecon)
        self.recon_sld.valueChanged.connect(self.updateScatterRecon)
        self.scatterWidgetRecon.mousePressSig.connect(self.updateInnerScatterRecon)
        self.scatterWidgetRecon.roiDraggedSig.connect(self.updateInnerScatterRecon)
        self.apply_globally_recon.clicked.connect(self.sendRecon)
        self.slope_value_recon.returnPressed.connect(self.slopeEnteredRecon)
        self.first_run_recon = True

        #_______________________ projecion compare window ______________________ win 3
        self.projection_window = QtWidgets.QWidget()
        self.projection_window.resize(1000,500)
        self.projection_window.setWindowTitle('reprojection tools')

        self.miniProjectionWidget1 = xrftomo.MiniReconView()
        self.miniProjectionWidget2 = xrftomo.MiniReconView()

        self.elem_options = QtWidgets.QComboBox()
        self.elem_options.setFixedWidth(100)
        spacer = QtWidgets.QLabel("")

        ##_____ left blok: scatter view _____
        hboxA1 = QtWidgets.QHBoxLayout()
        hboxA1.addWidget(self.elem_options)

        vboxA1 = QtWidgets.QVBoxLayout()
        vboxA1.addWidget(self.miniProjectionWidget1)
        vboxA1.addLayout(hboxA1)
        vboxA1.addWidget(spacer)
        

        ##_____ right block: recon_view _____
        self.compare_metric = QtWidgets.QComboBox()
        metric = ["MSE", "SSM", "pearson", "adaptive"]
        for k in range(len(metric)):
            self.compare_metric.addItem(metric[k])

        self.compare_button = QtWidgets.QPushButton("compare")
        self.compare_button.clicked.connect(self.updateMiniReproj)

        self.compare_results = QtWidgets.QLabel("-1")

        sf_lbl = QtWidgets.QLabel("scale factor")
        self.sf_txt = QtWidgets.QLabel("-1")
        # [recon#][method][recon]
        # [start_lbl][start_txt]
        # [end_lbl][end_txt]
        # [compare_metric][compare result lbl]

        spacer = QtWidgets.QLabel("")

        hboxB4 = QtWidgets.QHBoxLayout()
        hboxB4.addWidget(self.compare_metric)
        hboxB4.addWidget(self.compare_results)
        hboxB4.addWidget(self.compare_button)

        hboxB5 = QtWidgets.QHBoxLayout()
        hboxB5.addWidget(sf_lbl)
        hboxB5.addWidget(self.sf_txt)

        vboxB1 = QtWidgets.QVBoxLayout()
        vboxB1.addWidget(self.miniProjectionWidget2)
        vboxB1.addLayout(hboxB4)
        vboxB1.addLayout(hboxB5)

        hboxC1 = QtWidgets.QHBoxLayout()
        hboxC1.addLayout(vboxA1)
        hboxC1.addLayout(vboxB1)

        self.projection_window.setLayout(hboxC1)

        self.elem_options.currentIndexChanged.connect(self.updateMiniProj)
        self.first_run_a = True


  #_______________________ pixel distance window ______________________ win4
        self.pixel_distance_window = QtWidgets.QWidget()
        self.pixel_distance_window.resize(1000,500)
        self.pixel_distance_window.setWindowTitle('spatial analysis')

        self.miniReconWidget_w4 = xrftomo.MiniReconView()
        self.miniHisto_w4 = xrftomo.MiniReconView()

        self.recon_sld_w4 = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)

        recons_list_lbl = QtWidgets.QLabel("recons list")
        self.recons_list_w4 = QtWidgets.QComboBox()
        self.recons_list_w4.setFixedWidth(100)

        numbins_lbl_w4 = QtWidgets.QLabel("number of bins")
        self.numbins_box_w4 = QtWidgets.QLineEdit("100")

        stack_range1_lbl_w4 = QtWidgets.QLabel("lower slice index")
        stack_range2_lbl_w4 = QtWidgets.QLabel("upper slice index")
        self.stack_range1_w4 = QtWidgets.QLineEdit("0")
        self.stack_range2_w4 = QtWidgets.QLineEdit("1")


        ##_____ left blok: recon view _____
        hboxA_w4 = QtWidgets.QHBoxLayout()
        hboxA_w4.addWidget(recons_list_lbl)
        hboxA_w4.addWidget(self.recons_list_w4)

        hboxB_w4 = QtWidgets.QHBoxLayout()
        hboxB_w4.addWidget(numbins_lbl_w4)
        hboxB_w4.addWidget(self.numbins_box_w4)

        hboxC_w4 = QtWidgets.QHBoxLayout()
        hboxC_w4.addWidget(stack_range1_lbl_w4)
        hboxC_w4.addWidget(self.stack_range1_w4)

        hboxD_w4 = QtWidgets.QHBoxLayout()
        hboxD_w4.addWidget(stack_range2_lbl_w4)
        hboxD_w4.addWidget(self.stack_range2_w4) 

        hboxA1 = QtWidgets.QHBoxLayout()
        hboxA1.addWidget(recons_list_lbl)
        hboxA1.addWidget(self.recons_list_w4)


        vboxA1 = QtWidgets.QVBoxLayout()
        vboxA1.addWidget(self.miniReconWidget_w4)
        vboxA1.addLayout(hboxA1)
        vboxA1.addWidget(spacer)
        

        ##_____ right block: pixel distance analysis _____
        vboxB1 = QtWidgets.QVBoxLayout()
        vboxB1.addWidget(self.miniHisto_w4)

        hboxC1 = QtWidgets.QHBoxLayout()
        hboxC1.addLayout(hboxA_w4)
        hboxC1.addLayout(vboxB1)

        self.pixel_distance_window.setLayout(hboxC1)

        self.recons_list_w4.currentIndexChanged.connect(self.updateDistanceHisto)
        # self.recon_sld_w4.valueChanged.connect(self.updateDistanceHisto)
        self.first_run_w4 = True

  #_______________________ onion window ______________________ win5

        self.onion_window = QtWidgets.QWidget()
        self.onion_window.resize(1000,500)
        self.onion_window.setWindowTitle('onion analysis')

        self.miniReconWidget_w5 = xrftomo.MiniReconView()
        self.miniHisto_w5 = xrftomo.MiniReconView()

        elem1_list_lbl = QtWidgets.QLabel("recons list")
        self.elem1_list_w5 = QtWidgets.QComboBox()
        self.elem1_list_w5.setFixedWidth(100)

        elem2_list_lbl = QtWidgets.QLabel("recons list")
        self.elem2_list_w5 = QtWidgets.QComboBox()
        self.elem2_list_w5.setFixedWidth(100)

        self.recon_sld_w5 = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.recon_lcd_w5 = QtWidgets.QLCDNumber(self)
        recon_lbl_w5 = QtWidgets.QLabel("recon index")

        layer_depth_lbl_w5 = QtWidgets.QLabel("layer depth (micron)")
        elem1_thresh_lbl_w5 = QtWidgets.QLabel("element1 threshold 0-1")
        self.layer_depth_w5 = QtWidgets.QLineEdit("50")
        self.elem1_thresh_w5 = QtWidgets.QLineEdit("0.25")

        self.create_onion_button = QtWidgets.QPushButton("create onion")
        self.create_onion_button.clicked.connect(self.createOnion)

        self.run_layer_analysis = QtWidgets.QPushButton("run analysis")
        self.run_layer_analysis.clicked.connect(self.updateOnionHisto)

        ##_____ left blok: recon view _____
        hboxA_w5 = QtWidgets.QHBoxLayout()
        hboxA_w5.addWidget(elem1_list_lbl)
        hboxA_w5.addWidget(self.elem1_list_w5)
        hboxA_w5.addWidget(self.create_onion_button)

        hboxB_w5 = QtWidgets.QHBoxLayout()
        hboxB_w5.addWidget(layer_depth_lbl_w5)
        hboxB_w5.addWidget(self.layer_depth_w5)

        hboxC_w5 = QtWidgets.QHBoxLayout()
        hboxC_w5.addWidget(elem1_thresh_lbl_w5)
        hboxC_w5.addWidget(self.elem1_thresh_w5)

        hboxD_w5 = QtWidgets.QHBoxLayout()
        hboxD_w5.addWidget(recon_lbl_w5)
        hboxD_w5.addWidget(self.recon_lcd_w5)
        hboxD_w5.addWidget(self.recon_sld_w5)

        vboxA1 = QtWidgets.QVBoxLayout()
        vboxA1.addWidget(self.miniReconWidget_w5)
        vboxA1.addLayout(hboxA_w5)
        vboxA1.addLayout(hboxD_w5)
        vboxA1.addLayout(hboxB_w5)
        vboxA1.addLayout(hboxC_w5)

        ##_____ right block: pixel distance analysis _____
        hboxE_w5 = QtWidgets.QHBoxLayout()
        hboxE_w5.addWidget(elem2_list_lbl)
        hboxE_w5.addWidget(self.elem2_list_w5)
        hboxE_w5.addWidget(self.run_layer_analysis)

        vboxB1 = QtWidgets.QVBoxLayout()
        vboxB1.addWidget(self.miniHisto_w5)
        vboxB1.addLayout(hboxE_w5)

        hboxC1 = QtWidgets.QHBoxLayout()
        hboxC1.addLayout(vboxA1)
        hboxC1.addLayout(vboxB1)

        self.onion_window.setLayout(hboxC1)

        self.first_run_w5 = True
        self.onion_layers = None


    def onUpdateText(self, text):
        cursor = self.message_window.textCursor()
        cursor.insertText(text)
        self.message_window.setTextCursor(cursor)
        self.message_window.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__


    def update_software(self):
        TOP = "/".join(os.getcwd().replace("\\","/").split("/")[:-1])+"/"
        bat_file = TOP+"Menu/start_xrftomo.bat"
        with open(bat_file,'r') as f:
            lines = f.readlines()
        conda_env = os.environ['CONDA_PREFIX'].replace("\\","/").split("/")[-1]
        command_string = "cd {} \n conda activate {} \n git stash \n git pull;".format(TOP.replace("/","\\"), conda_env)
        p1 = subprocess.Popen(command_string, shell=True)
        p1.wait()

        #delete and restore .bat file
        command_string = "rm {}".format(bat_file)
        p1 = subprocess.Popen(command_string, shell=True)
        p1.wait()
        mybat = open(bat_file, 'w+')
        mybat.write(lines[0])
        mybat.close()

        #this next step will probably close the software...
        command_string = "cd {} \n conda activate {} \n pip uninstall -y xrftomo \n python setup.py install".format(TOP, conda_env)
        p1 = subprocess.Popen(command_string, shell=True)
        p1.wait()
        self.close()

    def updateOnion(self):
        if self.first_run_w5:
            e1 = 0
            self.first_run_w5 = False

        else:
            e1 = self.elem1_list_w5.currentIndex()

        self.elem1_list_w5.clear()
        self.elem2_list_w5.clear()
        try:
            self.recon_sld_w5.setRange(0, len(self.recon_dict[self.recon_dict.keys()[0]])-1)
        except TypeError:
            print("run reconstruction first")
            return


        for i in self.elements:
            self.elem1_list_w5.addItem(i)
            self.elem2_list_w5.addItem(i)
        try:
            self.elem1_list_w5.setCurrentIndex(e1)
            self.elem2_list_w5.setCurrentIndex(e1)
            self.elem1_list_w5.setCurrentText(self.elements[e1])
            self.elem2_list_w5.setCurrentText(self.elements[e1])
        except:
            self.elem1_list_w5.setCurrentIndex(0)
            self.elem2_list_w5.setCurrentIndex(0)

        recon_indx_w5 = self.recon_sld_w5.value()
        self.recon_lcd_w5.display(recon_indx_w5)
        return

    def updateOnionHisto(self):

        if self.onion_layers.any() == None:
            print('create onion first')
            return

        num_layers = self.onion_layers.max()
        total_signal = np.zeros(num_layers)
        img = self.recon_dict[self.elem2_list_w5.currentText(), self.recon_sld_w5.value()]

        for i in range(num_layers):
            depth_mask = self.onion_layers == (i+1)
            total_signal[i] = np.sum(img*depth_mask)

        #TODO: unreferenced variable X
        # self.miniHisto_w5.barView.setOpts(x=x,height=total_signal, width=9)
        return

    def createOnion(self):

        layer_depth = eval(self.layer_depth_w5.text())
        threshold = eval(self.elem1_thresh_w5.text())
        img = self.recon_dict[self.elem1_list_w5.currentText(), self.recon_sld_w5.value()]
        self.onion_slice, self.onion_layers = self.peel_onion(img,threshold,layer_depth)
        self.miniReconWidget_w5.reconView.setImage(self.onion_slice)
        pass

    def peel_onion(self, data, data_thresh, layer_depth):
        reached_core = False
        #establish surface aka first layer
        layer_0 = self.create_mask(data, data_thresh)      #bool array xy
        msk = np.ones_like(layer_0)*layer_0*1     #uint8 array xy
        msks = msk.copy()
        i = 0
        #peel away layers find out how many layers there are first
        while not reached_core:
            print("current layer: {}".format(i))
            i+=1
            try:
                msk = ndi.binary_erosion(msk, structure=np.ones((layer_depth*2, layer_depth*2)))
                msks = msk+msks
                if msk.max() == 0:
                    reached_core = True

            except: 
                reached_core = True
        mask_incremental = msks.copy()
        msks = msks*255//i
        superimposed = (msks + data/np.max(data)*layer_0*255*0.6)
        superimposed_img = superimposed//(superimposed.max()/255)
        
        return superimposed_img, mask_incremental, 


    def create_mask(self, data, mask_thresh=None, scale=.8):
        # Remove nan values
        mask_nan = np.isfinite(data)
        data[~np.isfinite(data)] = 0
        #     data /= data.max()
        # Median filter with disk structuring element to preserve cell edges.
        data = ndi.median_filter(data, size=int(data.size ** .5 * .05), mode='nearest')
        #     data = rank.median(data, disk(int(size**.5*.05)))
        # Threshold
        if mask_thresh == None:
            mask_thresh = np.nanmean(data) * scale / np.nanmax(data)
        mask = np.isfinite(data)
        mask[data / np.nanmax(data) < mask_thresh] = False
        # Remove small spots
        mask = remove_small_objects(mask, data.size // 100)
        # Remove small holes
        mask = ndi.binary_fill_holes(mask)
        return mask * mask_nan

    def updateMiniReproj(self):

        e1 = self.elem_options.currentIndex()

        data = self.data
        element= e1

        try:
            recon = self.recon
        except:
            return 0,0
        self.reprojection = self.reproject(recon)
        try:
            dummy, sf = self.compare_projections(self.compare_metric.currentIndex(), self.proj, self.reprojection)
        except:
            sf = 1
            pass

        self.reprojection /= sf
        results, dummy = self.compare_projections(self.compare_metric.currentIndex(), self.proj, self.reprojection)

        self.compare_results.setText(str(results))
        self.sf_txt.setText(str(sf))

        self.miniProjectionWidget2.reconView.setImage(self.reprojection)
        return


    def reproject(self, recon):
        try:
            num_slices = recon.shape[0]
        except:
            return

        width = recon.shape[1]
        reprojection = np.zeros([num_slices, width])
        tmp = np.zeros([num_slices, width])

        for i in range(num_slices):
            reprojection[i] = np.sum(recon[i], axis=0)

        return reprojection

    def compare_projections(self, metric, projA, projB):
        d = len(projA)
        if d < 2:
            return 0, 0

        if metric == 0: #MSE
            err = projA - projB
            #mean squared error
            result = (np.square(err)).mean(axis=None)
            sf = np.sum(projB)/np.sum(projA)

        elif metric == 1: #SSM
            errMat = np.zeros(projA.shape[0])
            simMat = np.zeros(projA.shape[0])

            for i in range(projA.shape[0]):
                err = np.sum((projA[i].astype("float") - projB[i].astype("float")) ** 2)
                try:
                    err /= float(projA[i].shape[0] * projA[i].shape[1])
                except:
                    print("error")
                    result = -1
                    sf = -1
                    return result, sf
                sim = measure.compare_ssim(projA[i], projB[i])

                errMat[i] = err
                simMat[i] = sim
                errVal = np.sum(errMat)/len(errMat)
                simVal = np.sum(simMat)/len(simMat)
            result = simVal
            sf = np.sum(projB)/np.sum(projA)


        elif metric == 2: #pearson
            result, p = stats.pearsonr(projA.flatten(), projB.flatten())

            sf = np.sum(projB)/np.sum(projA)


        elif metric == 3:
            scaler_arr = np.zeros(projA.shape[0])
            for i in range(projA.shape[0]):

                if projA[i].max() == 0:
                    projA[i] = np.zeros(projA.shape[1])
                else:
                    scaler_arr[i] = projB[i].max()/projA[i].max()
            new_reprojection = np.asarray([projB[i]*scaler_arr[i] for i in range(len(scaler_arr))])
            sf = np.mean(scaler_arr[scaler_arr> scaler_arr.max()*.5])
            #mean squared error
            result = (np.square(projA - new_reprojection)).mean(axis=None)

        else:
            result = -1
            sf = -1

        return result, sf
        


    def updateMiniProj(self):
        thetas = self.thetas
        if self.first_run_a:
            e1 = 0
            self.first_run_a = False

        else:
            e1 = self.elem_options.currentIndex()

        self.elem_options.currentIndexChanged.disconnect(self.updateMiniProj)
        self.elem_options.clear()

        for i in self.elements:
            self.elem_options.addItem(i)
        try:
            self.elem_options.setCurrentIndex(e1)
            self.elem_options.setCurrentText(self.elements[e1])
        except:
            self.elem_options.setCurrentIndex(0)

        #find where proj index angle ==0:
        zero_index = np.where(abs(thetas)==abs(thetas).min())[0][0]
        self.proj = np.flipud(self.data[e1,zero_index])

        self.elem_options.currentIndexChanged.connect(self.updateMiniProj)
        self.miniProjectionWidget1.reconView.setImage(self.proj)
        return

    def updateDistanceHisto(self):
        if self.first_run_w4:
            e1 = 0
            self.first_run_w4 = False

        else:
            e1 = self.recons_list_w4.currentIndex()
        try:
            self.recons_list_w4.currentIndexChanged.disconnect(self.updateDistanceHisto)
        except:
            print("method not connected")
        self.recons_list_w4.clear()
        try:
            #TODO: tried running spatial analysis without reconstructing, it failed. fix this
            """line 1149, in updateDistanceHisto self.recon_sld_w4.setRange(0, len(self.recon_dict[list(self.recon_dict.keys())[0]]) - 1)
            IndexError: list
            index
            out
            of
            range"""

            self.recon_sld_w4.setRange(0, len(self.recon_dict[list(self.recon_dict.keys())[0]])-1)
        except TypeError:
            print("run reconstruction first")
            return

        elem_indx_w4 = self.recons_list_w4.currentIndex()
        recon_indx_w4 = self.recon_sld_w4.value()

        for i in self.elements:
            self.recons_list_w4.addItem(i)
        try:
            self.recons_list_w4.setCurrentIndex(e1)
            self.recons_list_w4.setCurrentText(self.elements[e1])
        except:
            self.recons_list_w4.setCurrentIndex(0)

        self.recons_list_w4.currentIndexChanged.connect(self.updateDistanceHisto)

        ##calculate distance_array
        recon_element = self.recons_list_w4.currentText()
        recon_indx = self.recon_sld_w4.value()

        distance_array = self.calculate_all_distances(self.recon_dict[recon_element])
        
        #generate histogram
        # Creating histogram 
        fig, axs = plt.subplots(1, 1, figsize =(10, 7), tight_layout = True)
        #whole numbers
        distance_array = distance_array.round()
        #cutoff max distance
        # distance_array[distance_array < 100]
        #calculate number of bins based on max value
        num_bins = int(distance_array.max())

        axs.hist(distance_array, bins = num_bins,  density = True)
        axs.set_title(self.fileTableWidget.dirLineEdit.text())
        axs.set_xlabel("distance (micron)")
        #    Show plot
        plt.show()

        return

    def calculate_pixel_distance(self,img):
        #TODO: do something if empty array
        point_arr = []


        #filter image so there arent so many points to calculate distances for,
        img[img<img.max()*0.05] = 0
        #then downsample the image to 50% or variable.

        #find non-zero pixels in image
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i,j]>0:
                    point_arr.append([i,j])

        #find pixel distances using combination of points array, nCr.
        point_arr = np.asanyarray(point_arr)
        num_points = len(point_arr)
        sub_points = list(np.arange(1, num_points))
        distance_arr = []
        for i in range(num_points-1):
            if len(sub_points)==0:
                break
            for j in sub_points:
                distance_arr.append(np.sqrt( (point_arr[i,0]-point_arr[j,0])**2 +
                                             (point_arr[i,1]-point_arr[j,1])**2  ))
            del sub_points[0]

        print(distance_arr)
        return distance_arr

    def calculate_all_distances(self,img_stack):
        #remove slices in stack where values all zero
        num_slices = img_stack.shape[0]
        non_zero_slices = []
        for i in range(num_slices):
            if img_stack[i].max()>0:
                non_zero_slices.append(i)

        slice_arr = [img_stack[i] for i in non_zero_slices]
        num_images = len(slice_arr)
        if len(slice_arr)==0:
            print("")
            return
        distance_arr = np.asarray(self.calculate_pixel_distance(slice_arr[0]))


        for i in range(1, num_images):
            distance_arr = np.append(distance_arr, np.asarray(self.calculate_pixel_distance(slice_arr[i])))

        return distance_arr

    def update_padding(self, x,y):
        self.sinogramWidget.x_padding_hist.append(x)
        self.sinogramWidget.y_padding_hist.append(y)


    def subPixShiftChanged(self):

        shift_size_arr = np.array([1,2,5,10])
        bool_arr = [self.subPix_1.isChecked(), self.subPix_05.isChecked(), self.subPix_025.isChecked(),self.subPix_01.isChecked()]
        shift_size = shift_size_arr[bool_arr.index(True)]
        print(str(shift_size))

        self.sinogramWidget.sub_pixel_shift = shift_size
        self.imageProcessWidget.sub_pixel_shift = shift_size
        return

    def hardwareSelectChanged(self):
        bool_arr = [self.CPU.isChecked(), self.GPU.isChecked()]
        if self.CPU.isChecked():
            #TODO: reconstructionWidget; populate recon-method with CPU options

            pass
        else:
            #TODO: reconstructionWidget; populate recon-method with GPU options
            pass


    def updateScatter(self):
        if self.first_run:
            self.scatterWidget.ROI.endpoints[1].setPos(self.data[0,0].max(), self.data[0,0].max())
            e1 = 0
            e2 = 0

            self.first_run = False

        else:
            e1 = self.elem1_options.currentIndex()
            e2 = self.elem2_options.currentIndex()

        self.projection_sld.setRange(0, self.data.shape[1]-1)
        self.elem1_options.currentIndexChanged.disconnect(self.updateScatter)
        self.elem2_options.currentIndexChanged.disconnect(self.updateScatter)

        proj_indx = self.projection_sld.value()
        self.elem1_options.clear()
        self.elem2_options.clear()

        for i in self.elements:
            self.elem1_options.addItem(i)
            self.elem2_options.addItem(i)
        try:
            self.elem1_options.setCurrentIndex(e1)
            self.elem1_options.setCurrentText(self.elements[e1])
            self.elem2_options.setCurrentIndex(e2)
            self.elem2_options.setCurrentText(self.elements[e2])
            self.scatterWidget.p1.setLabel(axis='left', text=self.elements[e1])
            self.scatterWidget.p1.setLabel(axis='bottom', text=self.elements[e2])

        except:
            self.elem1_options.setCurrentIndex(0)
            self.elem2_options.setCurrentIndex(0)

        elem1 = self.data[e1,proj_indx]
        elem1 = elem1.flatten()
        elem2 = self.data[e2, proj_indx]
        elem2 = elem2.flatten()

        #update projection index LCD
        self.projection_lcd.display(self.projection_sld.value())

        self.elem1_options.currentIndexChanged.connect(self.updateScatter)
        self.elem2_options.currentIndexChanged.connect(self.updateScatter)
        # self.elem1_options.currentIndexChanged.connect(self.updateInnerScatter)
        # self.elem2_options.currentIndexChanged.connect(self.updateInnerScatter)

        self.scatterWidget.plotView.setData(elem2, elem1)
        self.scatterWidget.p1.setLabel(axis='left', text=self.elements[e1])
        self.scatterWidget.p1.setLabel(axis='bottom', text=self.elements[e2])
        self.updateInnerScatter()
        return




    # def updateWidth(self):

    #     # self.width_lcd.display(self.width_sld.value())
    #     width_values = np.linspace(0,1,101)
    #     self.width_sld.setRange(0, len(width_values)-1)
    #     self.width_lcd.display(width_values[self.width_sld.value()])
    #     return

    def updateInnerScatter(self,*dummy):
        self.scatterWidget.mousePressSig.disconnect(self.updateInnerScatter)
        self.scatterWidget.roiDraggedSig.disconnect(self.updateInnerScatter)
        e1 = self.elem1_options.currentIndex()
        e2 = self.elem2_options.currentIndex()

        #Normalizeself.projection_sld.currentIndex()
        elem1 = self.data[self.elem1_options.currentIndex(),self.projection_sld.value()]
        elem1 = elem1.flatten()
        elem2 = self.data[self.elem2_options.currentIndex(), self.projection_sld.value()]
        elem2 = elem2.flatten()

        # get slope then calculate new handle pos
        x_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().x()
        y_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().y()
        try:
            slope = y_pos/x_pos
        except ZeroDivisionError:
            slope = 1


        x_pos = 1/slope
        y_pos = x_pos*slope

        if elem2.max()*slope < elem1.max():
            x_pos = elem2.max()
            y_pos = x_pos*slope
        if elem2.max()*slope > elem1.max():
            x_pos = elem1.max()/slope
            y_pos = x_pos*slope

        self.scatterWidget.ROI.endpoints[1].setPos(x_pos,y_pos)
        self.slope_value.setText(str(round(slope,4)))

        tmp_arr = [(slope*elem2) <= elem1]
        tmp_elem1 = elem1[tmp_arr[0]]
        tmp_elem2 = elem2[tmp_arr[0]]
        self.scatterWidget.plotView2.setData(tmp_elem2, tmp_elem1, brush='r')

        self.scatterWidget.mousePressSig.connect(self.updateInnerScatter)
        self.scatterWidget.roiDraggedSig.connect(self.updateInnerScatter)

        return

    def slopeEntered(self):
        slope = eval(self.slope_value.text())
        if slope < 0 :
            return
        self.scatterWidget.mousePressSig.disconnect(self.updateInnerScatter)
        self.scatterWidget.roiDraggedSig.disconnect(self.updateInnerScatter)


        e1 = self.elem1_options.currentIndex()
        e2 = self.elem2_options.currentIndex()

        #Normalizeself.projection_sld.currentIndex()
        elem1 = self.data[self.elem1_options.currentIndex(),self.projection_sld.value()]
        elem1 = elem1.flatten()
        elem2 = self.data[self.elem2_options.currentIndex(), self.projection_sld.value()]
        elem2 = elem2.flatten()
        x_pos = 1/slope
        y_pos = x_pos*slope

        if elem2.max()*slope < elem1.max():
            x_pos = elem2.max()
            y_pos = x_pos*slope
        if elem2.max()*slope > elem1.max():
            x_pos = elem1.max()/slope
            y_pos = x_pos*slope

        self.scatterWidget.ROI.endpoints[1].setPos(x_pos,y_pos)
        self.slope_value.setText(str(round(slope,4)))

        tmp_arr = [(slope*elem2) <= elem1]
        tmp_elem1 = elem1[tmp_arr]
        tmp_elem2 = elem2[tmp_arr]
        self.scatterWidget.plotView2.setData(tmp_elem2, tmp_elem1, brush='r')

        self.scatterWidget.mousePressSig.connect(self.updateInnerScatter)
        self.scatterWidget.roiDraggedSig.connect(self.updateInnerScatter)


    def updateScatterRecon(self):
        if self.first_run_recon:
            try:
                #TODO: ran scatterplot without reconstructing, it failed
                self.scatterWidget.ROI.endpoints[1].setPos(self.recon.shape[1], self.recon.shape[1])
                e1 = 0
                e2 = 0

                self.recon_sld.setRange(0, self.recon.shape[0] - 1)
                self.elem1_options_recon.currentIndexChanged.disconnect(self.updateScatterRecon)
                self.elem2_options_recon.currentIndexChanged.disconnect(self.updateScatterRecon)
                recon_indx = self.recon_sld.value()
                self.elem1_options_recon.clear()
                self.elem2_options_recon.clear()

                for i in self.elements:
                    self.elem1_options_recon.addItem(i)
                    self.elem2_options_recon.addItem(i)
                try:
                    self.elem1_options_recon.setCurrentIndex(e1)
                    self.elem1_options_recon.setCurrentText(self.elements[e1])
                    self.elem2_options_recon.setCurrentIndex(e2)
                    self.elem2_options_recon.setCurrentText(self.elements[e2])
                    self.scatterWidgetRecon.p1.setLabel(axis='left', text=self.elements[e1])
                    self.scatterWidgetRecon.p1.setLabel(axis='bottom', text=self.elements[e2])

                except:
                    self.elem1_options_recon.setCurrentIndex(0)
                    self.elem2_options_recon.setCurrentIndex(0)

                e1 = self.elem1_options_recon.currentIndex()
                e2 = self.elem2_options_recon.currentIndex()
                e1_txt = self.elem1_options_recon.currentText()
                e2_txt = self.elem2_options_recon.currentText()
                elem1 = self.recon_dict[e1_txt][recon_indx]
                elem1 = elem1.flatten()
                elem2 = self.recon_dict[e2_txt][recon_indx]
                elem2 = elem2.flatten()


                self.first_run_recon = False
            except TypeError:
                print("run reconstruction first")
                return
        else:
            recon_indx = self.recon_sld.value()
            e1 = self.elem1_options_recon.currentIndex()
            e2 = self.elem2_options_recon.currentIndex()
            e1_txt = self.elem1_options_recon.currentText()
            e2_txt = self.elem2_options_recon.currentText()
            elem1 = self.recon_dict[e1_txt][recon_indx]
            elem1 = elem1.flatten()
            elem2 = self.recon_dict[e2_txt][recon_indx]
            elem2 = elem2.flatten()


        #update projection index LCD
        self.recon_lcd.display(self.recon_sld.value())
        self.elem1_options_recon.currentIndexChanged.connect(self.updateScatterRecon)
        self.elem2_options_recon.currentIndexChanged.connect(self.updateScatterRecon)
        self.scatterWidgetRecon.plotView.setData(elem2, elem1)
        self.scatterWidgetRecon.p1.setLabel(axis='left', text=self.elements[e1])
        self.scatterWidgetRecon.p1.setLabel(axis='bottom', text=self.elements[e2])
        self.updateInnerScatterRecon()
        return


    def updateInnerScatterRecon(self,*dummy):
        self.scatterWidgetRecon.mousePressSig.disconnect(self.updateInnerScatterRecon)
        self.scatterWidgetRecon.roiDraggedSig.disconnect(self.updateInnerScatterRecon)
        e1 = self.elem1_options_recon.currentText()
        e2 = self.elem2_options_recon.currentText()

        #Normalizeself.projection_sld.currentIndex()

        elem1 = self.reconstructionWidget.recon_dict[e1][self.recon_sld.value()]
        elem1 = elem1.flatten()
        elem2 = self.reconstructionWidget.recon_dict[e2][self.recon_sld.value()]
        elem2 = elem2.flatten()

        # get slope then calculate new handle pos
        x_pos = self.scatterWidgetRecon.p1.items[3].getHandles()[1].pos().x()
        y_pos = self.scatterWidgetRecon.p1.items[3].getHandles()[1].pos().y()
        try:
            slope = y_pos/x_pos
        except ZeroDivisionError:
            slope = 1

        x_pos = 1/slope
        y_pos = x_pos*slope

        if elem2.max()*slope < elem1.max():
            x_pos = elem2.max()
            y_pos = x_pos*slope
        if elem2.max()*slope > elem1.max():
            x_pos = elem1.max()/slope
            y_pos = x_pos*slope

        self.scatterWidgetRecon.ROI.endpoints[1].setPos(x_pos,y_pos)
        self.slope_value_recon.setText(str(round(slope,4)))

        tmp_arr = [(slope*elem2) <= elem1]
        tmp_elem1 = elem1[tmp_arr[0]]
        tmp_elem2 = elem2[tmp_arr[0]]
        self.scatterWidgetRecon.plotView2.setData(tmp_elem2, tmp_elem1, brush='r')

        self.scatterWidgetRecon.mousePressSig.connect(self.updateInnerScatterRecon)
        self.scatterWidgetRecon.roiDraggedSig.connect(self.updateInnerScatterRecon)

        return

    def slopeEnteredRecon(self):
        slope = eval(self.slope_value_recon.text())
        if slope < 0 :
            return
        self.scatterWidgetRecon.mousePressSig.disconnect(self.updateInnerScatterRecon)
        self.scatterWidgetRecon.roiDraggedSig.disconnect(self.updateInnerScatterRecon)

        e1 = self.elem1_options_recon.currentText()
        e2 = self.elem2_options_recon.currentText()
        elem1 = self.reconstructionWidget.recon_dict[e1][self.recon_sld.value()]
        elem1 = elem1.flatten()
        elem2 = self.reconstructionWidget.recon_dict[e2][self.recon_sld.value()]
        elem2 = elem2.flatten()

        #TODO: Exception error div by zero
        try:
            x_pos = 1/slope
        except ZeroDivisionError:
            x_pos = 1

        y_pos = x_pos*slope


        if elem2.max()*slope < elem1.max():
            x_pos = elem2.max()
            y_pos = x_pos*slope
        if elem2.max()*slope > elem1.max():
            x_pos = elem1.max()/slope
            y_pos = x_pos*slope

        self.scatterWidgetRecon.ROI.endpoints[1].setPos(x_pos,y_pos)
        self.slope_value_recon.setText(str(round(slope,4)))

        tmp_arr = [(slope*elem2) <= elem1]
        tmp_elem1 = elem1[tmp_arr]
        tmp_elem2 = elem2[tmp_arr]
        self.scatterWidgetRecon.plotView2.setData(tmp_elem2, tmp_elem1, brush='r')

        self.scatterWidgetRecon.mousePressSig.connect(self.updateInnerScatterRecon)
        self.scatterWidgetRecon.roiDraggedSig.connect(self.updateInnerScatterRecon)


    #TODO: remove mini-recon stuff 
    def updateMiniRecon(self):
        
        e1 = self.elem1_options.currentIndex()
        e2 = self.elem2_options.currentIndex()

        data2 = self.data.copy()
        element= e2
        original_shape = data2[element,0].shape
        tmp_data = np.zeros_like(data2[element])


        #_____ calculate points within bounded region _____
        #get handle pos
        x_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().x()
        y_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().y()
        slope = y_pos/x_pos

        for i in range(data2.shape[1]):
            #Normalizeself.projection_sld.currentIndex()
            elem1 = self.data[e1,i] 
            elem1 = elem1.flatten()

            elem2 = self.data[e2, i]
            elem2 = elem2.flatten()

            tmp_arr = [(slope * elem2) < elem1]
            bounded_index = np.where(tmp_arr)[1]

            tmp = data2[e2, i].flatten()
            tmp[bounded_index] = 0
            tmp_data[i] = tmp.reshape(original_shape)


        data2[element] = tmp_data
        center = self.data.shape[3]//2
        beta = 1
        delta = 0.01
        iters = 10
        thetas = self.thetas
        mid_indx = data2.shape[2]//2
        tmp_data2 = data2.copy()
        tmp_data2[element] = tmp_data
        tmp_data2 = tmp_data2[:, :, mid_indx:mid_indx + 1, :]

        #TODO: unresolved method
        recon = self.reconstructionWidget.actions.reconstruct(tmp_data2, element, center, beta, delta, iters, thetas, 0, show_stats=False)

        self.miniReconWidget.reconView.setImage(recon[0])
        return

    def sendData(self):

        e1 = self.elem1_options.currentIndex()
        e2 = self.elem2_options.currentIndex()
        proj_indx = self.projection_sld.value()

        data2 = self.data.copy()
        element= e2
        original_shape = data2[element,0].shape
        tmp_data = np.zeros_like(data2[element])

        #get handle pos
        x_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().x()
        y_pos = self.scatterWidget.p1.items[3].getHandles()[1].pos().y()
        slope = y_pos/x_pos

        for i in range(data2.shape[1]):
            #Normalizeself.projection_sld.currentIndex()
            elem1 = self.data[e1,i] 
            elem1 = elem1.flatten()
            data1 = self.data[e1,i].flatten()

            elem2 = self.data[e2, i]
            elem2 = elem2.flatten()

            tmp_arr = [(slope * elem2) < elem1]
            bounded_index = np.where(tmp_arr)[1]

            tmp = data2[e2, i].flatten()
            tmp[bounded_index] = 0
            tmp_data[i] = tmp.reshape(original_shape)

        data2[element] = tmp_data

        self.data = data2.copy()
        self.update_data(self.data)


    def sendRecon(self):

        e1 = self.elem1_options_recon.currentText()
        e2 = self.elem2_options_recon.currentText()
        # recon_indx = self.recon_sld.value()

        recon2 = self.recon_dict[e2].copy()
        original_shape = recon2[0].shape
        tmp_data = np.zeros_like(recon2)

        #get handle pos
        x_pos = self.scatterWidgetRecon.p1.items[3].getHandles()[1].pos().x()
        y_pos = self.scatterWidgetRecon.p1.items[3].getHandles()[1].pos().y()
        slope = y_pos/x_pos

        for i in range(recon2.shape[0]-1):
            #Normalizeself.projection_sld.currentIndex()
            elem1 = self.recon_dict[e1][i].flatten()
            elem2 = self.recon_dict[e2][i].flatten()

            tmp_arr = [(slope * elem2) < elem1]
            bounded_index = np.where(tmp_arr)[1]

            tmp = recon2[i].flatten()
            tmp[bounded_index] = 0
            tmp_data[i] = tmp.reshape(original_shape)

        recon2 = tmp_data

        self.recon = recon2.copy()
        self.recon_dict[e2] = recon2.copy()
        self.update_recon(self.recon)
        self.update_recon_dict(self.recon_dict)

    def refresh_filetable(self):
        self.fileTableWidget.onLoadDirectory()
        return

    def toggleDebugMode(self, *mode):
        mode = mode[0]
        if mode == False or mode == True:
            self.set_debugMode(mode)
            self.debugMode.setChecked(mode)
        else:
            self.params.experimental = not self.params.experimental
            mode = self.params.experimental
            self.debugMode.setChecked(mode)
            self.set_debugMode(mode)

    def toggle_aspect_ratio(self, checkbox_state):
        if checkbox_state:
            self.imageProcessWidget.imageView.p1.vb.setAspectLocked(True)
            self.sinogramWidget.sinoView.p1.vb.setAspectLocked(True)
            self.sinogramWidget.imageView.p1.vb.setAspectLocked(True)
            # self.sinogramWidget.diffView.p1.vb.setAspectLocked(True)
            self.reconstructionWidget.ReconView.p1.vb.setAspectLocked(True)
            self.laminographyWidget.ReconView.p1.vb.setAspectLocked(True)
        else:
            self.imageProcessWidget.imageView.p1.vb.setAspectLocked(False)
            self.sinogramWidget.sinoView.p1.vb.setAspectLocked(False)
            self.sinogramWidget.imageView.p1.vb.setAspectLocked(False)
            # self.sinogramWidget.diffView.p1.vb.setAspectLocked(False)
            self.reconstructionWidget.ReconView.p1.vb.setAspectLocked(False)
            self.laminographyWidget.ReconView.p1.vb.setAspectLocked(False)

    def loadSettingsChanged(self):
        load_settings = []
        for child in self.config_options.children():
            if isinstance(child, QtWidgets.QCheckBox):
                load_settings.append(child.isChecked())
            else:
                pass

        self.params.load_settings = str(load_settings)
        # return
    def set_debugMode(self, mode):

        self.sinogramWidget.ViewControl.iterative.setVisible(mode)
        self.sinogramWidget.ViewControl.pirt.setVisible(mode)
        self.sinogramWidget.ViewControl.opflow.setVisible(mode)
        self.sinogramWidget.ViewControl.cross_correlate_sinogram.setVisible(mode)
        self.sinogramWidget.ViewControl.dy_sum.setVisible(mode)
        self.sinogramWidget.ViewControl.center.setVisible(mode)
        self.sinogramWidget.ViewControl.phasecor.setVisible(mode)
        self.sinogramWidget.ViewControl.adjust_sino.setVisible(mode)
        self.sinogramWidget.ViewControl.change_rotation_axis.setVisible(mode)

        self.reconstructionWidget.ViewControl.beta_lbl.setVisible(mode)
        self.reconstructionWidget.ViewControl.delta_lbl.setVisible(mode)
        self.reconstructionWidget.ViewControl.lower_thresh_lbl.setVisible(mode)
        self.reconstructionWidget.ViewControl.beta.setVisible(mode)
        self.reconstructionWidget.ViewControl.delta.setVisible(mode)
        self.reconstructionWidget.ViewControl.lower_thresh.setVisible(mode)

        self.scatterPlotAction.setVisible(mode)
        self.scatterPlotReconAction.setVisible(mode)
        self.layerDensityAction.setVisible(mode)
        self.pixelDistanceAction.setVisible(mode)

        self.saveCorrAnalysisAction.setVisible(mode)
        # self.saveRecon2npyAction.setVisible(mode)
        # self.saveToNumpyAction.setVisible(mode)

        return

    def openFolder(self):
        try:
            folderName = QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
        except IndexError:
            print("no folder has been selected")
        except OSError:
            print("no folder has been selected")
        return folderName

    def openH5(self):
        currentDir = self.fileTableWidget.dirLineEdit.text()
        files = QFileDialog.getOpenFileNames(self, "Open h5", QtCore.QDir.currentPath(), "h5 (*.h5*)" )
        files = files[0]
        if files == '' or files== []:
            return
        ext = self.fileTableWidget.extLineEdit.text().strip("*.")
        dir_ending_index = files[0].rfind("/")
        path = files[0][:dir_ending_index]
        files = [files[i] for i, file in enumerate(files) if file.split(".")[-1]==ext]
        fnames = [file.split("/")[-1] for file in files]


        self.fileTableWidget.dirLineEdit.setText(path)
        self.fileTableWidget.extLineEdit.setText(ext)
        self.clear_all()
        if files == []:
            print("check file extension")
            return
        self.fileTableWidget.onLoadDirectory(files, path)

        #disable preprocessing, alignment, reconstructions, save, tools and edit, 
        #Clear self.data, history and reset everytihng prior to loading. 

        self.tab_widget.setTabEnabled(1,False)
        self.tab_widget.setTabEnabled(2,False)
        self.tab_widget.setTabEnabled(3,False)
        self.tab_widget.setTabEnabled(4,False)
        self.afterConversionMenu.setDisabled(True)
        self.editMenu.setDisabled(True)
        self.toolsMenu.setDisabled(True)


    def open_complete_H5(self):
        self.fileTableWidget.data_menu.clear()
        self.fileTableWidget.element_menu.clear()
        self.fileTableWidget.scaler_menu.clear()
        self.fileTableWidget.theta_menu.clear()
        currentDir = self.fileTableWidget.dirLineEdit.text()
        file = QFileDialog.getOpenFileName(self, "Open complete h5", currentDir, "h5 (*.h5*)")
        file = file[0]
        if file == '' or file == []:
            return

        self.fileTableWidget.dirLineEdit.setText("")
        self.fileTableWidget.extLineEdit.setText("h5")
        self.clear_all()
        if file == []:
            print("check file extension")
            return
        img = h5py.File(file, 'r')
        fnames = img["names"]
        data = img["data"]
        elements = img["elements"]
        thetas = [float(theta) for theta in list(img["thetas"])]
        # recons = img["recons"]

        self.fnames = [fname.decode("utf-8").split("/")[-1] for fname in list(fnames)]
        self.data = np.array(data)
        self.elements = [element.decode("utf-8") for element in list(elements)]
        self.thetas = np.array(thetas)

        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        self.tab_widget.setTabEnabled(4, False)
        self.afterConversionMenu.setDisabled(True)
        self.editMenu.setDisabled(True)
        self.toolsMenu.setDisabled(True)

        self.update_data(self.data)
        # self.recon_dict = {}
        # for i, element in enumerate(self.elements):
        #     self.recon_dict[element] = recons[i]

        self.updateImages(True)
        # self.reconstructionWidget.recon_dict = self.recon_dict
        # self.reconstructionWidget.recon = recons[0]
        # self.laminographyWidget.recon_dict = self.recon_dict
        # self.laminographyWidget.recon = recons[0]
        self.fileTableWidget.fileTableModel.update_fnames(self.fnames)
        self.fileTableWidget.fileTableModel.update_thetas(thetas)
        self.fileTableWidget.fileTableView.sortByColumn(1, 0)
        self.fileTableWidget.elementTableModel.loadElementNames(self.elements)
        self.fileTableWidget.elementTableModel.setAllChecked(True)
        print("saved to memory")

        return
    def openTiffs(self):
        files = QFileDialog.getOpenFileNames(self, "Open Tiffs", QtCore.QDir.currentPath(), "TIFF (*.tiff *.tif)" )
        if files[0] == '' or files[0] == []:
            return

        dir_ending_index = files[0][0].split(".")[0][::-1].find("/")+1
        path = files[0][0].split(".")[0][:-dir_ending_index]
        ext = "*."+files[0][0].split(".")[-1]
        self.fileTableWidget.dirLineEdit.setText(path)
        self.fileTableWidget.extLineEdit.setText(ext)
        # self.clear_all()
        self.fileTableWidget.onLoadDirectory()

        #disable preprocessing, alignment, reconstructions, save, tools and edit, 
        #Clear self.data, history and reset everytihng prior to loading. 

        self.data = xrftomo.read_tiffs(files[0])
        self.fnames = [files[0][i].split("/")[-1] for i in range(len(files[0]))]
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        self.tab_widget.setTabEnabled(4, False)
        self.afterConversionMenu.setDisabled(True)
        self.editMenu.setDisabled(True)
        self.toolsMenu.setDisabled(True)
        self.update_data(self.data)
        return

    def openStack(self):
        file = QFileDialog.getOpenFileName(self, "Open Theta.txt", QtCore.QDir.currentPath(), "tiff (*.tiff)" )
        if file[0] == '':
            return
        im = io.imread(file[0])
        data = np.zeros([1, im.shape[0], im.shape[1], im.shape[2]])
        data[0] = im
        self.data = data
        self.fnames = ["file_{}".format(i) for i in range(self.data.shape[1])]
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        self.tab_widget.setTabEnabled(4, False)
        self.afterConversionMenu.setDisabled(True)
        self.editMenu.setDisabled(True)
        self.toolsMenu.setDisabled(True)
        # update images seems to have dissappeare.

        self.thetas = np.asarray([i for i in range(self.data.shape[1])])
        self.elements = ["Channel_1"]
        self.updateImages(True)
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setTabEnabled(2, True)
        self.tab_widget.setTabEnabled(3, True)
        if self.tcp_installed: self.tab_widget.setTabEnabled(4, True)


        self.afterConversionMenu.setDisabled(False)
        self.editMenu.setDisabled(False)
        self.toolsMenu.setDisabled(False)
        self.viewMenu.setDisabled(False)
        print("Angle information loaded.")

    def openThetas(self):
        file = QFileDialog.getOpenFileName(self, "Open Theta.txt", QtCore.QDir.currentPath(), "text (*.txt)" )
        if file[0] == '':
            return

        try:
            tmp = self.data
            if tmp.all() == None:
                raise AttributeError
            data_loaded = True
            num_projections = self.data.shape[1]
        except ValueError:
            pass
        except AttributeError:
            # checking that number of projections is the same as the number of angles being loaded from text file,
            # but in the case that thetas are loaded before loading projections, then self.data will not be defined.
            # 1) check if fnames are loaded in filetable: if yes, compare against those.
            # 2) if not, insert message to select a directory with valid h5 files or load tiffs first.
            data_loaded = False
            try:
                #case 1 is true, check for number of fnames and create a list of these fnames as self.fnames
                num_projections = len(self.fileTableWidget.fileTableModel.arrayData)
                self.fnames = [self.fileTableWidget.fileTableModel.arrayData[x].filename for x in range(num_projections)]

            except AttributeError:
                # case 1 is false:
                # show message asking user to load data first or select valid directory.
                print("select valid directory or load data first. ")
                return
        try:
            fnames, thetas = xrftomo.load_thetas_file(file[0])
            num_projections = self.data.shape[1]
            self.fnames = [self.fileTableWidget.fileTableModel.arrayData[x].filename for x in range(num_projections)]
        except:
            return
        if not len(thetas)==len(fnames):
            print("nummber of angles different than number of loaded images. ")
            return

        if thetas == []:
            print("No angle information loaded")
            return

        if fnames == []:
            print("No filenames in .txt. Assuming Tiff order corresponds to loaded theta order")
            sorted_index = np.argsort(thetas)
            thetas = np.asarray(thetas)[sorted_index]
            self.fnames = np.asarray(self.fnames)[sorted_index]

        #compare list size first:
        if len(fnames) != len(thetas):
            print("number of projections differ from number of loaded angles")
            return

        #filenames from textfile and file from filetable may be similar but not idential. compare only the numberic values
        fname_set1 = self.peel_string(fnames)
        fname_set2 = self.peel_string(self.fnames)

        if set(fname_set1) == set(fname_set2): #if list of fnames from theta.txt have containst same fnames as from the tiffs..
            sorted_index = [fname_set2.index(i) for i in fname_set1]
            self.fnames = np.asarray(self.fnames)[sorted_index]

        if set(fname_set1) != set(fname_set2) and fnames != []: #fnames from tiffs and thetas.txt do not match
            print("fnames from tiffs and thetas.txt do not match. Assuming fnames from table correspond to the same order as the loaded angles.")
            sorted_index = np.argsort(thetas)
            thetas = np.asarray(thetas)[sorted_index]
            self.fnames = np.asarray(self.fnames)[sorted_index]

        self.thetas = [float(list(thetas)[i]) for i in range(len(thetas))]
        self.fnames = [str(list(self.fnames)[i]) for i in range(len(self.fnames))]
        sorted_index = np.argsort(self.thetas)
        self.thetas = np.asarray(self.thetas)[sorted_index]
        self.fnames = np.asarray(self.fnames)[sorted_index]

        for i in range(len(self.thetas)):
            self.fileTableWidget.fileTableModel.arrayData[i].theta = self.thetas[i]
            self.fileTableWidget.fileTableModel.arrayData[i].filename = self.fnames[i]

        #check elementtable if there any elements, if not then manually set a single element
        if len(self.fileTableWidget.elementTableModel.arrayData) == 0 or len(self.fileTableWidget.elementTableModel.arrayData) == 1:
            self.elements = ["Channel_1"]

        self.thetas = np.asarray(self.thetas)

        if data_loaded:
            self.data = self.data[:, sorted_index]
            self.updateImages(True)
            self.tab_widget.setTabEnabled(1, True)
            self.tab_widget.setTabEnabled(2, True)
            self.tab_widget.setTabEnabled(3, True)
            if self.tcp_installed: self.tab_widget.setTabEnabled(4, True)
            self.afterConversionMenu.setDisabled(False)
            self.editMenu.setDisabled(False)
            self.toolsMenu.setDisabled(False)
            self.viewMenu.setDisabled(False)
            print("Angle information loaded.")

        return

    def match_filenames_to_thetas(self):
        """Open popup table: filenames, extracted scan#, and columns from a loaded txt file."""
        try:
            filenames = [
                self.fileTableWidget.fileTableModel.arrayData[i].filename
                for i in range(len(self.fileTableWidget.fileTableModel.arrayData))
            ]
        except (AttributeError, TypeError):
            filenames = getattr(self, 'fnames', None) or []
        if not filenames:
            QMessageBox.information(
                self, "No filenames",
                "Load a directory or files first so that filenames are available."
            )
            return
        dlg = MatchFilenamesThetasDialog(filenames, self)
        dlg.exec_()

    def peel_string(self, string_list):
        peel_back = True
        peel_front = True
        while peel_back:
            if len(set([string_list[x][0] for x in range(len(string_list))])) == 1:
                string_list = [string_list[x][1:] for x in range(len(string_list))]
            else:
                peel_back = False
        while peel_front:
            if len(set([string_list[x][-1] for x in range(len(string_list))])) == 1:
                string_list = [string_list[x][:-1] for x in range(len(string_list))]
            else:
                peel_front = False
        return string_list


    # def onTabChanged(self, index):
    #     if self.prevTab == self.TAB_FILE:
    #         self.loadImages()
    #     elif self.prevTab == self.TAB_IMAGE_PROC:
    #         pass
    #     elif self.prevTab == self.TAB_SINOGRAM:
    #         pass
    #     elif self.prevTab == self.TAB_RECONSTRUCTION:
    #         pass
    #     elif self.prevTab == self.TAB_LAMINOGRAPHY:
    #         pass
    #     self.prevTab = index

    # def saveScatterPlot(self):
    #     try:
    #         self.writer.save_scatter_plot(self.figure)
    #     except AttributeError:
    #         print("Run correlation analysis first")
    #     return

    def save_proj_stack(self):
        self.writer.save_proj_stack(self.data, self.elements)

    def save_proj_indiv(self):
        self.writer.save_proj_indiv(self.data, self.elements)

    def save_proj_npy(self):
        self.writer.save_proj_npy(self.data, self.elements)

    def save_recon_stack(self):
        self.writer.save_recon_stack(self.recon_dict)

    def save_recon_indiv(self):
        element = self.imageProcessWidget.ViewControl.combo1.currentText()
        self.writer.save_recon_indiv(self.recon, element)

    def save_recon_npy(self):
        self.writer.save_recon_npy(self.recon_dict)

    def save_sino_stack(self):
        self.writer.save_sino_stack(self.data, self.elements)

    def save_sino_indiv(self):
        self.writer.save_sino_indiv(self.data, self.elements)

    def save_sino_npy(self):
        self.writer.save_sino_npy(self.data, self.elements)

    def save_align_npy(self):
        self.writer.save_align_npy(self.fnames, self.x_shifts, self.y_shifts)

    def save_align_txt(self):
        self.writer.save_align_txt(self.fnames, self.x_shifts, self.y_shifts)

    def save_thetas_npy(self):
        self.writer.save_thetas_npy(self.fnames, self.thetas)

    def save_thetas_txt(self):
        self.writer.save_thetas_txt(self.fnames, self.thetas)

    def save_hdf5(self):
        self.writer.save_hdf5(self.fnames, self.data, self.thetas, self.elements, self.recon_dict)

    def saveCorrAlsys(self):
        try:
            self.writer.save_correlation_analysis(self.elements, self.rMat)
        except AttributeError:
            print("Run correlation analysis first")
        return

    # def save_align_txt(self):
    #     try:
    #         self.writer.save_align_txt(self.fnames, self.x_shifts, self.y_shifts)
    #     except AttributeError:
    #         print("Alignment data does not exist.")
    #     return
    # def save_align_npy(self):
    #     try:
    #         self.writer.save_align_npy(self.fnames, self.x_shifts, self.y_shifts)
    #     except AttributeError:
    #         print("Alignment data does not exist.")
    #     return
    # def saveProjections(self):
    #     try:
    #         self.writer.save_projections(self.fnames, self.data, self.elements)
    #     except AttributeError:
    #         print("projection data do not exist")
    #     return
    #
    # def saveSinogram(self):
    #     try:
    #         self.writer.save_sinogram(self.sino)
    #     except AttributeError:
    #         print("sinogram data do not exist")
    #     return
    #
    # def saveSinogram2(self):
    #     try:
    #         self.writer.save_sinogram2(self.data, self.elements)
    #     except AttributeError:
    #         print("sinogram data do not exist")
    #     return
    #
    # def saveReconstruction(self, recon):
    #     try:
    #         self.writer.save_reconstruction(self.recon)
    #     except AttributeError:
    #         print("reconstructed data do not exist")
    #     return
    # def saveRecon2npy(self, recon):
    #     try:
    #         self.writer.save_recon_2npy(self.recon)
    #     except AttributeError:
    #         print("reconstructed data does not exist")
    #     return
    #
    # def saveReconArray2npy(self, recon):
    #     try:
    #         self.writer.save_recon_array_2npy(self.recon_array)
    #     except AttributeError:
    #         print("reconstructed data does not exist")
    #     return

    # def saveToHDF(self):
    #     try:
    #         self.writer.save_dxhdf(self.data, self.elements, self.thetas)
    #     except AttributeError:
    #         print("projection data do not exist")
    #     return

    # def saveThetas(self):
    #     try:
    #         files = [i.filename for i in self.fileTableWidget.fileTableModel.arrayData]
    #         k = np.arange(len(files))
    #         thetas = [i.theta for i in self.fileTableWidget.fileTableModel.arrayData]
    #         files_bool = [i.use for i in self.fileTableWidget.fileTableModel.arrayData]
    #         self.fnames = [files[j] for j in k if files_bool[j]==True]
    #         self.thetas = np.asarray([thetas[j] for j in k if files_bool[j]==True])
    #         self.writer.save_thetas(self.fnames, self.thetas)
    #     except AttributeError:
    #         print("filename or angle information does not exist")
    #     return
    #
    # def saveToNumpy(self):
    #     try:
    #         self.writer.save_numpy_array(self.data, self.thetas, self.elements)
    #     except AttributeError:
    #         print("data has not been imported first")
    #     return

    def loadImages(self):
        file_array = self.fileTableWidget.fileTableModel.arrayData
        self.element_array = self.fileTableWidget.elementTableModel.arrayData
        #for fidx in range(len(file_array)):

    # def reset_widgets(self):

    def updateImages(self, from_open=False):
        self.prevTab = self.tab_widget.currentIndex()
        self.data_history = []
        self.x_shifts_history = []
        self.y_shifts_history = []
        self.theta_history = []
        self.fname_history = []
        # self.centers_history = []

        if not from_open:
            self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.data, self.elements, self.thetas, self.fnames = self.fileTableWidget.onSaveDataInMemory()
            #create empty recon_dict here
            self.recon_dict = {}
            for element in self.elements:
                self.recon_dict[element] = np.zeros((self.data.shape[2],self.data.shape[3],self.data.shape[3]))
            #populate scatter plot combo box windows
            self.first_run = True

            self.app.restoreOverrideCursor()

            if len(self.data) == 0:
                return
            if len(self.elements) == 0:
                return
            if len(self.thetas) == 0:
                return
            if len(self.fnames) == 0:
                return
            self.updateScatter()

        self.centers = [100,100,self.data.shape[3]//2]
        self.x_shifts = np.zeros(self.data.shape[1], dtype="int")
        self.y_shifts = np.zeros(self.data.shape[1], dtype="int")
        self.original_data = self.data.copy()
        self.original_fnames = self.fnames.copy()
        self.original_thetas = self.thetas.copy()

        self.init_widgets()
        self.imageProcessWidget.showImgProcess()
        self.imageProcessWidget.imageView.setAspectLocked(True)

        self.sinogramWidget.showSinogram()
        self.sinogramWidget.showImgProcess()
        self.sinogramWidget.showDiffProcess()
        self.sinogramWidget.showSinoCurve()
        self.reconstructionWidget.showReconstruct()
        self.laminographyWidget.showReconstruct()
        # self.reset_widgets()

        self.tab_widget.setTabEnabled(1,True)
        self.tab_widget.setTabEnabled(2,True)
        self.tab_widget.setTabEnabled(3,True)
        self.tab_widget.setTabEnabled(4, True)
        self.afterConversionMenu.setDisabled(False)
        self.editMenu.setDisabled(False)
        self.toolsMenu.setDisabled(False)
        self.viewMenu.setDisabled(False)
        self.update_history(self.data)
        self.update_alignment(self.x_shifts, self.y_shifts)
        self.refreshUI()

    def refreshUI(self):
        # try:
        #     self.tab_widget.currentChanged.disconnect()
        # except:
        #     pass

        self.tab_widget.removeTab(0)
        self.tab_widget.removeTab(1)
        self.tab_widget.removeTab(2)
        self.tab_widget.removeTab(3)
        self.tab_widget.removeTab(4)
        self.tab_widget.insertTab(0, self.fileTableWidget, "Files")
        self.tab_widget.insertTab(1, self.imageProcessWidget, "Pre Processing")
        self.tab_widget.insertTab(2, self.sinogramWidget, "Alignment")
        self.tab_widget.insertTab(3, self.reconstructionWidget, "Tomography")
        self.tab_widget.insertTab(4, self.laminographyWidget, "Laminography")
        self.tab_widget.setCurrentIndex(self.prevTab)

    def init_widgets(self):
        self.imageProcessWidget.data = self.data
        self.imageProcessWidget.elements = self.elements
        self.imageProcessWidget.thetas = self.thetas
        self.imageProcessWidget.fnames = self.fnames
        self.imageProcessWidget.x_shifts = self.x_shifts
        self.imageProcessWidget.y_shifts = self.y_shifts
        self.imageProcessWidget.centers = self.centers
        self.imageProcessWidget.ViewControl.combo1.setCurrentIndex(0)
        self.imageProcessWidget.sld.setValue(0)

        self.sinogramWidget.data = self.data 
        self.sinogramWidget.elements = self.elements 
        self.sinogramWidget.thetas = self.thetas 
        self.sinogramWidget.fnames = self.fnames 
        self.sinogramWidget.x_shifts = self.x_shifts 
        self.sinogramWidget.y_shifts = self.y_shifts 
        self.sinogramWidget.centers = self.centers 
        self.sinogramWidget.ViewControl.combo1.setCurrentIndex(0)
        self.sinogramWidget.sld.setValue(0)

        self.reconstructionWidget.data_original = self.original_data
        self.reconstructionWidget.data = self.data 
        self.reconstructionWidget.elements = self.elements 
        self.reconstructionWidget.thetas = self.thetas 
        self.reconstructionWidget.fnames = self.fnames
        self.reconstructionWidget.x_shifts = self.x_shifts
        self.reconstructionWidget.y_shifts = self.y_shifts
        self.reconstructionWidget.centers = self.centers
        self.reconstructionWidget.ViewControl.combo1.setCurrentIndex(0)

        self.laminographyWidget.data_original = self.original_data
        self.laminographyWidget.data = self.data 
        self.laminographyWidget.elements = self.elements 
        self.laminographyWidget.thetas = self.thetas 
        self.laminographyWidget.fnames = self.fnames
        self.laminographyWidget.x_shifts = self.x_shifts
        self.laminographyWidget.y_shifts = self.y_shifts
        self.laminographyWidget.centers = self.centers
        self.laminographyWidget.ViewControl.elem.setCurrentIndex(0)


        self.imageProcessWidget.sld.setValue(0)
        self.reconstructionWidget.sld.setValue(0)
        self.laminographyWidget.sld.setValue(0)
        self.imageProcessWidget.lcd.display(str(self.thetas[0]))
        self.reconstructionWidget.recon = []
        self.laminographyWidget.recon = []
        self.sinogramWidget.sld.setValue(1)

    def update_history(self, data):
        index = self.imageProcessWidget.sld.value()
        self.update_data(data)
        self.update_theta(index, self.thetas)
        self.update_filenames(self.fnames, index)
        self.update_alignment(self.x_shifts, self.y_shifts)

        self.data_history.append(data.copy())
        self.theta_history.append(self.thetas.copy())
        self.x_shifts_history.append(self.x_shifts.copy())
        self.y_shifts_history.append(self.y_shifts.copy())
        # self.centers_history.append(self.centers.copy())
        self.fname_history.append(self.fnames.copy())
        print('history save event: ', len(self.data_history))

        if len(self.data_history) > 10:
            del self.data_history[0]
            del self.theta_history[0]
            del self.x_shifts_history[0]
            del self.y_shifts_history[0]
            # del self.centers[0]
            del self.fname_history[0]
        return

    def update_recon(self, recon):
        self.recon = recon
        self.reconstructionWidget.recon = recon
        self.reconstructionWidget.update_recon_image()
        self.laminographyWidget.recon = recon
        self.laminographyWidget.update_recon_image()
        return


    def update_recon_dict(self, recon_dict):
        self.recon_dict = recon_dict
        self.reconstructionWidget.recon_dict = recon_dict
        self.reconstructionWidget.update_recon_image()
        self.laminographyWidget.recon_dict = recon_dict
        self.laminographyWidget.update_recon_image()
        return

    def update_sino(self, sino):
        self.sino = sino.copy()
        return

    def update_data(self, data):
        self.data = data 
        self.imageProcessWidget.data = self.data
        self.imageProcessWidget.imageChanged()
        self.sinogramWidget.data = self.data
        self.sinogramWidget.imageChanged()
        self.reconstructionWidget.data = self.data
        self.laminographyWidget.data = self.data
        return

    def update_theta(self, index, thetas):
        self.thetas = thetas
        self.imageProcessWidget.thetas = self.thetas
        self.sinogramWidget.thetas = self.thetas
        self.reconstructionWidget.thetas = self.thetas
        self.laminographyWidget.thetas = self.thetas
        return

    def update_alignment(self, x_shifts, y_shifts):
        self.x_shifts = x_shifts
        self.y_shifts = y_shifts
        # self.centers = centers 
        self.imageProcessWidget.x_shifts = self.x_shifts
        self.imageProcessWidget.y_shifts = self.y_shifts
        self.imageProcessWidget.actions.x_shifts = self.x_shifts
        self.imageProcessWidget.actions.y_shifts = self.y_shifts
        self.sinogramWidget.x_shifts = self.x_shifts
        self.sinogramWidget.y_shifts = self.y_shifts
        self.sinogramWidget.actions.x_shifts = self.x_shifts
        self.sinogramWidget.actions.y_shifts = self.y_shifts
        self.reconstructionWidget.x_shifts = self.x_shifts
        self.reconstructionWidget.y_shifts = self.y_shifts
        self.laminographyWidget.x_shifts = self.x_shifts
        self.laminographyWidget.y_shifts = self.y_shifts
        # self.sinogramWidget.actions.centers = self.centers
        return
        
    def update_filenames(self, fnames, index):
        self.fnames = fnames 
        self.imageProcessWidget.fnames = fnames
        self.imageProcessWidget.updateFileDisplay(fnames, index)
        return

    def update_slider_range(self, thetas):
        index = self.imageProcessWidget.sld.value()
        self.imageProcessWidget.updateSldRange(index, thetas)
        self.sinogramWidget.updateImgSldRange(index, thetas)
        self.sinogramWidget.updateDiffSldRange(index, thetas)
        return

    def clear_all(self):
        self.data_history = []
        self.x_shifts_history = []
        self.y_shifts_history = []
        self.fname_history = []
        self.update_alignment([],[])

        self.imageProcessWidget.sld.setValue(0)
        self.imageProcessWidget.sld.setRange(0,0)
        self.imageProcessWidget.lcd.display(0)
        self.sinogramWidget.sld.setRange(0,0)
        self.sinogramWidget.sld.setRange(0,0)
        self.reconstructionWidget.sld.setValue(0)
        self.reconstructionWidget.sld.setRange(0,0)
        self.laminographyWidget.sld.setValue(0)
        self.laminographyWidget.sld.setRange(0,0)

        self.imageProcessWidget.imageView.projView.clear()
        self.sinogramWidget.sinoView.projView.clear()
        self.reconstructionWidget.ReconView.projView.clear()
        self.laminographyWidget.ReconView.projView.clear()

        self.data = None
        self.recon = None
        self.recon_dict = {}
        self.imageProcessWidget.data = None
        self.sinogramWidget.data = None
        self.sinogramWidget.sinogramData = None
        self.reconstructionWidget.data = None
        self.reconstructionWidget.recon = None
        self.laminographyWidget.data = None
        self.laminographyWidget.recon = None
        self.refreshUI()
        return

    def undo(self):
        try:
            if len(self.data_history) <=1:
                print("maximum history stplt.imshow(self.data_history[1][0])ate reached, cannot undo further")
            else:
                del self.data_history[-1]
                del self.x_shifts_history[-1]
                del self.y_shifts_history[-1]
                del self.theta_history[-1]
                del self.fname_history[-1]
                # del self.centers_history[-1]
                self.data = self.data_history[-1].copy()
                self.x_shifts = self.x_shifts_history[-1].copy()
                self.y_shifts = self.y_shifts_history[-1].copy()
                self.thetas = self.theta_history[-1].copy()
                self.fnames = self.fname_history[-1].copy()
                # self.centers = self.centers_history[-1]

                self.update_alignment(self.x_shifts, self.y_shifts)
                self.update_slider_range(self.thetas)
                # TODO: reset tomography/lami/recon data
                self.sinogramWidget.ySizeChanged(self.data.shape[2])
                index = self.imageProcessWidget.sld.value()
                self.update_theta(index, self.thetas)
                self.update_filenames(self.fnames, index)
                self.update_data(self.data)

        except AttributeError:
            print("Load dataset first")
            return
        print(len(self.data_history))
        return

    def restore(self):
        try:
            num_projections = self.original_data.shape[1]
            self.data = self.original_data.copy()
            self.thetas = self.original_thetas.copy()
            self.fnames = self.original_fnames.copy()
            self.x_shifts = np.zeros(self.data.shape[1], dtype="int")
            self.y_shifts = np.zeros(self.data.shape[1], dtype="int")
            self.centers = [100,100,self.data.shape[3]//2]
            # self.ySizeChangedSig.emit(self.data.shape[2])
            # self.xSizeChangedSig.emit(self.data.shape[3])
            # # self.dataChangedSig.emit(data)
            # TODO: reset tomography/lami/recon data
            self.sinogramWidget.x_padding_hist = [0]
            self.sinogramWidget.y_padding_hist = [0]
            self.update_history(self.data)
            self.sinogramWidget.ySizeChanged(self.data.shape[2])
            self.reconstructionWidget.reset_recons()
            self.laminographyWidget.reset_recons()
            index = self.imageProcessWidget.sld.value()
            self.update_theta(index, self.thetas)
            self.update_filenames(self.fnames, index)
            self.update_data(self.data)
            self.update_slider_range(self.thetas)

        except AttributeError:
            print("Load dataset first")
            return

    def projWindow(self):
        self.projection_window.show()
        self.updateMiniProj()

    def scatterPlot(self):
        self.scatter_window.show()
        self.updateScatter()

    def scatterPlotRecon(self):
        self.scatter_window_recon.show()
        self.updateScatterRecon()

    def pixDistanceWindow(self):
        self.pixel_distance_window.show()
        self.updateDistanceHisto()

        # self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        #create window, create two drop-down menus (for element selection)
        #load data[element1], load data2[element2], normalize the two,
        #assign elem1 to x axis, assign elem2 to y axis
        #divide data[elem2] by data[elem1], plot this.

    def onionWindow(self):
        self.onion_window.show()
        self.updateOnion()

    def xy_power(self):

        # dc=pylab.average(ti)
        # dc_img=ti-dc #substract dc value
        # x_axis=f1['MAPS']['x_axis'] #Get the array of x_axis
        # n_x=len(x_axis) #get the number of steps in x direction
        # x_delta_um=abs(x_axis[n_x-1]-x_axis[0])/n_x  #calculate the stepsize in x direction

        # f1=h5py.File(input_path)#read the HDF5 file
        # a=f1['MAPS']['mca_arr']
        # ti=a[channel,:,:] # select the channel associated with Ti fluorescence peak from XRF dectector 0
        # #for i in range(19):
        #    # ti+=a[channel+i,:,:]

        # fft_img=fft2(dc_img)
        # Fc_img=fftshift(fft_img)
        # abs_img=abs(Fc_img)
        # log_img=pylab.log(1+abs_img)
        # power_img=(abs_img)**2# power imaging

        # npiy, npix=power_img.shape
        # x1=np.arange(npix/2)
        # y1=np.arange(npiy/2)
        # f_x1=x1*(1./(n_x*x_delta_um))
        # f_y1=y1*(1./(n_x*x_delta_um))

        # x_power=np.array([0 for i in range(npix/2)], dtype=np.float32)
        # for i in range(npix/2):
        #     x_power[i]=power_img[npiy/2][npix/2+i-1]
        # y_power=np.array([0 for i in range(npiy/2)], dtype=np.float32)
        # for j in range(npiy/2):
        #     y_power[j]=power_img[npiy/2+j-1][npix/2]
            
        # #display fluorescence imaging
        # plt.subplot(221)
        # plt.imshow(ti)
        # plt.title('Fluorescence Imaging')

        # #display 2D-FFT
        # plt.subplot(223)
        # plt.imshow(log_img)
        # plt.title('2D-FFT')

        # #x direction power spectrum
        # plt.subplot(222)
        # plt.loglog(f_x1, x_power)
        # plt.xlim((1,10))
        # plt.title('X direction power spectrum')
        # plt.xlabel('Spatial frequency f(um^-1)')
        # plt.ylabel('Intensity(arb.units)')

        # #y direction power spectrum
        # plt.subplot(224)
        # plt.loglog(f_y1, y_power)
        # plt.xlim((1,10))
        # plt.title('Y direction power spectrum')
        # plt.xlabel('Spatial frequency f(um^-1)')
        # plt.ylabel('Intensity(arb.units)')

        # output_path= '/pf/esafs/edu/northwestern/k-brister/93940/data_analysed/bnp_power_spec_output/'+ os.path.splitext(filename)[0]+'_xy_directions.png'
        # print("output_path= "+output_path) 
        # plt.savefig(output_path)
        # plt.show()


        pass



    # def corrElem(self):
    #     self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    #
    #     data = self.data
    #     #normalize data
    #     # nom_data = self.normData(data)
    #     # errMat = np.zeros((data.shape[0],data.shape[0]))
    #     # simMat = np.zeros((data.shape[0],data.shape[0]))
    #     self.rMat = np.zeros((data.shape[0],data.shape[0]))
    #     for i in range(data.shape[0]):      #elemA
    #         for j in range(data.shape[0]):  #elemB
    #             elemA = data[i]
    #             elemB = data[j]
    #             # corr = np.mean(signal.correlate(elemA, elemB, method='direct', mode='same') / (data.shape[1]*data.shape[2]*data.shape[3]))
    #             rval = self.compare(elemA, elemB)
    #             # errMat[i,j]= err
    #             # simMat[i,j]= sim
    #             self.rMat[i,j]= rval
    #
    #     sns.set(style="white")
    #
    #     # Generate a mask for the upper triangle
    #     mask = np.zeros_like(self.rMat, dtype=np.bool)
    #     mask[np.triu_indices_from(mask,1)] = True
    #
    #     # Set up the matplotlib figure
    #     self.analysis_figure, ax = plt.subplots(figsize=(11, 9))
    #
    #     # Generate a custom diverging colormap
    #     cmap = sns.diverging_palette(220, 10, as_cmap=True)
    #
    #     # Draw the heatmap with the mask and correct aspect ratio
    #     d = pd.DataFrame(data=self.rMat, columns=self.elements, index=self.elements)
    #     sns.heatmap(d, mask=mask, annot=True, cmap=cmap, vmax=self.rMat.max(), center=0,
    #                 square=True, linewidths=.5, cbar_kws={"shrink": .5})
    #     self.analysis_figure.show()
    #
    #     self.app.restoreOverrideCursor()
        return self.rMat

    # def normData(self,data):
    #     norm = np.zeros_like(data)
    #     for i in range(data.shape[0]):
    #         data_mean = np.mean(data[i])
    #         data_std = np.std(data[i])
    #         data_med = np.median(data[i])
    #         data_max = np.max(data[i])
    #         new_max = data_mean+10*data_std
    #         current_elem = data[i]
    #         current_elem[data[i] >= new_max] = new_max
    #         data[i] = current_elem

    #     return data 

    def compare(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;

        d = len(imageA)
        # d2 = len(imageB)
        # errMat = np.zeros(imageA.shape[0])
        # simMat = np.zeros(imageA.shape[0])
        rMat = np.zeros(imageA.shape[0])


        if d > 2:
            for i in range(imageA.shape[0]):
                # err = np.sum((imageA[i].astype("float") - imageB[i].astype("float")) ** 2)
                # err /= float(imageA[i].shape[0] * imageA[i].shape[1])
                # sim = measure.compare_ssim(imageA[i], imageB[i])
                r, p = stats.pearsonr(imageA[i].flatten(), imageB[i].flatten())

                # errMat[i] = err
                # simMat[i] = sim
                rMat[i] = r
                # errVal = np.sum(errMat)/len(errMat)
                # simVal = np.sum(simMat)/len(simMat)
            rVal = np.sum(rMat)/len(rMat)
        else:
            # err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            # err /= float(imageA.shape[0] * imageA.shape[1])
            # sim  = measure.compare_ssim(imageA, imageB)
            # errVal = err
            # simVal = sim
            r, p = stats.pearsonr(imageA.flatten(), imageB.flatten())

            rVal = r

        # return the MSE, the lower the error, the more "similar"
        return rVal

    def keyMapSettings(self):
        self.keymap_options.show()
        return

    def configSettings(self):
        self.config_options.show()
        return

    def _save_session_on_close(self):
        """Save directory, filenames, thetas, tag paths, and selected elements/scalers for next launch."""
        try:
            self.params.input_path = self.fileTableWidget.dirLineEdit.text()
            self.params.file_extension = self.fileTableWidget.extLineEdit.text().strip()
            self.params.data_tag = self.fileTableWidget.data_menu.property("full_path") or self.fileTableWidget.data_menu.currentText() or getattr(self.params, 'data_tag', '')
            self.params.element_tag = self.fileTableWidget.element_menu.property("full_path") or self.fileTableWidget.element_menu.currentText() or getattr(self.params, 'element_tag', '')
            self.params.scaler_tag = self.fileTableWidget.scaler_menu.property("full_path") or self.fileTableWidget.scaler_menu.currentText() or getattr(self.params, 'scaler_tag', '')
            self.params.theta_tag = self.fileTableWidget.theta_menu.property("full_path") or self.fileTableWidget.theta_menu.currentText() or getattr(self.params, 'theta_tag', '')
            arr = self.fileTableWidget.fileTableModel.arrayData
            if arr:
                self.params.last_filenames = str([getattr(x, 'filename', '') for x in arr])
                self.params.last_thetas = str([float(getattr(x, 'theta', 0)) for x in arr])
            else:
                self.params.last_filenames = '[]'
                self.params.last_thetas = '[]'
            elem_arr = self.fileTableWidget.elementTableModel.arrayData
            scaler_arr = self.fileTableWidget.scalerTableModel.arrayData
            if elem_arr:
                self.params.selected_elements = str(list(np.where([getattr(x, 'use', True) for x in elem_arr])[0]))
            if scaler_arr:
                self.params.selected_scalers = str(list(np.where([getattr(x, 'use', True) for x in scaler_arr])[0]))
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self._save_session_on_close()
            sections = config.TOMO_PARAMS + ('gui', )
            home = expanduser("~")
            config.write('{}/xrftomo.conf'.format(home), args=self.params, sections=sections)
            self.sinogramWidget.ViewControl.iterative.close()
            self.sinogramWidget.ViewControl.pirt.close()
            self.sinogramWidget.ViewControl.move2edge.close()
            self.sinogramWidget.ViewControl.sino_manip.close()
            self.imageProcessWidget.ViewControl.reshape_options.close()
            self.config_options.close()
            self.keymap_options.close()
            matplotlib.pyplot.close()

        except IOError as e:
            self.gui_warn(str(e))
            self.on_save_as()

def main(params):
    # BREAKPOINT: Debugger should stop here when GUI starts
    print("DEBUG: GUI main function called")
    # import pdb; pdb.set_trace()  # Uncomment to force breakpoint
    
    app = QApplication(sys.argv)
    mainWindow = xrftomoGui(app, params)
    mainWindow.show()
    sys.exit(app.exec_())
