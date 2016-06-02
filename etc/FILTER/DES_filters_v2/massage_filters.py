#!/usr/bin/env python

import os,sys

filters = ('u','g','r','i','z','y')

#header = """# %s DECam filter response from David James\n"""
header = "# %s DEcam filter response from: https://cdcvs.fnal.gov/redmine/attachments/download/10048/20130322.tar.gz\n"


for filter in filters:
    #fname   = 'DES%s-FullSize-woptics-watmos.par' % filter
    fname   = '20130322_%s.dat' % filter    
    resname = '%s_DECam.res' % filter
    res = open(resname,"w")

    res.write(header % filter)

    for line in open(fname).readlines():

        if line[0] == "#":
            continue
        vals = line.split()

        wave = float(vals[0])
        tran = float(vals[1])
        if tran < 0:
            tran = 0
        
        res.write("%8.1f %9.6f\n" % (wave,tran))
    print "# Wrote %s" % resname
    res.close()
