"""Fits file class for handling FITS files in the application."""
from astropy.io import fits

class FitsFile:
    """Class representing a FITS file."""

    def __init__(self, filename):
        """Initialize the FitsFile instance.
        
        Arguments
        ---------
        filename: str
        The path to the FITS file.
        """
        self.filename = filename
        self.title = self.filename.split("/")[-1]  # Get the file name from the path

        self.data = None
        self.header = None
        self.type = None
        self.load_data()

        # this variable is used to track if the FITS file has been modified 
        # since the last save operation
        self.modified = False   

    def __lt__(self, other):
        if not isinstance(other, FitsFile):
            return NotImplemented
        return self.title < other.title

    def calibrate(self, dark=None, flat=None):
        """Calibrate the FITS file with dark and flat frames.
        
        Arguments
        ---------
        dark: FitsFile - Default None
        The dark frame to use for calibration.
        
        flat: FitsFile - Default None
        The flat frame to use for calibration.
        
        Raises
        ------
        ValueError: If the FITS file is not an image or does not have data.
        """
        if self.data is None:
            raise ValueError("The FITS file does not contain any data.")
        
        if dark is not None:
            self.data -= dark.data
            self.header["HISTORY"] = f"Subtracted dark frame: {dark.title}"
            self.modified = True

        if flat is not None:
            self.data /= flat.data
            self.header["HISTORY"] = f"Divided by flat frame: {flat.title}"
            self.modified = True

    def load_data(self):
        """Load data from the FITS file."""
        with fits.open(self.filename) as hdul:
            # Check if the file is empty
            if len(hdul) == 0:
                raise ValueError(f"The FITS file '{self.filename}' is empty or not a valid FITS file.")
            # Image files
            if isinstance(hdul[0], fits.ImageHDU) or isinstance(hdul[0], fits.PrimaryHDU):
                self.data = hdul[0].data.astype(float)  # Convert data to float
                self.header = hdul[0].header
                self.type = "IMAGE"

                if "EXPTIME" in self.header:
                    self.exposure_time = self.header["EXPTIME"]
                if "FILTER" in self.header:
                    self.filter = self.header["FILTER"]
                if "IMAGETYP" in self.header:
                    self.image_type = self.header["IMAGETYP"]
                
            # TODO: check other types of HDU

    def save(self, filename=None):
        """Save the FITS file.
        
        Arguments
        ---------
        filename: str - Default None
        The path to save the FITS file. If None, it will use the original filename
        """
        if filename is None:
            filename = self.filename
        hdu = fits.PrimaryHDU(data=self.data, header=self.header)
        hdu.writeto(filename, overwrite=True)

        self.modified = False
    