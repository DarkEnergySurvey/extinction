
"""
Set of python routines to perform galactic extintion correction

Felipe Menanteau <felipe@illinois.edu>
NCSA, Oct 2013

"""

import os
import sys
from math import log10
import tempfile
import time
import logging
import numpy
from despyastro import tableio
from despyastro import coords
from despymisc.miscutils import elapsed_time
from extinction.extinction_utils import create_logger

# Create a logger for all functions
LOGGER = create_logger(level=logging.NOTSET, name='SFD98')

if not os.getenv('EXTINCTION_DIR'):
    vals = __file__.split('/')
    EXTINCTION_DIR = os.path.join("/".join(vals[:-3]), "etc")
    LOGGER.debug("Setting up EXTINCTION_DIR path: %s", EXTINCTION_DIR)
else:
    EXTINCTION_DIR = os.environ['EXTINCTION_DIR']

# Set up path for SEDs and FILTERs
FILTER_PATH = os.path.join(EXTINCTION_DIR, "etc", "FILTER")
SED_PATH = os.path.join(EXTINCTION_DIR, "etc", "SED")

# Set up $DUST_DIR location
if not os.getenv('DUST_DIR'):
    os.environ['DUST_DIR'] = os.path.join(EXTINCTION_DIR)
    LOGGER.debug("Setting up $DUST_DIR to: %s", os.environ['DUST_DIR'])

# Read in the FILTER response
def get_filter(filter, verb=False):

    filter_file = os.path.join(FILTER_PATH, "%s.res" % filter)
    if verb:
        print("# Reading filter: %s "% filter_file)
    x_res, y_res = tableio.get_data(filter_file, cols=(0, 1))
    return x_res, y_res

# Read the SED and FILTER and return in the SED wavelenhgth grid over
# the relevant range
def get_sednfilter(sed, filter, verb=False):

    from scipy import interpolate

    filter_file = os.path.join(FILTER_PATH, "%s.res" % filter)
    sed_file = os.path.join(SED_PATH, "%s.sed" % sed)
    if verb:
        LOGGER.info("Reading filter: %s ", filter_file)
        LOGGER.info("Reading filter: %s ", sed_file)

    x_res, y_res = tableio.get_data(filter_file, cols=(0, 1))
    x_sed, y_sed = tableio.get_data(sed_file, cols=(0, 1))
    #nres = len(x_res)
    nsed = len(x_sed)

    # Define the limits of interest in wavelenght to interpolate
    i1 = numpy.searchsorted(x_sed, x_res[0]) # - 1
    i1 = numpy.maximum(i1, 0)      # avoids going below
    i2 = numpy.searchsorted(x_sed, x_res[-1]) #+ 1
    i2 = numpy.minimum(i2, nsed - 1) # avoids going beyound

    # Linear interpolation with scipy
    f = interpolate.interp1d(x_res, y_res)

    # wave, sed, response
    return x_sed[i1:i2], y_sed[i1:i2], f(x_sed[i1:i2])

def compute_AEBV(filter='r_SDSS', sed='flat', Rv=3.1):

    """
    Return A(lambda)/E(B-V) for a given filter response and SED. Any
    SED can be used or a flat SED which is basically no SED convolved.
    Returns A(lambda)/A(V) and A(lambda)/E(B-V)
    """

    Vfilter = 'V_Bessell'
    Bfilter = 'B_Bessell'
    AV = 0.1

    # Get A(filter)
    if sed == 'flat':
        (xl, yf) = get_filter(filter)
        ysed = xl * 0.0 + 0.1
    else:
        (xl, ysed, yf) = get_sednfilter(sed, filter)

    Ax = AAV_ccm(xl, Rv=Rv)
    mx_0 = -2.5 * log10(flux(xl, ysed, yf)) # Normal
    mx_1 = -2.5 * log10(flux(xl, ysed * 10**(-0.4 * Ax * AV), yf)) # Redder
    A_AV = (mx_1 - mx_0) / AV # this is A(Lambda)/A(V)

    # Get A(V)
    if sed == 'flat':
        (xl, yf) = get_filter(Vfilter)
        ysed = xl * 0.0 + 0.1
    else:
        (xl, ysed, yf) = get_sednfilter(sed, Vfilter)
    ysed = numpy.array(ysed) * 0.0 + 1.0
    Ax = AAV_ccm(xl, Rv=Rv)
    mV_0 = -2.5 * log10(flux(xl, ysed, yf)) # Normal
    mV_1 = -2.5 * log10(flux(xl, ysed * 10**(-0.4 * Ax * AV), yf)) # Redder

    # Get A(B)
    if sed == 'flat':
        (xl, yf) = get_filter(Bfilter)
        ysed = xl * 0.0 + 0.1
    else:
        (xl, ysed, yf) = get_sednfilter(sed, Bfilter)
    ysed = numpy.array(ysed) * 0.0 + 1.0
    Ax = AAV_ccm(xl, Rv=Rv)
    mB_0 = -2.5 * log10(flux(xl, ysed, yf)) # Normal
    mB_1 = -2.5 * log10(flux(xl, ysed * 10**(-0.4 * Ax * AV), yf)) # Redder

    # Compute A/E(B-V)
    A_EBV = (mx_1 - mx_0) / ((mB_1 - mV_1) - (mB_0 - mV_0))

    # Returns:
    #          A(Lambda)/A(V), A(Lambda)/E(B-V), A(V)/E(B-V)
    return A_AV, A_EBV, A_EBV / A_AV

