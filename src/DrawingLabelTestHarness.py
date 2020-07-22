# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 21:36:13 2020

@author: J.H.Pickering@leeds.ac.uk
"""
import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from skimage import data
from PIL import Image

import image_artifacts as ia

from DrawingLabel import DrawingLabel

from Ui_DrawingLabelTestHarness import Ui_DrawingLabelTestHarness

class DrawingLabelTestHarness(qw.QDialog, Ui_DrawingLabelTestHarness):
    
    def __init__(self, parent=None):
        super(DrawingLabelTestHarness, self).__init__()
        self._parent = parent
        self.NAME = self.tr("DrawingLabelTestHarness")
        self.setupUi(self)
        self._drawing = DrawingLabel(self._scrollArea)
        
        im = Image.fromarray(data.clock())
        im = im.convert("RGBA")
        ims = im.convert("RGBA").tobytes("raw", "RGBA")
        qim = qg.QImage(ims, im.size[0], im.size[1], qg.QImage.Format_ARGB32)
        
        self._drawing.setBackgroudPixmap(qg.QPixmap.fromImage(qim))
        
        self._scrollArea.setWidget(self._drawing)
        
        self._store = ia.ArtifactStore("test")
        
    @qc.pyqtSlot()
    def state_toggle(self):
        if self._drawButton.isChecked():
            self._drawing.setDrawing()
        else:
            self._drawing.setAdjusting()
            
    @qc.pyqtSlot()
    def labels_toggled(self):
        if self._labelsBox.isChecked():
            self._drawing.showLabels(True)
        else:
            self._drawing.showLabels(False)
            
    @qc.pyqtSlot()
    def createCopyToggled(self):
        if self._createButton.isChecked():
            self._drawing.setCreating()
            self.setDrawAdjustEnabled(True)
        else:
            self._drawing.setCopying()
            self._adjustButton.setChecked(True)
            self.setDrawAdjustEnabled(False)
            
    def setDrawAdjustEnabled(self, state):
        self._drawButton.setEnabled(state)
        self._adjustButton.setEnabled(state)
        
    @qc.pyqtSlot()
    def calculate(self):
        print("calculate")
        tmp = self._drawing.size
        if not tmp[0] > 0 and tmp[1] > 0:
            print("you must have lines and new lines")
            return
            
        if self._drawing.linesBase is None:
            print("lines none")
            
        if self._drawing.linesNew is None:
            print("new lines none")
            
        self._store[0] = self._drawing.linesBase
        self._store[1] = self._drawing.linesNew
        
        diffs = self._store.differences(0, 1)
        
        self._tableWidget.setColumnCount(2)
        self._tableWidget.setRowCount(len(diffs))
        
        self._tableWidget.setHorizontalHeaderLabels(["Line", "Displacement (pixels)"])
        
        i = 0
        for d in diffs:
            print(d)
            self._tableWidget.setItem(i,0, qw.QTableWidgetItem(str(d.lines_label)))
            self._tableWidget.setItem(i,1, qw.QTableWidgetItem(str(d.average)))
            i+=1
        
    @qc.pyqtSlot()      
    def saveImage(self):
        file = qc.QFile("my_image.png")
        self._drawing.save(file)

    @qc.pyqtSlot()
    def zoom_changed(self):
        self._drawing.setZoom(self._zoomSpinBox.value())
        
def run():
    """
    use a local function to make an isolated the QApplication object
    """
    def inner_run():
        app = qw.QApplication(sys.argv)

        window = DrawingLabelTestHarness(app)
        window.show()
        app.exec_()
        
    inner_run()

if __name__ == "__main__":
    run()