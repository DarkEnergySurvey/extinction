#------------------------------------------------------------------------------
# D Schlegel, 12 March 1999, Princeton
#------------------------------------------------------------------------------
#
# Makefile for C and Fortran code to read SFD (1998) dust maps or
# Finkbeiner et al (1999) Galactic dust emission predictions.
#
# Compile everything with "make all", which will put the binaries in
# the directory specified by $DESTDIR.
#
# This software is written to ANSI C specifications.  This is supported
# on many platforms by the Gnu C compiler, which can be obtained via
# anonymous FTP from "prep.ai.mit.edu".  First read the file
# "/pub/gnu/GNUinfo/FTP" for information about downloading.
#
# This code has only been tested with the "gcc" compiler on a Sun Sparcstation
# running SunOS 5.6 (Solaris), on a DEC Alpha running DEC Unix 4.0b, and on
# a Pentium PC running Linux 2.0.34.  It has also been tested with the native
# "cc" compiler on a Silicon Graphics machine running IRIX.  Select the
# compiler flags below appropriate to your system.
#
# There are several test codes for linking with Fortran:
#   testf_lambert.f
#   testf_sync.f
#   testf_thermal.f
#------------------------------------------------------------------------------
# Select destination directory for the binaries:
#DESTDIR = ./

# Select OS -- F. Menanteau
UNAME_S := $(shell uname)

DESTDIR = bin

# COMPILE ON A SUN RUNNING SOLARIS
# Use the gnu compilers (gcc,g77)
ifeq ($(UNAME_S),SunOS)
  #DESTDIR = bin.SunOS
  CC = gcc
  FC = g77
  CFLAGS = -O2 -D__SUN
  FFLAGS = -O3
endif

# COMPILE ON AN x86 RUNNING LINUX
# Use the gnu compilers (gcc,g77)
# Note that Linux already defines LITTLE_ENDIAN
ifeq ($(UNAME_S),Linux)
   #DESTDIR = bin.Linux_x86_64
   CC = gcc	
   FC = g77
   CFLAGS = -O2 -D__LINUX
   FFLAGS = -O3
endif

# Felipe Menanteau, NCSA Oct 2013
# COMPILE ON OSX 
# Use the gnu compilers (gcc,g77)
# Note that OSX requites LITTLE_ENDIAN !!!!
ifeq ($(UNAME_S),Darwin)
   #DESTDIR = bin.Darwin_x86_64
   CC = gcc
   FC = g77 
   CFLAGS =  -O2 -D__OSX -arch i386 -arch x86_64 -DLITTLE_ENDIAN
   FFLAGS =  -O3
endif	

# COMPILE ON A DEC ALPHA
# Use the gnu compilers (gcc,g77)
#DESTDIR = ./
#CC = gcc
#FC = g77
#CFLAGS = -O2 -DLITTLE_ENDIAN
#FFLAGS = -O3

# COMPILE ON A SILICON GRAPHICS RUNNING IRIX
# Use the native compilers (cc,f77) on SGI machines.
# Alternatively, it seems that one can use the gcc compiler, but remove the
# includes for <stdlib.h> from predict_thermal.c, dust_getval.c, subs_lambert.c
#DESTDIR = ../bin.iris4d
#CC = cc
#FC = f77
#CFLAGS = -O2
#FFLAGS = -O3

# For the old Sun compiler, the following may work:
#CC = cc
#CFLAGS = -O2 -DOLD_SUNCC -D__SUN

# A report from J. Vinko that the following will work with the Sun compiler:
#CC = cc
#CFLAGS = -xO2 -D__SUN

# -----------------------------------------------------------------------------
# Make the DESTDIR DIR - (Felipe Menanteau)
makedir: 
	mkdir -p $(DESTDIR)

#------------------------------------------------------------------------------
# Define C libraries:
CLIBS = -lm

# Define files for the basic FITS routines:
SIMPLEFITS = subs_fits.o subs_memory.o subs_inoutput.o

simplefits:	$(SIMPLEFITS)

lambert:     dust_getval lambert_getval predict_sync predict_thermal \
	testf_lambert testf_sync testf_thermal

all:	makedir simplefits lambert

# Just dust_getval -- Added by Felipe Menanteau
dust: makedir dust_getval

#------------------------------------------------------------------------------
# LAMBERT

dust_getval: dust_getval.o subs_lambert.o subs_asciifile.o $(SIMPLEFITS)
	$(CC) $(CFLAGS) -o $(DESTDIR)/dust_getval dust_getval.o \
	subs_lambert.o subs_asciifile.o \
	$(SIMPLEFITS) $(CLIBS)

lambert_getval: lambert_getval.o subs_lambert.o $(SIMPLEFITS)
	$(CC) $(CFLAGS) -o $(DESTDIR)/lambert_getval lambert_getval.o \
	subs_lambert.o \
	$(SIMPLEFITS) $(CLIBS)

predict_sync: predict_sync.o subs_predict.o subs_lambert.o \
	subs_asciifile.o $(SIMPLEFITS)
	$(CC) $(CFLAGS) -o $(DESTDIR)/predict_sync predict_sync.o \
	subs_predict.o subs_lambert.o subs_asciifile.o \
	$(SIMPLEFITS) $(CLIBS)

predict_thermal: predict_thermal.o subs_predict.o subs_lambert.o \
	subs_asciifile.o $(SIMPLEFITS)
	$(CC) $(CFLAGS) -o $(DESTDIR)/predict_thermal predict_thermal.o \
	subs_predict.o subs_lambert.o subs_asciifile.o \
	$(SIMPLEFITS) $(CLIBS)

testf_lambert: testf_lambert.o subs_lambert.o $(SIMPLEFITS)
	$(FC) $(FFLAGS) -o $(DESTDIR)/testf_lambert testf_lambert.o \
	subs_lambert.o \
	$(SIMPLEFITS) $(CLIBS)

testf_sync: testf_sync.o subs_predict.o subs_lambert.o $(SIMPLEFITS)
	$(FC) $(FFLAGS) -o $(DESTDIR)/testf_sync testf_sync.o \
	subs_predict.o subs_lambert.o \
	$(SIMPLEFITS) $(CLIBS)

testf_thermal: testf_thermal.o subs_predict.o subs_lambert.o $(SIMPLEFITS)
	$(FC) $(FFLAGS) -o $(DESTDIR)/testf_thermal testf_thermal.o \
	subs_predict.o subs_lambert.o \
	$(SIMPLEFITS) $(CLIBS)

#------------------------------------------------------------------------------
clean:
	/bin/rm -f *.o

#------------------------------------------------------------------------------
