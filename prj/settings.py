DEPRECATED_PYPROJECTS = 'PyProjects'


DEFAULT_PATHS = { '$PYPROJECTS': ['$DRIVE:\\PProjects\\PyProjects'],
                  '$PYPROJECTS_TEST': ['$DRIVE:\\PProjects\\PyProjects_test'],
                  '$CURPYPROJECTS': ['$PRJPATH\\..', '$PYPROJECTS'],
                  
                  '$PPATH': ['$P_IN',
                             '$CURPYPROJECTS\\$P_IN'],
                  
                  '$DPATH':  ['$D_IN',
                              '$DRIVE:\\PProjects\\PData\\$PRJNAME\\$D_IN'],
                  '$MDPATH': ['$MD_IN',
                              '$PRJPATH\\myData\\$MD_IN',
                              '$CURPYPROJECTS\\myData\\$MD_IN'],
                  
                  '$SRCDIR': ['$PRJPATH\\$SD_IN'],
                  '$EXTLIB': ['$EL_IN',
                              '$PRJPATH\\$EL_IN',
                              '$CURPYPROJECTS\\$EL_IN'],
                  
                  
                  '$BACKUP': ['$DRIVE:\\_backup']
                  
                  }

#Input paths can be absolute or relative
#If DEFAULTS_PATHS[x] doesn't list PARAM_MAP[x] value, then absolute paths 
#aren't included for the attribute (x) [for example if x='$SRCDIR' (attr=Project.srcDirs)]

#Note: DPATH AND MDPATH have \\(M)D_IN ending to eliminate the possibility of
# the body of that default path being returned (os.path.exists(body)) IF input path given
# However if [input_path = '$DEFAULT\\.', attr=X], then X_IN = '.' and body is returned

#prj.prj.resolve_path() will eliminate the possibility of
# os.path.realpath(relative_path) -> accidentally_existing_absolute_path
PARAM_MAP = {'$PPATH': '$P_IN',
             '$DPATH': '$D_IN',
             '$MDPATH': '$MD_IN',
             '$SRCDIR': '$SD_IN',
             '$EXTLIB': '$EL_IN'}

REQUIRES_INPUT = ['$PPATH','$SRCDIR','$EXTLIB']


PRJ_VARIABLES = ['$PRJDRIVE:','$PRJPATH','$PRJNAME','$PRJDIRNAME']

PRJ_FN = 'prj.yaml'
