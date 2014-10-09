#!/usr/bin/env python

import os,sys
import time
import numpy
import Xcorrect as X
import pyfits

DECam_filters = ('g_DECam','r_DECam','i_DECam','z_DECam','y_DECam')

class coaddCatalog:

    def __init__(self,CatName,OutName):

        self.CatName = CatName
        self.OutName = OutName
        

    def readCat(self):

        """ Read in the SExtractor Coadd Catalog"""

        print "# Reading: %s" % self.CatName
        hdulist = pyfits.open(self.CatName)
        
        # Trick to avoid reading the LDAC table --  use [-1]
        # the SEx Catalog table is the last entry in the hdulist 
        tbdata = hdulist[-1].data
        cols   = hdulist[-1].columns
        
        # Store the Relevant positional information
        self.NUMBER      = tbdata['NUMBER']
        try:
            self.ra      = tbdata['ALPHAWIN_J2000']
            self.dec     = tbdata['DELTAWIN_J2000']
            print "# Using ALPHAWIN_2000, DELTAWIN_J2000 for RA,DEC"
        except:
            try:
                self.ra   = tbdata['ALPHA_J2000']
                self.dec  = tbdata['DELTA_J2000']
                print "# Using ALPHA_2000, DELTA_J2000 for RA,DEC"
            except:
                raise sys.exit("ERROR: Cannot find appropiate RA,DEC set for file:%s" % self.CatName)

        
    def getXCorr(self):

        """
        Get the dust correction for current object in self.objectsRA, and seld.objectsDEC
        Return ndarray Xc[filter], Xc_err[filter]
        """
        (self.Xc,self.Xc_err,self.eBV,self.l,self.b) = X.Xcorrection(self.ra,self.dec,DECam_filters)

    def writeTable(self):

        # Create the columns for pyfits
        ids = pyfits.Column(name='NUMBER',        format='IJ',  disp='I10', array=self.NUMBER)
        Xg =  pyfits.Column(name='XCORR_SFD98_G', format='1E', disp = 'F8.4', unit = 'mag', array=self.Xc['g_DECam'])
        Xr =  pyfits.Column(name='XCORR_SFD98_R', format='1E', disp = 'F8.4', unit = 'mag', array=self.Xc['r_DECam'])
        Xi =  pyfits.Column(name='XCORR_SFD98_I', format='1E', disp = 'F8.4', unit = 'mag', array=self.Xc['i_DECam'])
        Xz =  pyfits.Column(name='XCORR_SFD98_Z', format='1E', disp = 'F8.4', unit = 'mag', array=self.Xc['z_DECam'])
        Xy =  pyfits.Column(name='XCORR_SFD98_Y', format='1E', disp = 'F8.4', unit = 'mag', array=self.Xc['y_DECam'])
        eBV = pyfits.Column(name='eBV',           format='1E', disp = 'F8.4', unit = 'mag', array=self.eBV)
        L   = pyfits.Column(name='L',             format='1D', disp = 'F11.7',unit = 'deg', array=self.l)
        B   = pyfits.Column(name='B',             format='1D', disp = 'F11.7',unit = 'deg', array=self.b)

        tbhdu = pyfits.new_table([ids, Xg, Xr, Xi, Xz, Xy, eBV, L, B])
        print "# Writing %s" % self.OutName
        tbhdu.writeto(self.OutName,clobber=True)

# Format time
def elapsed_time(t1,verb=False):
    import time
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verb:
        print >>sys.stderr,"Elapsed time: %s" % stime
    return stime

def cmdline():

    import argparse
    parser = argparse.ArgumentParser(description="Computes SFD98 Galactic extinction from a SExtractor file")

    # The optional arguments
    parser.add_argument("CatName", action="store", default=None,
                        help="Input Catalog Name")

    parser.add_argument("OutName", action="store", default=None,
                        help="Output Dust Correction")

    args = parser.parse_args()

    return args

######################
# Call the procedure
######################
if __name__ == '__main__':

    t0 = time.time()
    # The start time
    tstart   = time.time()

    # Get the command line options
    args = cmdline()

    # Make the object
    p = coaddCatalog(args.CatName,args.OutName)
    p.readCat()
    p.getXCorr()
    p.writeTable()

    print "# Total time: %s" % elapsed_time(t0)

    
