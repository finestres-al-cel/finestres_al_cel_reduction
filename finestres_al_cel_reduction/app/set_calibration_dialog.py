""" Dialog to set calibration settings"""
import os

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QGridLayout, 
    QLabel, QListWidget, QListWidgetItem, QPushButton,
)


from finestres_al_cel_reduction.app.error_dialog import ErrorDialog
from finestres_al_cel_reduction.master_fits_file import MasterFitsFile
from finestres_al_cel_reduction.fits_file import FitsFile
from finestres_al_cel_reduction.app.warning_dialog import WarningDialog

class SetCalibrationDialog(QDialog):
    """ Class to define the settings for the stellar finder

    Methods
    -------
    (see QDialog)
    __init__

    Arguments
    ---------
    (see QDialog)

    buttonBox: QDialogButtonBox
    Accept/cancel button

    fwhmQuestion: QLineEdit
    Field to modify the FWHM for the Gaussian Kernel used for the detection

    minsepFwhmQuestion: QLineEdit
    Field to modify the minimum separation between detected objects (in units
    of the FWHM)

    thresholdQuestion: QLineEdit
    Field to modify the detection threshold
    """
    def __init__(self):
        """Initialize instance"""
        super().__init__()

        # Initialize variables
        self.calibration_folder = None
        self.darks = {}
        self.flats = {}
        self.fitsListWidget = QListWidget()
        self.mastersListWidget = QListWidget()
        self.master_darks = {}
        self.master_flats = {} 
        
        self.setWindowTitle("Set Calibration")

        # OK and Cancel buttons
        QButtons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QButtons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Calibration folder
        self.selectCalibrationFolderButton = QPushButton("Select Calibration Folder")
        self.selectCalibrationFolderButton.clicked.connect(self.select_calibration_folder)
        self.selectedCalibrationFolderLabel = QLabel(
            self.calibration_folder if self.calibration_folder is not None else " "*200)

        # Add QListWidget for FITS files
        self.fitsListWidget.setMinimumHeight(self.fitsListWidget.sizeHintForRow(0) * 5 + 2 * self.fitsListWidget.frameWidth())
        
        # Generate masters button
        self.generateMastersButton = QPushButton("Generate Masters (replace existing)")
        self.generateMastersButton.clicked.connect(self.generate_masters)

        # Add QListWidget for FITS files
        self.mastersListWidget.setMinimumHeight(self.mastersListWidget.sizeHintForRow(0) * 5 + 2 * self.mastersListWidget.frameWidth())

        # Set layout
        layout = QGridLayout()
        layout.addWidget(self.selectCalibrationFolderButton, 0, 0)
        layout.addWidget(self.selectedCalibrationFolderLabel, 0, 1)
        layout.addWidget(self.fitsListWidget, 1, 0, 1, 2)
        layout.addWidget(self.generateMastersButton, 3, 0)
        layout.addWidget(self.mastersListWidget, 4, 0, 1, 2)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def add_items_to_list_widget(self):
        """Add items to a QListWidget with headers"""
        self.fitsListWidget.clear()

        # Add grouped darks to the list qwidget
        header = QListWidgetItem("Darks")
        font = QFont()
        font.setBold(True)
        header.setFont(font)
        self.fitsListWidget.addItem(header)
        for exp_time in sorted(self.darks):
            subheader = QListWidgetItem(f"  Exposure: {exp_time}s")
            self.fitsListWidget.addItem(subheader)
            for file in self.darks[exp_time]:
                self.fitsListWidget.addItem(f"    {file.title}")

        # Add grouped flats to the list qwidget
        header = QListWidgetItem("Flats")
        font = QFont()
        font.setBold(True)
        header.setFont(font)
        self.fitsListWidget.addItem(header)
        for filter_name in sorted(self.flats):
            subheader = QListWidgetItem(f"  Filter: {filter_name}")
            self.fitsListWidget.addItem(subheader)
            for file in self.flats[filter_name]:
                self.fitsListWidget.addItem(f"    {file.title}")
        
    def add_items_to_masters_list_widget(self):
        """Add items to the masters QListWidget with headers"""
        self.mastersListWidget.clear()

        # Add grouped items to the masters' list widget
        header = QListWidgetItem("Darks")
        font = QFont()
        font.setBold(True)
        header.setFont(font)
        self.mastersListWidget.addItem(header)
        for exp_time in sorted(self.master_darks):
            subheader = QListWidgetItem(f"  Exposure: {exp_time}s")
            self.mastersListWidget.addItem(subheader)
            for file in self.master_darks[exp_time]:
                self.mastersListWidget.addItem(f"    {file.title}")

        # Add grouped flats to the list qwidget
        header = QListWidgetItem("Flats")
        font = QFont()
        font.setBold(True)
        header.setFont(font)
        self.mastersListWidget.addItem(header)
        for filter_name, files in sorted(self.master_flats.items()):
            subheader = QListWidgetItem(f"  Filter: {filter_name}")
            self.mastersListWidget.addItem(subheader)
            for file in files:
                self.mastersListWidget.addItem(f"    {file.title}")

    def generate_masters(self):
        """Generate master darks and flats from the selected folder"""
        # first generate the master darks
        if not self.calibration_folder:
            errorDialog = ErrorDialog("Calibration folder not selected.")
            errorDialog.exec()
            return
        
        # Generate master darks
        if len(self.darks) == 0:
            errorDialog = ErrorDialog("No dark frames found in the selected folder.")
            errorDialog.exec()
            return
        
        # Generate master darks
        self.master_darks = {}
        for exposure_time, files in self.darks.items():
            if len(files) == 0:
                continue
            filename = os.path.join(self.calibration_folder, f"master_dark_{exposure_time}s.fits")
            try:
                # Create master flat file
                master_dark = MasterFitsFile(filename, files, average="median")
                master_dark.save()
                if exposure_time not in self.master_darks:
                    self.master_darks[exposure_time] = [master_dark]
                else:
                    self.master_darks[exposure_time].append(master_dark)
            except Exception as e:
                errorDialog = ErrorDialog(f"Error generating master dark for {exposure_time}s: {str(e)}")
                errorDialog.exec()
                return
            
        # check that list of mater darks are one per exposure time
        for exposure_time, files in self.master_darks.items():
            if len(files) != 1:
                errorDialog = ErrorDialog(f"Error: More than one master dark for {exposure_time}s exposure time.")
                errorDialog.exec()
                return
            
        # Generate master flats
        self.master_flats = {}
        for filter_name, files in self.flats.items():
            if len(files) == 0:
                continue

            filename = os.path.join(self.calibration_folder, f"master_flat_{filter_name}.fits")
            try:        
                for file in files:
                    # Calibrate flat files
                    dark_list = self.master_darks.get(file.exposure_time, None)
                    if dark_list is None:
                        dark_list = None
                    else:
                        dark = dark_list[0]
                        
                    file.calibrate(
                        dark=dark,
                        flat=None,  # No flat calibration for flats
                    )

                # Create master flat file
                master_flat = MasterFitsFile(filename, files, average="median")
                master_flat.normalize()  # Normalize the master flat
                master_flat.save()
                if filter_name not in self.master_flats:
                    self.master_flats[filter_name] = [master_flat]
                else:
                    self.master_flats[filter_name].append(master_flat)
            except Exception as e:
                errorDialog = ErrorDialog(f"Error generating master flat for filter {filter_name}: {str(e)}")
                errorDialog.exec()
                raise e
                return
        
        # check that list of mater flats are one per exposure time and filter
        for filter_name, files in self.master_flats.items():
            if len(files) != 1:
                errorDialog = ErrorDialog(
                    f"Error: More than one master flat for filter {filter_name}.")
                errorDialog.exec()
                return
    
        self.add_items_to_masters_list_widget()

    def select_calibration_folder(self):
        """Select calibration folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Calibration Folder")
        if folder:
            self.calibration_folder = folder
            # update answer label
            self.selectedCalibrationFolderLabel.setText(
                self.calibration_folder if self.calibration_folder is not None else "None")

            # List FITS files
            self.darks = {}
            self.flats = {}
            self.master_darks = {}
            self.master_flats = {}
            for fname in os.listdir(folder):
                if fname.lower().endswith((".fits", ".fit", ".fits.gz")):
                    # Open file to get header information
                    file = FitsFile(os.path.join(folder, fname))
                    if file.type != "IMAGE":
                        continue # Skip non-image files
                    if file.exposure_time is None:
                        warningDialog = WarningDialog(
                        f"Warning: No exposure time in {file.filename}. Skipping.")
                        warningDialog.exec()
                        continue
                    # Dark frames
                    if file.image_type == "Dark Frame":
                        exposure_time = file.exposure_time
                        if exposure_time not in self.darks:
                            self.darks[exposure_time] = [file]
                        else:
                            self.darks[exposure_time].append(file)
                    # Flat frames
                    elif file.image_type == "Flat":
                        filter_name = file.filter
                        if filter_name is None:
                            warningDialog = WarningDialog(
                            f"Warning: No filter in {file.filename}. Skipping.")
                            warningDialog.exec()
                            continue
                        if filter_name not in self.darks:
                            self.flats[filter_name] = [file]
                        else:
                            self.flats[filter_name].append(file)
                    # Master dark frames
                    elif file.image_type == "Master Dark Frame":
                        exposure_time = file.exposure_time
                        if exposure_time not in self.master_darks:
                            self.master_darks[exposure_time] = [file]
                        else:
                            self.master_darks[exposure_time].append(file)
                    # Master flat frames
                    elif file.image_type == "Master Flat":
                        filter_name = file.filter
                        if filter_name not in self.master_flats:
                            self.master_flats[filter_name] = []
                        self.master_flats[filter_name].append(file)
                    # Light frames
                    elif file.image_type == "Light Frame":
                        continue
                    # Unknown image type
                    else:
                        warningDialog = WarningDialog(
                            f"Warning: Unknown image type '{file.image_type}' in {file.filename}. Skipping.")
                        warningDialog.exec()
                        continue

            self.add_items_to_list_widget()
            self.add_items_to_masters_list_widget()

