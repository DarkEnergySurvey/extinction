#!/usr/bin/env python

import os,sys
import coreutils.desdbi
import time
import numpy
import Xcorrect as X

DECam_filters = ('g_DECam','r_DECam','i_DECam','z_DECam','y_DECam')

class sva1_coadd:

    def __init__(self,
                 db_section = "db-dessci"):
        
        #self.coadd_version = coadd_version

        # Setup desar queries here for later
        try:
            desdmfile = os.environ["des_services"]
        except KeyError:
            desdmfile = None
        self.dbh = coreutils.desdbi.DesDbi(desdmfile,db_section)

        self.tilenames = None

        # Get all of the tilenames
        #self.query_sva1_tilenames()

    def query_sva1_tilenames(self):

        """ DESAR query to get all tilenames for SVA1 """

        # Run only once
        if self.tilenames:
            return
        
        cur = self.dbh.cursor()

        query = "select unique tilename, run from  SVA1_COADD_FILE"
        print "# Will execute the SQL query:\n********%s\n********" % query
        cur.execute(query)
        
        self.run_names = {}
        self.tilenames = []
        for item in cur:
            tilename = item[0]
            self.run_names[tilename] = item[1]
            self.tilenames.append(tilename)
        return


    def getRADEC_sva1_coadd_tilename(self,tilename):
        
        print "# Building the list of files to be used from DESAR/SQL queries"
        cur = self.dbh.cursor()
        self.tilename = tilename

        queryitems = ["coadd_objects_id","ra", "dec","tilename"]
        querylist = ",".join(queryitems)
        query = """
        select  %s from sva1_coadd_objects where tilename='%s'""" % (querylist,tilename)

        print "# Will execute the SQL query:\n********%s\n********" % query
        t0 = time.time()
        # Do the query
        cur.arraysize = 1000
        cur.execute(query) 
        # Get them all at once
        list_of_tuples = cur.fetchall()
        # Use zip and "*" to unpack tuples and make list and nd-arrays
        ids, ra, dec, tilename =  zip(*list_of_tuples)
        self.objectsID  = numpy.array(list(ids))
        self.objectsRA  = numpy.array(list(ra))
        self.objectsDEC = numpy.array(list(dec))
        print "# SQL query done in:  %s" % elapsed_time(t0)


    def getXCORR_sva1_coadd_allobjects(self,Nget=50000):
        
        cur = self.dbh.cursor()
        
        # Figure out how many objects in total
        query = """select count(*) from  SVA1_COADD_OBJECTS"""
        cur.execute(query) 
        Ntotal = cur.fetchone()[0]

        # Make the main query
        t0 = time.time()
        queryitems = ["coadd_objects_id","ra", "dec","tilename"]
        querylist = ",".join(queryitems)
        query = """select %s from sva1_coadd_objects """ % querylist
        print "# Will execute the SQL query:\n********\n%s\n********" % query
        cur.execute(query) 
        print "# Query time: %s" % elapsed_time(t0)

        list_of_tuples = ('empty') 
        counter = 0
        # Do Nget at a time, loop over
        while list_of_tuples is not None: # and counter < 3:

            t1 = time.time()
            list_of_tuples = cur.fetchmany(Nget)
            # Use zip and "*" to unpack tuples and make list and nd-arrays
            ids, ra, dec, tilename =  zip(*list_of_tuples)
            self.objectsID  = numpy.array(list(ids))
            self.objectsRA  = numpy.array(list(ra))
            self.objectsDEC = numpy.array(list(dec))
            self.TILENAME   = list(tilename)
            print "# SQL fetchmany done in:  %s" % elapsed_time(t0)

            # Compute the Correction
            self.getXCorr()
            # Insert into the table
            self.InsertXCorr()
            counter = counter + 1
            
            perc = float(Nget*counter)/float(Ntotal)
            print "# Processed %s of %s so far --- %.2f%% done" % (Nget*counter, Ntotal, 100*perc)
            print "# Fetch+computing time: %s" % elapsed_time(t1)

        print "# Total loop time: %s" % elapsed_time(t0)
        
    def getXCorr(self):

        """
        Get the dust correction for current object in self.objectsRA, and seld.objectsDEC
        Return ndarray Xc[filter], Xc_err[filter]
        """
        (self.Xc,self.Xc_err,self.eBV,self.l,self.b) = X.Xcorrection_SFD98(self.objectsRA,self.objectsDEC,DECam_filters)

    def InsertXCorr(self,table='felipe.sva1_coadd_objects_xcorr',tilename=None):

        t0 = time.time()
        dbh = self.dbh 
        columns = ('COADD_OBJECTS_ID',
                   'XCORR_SFD98_G',
                   'XCORR_SFD98_R',
                   'XCORR_SFD98_I',
                   'XCORR_SFD98_Z',
                   'XCORR_SFD98_Y',
                   'eBV',
                   'L',
                   'B',
                   'TILENAME')

        # Force a tilename for all entries
        NID  = len(self.objectsID)
        if tilename:
            self.TILENAME = [self.tilename]*NID 

        rows = zip( self.objectsID.tolist(),
                    self.Xc['g_DECam'],
                    self.Xc['r_DECam'],
                    self.Xc['i_DECam'],
                    self.Xc['z_DECam'],
                    self.Xc['y_DECam'],
                    self.eBV,
                    self.l,
                    self.b,
                    self.TILENAME) 

        print "# Will insert %s rows to: %s" % (NID,table)
        print "# Will insert columns to: %s" % table
        for c in columns:
            print "# \t %s " % c

        dbh.insert_many(table, columns, rows) 
        dbh.commit()
        print "# Insert Done, time: %s" % elapsed_time(t0)

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
    parser = argparse.ArgumentParser(description="Computes SFD98 Galactic extinction for SVA1_COADD_OBJECTS all at once")

    # The positional arguments
    #parser.add_argument("fileName", help="Fits file to process")
    #parser.add_argument("outdir",   help="Path to output files [will preserve same name]")

    # The optional arguments
    parser.add_argument("--TileName", action="store", default=None,
                        help="TileName to compute")
    
    parser.add_argument("--allTiles", action="store_true", default=False,
                        help="Compute Extiction correction for all tilename at once [default=False]")

    args = parser.parse_args()

    if args.TileName:
        args.allTiles = False

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

    # initialize the class and collect files
    p = sva1_coadd()

    # Do only one tile
    if args.TileName:
        p.getRADEC_sva1_coadd_tilename(args.TileName)
        p.getXCorr()
        p.InsertXCorr(tilename=args.TileName)
        print "# Total time: %s" % elapsed_time(t0)
        sys.exit()

    # Do them all
    else:
        p.getXCORR_sva1_coadd_allobjects()
        print "# Total time: %s" % elapsed_time(t0)


    
