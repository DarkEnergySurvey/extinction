import distutils
from distutils.core import setup
import glob

sed_files = glob.glob("etc/SED/*.sed")
flt_files = glob.glob("etc/FILTER/*.res")
sql_files = glob.glob("etc/*.sql")
bin_files = glob.glob("bin/compute_*") + glob.glob("bin/*.txt")

# The main call
setup(name='extinction',
      version ='3.0.0',
      license = "GPL",
      description = "A Dust Extinction correction module for DESDM.",
      author = "Felipe Menanteau",
      author_email = "felipe@illinois.edu",
      packages = ['extinction'],
      package_dir = {'': 'python'},
      scripts = bin_files,
      data_files=[('etc/SED',   sed_files),
                  ('etc/FILTER',flt_files),
                  ('etc',   sql_files),
                  ('ups', ['ups/extinction.table']),]
      )





