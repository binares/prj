from setuptools import setup

setup(
   name='prj',
   version='0.3.1',
   description='Setup path dependencies of a (Windows) python project from any submodule, or via interactive shell/IDLE.',
   author='binares',
   packages=['prj'],
   python_requires='>=3.4',
   install_requires=[
      'pywin32>=223;platform_system=="Windows"',
      'PyYAML>=3.10, <5'
   ],
)
