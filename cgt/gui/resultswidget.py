## -*- coding: utf-8 -*-
"""
Created on Thursday 05 Aug 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
import PyQt5.Qt as qt

import pyqtgraph as pg

from cgt.model.velocitiescalculator import VelocitiesCalculator
from cgt.util.utils import (ItemDataTypes,
                            MarkerTypes,
                            get_region,
                            hash_graphics_line,
                            hash_graphics_point,
                            get_frame,
                            get_region)

from cgt.gui.Ui_resultswidget import Ui_ResultsWidget

class ResultsWidget(qw.QWidget, Ui_ResultsWidget):
    """
    class for display of results
    """

    ## signal that a frame is required
    request_frame = qc.pyqtSignal(int)

    ## signal that the queue should be cleared
    clear_queue = qc.pyqtSignal()

    def __init__(self, parent, data_source):
        """
        setup object and window
            Args:
                parent (QWidget): parent widget
                data_source (CrystalGrowthTrackerMain): holder of the results
        """
        super().__init__(parent)
        self.setupUi(self)

        ## holder of the results
        self._data_source = data_source

        ## the graph of the results
        self._graph = None

        ## pointer for the video source
        self._video_source = None

        ## the region in use
        self._current_region = None

        # the start lines
        self._lines = None

        # the start points
        self._points = None

        # ensure view has a scene graph
        self._regionView.setScene(qw.QGraphicsScene())

        self._graph = pg.PlotWidget(title="<b>Marker Displacments</b>")
        self._graph.setBackground('w')
        self._graphScrollArea.setWidget(self._graph)

        self.setup_display()

    def setEnabled(self, enabled):
        """
        enable/disable widget on enable the source
        is connected on disable play is paused
        """
        if enabled:
            super().setEnabled(True)
            self.setup_display()
            self._video_source.simple_connect_viewer(self)
            self.show_results(self._regionBox.currentIndex())
        elif not enabled:
            for item in self._regionView.scene().items():
                self._regionView.scene().removeItem(item)
            super().setEnabled(False)

    def setup_display(self):
        """
        initalize the display
        """
        results = self._data_source.get_results()
        if results is None:
            return

        old_index = self._regionBox.currentIndex()
        self._regionBox.clear()

        for i in range(len(results.get_regions())):
            self._regionBox.addItem(str(i))

        if len(results.get_regions()) > 0:
            if old_index < 0:
                old_index = 0
            self.show_results(old_index)

    @qc.pyqtSlot(int)
    def show_results(self, index):
        """
        show the table and graph
            Args:
                index (int): the index of the region
        """
        self.fill_table(index)
        self.draw_graph_of_region(index)
        self.display_region(index)

    def display_region(self, index):
        """
        display the selected region
            Args:
                index (int): array index of the region
        """
        results = self._data_source.get_results()
        self._current_region = results.get_regions()[index]
        line_markers = results.get_lines_for_region(index)
        point_markers = results.get_points_for_region(index)

        self._lines = []
        self._points = []
        if line_markers is not None:
            for marker in line_markers:
                self._lines.append(marker[0])

        if point_markers is not None:
            for marker in point_markers:
                self._points.append(marker[0])

        self.post_request_frame(0)

    @qc.pyqtSlot(qg.QPixmap, int)
    def display_image(self, pixmap, frame_number):
        """
        callback function to display an image from a source
            Args:
                pixmap (QPixmap) the pixmap to be displayed
                frame_number (int) the frame number of the video
        """
        scene = self._regionView.scene()
        scene.clear()

        rect = self._current_region.rect().toRect()
        pixmap = pixmap.copy(rect)
        scene.addPixmap(pixmap)
        pen = self._data_source.get_pens().get_display_pen()
        for line in self._lines:
            scene.addItem(clone_line(line, pen))
        for point in self._points:
            scene.addItem(clone_point(point, pen))

    @qc.pyqtSlot(float)
    def zoom_changed(self, value):
        """
        callback for change of zoom
            Args:
                value (float): the new zoom
        """
        self._regionView.setTransform(qg.QTransform())
        self._regionView.scale(value, value)

    def fill_table(self, index):
        """
        fill the tree widget
        """
        self._resultsTable.clear()

        headers = ["Marker", "Start Frame", "End Frame", "Displacement"]
        self._resultsTable.setColumnCount(4)
        self._resultsTable.setHorizontalHeaderLabels(headers)

        self._resultsTable.setRowCount(10)

        calc = self.calculate_speeds(index)
        lines = calc.get_line_displacements()
        points = calc.get_point_displacements()

        row = 0
        for j, line in enumerate(lines):
            for displacement in line:
                self._resultsTable.setItem(row, 0, qw.QTableWidgetItem(self.tr(f"Line {j}")))
                self._resultsTable.setItem(row, 1, qw.QTableWidgetItem(str(displacement.get_start())))
                self._resultsTable.setItem(row, 2, qw.QTableWidgetItem(str(displacement.get_end())))
                self._resultsTable.setItem(row, 3, qw.QTableWidgetItem( f"{displacement.get_length():.2f}"))
                row += 1

        for j, point in enumerate(points):
            for displacement in point:
                self._resultsTable.setItem(row, 0, qw.QTableWidgetItem(self.tr(f"Point {j}")))
                self._resultsTable.setItem(row, 1, qw.QTableWidgetItem(str(displacement.get_start())))
                self._resultsTable.setItem(row, 2, qw.QTableWidgetItem(str(displacement.get_end())))
                self._resultsTable.setItem(row, 3, qw.QTableWidgetItem( f"{displacement.get_length():.2f}"))
                row += 1

    def draw_graph_of_region(self, index):
        """
        callback for change of region
            Args:
                index (int): the array index of the region
        """
        self._graph.clear()

        label_style = {'font-weight': 'bold'}
        calc = self.calculate_speeds(index)
        lines = calc.get_line_displacements()
        points = calc.get_point_displacements()

        tick_font = qg.QFont()
        tick_font.setBold(True)

        self._graph.getAxis('left').setLabel("Displacement (micron)", **label_style)
        self._graph.getAxis('left').setTickFont(tick_font)
        self._graph.getAxis('bottom').setLabel("Frame (number)", **label_style)
        self._graph.getAxis('bottom').setTickFont(tick_font)

        pen = 0
        pens = len(lines) + len(points)
        for i, marker in enumerate(lines):
            displacements = [0.0]
            frames = [0]
            for dis in marker:
                new_dis = displacements[-1] + dis.get_length()
                displacements.append(new_dis)
                frames.append(dis.get_end())

            self._graph.plot(frames, displacements, pen=(pen, pens), name=f"Line {i}")
            pen += 1

        for i, marker in enumerate(points):
            displacements = [0.0]
            frames = [0]
            for dis in marker:
                new_dis = displacements[-1] + dis.get_length()
                displacements.append(new_dis)
                frames.append(dis.get_end())

            self._graph.plot(frames, displacements, pen=(pen, pens), name=f"Point {i}")
            pen += 1

        self._graph.addLegend()

    def calculate_speeds(self, index):
        """
        carry out speeds calculation
            Args:
                index (int) the region
        """
        results = self._data_source.get_results()
        lines = []
        for marker in results.get_lines():
            if get_region(marker[0]) == index:
                lines.append(marker)

        points = []
        for marker in results.get_points():
            if get_region(marker[0]) == index:
                points.append(marker)

        fps = self._data_source.get_project()["frame_rate"]
        scale = self._data_source.get_project()["resolution"]
        calculator = VelocitiesCalculator(lines, points, fps, scale)
        calculator.process_latest_data()
        return calculator

    def set_video_source(self, video_source):
        """
        set the video_source object, set length for controls
            Args:
                video_source (VideoSource): the source object
        """
        self._video_source = video_source

    def post_request_frame(self, frame_number):
        """
        a specific frame should be displayed
        """
        self.request_frame.emit(frame_number)

def clone_line(marker, pen):
    """
    clone a line or cross
        Args:
            line (QGraphicsLineItem) the item to clone
        Returns:
            if item is Line or path a clone else None
    """
    line = marker.line()
    graph_line = qw.QGraphicsLineItem(line)
    graph_line.setPos(marker.pos())
    graph_line.setPen(pen)

    graph_line.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.LINE)
    graph_line.setData(ItemDataTypes.PARENT_HASH, hash_graphics_line(marker))
    graph_line.setData(ItemDataTypes.FRAME_NUMBER, get_frame(marker))
    graph_line.setData(ItemDataTypes.REGION_INDEX, get_region(marker))
    return graph_line

def clone_point(marker, pen):

    path = marker.path()
    centre = marker.data(ItemDataTypes.CROSS_CENTRE)
    graph_path = qw.QGraphicsPathItem(path)
    graph_path.setPos(marker.pos())
    graph_path.setPen(pen)

    graph_path.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.POINT)
    graph_path.setData(ItemDataTypes.PARENT_HASH, hash_graphics_point(marker))
    graph_path.setData(ItemDataTypes.FRAME_NUMBER, get_frame(marker))
    graph_path.setData(ItemDataTypes.REGION_INDEX, get_region(marker))
    graph_path.setData(ItemDataTypes.CROSS_CENTRE, centre)
    return graph_path
