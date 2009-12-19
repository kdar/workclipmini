#from distutils.core import setup, Extension
#
#setup(
#  name="Workclipmini",
#  version="1.0",
#  ext_modules=[Extension('HotKey', sources=['HotKeymodule.c'], extra_link_args=['-framework', 'Carbon'])]
#)

from setuptools import setup
from setuptools.extension import Extension

setup(
  install_requires=['distribute'],
  name="Workclipmini",
  version="1.0",
  ext_modules=[Extension('HotKey', sources=['HotKeymodule.c'], extra_link_args=['-framework', 'Carbon'])]
)