"""Fits file class for handling FITS files in the application."""
from astropy.io import fits
import numpy as np
import copy

from finestres_al_cel_reduction.fits_file import FitsFile

VALID_AVERAGE_METHODS = ["mean", "median"]

class ColorFitsFile(FitsFile):
    """Class representing a color FITS file, combined from individual exposures."""

    def __init__(self, filename, red_file, green_file, blue_file, weights, average="mean"):
        """Initialize the FitsFile instance.
        
        Arguments
        ---------
        filename: str
        The path to the FITS file.

        red_file: FitsFile
        The red channel FITS file.

        green_file: FitsFile
        The green channel FITS file.

        blue_file: FitsFile
        The blue channel FITS file.

        weights: list of float
        The weights for each channel in the color combination. Should be a list of three floats.

        average: str - Default "mean"
        The method used to combine the individual exposures. Can be "mean" or "median".

        Raises
        -------
        ValueError:
        - If the average method is not valid
        """
        if average not in VALID_AVERAGE_METHODS:
            raise ValueError(
                f"Invalid average method '{average}'. "
                f"Valid methods are: {VALID_AVERAGE_METHODS}.")
        self.average = average

        if not isinstance(red_file, FitsFile):
            raise ValueError("red_file must be an instance of FitsFile.")
        self.red_file = red_file

        if not isinstance(green_file, FitsFile):
            raise ValueError("green_file must be an instance of FitsFile.")
        self.green_file = green_file

        if not isinstance(blue_file, FitsFile):
            raise ValueError("blue_file must be an instance of FitsFile.")
        self.blue_file = blue_file
    
        self.weights = weights

        self.filename = filename
        self.title = self.filename.split("/")[-1]  # Get the file name from the path
        
        self.data = None
        self.header = None
        self.type = None
        self.combine_individual_exposures()

    def combine_individual_exposures(self):
        """Combine individual exposure FITS files into a master.
        List of individual exposure FITS files to combine.

        Raises
        -------
        ValueError: 
        - if the average method is not valid
        """    
        self.type = "COLOR IMAGE"
        self.image_type = "Color Stack"
        self.exposure_time = np.nan
        
        # Get data arrays
        red = self.red_file.data
        green = self.green_file.data
        blue = self.blue_file.data

        # Check that all arrays have the same shape
        if red.shape != green.shape or red.shape != blue.shape:
            raise ValueError("Red, green, and blue images must have the same shape.")

        # Apply weights (self.weights is a 3x3 matrix)
        # weights: rows = output channels (R,G,B), cols = input channels (R,G,B)
        # For standard RGB, this is the identity matrix.
        weighted = []
        for index in range(3):
            # self.weights[index] is the weights for output channel index
            channel = (
                self.weights[index][0] * red +
                self.weights[index][1] * green +
                self.weights[index][2] * blue
            )
            weighted.append(channel)
        # Stack into a 3D array (height, width, 3)
        self.data = np.stack(weighted, axis=-1)

