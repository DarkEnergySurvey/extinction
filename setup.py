import distutils
from distutils.core import setup, Extension, Command
import os
import sys
import glob
import shutil
import platform

package_basedir = os.path.abspath(os.curdir)

#CodeC_dir       = 'src/CodeC_FMupdate'
CodeC_dir       = 'src/CodeC_DESDMpatched'
CodeC_build_dir = os.path.join('build',os.path.basename(CodeC_dir))
makefile = os.path.join(CodeC_build_dir, 'Makefile')
DESTDIR = os.path.join(package_basedir,"build/bin")

# Make a copy in build...
def copy_update(dir1,dir2):
    print "# Copying %s --> %s" % (dir1,dir2)
    f1 = os.listdir(dir1)
    for f in f1:
        path1 = os.path.join(dir1,f)
        path2 = os.path.join(dir2,f)
        if not os.path.exists(path2):
            shutil.copy(path1,path2)
        else:
            stat1 = os.stat(path1)
            stat2 = os.stat(path2)
            if (stat1.st_mtime > stat2.st_mtime):
                shutil.copy(path1,path2)

def compile_CodeC():
    os.chdir(CodeC_build_dir)
    ret = os.system('make dust DESTDIR=%s' % DESTDIR)
    if ret != 0:
        raise ValueError("could not compile CodeC ")
    os.chdir(package_basedir)


if not os.path.exists('build'):
    ret=os.makedirs('build')

# Make CodeC build location
if not os.path.exists(CodeC_build_dir):
    ret=os.makedirs(CodeC_build_dir)
# Copy and Compile dust_geteval
copy_update(CodeC_dir, CodeC_build_dir)
compile_CodeC()

# Define data_files to copy
map_files = glob.glob("etc/maps/*.fits")
sed_files = glob.glob("etc/SED/*.sed")
flt_files = glob.glob("etc/FILTER/*.res")


# The main call
setup(name='extinction',
      version ='0.1.0',
      license = "GPL",
      description = "A Dust Extinction correction module for DESDM.",
      author = "Felipe Menanteau",
      author_email = "felipe@illinois.edu",
      packages = ['Xcorrect'],
      package_dir = {'': 'python'},
      scripts = ['build/bin/dust_getval','bin/compute_ffactors.py'],
      data_files=[('ups',['ups/extinction.table']),
                  ('etc/maps',  map_files),
                  ('etc/SED',   sed_files),
                  ('etc/FILTER',flt_files)]
     )





