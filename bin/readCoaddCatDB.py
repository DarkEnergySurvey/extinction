#!/usr/bin/env python

import os,sys
import coreutils.desdbi
import time
import numpy
import Xcorrect as X

DECam_filters = ('g_DECam','r_DECam','i_DECam','z_DECam','y_DECam')

class coadd:

    def __init__(self,coadd_version='SVA1_COADD',
                 tilename   = None,
                 db_section = "db-desoper",
                 outdir = "color_tiles"):
        
        self.tilename      = tilename
        self.coadd_version = coadd_version
        self.outdir        = outdir

        # Setup desar queries here for later
        try:
            desdmfile = os.environ["des_services"]
        except KeyError:
            desdmfile = None
        self.dbh = coreutils.desdbi.DesDbi(desdmfile,db_section)

        # Get the tilenames for the version and run names
        self.query_desar_tilenames()


    def query_desar_tilenames(self):

        """ DESAR query to get all tilenames for a given tag """
        
        cur = self.dbh.cursor()

        # Query to get them
        # SELECT distinct run from runtag where tag='SVA1_COADD';
        # Files are in
        # /archive_data/Archive/OPS/coadd/20130904000011_DES0437-4414/coadd/>

        query = "SELECT distinct tilename,run from coadd where run in (SELECT distinct run from runtag where tag='%s')" % self.coadd_version
        print "# Will execute the SQL query:\n********%s\n********" % query
        cur.execute(query)
        
        self.run_names = {}
        self.tilenames = []
        for item in cur:
            tilename = item[0]
            self.run_names[tilename] = item[1]
            self.tilenames.append(tilename)
        return


    def getRADEC_coaddtile_SQL(self,tilename):
        
        print "# Building the list of files to be used from DESAR/SQL queries"
        cur = self.dbh.cursor()

        # ---------------------------------------------------------        
        # Another way suggested by Todd via the catalogs table
        #queryitems = ["o.ra","o.dec",
        #              "o.imageid_g", "o.imageid_r", "o.imageid_i", "o.imageid_z", "o.imageid_Y","c.id"]
        #query_alt = """
        #select %s
        #from catalog c, coadd_objects co
        #where c.tilename = '%s'
        #  and c.run='%s'
        #  and (
        #      (c.id = co.catalogid_g and c.band='g') OR
        #      (c.id = co.catalogid_i and c.band='i') OR
        #      (c.id = co.catalogid_r and c.band='r') OR
        #      (c.id = co.catalogid_z and c.band='z') OR
        #     (c.id = co.catalogid_y and c.band='Y') )""" % ( querylist, tilename, self.run_names[tilename])
        # ---------------------------------------------------------        

        # The reason why this query is so long is because the
        # COADD_OBJECTS table doesn't have any type of ID that
        # indentifies the COADD_OBJECTS_ID column with parent
        # tile. The only way is via the
        # COADD_OBJECTS.IMAGEGID_G/R/I/Z/Y colums that relate to
        # CATALOGID_G/R/I/Z/Y colums and to IMAGEGID_G/R/I/Z/Y colums
        # 
        queryitems = ["o.coadd_objects_id","o.ra", "o.dec"]
        querylist = ",".join(queryitems)
        query = """
        select %s
        from coadd c, coadd_objects o
        where c.tilename = '%s'
          and c.run = '%s'
          and (
               c.id=o.imageid_g OR
               c.id=o.imageid_r OR
               c.id=o.imageid_i OR
               c.id=o.imageid_z OR
               c.id=o.imageid_Y) """ % ( querylist, tilename, self.run_names[tilename])

        print "# Will execute the SQL query:\n********%s\n********" % query
        t0 = time.time()
        # Do the query
        cur.execute(query) 
        # Get them all at once
        list_of_tuples = cur.fetchall()
        # Use zip and "*" to unpack tuples and make list and nd-arrays
        ids, ra, dec =  zip(*list_of_tuples)
        self.objectsID  = numpy.array(list(ids))
        self.objectsRA  = numpy.array(list(ra))
        self.objectsDEC = numpy.array(list(dec))
        print "# SQL query done in:  %s" % elapsed_time(t0)


        
    def getXCorr(self):

        """
        Get the dust correction for current object in self.objectsRA, and seld.objectsDEC
        Return ndarray Xc[filter], Xc_err[filter]
        """
        Xc, Xc_err = X.Xcorrection(self.objectsRA,self.objectsDEC,DECam_filters)


# Format time
def elapsed_time(t1,verb=False):
    import time
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verb:
        print >>sys.stderr,"Elapsed time: %s" % stime
    return stime

def cmdline():

    from optparse import OptionParser

    # Read in the command line options
    USAGE = "\n"
    USAGE = USAGE + "\t %prog <tilename> [COADD-VERSION]\n" 
    USAGE = USAGE + "\t i.e.: \n"
    USAGE = USAGE + "\t %prog DES0056-4831 [SVA1_COADD] \n"

    # color_tile.py DES0056-4831

    parser = OptionParser(usage=USAGE)

    parser.add_option("--outdir",
                      dest="outdir", default='./color_tiles',
                      help="Output Directory to put files in")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("\n\tERROR:incorrect number of arguments")        

    return options,args


######################
# Call the procedure
######################
if __name__ == '__main__':

    t0 = time.time()
    # The start time
    tstart   = time.time()

    # Get the command line options
    opt,arg = cmdline()
    tilename = arg[0]
    try:
        coadd_version = arg[1] 
    except:
        coadd_version = 'SVA1_COADD'

    # initialize the class and collect files
    p = coadd(coadd_version=coadd_version)
    #p.getRADEC_coaddtile_SQL(tilename)
    #p.getXCorr()

    # Make the list of files
    for tilename in sorted(p.tilenames):
        t1 = time.time()
        print "# TILE:%s" % tilename
        p.getRADEC_coaddtile_SQL(tilename)
        p.getXCorr()
        print "# TILE Total time: %s" % elapsed_time(t1)

    print "# Total time: %s" % elapsed_time(t0)


    
