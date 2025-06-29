""" Dialog to set calibration settings"""
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, 
    QLabel, QListWidget, QListWidgetItem, QPushButton,
)

from finestres_al_cel_reduction.master_fits_file import MasterFitsFile

class StackDialog(QDialog):
    """ Class to define the settings for the stacking process"""
    def __init__(self, files):
        """Initialize instance
        
        Arguments
        ---------
        files: list of finestres_al_cel_reduction.fits_file.FitsFile
        List of available FITS files to stack. Only selected files will be stacked
        """
        super().__init__()

        self.setWindowTitle("Stack Files")

        # Initialize variables
        self.files = files
        self.stack = {}

        # Initialize files list
        self.unselected_files = {}
        for file in self.files:
            filter_name = getattr(file, "filter", "Unknown")
            self.unselected_files.setdefault(filter_name, []).append(file)
        self.selected_files = {}

        # Widgets
        self.unselectedList = QListWidget()
        self.selectedList = QListWidget()
        self.unselectedList.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.selectedList.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        # Populate selected and unselected lists
        self.update_selected_list()
        self.update_unselected_list()
        
        # Buttons to move items
        self.addButton = QPushButton("→")
        self.removeButton = QPushButton("←")
        self.addButton.clicked.connect(self.move_to_selected)
        self.removeButton.clicked.connect(self.move_to_unselected)

        # OK/Cancel
        QButtons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QButtons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Available Images"), 0, 0)
        layout.addWidget(QLabel("Selected for Stacking"), 0, 2)
        layout.addWidget(self.unselectedList, 1, 0, 2, 1)
        layout.addWidget(self.addButton, 1, 1)
        layout.addWidget(self.removeButton, 2, 1)
        layout.addWidget(self.selectedList, 1, 2, 2, 1)
        layout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.setLayout(layout)

    def accept(self):
        """Run stacking before accepting the dialog."""
        # Gather selected files
        for filter_name, files in self.selected_files.items():
            filename = os.path.join(
                os.path.dirname(files[0].filename), 
                f"master_stack_{filter_name}.fits"
            )
            self.stack[filter_name] = MasterFitsFile(
                filename, files, average="median")

        # Now accept/close the dialog
        super().accept()

    def move_to_selected(self):
        """Move selected items from unselectedList to selectedList"""
        items_to_move = list(self.unselectedList.selectedItems())
        for item in items_to_move:
            file = item.data(Qt.ItemDataRole.UserRole)
            if file is not None:
                filter_name = getattr(file, "filter", "Unknown")
                # Add file to selected_files
                self.selected_files.setdefault(filter_name, []).append(file)
                # Remove from unselected_files
                self.unselected_files[filter_name].remove(file)
        
        remove_filters = [
            filter for filter in self.unselected_files 
            if len(self.unselected_files[filter]) == 0]
        for filter in remove_filters:
            del self.unselected_files[filter]

        self.update_selected_list()
        self.update_unselected_list()

    def move_to_unselected(self):
        """Move selected items from selectedList to unselectedList"""
        items_to_move = list(self.selectedList.selectedItems())
        for item in items_to_move:
            file = item.data(Qt.ItemDataRole.UserRole)
            if file is not None:
                filter_name = getattr(file, "filter", "Unknown")
                # Add file to unselected_files
                self.unselected_files.setdefault(filter_name, []).append(file)
                # Remove from selected_files
                self.selected_files[filter_name].remove(file)
                
        remove_filters = [
            filter for filter in self.selected_files 
            if len(self.selected_files[filter]) == 0]
        for filter in remove_filters:
            del self.selected_files[filter]

        self.update_selected_list()
        self.update_unselected_list()
        
    def update_selected_list(self):
        """Update the selected list with files grouped by filter."""
        self.selectedList.clear()
        font = QFont()
        font.setBold(True)
        for filter_name in sorted(self.selected_files):
            header = QListWidgetItem(f"Filter: {filter_name}")
            header.setFont(font)
            self.selectedList.addItem(header)
            for file in sorted(self.selected_files[filter_name]):
                item = QListWidgetItem(f"    {file.title}")
                item.setData(Qt.ItemDataRole.UserRole, file)
                self.selectedList.addItem(item)

    def update_unselected_list(self):
        """Update the unselected list with files grouped by filter."""
        self.unselectedList.clear()
        font = QFont()
        font.setBold(True)
        for filter_name in sorted(self.unselected_files):
            header = QListWidgetItem(f"Filter: {filter_name}")
            header.setFont(font)
            self.unselectedList.addItem(header)
            for file in sorted(self.unselected_files[filter_name]):
                item = QListWidgetItem(f"    {file.title}")
                item.setData(Qt.ItemDataRole.UserRole, file)
                self.unselectedList.addItem(item)

    