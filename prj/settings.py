import os
import platform
_IS_WINDOWS = (platform.system() == 'Windows')


DEPRECATED_PYPROJECTS = 'PyProjects'


DEFAULT_PATHS = { '$PYPROJECTS': ['$DRIVE:\\PProjects\\PyProjects'],
                  '$PYPROJECTS_TEST': ['$DRIVE:\\PProjects\\PyProjects_test'],
                  '$CURPYPROJECTS': ['$PRJPATH\\..', '$PYPROJECTS'],

                  '$C_OR_TILDE': ['C:'] if _IS_WINDOWS else ['~'],
                  
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

if not _IS_WINDOWS:
    for _v in DEFAULT_PATHS.values():
        for _i in range(len(_v)):
            _v[_i] = _v[_i].replace('$DRIVE:', '~').replace('\\','/')


for _drive in ('D:','E:','F:','G:','H:','I:','J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'S:', 'T:', 'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:'):
    DEFAULT_PATHS['${}_OR_TILDE'.format(_drive[0])] = [_drive] if _IS_WINDOWS else ['~']

#Input paths can be absolute or relative
#If DEFAULTS_PATHS[x] doesn't list PARAM_MAP[x] value, then absolute paths 
#aren't included for the attribute (x) [for example if x='$SRCDIR' (attr=Project.srcDirs)]

#Note: DPATH AND MDPATH have \\(M)D_IN ending to eliminate the possibility of
# the body of that default path being returned (os.path.exists(body)) IF input path given
# However if [input_path = '$DEFAULT\\.', attr=X], then X_IN = '.' and body is returned

#prj.prj.resolve_path() will eliminate the possibility of
# os.path.realpath(relative_path) -> accidentally_existing_absolute_path
SYMBOLS_MEANING_KEEP_ORIGINAL_INPUT_PATH = {
    '$PPATH': '$P_IN',
    '$DPATH': '$D_IN',
    '$MDPATH': '$MD_IN',
    '$SRCDIR': '$SD_IN',
    '$EXTLIB': '$EL_IN'
}

REQUIRES_INPUT = ['$PPATH','$SRCDIR','$EXTLIB']


PRJ_VARIABLES = ['$PRJDRIVE:','$PRJPATH','$PRJNAME','$PRJDIRNAME']

PRJ_FN = 'prj.yaml'