# Compute A(lambda)/A(V) using the prescription from Cardelli, Clayton
# & Mathis (1998) updated in the optical-NIR using O'Donnell (1994).
def AAV_ccm(wavelength, Rv=3.1):

    land = numpy.logical_and

    # Convert to inverse microns
    x = 10000.0 / wavelength
    a = x * 0.0
    b = x * 0.0

    # Compute a(x) and b(x) for all cases
    # Case 1: x < 0.3
    ix = numpy.where(x < 0.3)
    Nsel = len(ix[0])
    if Nsel > 0:
        sys.exit("Wavelength out of range of extinction function")

    # Case 2: Infrared 0.3< x<1.1
    ix = numpy.where(land(x > 0.3, x <= 1.1))
    Nsel = len(ix[0])
    if Nsel > 0:
        y = x[ix]
        a[ix] = 0.574 * y**1.61
        b[ix] = -0.527 * y**1.61

    # Case 3; Optical/NIR  1.1 < x <= 3.3
    ix = numpy.where(land(x > 1.1, x <= 3.3))
    Nsel = len(ix[0])
    if Nsel > 0:
        y = x[ix] - 1.82
        # Carelli fit
        a[ix] = 1.0 + 0.17699 * y - 0.50447 * y**2 - 0.02427 * y**3 + 0.72085 * y**4 + 0.01979 * y**5 - 0.77530 * y**6 + 0.32999 * y**7
        b[ix] = 1.41338 * y + 2.28305 * y**2 + 1.07233 * y**3 - 5.38434 * y**4 - 0.62251 * y**5 + 5.30260 * y**6 - 2.09002 * y**7
        # O'Donnell fit
        #a[ix] = 1.0 + 0.104*y - 0.609*y**2 + 0.701*y**3 + 1.137*y**4 - 1.718*y**5 - 0.827*y**6 + 1.647*y**7 - 0.505*y**8
        #b[ix] = 1.952*y + 2.908*y**2 - 3.989*y**3 - 7.985*y**4 + 11.102*y**5 + 5.491*y**6 - 10.805*y**7 + 3.347*y**8

    # Case 4: Mid-UV  3.3 < x <= 5.9
    ix = numpy.where(land(x > 3.3, x <= 5.9))
    Nsel = len(ix[0])
    if Nsel > 0:
        y = (x[ix] - 4.67) ** 2
        a[ix] = 1.752 - 0.316 * x[ix] - 0.104 / (y + 0.341)
        b[ix] = -3.090 + 1.825 * x[ix] + 1.206 / (y + 0.263)

    # Case 4: 5.9 < x < 8.0
    ix = numpy.where(land(x > 5.9, x <= 8.0))
    Nsel = len(ix[0])
    if Nsel > 0:
        y = (x[ix] - 4.67) ** 2
        a[ix] = 1.752 - 0.316 * x[ix] - 0.104/(y + 0.341)
        b[ix] = -3.090 + 1.825 * x[ix] + 1.206/(y + 0.263)
        y = x[ix] - 5.9
        a[ix] = a[ix] - 0.04473 * y**2 - 0.009779 * y**3
        b[ix] = b[ix] + 0.21300 * y**2 + 0.120700 * y**3

    # Case 5: 8 < x < 11 ; Far-UV
    ix = numpy.where(land(x > 8.0, x <= 11.0))
    Nsel = len(ix[0])
    if Nsel > 0:
        y = x[ix] - 8.0
        a[ix] = -1.072 - 0.628 * y + 0.137 * y**2 - 0.070 * y**3
        b[ix] = 13.670 + 4.257 * y - 0.420 * y**2 + 0.374 * y**3

    # Compute A(lambda)/A(V)
    AAV = a + b / Rv
    return AAV


def flux(xsr, ys, yr):
    """ Flux of spectrum ys observed through response yr,
        both defined on xsr
	Both f_nu and f_lambda have to be defined over lambda
    """
    norm = numpy.trapz(yr, xsr)
    f_l = numpy.trapz(ys * yr, xsr) / norm
    return f_l

