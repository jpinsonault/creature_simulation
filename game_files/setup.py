# Compile command: python setup.py build_ext --inplace --compiler=mingw32
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[
    	Extension("PygameUtils", ["PygameUtils.pyx"]),
    	Extension("GraphNode", ["GraphNode.py"]),
    	Extension("GameObjects", ["GameObjects.py"]),
        Extension("Camera", ["Camera.py"]),
    	Extension("QuadTree", ["QuadTree.py"])
    ],
    include_dirs=[numpy.get_include()]
)

print("""
	############
	# Success! #
	############""")
