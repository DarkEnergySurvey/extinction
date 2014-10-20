#!/usr/bin/env python

import os,sys
import Xcorrect as X

DECam_filters = ('g_DECam','r_DECam','i_DECam','z_DECam','y_DECam')
SDSS_filters  = ('g_SDSS','r_SDSS','i_SDSS','z_SDSS')
sed = 'El_cww'
Rv = 3.10

print "# Filter A(Lam)/A(V)  A(Lam)/A(V)  A(V)/E(B-V) -- Rv=%s" % Rv
for filter in DECam_filters:
    ALambda_AV, ALambda_EBV, AV_EBV = X.compute_AEBV(filter,sed='flat',Rv=Rv)
    print "%s   %10.6f   %10.6f   %10.6f" % (filter, ALambda_AV, ALambda_EBV, AV_EBV)
