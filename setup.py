import distutils
from distutils.core import setup 
import glob

sed_files = glob.glob("etc/SED/*.sed")
flt_files = glob.glob("etc/FILTER/*.res")
bin_files = glob.glob("bin/*.py") + glob.glob("bin/*.txt") + glob.glob("bin/*.sql")

# The main call
setup(name='extinction',
      version ='0.1.0',
      license = "GPL",
      description = "A Dust Extinction correction module for DESDM.",
      author = "Felipe Menanteau",
      author_email = "felipe@illinois.edu",
      packages = ['Xcorrect'],
      package_dir = {'': 'python'},
      scripts = bin_files,
      data_files=[('etc/SED',   sed_files),
                  ('etc/FILTER',flt_files)]
     )





