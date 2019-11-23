from setuptools import setup

setup(
   name='prj',
   version='0.3.1',
   description='Setup path dependencies of a (Windows) python project from any submodule, or via interactive shell/IDLE.',
   author='binares',
   packages=['prj'],
   python_requires='>=3.4',
   install_requires=[
      'pywin32>=222,<225;platform_system=="Windows"',
      'PyYAML>=3.10',
   ],
)

#pywin 225, 226, 227 raise
#ImportError: DLL load failed: The specified procedure could not be found.
#when trying `from win32 import win32api`
