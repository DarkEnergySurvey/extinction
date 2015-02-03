#!/usr/bin/env python

import os,sys
import despydb.desdbi
import time
import numpy
import Xcorrect as X

DECam_filters = ('g_DECam','r_DECam','i_DECam','z_DECam','y_DECam')

class coadd:

    def __init__(self,coadd_version, db_section = "db-desoper"):
        
        self.coadd_version = coadd_version

        # Setup desar queries here for later
        try:
            desdmfile = os.environ["des_services"]
        except KeyError:
            desdmfile = None
        self.dbh = despydb.desdbi.DesDbi(desdmfile,db_section)

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
        self.tilename = tilename


        # ---------------------------------------------------------        
        # Another way suggested by Todd via the catalogs table
        #queryitems = ["o.ra","o.dec",
        #              "o.imageid_g", "o.imageid_r", "o.imageid_i", "o.imageid_z", "o.imageid_Y","c.id"]
        #queryitems = ["co.coadd_objects_id","co.ra", "co.dec"]
        #querylist = ",".join(queryitems)
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
        #      (c.id = co.catalogid_y and c.band='Y') )""" % ( querylist, tilename, self.run_names[tilename])
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
        select distinct %s
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
        cur.arraysize = 1000
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
        (self.Xc,self.Xc_err,self.eBV,self.l,self.b) = X.Xcorrection_SFD98(self.objectsRA,self.objectsDEC,DECam_filters)


    def createXCorrTable(self,table='felipe.coadd_objects_xcorr'):

        t0 = time.time()
        cur = self.dbh.cursor()

        # make sure we delete before we created
        drop = "drop table %s purge" % table

        # Create command
        create = """
        create table %s (
        COADD_OBJECTS_ID        NUMBER(11)  NOT NULL,
        XCORR_SFD98_G           NUMBER(10,6),
        XCORR_SFD98_R           NUMBER(10,6),
        XCORR_SFD98_I           NUMBER(10,6),
        XCORR_SFD98_Z           NUMBER(10,6),
        XCORR_SFD98_Y           NUMBER(10,6),
        eBV                     NUMBER(10,6),
        L                       BINARY_FLOAT,
        B                       BINARY_FLOAT,
        TILENAME                VARCHAR2(20),
        constraint %s_pk PRIMARY KEY (coadd_objects_id)
        )"""  % (table,table.split(".")[1])


        # -- Add description of columns
        comments ="""comment on column %s.COADD_OBJECTS_ID is 'ID from COADD_OBJECTS table'
        comment on column %s.XCORR_SFD98_G    is 'g-band Galactic extinction Correction from SFD98 and Rv=3.1'
        comment on column %s.XCORR_SFD98_R    is 'r-band Galactic extinction Correction from SFD98 and Rv=3.1'
        comment on column %s.XCORR_SFD98_I    is 'i-band extinction Correction from SFD98 and Rv=3.1'
        comment on column %s.XCORR_SFD98_Z    is 'z-band extinction Correction from SFD98 and Rv=3.1'
        comment on column %s.XCORR_SFD98_Y    is 'Y-band extinction Correction from SFD98 and Rv=3.1'
        comment on column %s.eBV              is 'e(B-V) extinction'
        comment on column %s.L                is 'Galactic Longitude'
        comment on column %s.B                is 'Galactic Latitude'
        comment on column %s.TILENAME         is 'DES parent tilename'""" 

        print "# Will create new XCORR table: %s" % table
        try:
            print "# Dropping table: %s" % table
            cur.execute(drop)
        except:
            print "# Could not drop table: %s -- probably doesn't exist" % table
        print "# Creating table: %s" % table
        cur.execute(create)

        print "# Adding comments to: %s" % table
        for comment in comments.split("\n"):
            print comment % table
            cur.execute(comment % table)

        # Grand permission
        grant = "grant select on %s to des_reader" % table.split(".")[1]
        cur.execute(grant)
        self.dbh.commit()
        cur.close()
        return

    def InsertXCorr(self,table='felipe.coadd_objects_xcorr'):

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

        NID  = len(self.objectsID)
        rows = zip( self.objectsID.tolist(),
                    self.Xc['g_DECam'],
                    self.Xc['r_DECam'],
                    self.Xc['i_DECam'],
                    self.Xc['z_DECam'],
                    self.Xc['y_DECam'],
                    self.eBV,
                    self.l,
                    self.b,
                    [self.tilename]*NID) 
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

    description = """
    Compute SFD98 Galactic extinction for COADD_OBJECTS table, one tile at a time using a TAG for a CoaddVersion.
    """

    usage = """

    usage:
    compute_SFD98_coadd_objects.py [-h] [--TileName TILENAME]
                                      [--CreateTable]
                                      CoaddVersion TableName
    Examples:

    # Compute for all tiles in Y1A1_COADD_STRIPE82, store in felipe.coadd_objects_xcorr and create the table
    compute_SFD98_coadd_objects.py Y1A1_COADD_STRIPE82 felipe.coadd_objects_xcorr --CreateTable


    # Compute only one tilename and store in felipe.coadd_objects_xcorr
    compute_SFD98_coadd_objects.py Y1A1_COADD_STRIPE82 felipe.coadd_objects_xcorr --TileName DES2242-0041 

    """
    
    import argparse
    parser = argparse.ArgumentParser(description=description, usage=usage)

    # The positional arguments
    parser.add_argument("CoaddVersion", action="store", default=None,
                        help="DESAR TAGNAME to use (i.e. SVA1_COADD, Y1P1_COADD, Y1A1_COADD_STRIPE82)")

    parser.add_argument("TableName", action="store", default=None,
                        help="Table Name to store SFD98 Xcorrection information, (i.e. username.coadd_objects_xcorr)")

    # The optional arguments    
    parser.add_argument("--TileName", action="store", default=None,
                        help="TileName to compute")
    parser.add_argument("--CreateTable", action="store_true", default=False,
                        help="Forces Creation of TableName and will clobber if exists")

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

    # initialize the class and collect files
    print "# Initializing Tilenames"
    p = coadd(coadd_version=args.CoaddVersion)

    # Do only one tile
    if args.TileName:
        p.tilenames = [args.TileName]

    # Create XCORR table
    if args.CreateTable:
        print "# Will create %s" % args.TableName
        p.createXCorrTable(table=args.TableName)

    # Do them all
    ntiles  = len(p.tilenames)
    counter = 1
    # Make the list of files

    for tilename in sorted(p.tilenames):
        t1 = time.time()
        now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print "# --------------------------------------"
        print "# Starting TILE:%s (%s/%s)" % (tilename,counter,ntiles)
        print "# %s " % now
        p.getRADEC_coaddtile_SQL(tilename)
        p.getXCorr()
        p.InsertXCorr(table=args.TableName)
        print "# TILE Total time: %s" % elapsed_time(t1)
        counter = counter + 1
        
    print "# Total time: %s" % elapsed_time(t0)


    
