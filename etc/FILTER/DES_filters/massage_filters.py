#!/usr/bin/env python3

import os,sys
import tableio

filters = ('g','r','i','z','y')

header = """# %s DECam filter response from David James\n"""

for filter in filters:
    fname   = 'DES%s-FullSize-woptics-watmos.par' % filter
    resname = '%s_DECam.res' % filter
    res = open(resname,"w")

    res.write(header % filter)

    for line in open(fname).readlines():
        vals = line.split()

        if line[:11] != 'TRANMISSION':
            continue

        wave = float(vals[1])
        tran = float(vals[7])
        if tran < 0:
            tran = 0

        res.write("%8.1f %8.5f\n" % (wave,tran))
    print("# Wrote %s" % resname)
    res.close()
