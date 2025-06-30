""" Dialog to set calibration settings"""
import os
import numpy as np

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QGridLayout, 
    QLabel, QListWidgetItem, QTableWidget, QTableWidgetItem
)

from finestres_al_cel_reduction.color_fits_file import ColorFitsFile

class ColorStackDialog(QDialog):
    """ Class to define the settings for the stacking process"""
    def __init__(self, files):
        """Initialize instance
        
        Arguments
        ---------
        files: list of finestres_al_cel_reduction.fits_file.FitsFile
        List of available FITS files to stack. Only selected files will be stacked
        """
        super().__init__()

        self.color_stack = None

        self.setWindowTitle("Color Stack Files")

        # Initialize variables
        self.files = files
        file_titles = [file.title for file in self.files]
        self.stack = None

        # Image selecton buttons
        # red
        self.red_file_label = QLabel("Red Channe:")
        self.red_file = QComboBox()
        self.red_file.addItem("Select a file")
        self.red_file.addItems(file_titles)
        # green
        self.green_file_label = QLabel("Green Channel:")
        self.green_file = QComboBox()
        self.green_file.addItem("Select a file")
        self.green_file.addItems(file_titles)
        # blue
        self.blue_file_label = QLabel("Blue Channel:")
        self.blue_file = QComboBox()
        self.blue_file.addItem("Select a file")
        self.blue_file.addItems(file_titles)

        # Color weights matrix box
        self.weights_matrix = QTableWidget(3, 3)
        self.weights_matrix.setHorizontalHeaderLabels(["Red", "Green", "Blue"])
        self.weights_matrix.setVerticalHeaderLabels(["Red", "Green", "Blue"])
        for row in range(3):
            for column in range(3):
                self.weights_matrix.setItem(row, column, QTableWidgetItem("1.0" if row == column else "0.0"))

        # OK/Cancel
        QButtons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QButtons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.red_file_label, 0, 0)
        layout.addWidget(self.red_file, 0, 1)
        layout.addWidget(self.green_file_label, 1, 0)
        layout.addWidget(self.green_file, 1, 1)
        layout.addWidget(self.blue_file_label, 2, 0)
        layout.addWidget(self.blue_file, 2, 1)
        layout.addWidget(self.weights_matrix, 3, 0, 1, 3)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self):
        """Run stacking before accepting the dialog."""
        # Get selected file titles
        red_title = self.red_file.currentText()
        green_title = self.green_file.currentText()
        blue_title = self.blue_file.currentText()

        # Find the corresponding FitsFile objects
        red_file = next((f for f in self.files if f.title == red_title), None)
        green_file = next((f for f in self.files if f.title == green_title), None)
        blue_file = next((f for f in self.files if f.title == blue_title), None)

        # get the color weights
        weights = np.array([[
            float(self.weights_matrix.item(row, column).text()) 
            for column in range(3)] 
            for row in range(3)])

        filename = os.path.join(
            os.path.dirname(red_file.filename), 
            f"color_stack.fits"
        )
        self.color_stack = ColorFitsFile(
            filename, red_file, green_file, blue_file, weights, average="median")

        # Now accept/close the dialog
        super().accept()

    