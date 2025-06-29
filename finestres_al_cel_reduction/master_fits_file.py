"""Fits file class for handling FITS files in the application."""
from astropy.io import fits
import numpy as np
import copy

from finestres_al_cel_reduction.fits_file import FitsFile

VALID_AVERAGE_METHODS = ["mean", "median"]

class MasterFitsFile(FitsFile):
    """Class representing a master FITS file, combined from individual exposures."""

    def __init__(self, filename, individual_exposures, average="mean"):
        """Initialize the FitsFile instance.
        
        Arguments
        ---------
        filename: str
        The path to the FITS file.

        individual_exposures: list of finestres_al_cel_reduction.fits_file.FitsFile
        List of individual exposure FITS files used to create this master.

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

        self.filename = filename
        self.title = self.filename.split("/")[-1]  # Get the file name from the path
        
        self.data = None
        self.header = None
        self.type = None
        self.combine_individual_exposures(individual_exposures)

    def combine_individual_exposures(self, individual_exposures):
        """Combine individual exposure FITS files into a master.
        
        Arguments
        ---------
        individual_exposures: list of finestres_al_cel_reduction.fits_file.FitsFile
        List of individual exposure FITS files to combine.

        Raises
        -------
        ValueError: 
        - If no individual exposures are provided
        - if they are not valid FITS files
        - if they are not of the same type
        - if they do not have the same exposure time
        - if they do not have the same filter (flats only)
        - if the average method is not valid
        """
        if len(individual_exposures) == 0:
            raise ValueError("No individual exposures provided.")
        if not all(isinstance(item, FitsFile) for item in individual_exposures):    
            raise ValueError("All items in individual_exposures must be instances of FitsFile.")
        if not (all(item.type == "IMAGE" for item in individual_exposures)):
            raise ValueError("All individual exposures must be of type 'IMAGE'.")
            
        self.type = "IMAGE"
        self.image_type = individual_exposures[0].image_type
        self.exposure_time = individual_exposures[0].exposure_time
        if self.image_type != "Dark Frame":
            self.filter = individual_exposures[0].filter if hasattr(individual_exposures[0], "filter") else None
        for item in individual_exposures:
            if item.image_type != self.image_type:
                raise ValueError("All individual exposures must be of the same type.")
            if item.exposure_time != individual_exposures[0].exposure_time:
                raise ValueError("All individual exposures must have the same exposure time.")
            if self.image_type != "Dark Frame":
                if item.filter != individual_exposures[0].filter:
                    raise ValueError("All individual exposures must have the same filter.")
        # update image type to recognize it as a master file
        self.image_type = f"Master {self.image_type}"

        # Combine the data and headers of the individual exposures
        if self.average == "mean":
            self.data = np.nanmean([item.data for item in individual_exposures], axis=0)
        elif self.average == "median":
            self.data = np.nanmedian([item.data for item in individual_exposures], axis=0)
        # this should never happen as we check the average method at initialization
        else: # pragma: no cover
            raise ValueError(f"Invalid average method '{self.average}'. Valid methods are: {VALID_AVERAGE_METHODS}.")
        
        self.header = copy.deepcopy(individual_exposures[0].header)
        self.header["IMAGETYP"] = self.image_type
        self.header["HISTORY"] = f"Combined {len(individual_exposures)} exposures using {self.average} method."
        self.type = "IMAGE"

    def normalize(self):
        """Normalize the master FITS file data."""
        if self.image_type == "Master Flat":
            self.data = self.data / np.max(self.data.flatten())
            
        else:
            raise ValueError(f"Normalization is only applicable to master flat frames, not {self.image_type}.")