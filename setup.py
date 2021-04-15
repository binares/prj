import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
   name='prj',
   version='0.3.2',
   description='Setup path dependencies of a (Windows) python project from any submodule, or via interactive shell/IDLE.',
   long_description=README,
   long_description_content_type='text/markdown',
   url='https://github.com/binares/prj',
   author='binares',
   author_email='binares@protonmail.com',
   license='MIT',
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
