from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("MultiNN_c", ["MultiNN_c.pyx"])],
    include_dirs=[numpy.get_include()]
)

print("""
	############
	# Success! #
	############""")