def get_EBV_SFD98(ra, dec, tmp_path=None, units='degrees'):
    """
    function recieves a coordinate pair, RA and DEC
    from the caller, converts to galactic coords and runs the
    dust_getval code, installed in the path. Returns an extinction
    correction in magnitudes and an error object (a list of
    strings) of possible reported problems with the region of the
    sky.
    """
    if units == 'hours':
        ra = ra / 15.0

    # Make sure that we have the 'dust_getval' in the path
    if not inpath('dust_getval', verb=True):
        sys.exit("Exiting -- dust_getval not found")

    # Set up location of temporary paths
    if not tmp_path:
        tf = tempfile.NamedTemporaryFile()
        coords_lb = "%s_coords_galac.dat" % tf.name
        eBVdata = "%s_eBV.dat" % tf.name
    else:
        name = next(tempfile._get_candidate_names())
        coords_lb = os.path.join(tmp_path, "%s_coords_galac.dat" % name)
        eBVdata = os.path.join(tmp_path, "%s_eBV.dat" % name)

    LOGGER.info("Will write temporary file: %s", coords_lb)
    LOGGER.info("Will write temporary file: %s", eBVdata)

    # Check if they are floats and make then ndarrays
    if isinstance(ra, float) or isinstance(dec, float):
        ra = numpy.asarray(ra)
        dec = numpy.asarray(dec)

    if len(ra) != len(dec):
        LOGGER.info("ERROR: RA,DEC must have same dimensions")
        exit(1)

    # Convert RA and  to l,b using Eric Sheldon's coords.py
    # Write out a coords.dat file
    (l, b) = coords.eq2gal(ra, dec, b1950=False, dtype='f8')
    tableio.put_data(coords_lb, (l, b), fmt='{:12.8f} '*2)

    # ok, we have l and b. now onto the extinction stuff. build the dust_val command line
    cmd = "dust_getval infile=%s outfile=%s verbose=n interp=y" % (coords_lb, eBVdata)
    os.system(cmd)
    # dust_getval returns the original coords and the extinction correction in mags
    # [' 227.543  46.191      0.03452\n']
    # Get the array of eBV values for each coordinate position
    eBV = tableio.get_data(eBVdata, cols=(2, ))
    # Remove all of the temporary files
    os.remove(coords_lb)
    os.remove(eBVdata)

    # Also return l,b
    return eBV, l, b

# Check if executable is in path of user
def inpath(program, verb=None):
    """ Checks if program is in the user's path """
    for path in os.environ['PATH'].split(':'):
        if os.path.exists(os.path.join(path, program)):
            if verb:
                LOGGER.info("program: %s found in: %s", program, os.path.join(path, program))
            return 1
    if verb:
        LOGGER.info("program: %s NOT found in user's path ", program)
    return 0


def filterFactor(filter):

    """
    This function defines a dictionary A(Lambda)/E(B-V) values for
    a flat sed for Rv=3.10
    """

    ffactors = {

        # Older values from 02/2012
        #"g_DECam": 3.704722,
        #"r_DECam": 2.610357,
        #"i_DECam": 1.947345,
        #"z_DECam": 1.496843,
        #"y_DECam": 1.311188,

        # values from 03/2013
        "u_DECam": 4.708272,
        "g_DECam": 3.682995,
        "r_DECam": 2.604808,
        "i_DECam": 1.940133,
        "z_DECam": 1.450496,
        "y_DECam": 1.277421,
        "Y_DECam": 1.277421,

        # Values for VISTA filters (RAG added 09/2022)
        "VY_VISTA": 1.214631,
        "J_VISTA":  0.875079,
        "H_VISTA":  0.565934,
        "Ks_VISTA": 0.366106,

        "g_MOSAICII": 3.88489537829,
        "r_MOSAICII": 2.78438802442,
        "i_MOSAICII": 2.06519949822,
        "z_MOSAICII": 1.39714057191,
    }

    return ffactors[filter]


def Xcorrection_SFD98(ra, dec, filters, tmp_path=None, units='degrees'):

    """
    Gets e(B-V) for every source in the detection catalog for
    numpy arrays of ra and dec in degress and a set of filter/filters
    """

    t0 = time.time()
    LOGGER.info("Computing e(B-V) using SFD98 for %s (ra,dec) positions", len(ra))
    (eBV, l, b) = get_EBV_SFD98(ra, dec, tmp_path=tmp_path, units=units)
    LOGGER.info("Done in:  %s", elapsed_time(t0))

    # Check if list of filters
    #if type(filters) is types.ListType or type(filters) is types.TupleType:

    # Size of correction and error in magnitude
    XCorr = {}
    XCorrErr = {}

    for filter in filters:
        XCorr[filter] = filterFactor(filter) * eBV
        XCorrErr[filter] = XCorr[filter] * 0.16
        # spit out some info
        LOGGER.info("Dust Correction %s, mean, min, max:  %.4f %.4f, %.4f mags", filter,
                    XCorr[filter].mean(),
                    XCorr[filter].min(),
                    XCorr[filter].max())
    return XCorr, XCorrErr, eBV, l, b
