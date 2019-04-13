# prj
Setup path dependencies of a python project from any submodule, or via interactive shell/IDLE.
Currently only works on Windows platform + python3.

....................................................................

Suppose you have a project called MYPROJECT, with the file structure

```
MYPROJECT/
  myproject/
    test/
      test_foo.py
    __init__.py
    foo.py
  readme.txt
  
MY_EXTERNAL_LIBRARY/
  a_package/
    __init__.py
```

Normally if we'd like to run the test\_foo.py (which imports myproject.foo),
we'd open the cmd in MYPROJECT folder and type in `python -m myproject.test.test_foo"`

But suppose we are actively editing the test_foo.py in a python IDLE
and would like to run it via the IDLE. That could easily be done if the IDLE were
say pydev, where we have set MYPROJECT as the source folder.

Not so easy for those using the python standard IDLE, though. We'd have to add line 
`sys.path.insert(0,__file__+'/../..')`, and do so for every module we'd like to run 
(carefully counting the number of double dots). What if we move the file though?
Change it again.

With this package, we can create a file called prj.yaml in MYPROJECT (`MYPROJECT/prj.yaml`),
in which we declare:

```
srcDirs:
 - $PRJPATH
```
  
and to every module we want to run interactively (test_foo.py), we add the lines to the top:

 ```
 import prj
 P = prj.qs(__file__)
 ```
 
which returns Project object, and inserts full path to MYPROJECT folder to sys.path (index 0).

`prj.qs` searches from the path provided to its folder, to the folder's parent folder,
to parent folder's parent folder, and so on; until it finds the prj.yaml file.
Hence we can use `__file__` variable in any .py file of the project.

The project can also be set up via python interactive mode in cmd (open cmd and enter "python"):

```
>>>import prj
>>>P = prj.setup(full_path_to_MYPROJECT_directory)
>>>import myproject.test.test_foo as test_foo
>>>test_foo.test_this_function()
```
 
## ABOUT prj.yaml

The following parameters are accepted:

```
name: MYPROJECT
author: binares
version: 0.1.0

srcDirs:
 - $PRJPATH
 - $PRJPATH\myproject\test
 
extLibs:
 - $PRJPATH\..\MY_EXTERNAL_LIBRARY
 
#the one below = E:\\PROJECTDATA\MYPROJECT
data: E:\\PROJECTDATA\$PRJNAME
myData: E:\\MY_SECRET_PASSWORDS
 
#The path variables start with $
#Accepted path variables:
# $PRJPATH = $PPATH
# $PRJNAME
# $PRJDIRNAME
# $DRIVE - searches through all logical drives for the trailing path
# (e.g. $DRIVE:\\SOME_FOLDER); returns first found

#Variables can be combined too:
# $DRIVE:\\$PRJNAME
```

The Project object that was initiated now contains these attributes:

```
P.ppath #(path_to_MYPROJECT)
P.dpath = "E:\\PROJECTDATA\MYPROJECT"
P.mdpath = "E:\\MY_SECRET_PASSWORDS"
P.srcDirs = [path_to_MYPROJECT, path_to_MYPROJECT\myproject\test]
P.extLibs = [path_to_MY_EXTERNAL_LIBRARIES]
P.name = "MYPROJECT"
P.author = "binares"
P.version = "0.1.0"
```

After initiating a project, the sys.path will look like this:<br />
`[srcDirs from first to last, extLibs from first to last, the old sys.path]`

## FUNCTIONS

`prj.qs(_file_, ins_to='sys.path', build='if_not_implemented')`

`prj.setup(path, procedure='from_defaults', astype='$PPATH', 
          ins_to='sys.path', build=True, parent_prj=None)`
          
`prj.zip_contents(path,destination=None,compression='ZIP_DEFLATED',
                 include_pycache=False, exists='error')`
                 
Usage: `prj.zip_contents("C:\\MYPROJECT")` - creates zip file *C:\\\\MYPROJECT.zip* 
containing MYPROJECT contents. Can be any directory (not only projects).
   
`prj.Project.archive(package=None, destination='$PRJPATH\\..\\_backup',
                    compression='ZIP_DEFLATED', include_pycache=False,
                    exists='rename')`
                    
same as zip_contents, but does so directly for the project at hand.


