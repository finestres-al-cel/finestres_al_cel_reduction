"""FITS file viewer"""
import numpy as np

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg

class FitsFileView(QWidget):
    """Widget for displaying FITS file information"""

    def __init__(self, fits_file):
        """Initialize the FitsFileView

        Parameters
        ----------
        fits_file: finestres_al_cel_reduction.FitsFile
        The FITS file to display.
        """
        # initialize plotting
        super().__init__()
        self.show()

        self.fits_file = fits_file

        # Create plot widget
        self.plotWidget = pg.PlotWidget()
        self.imageItem = None
        self.colorBar = None
        self.colorBarValues = None

        # Create label for pixel value
        self.pixelValueLabel = QLabel("Pixel value: ")
        #self.pixelValueLabel.setStyleSheet("background: #222; color: #fff; padding: 2px;")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.plotWidget)
        layout.addWidget(self.pixelValueLabel)
        self.setLayout(layout)

        # plot image
        self.updatePlot()
        
        # Connect mouse move event
        self.plotWidget.scene().sigMouseMoved.connect(self.onMouseMoved)

    def onMouseMoved(self, pos):
        """Handle mouse movement over the plot
        
        Arguments
        ---------
        pos: QPointF
        The position of the mouse in the scene.
        """
        vb = self.plotWidget.getViewBox()
        if self.imageItem is None or self.fits_file.data is None:
            self.pixelValueLabel.setText("Pixel value: ")
            return
        mousePoint = vb.mapSceneToView(pos)
        x, y = int(mousePoint.x()), int(mousePoint.y())
        data = self.fits_file.data
        if (0 <= x < data.shape[1]) and (0 <= y < data.shape[0]):
            
            # If the data is a color image, compute luminance
            if data.ndim == 3 and data.shape[-1] == 3:
                # Standard luminance formula for RGB
                aux = data[y, x]
                value = 0.299 * aux[0] + 0.587 * aux[1] + 0.114 * aux[2]
            else:
                value = data[y, x]
            self.pixelValueLabel.setText(f"Pixel value at ({x}, {y}): {value:.2f}")
        else:
            self.pixelValueLabel.setText("Pixel value: ")


    def resetPlot(self):
        """Reset plot"""
        # reset labels
        self.plotWidget.setLabel(axis='left', text='')
        self.plotWidget.setLabel(axis='bottom', text='')
        # Remove existing items if they exists
        if self.colorBar is not None:
            self.plotWidget.getPlotItem().layout.removeItem(self.colorBar)
            self.colorBar = None
        if self.imageItem is not None:
            self.plotWidget.getPlotItem().removeItem(self.imageItem)
            self.imageItem = None
        # reset plot
        self.plotWidget.clear()

    def setPlot(self):
        """Load plot settings"""

        # add label
        self.plotWidget.showAxes(True)
        self.plotWidget.setLabel(axis='left', text='pix')
        self.plotWidget.setLabel(axis='bottom', text='pix')

        # Set To Larger Font
        leftAxis = self.plotWidget.getAxis('left')
        bottomAxis = self.plotWidget.getAxis('bottom')
        font = QFont("Helvetica", 18)
        leftAxis.label.setFont(font)
        bottomAxis.label.setFont(font)
        leftAxis.setTickFont(font)
        bottomAxis.setTickFont(font)

    def updatePlot(self):
        """Update plot"""
        # keep colorbar values before reset
        if self.colorBar is not None:
            self.colorBarValues = self.colorBar.values

        # reset plot
        self.resetPlot()

        # check data shape
        self.plotWidget.clear()
        data = self.fits_file.data
        if data is None:
            raise ValueError("No data in FITS file.")
        if data.ndim > 2:
            print(f"Data has shape {data.shape}, showing first slice.")
            data = data[0]
        
        # plot image
        self.imageItem = pg.ImageItem(self.fits_file.data)
        self.plotWidget.addItem(self.imageItem)

        colorMap = pg.colormap.get("CET-L2")  # choose perceptually uniform, diverging color map

        # generate an adjustabled color bar
        # if color image, compute luminance for colorbar scaling
        if data.ndim == 3 and data.shape[-1] == 3:
            # Standard luminance formula for RGB
            luminance = 0.299 * data[..., 0] + 0.587 * data[..., 1] + 0.114 * data[..., 2]
            vmin = np.nanpercentile(luminance, 5)
            vmax = np.nanpercentile(luminance, 95)
        else:
            # For grayscale images, use the data directly
            vmin = np.nanpercentile(self.fits_file.data, 3)
            vmax = np.nanpercentile(self.fits_file.data, 97)
        if vmin == vmax:
            vmax = vmin + 1  # avoid zero range

        self.colorBar = pg.ColorBarItem(
            values=(vmin, vmax),
            colorMap=colorMap)
        
        # link color bar and color map to correlogram, and show it in plotItem:
        self.colorBar.setImageItem(self.imageItem, insert_in=self.plotWidget.getPlotItem())

        # load plot settings
        self.setPlot()
