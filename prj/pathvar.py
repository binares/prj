import os, sys

opt = os.path

from .pathfuncs import get_drives, fix_drive_letter, _IS_WINDOWS
from .settings import (
    DEFAULT_PATHS,
    SYMBOLS_MEANING_KEEP_ORIGINAL_INPUT_PATH,
    REQUIRES_INPUT,
    PRJ_VARIABLES,
)

SEP = os.sep
_LOG = 0

#####################
# VARIABLE_HANDLING #
#####################
# /home/user/
# /dir/
# C:\
# \dir\


# returns LIST of paths
def replace_variables(
    path, dtype=None, custom_param_values={}, start="$PRJDRIVE:", aPrj=None
):
    drive_kwargs = {}
    if start == "$PRJDRIVE:" and aPrj is not None:
        drive_kwargs["start"] = opt.splitdrive(aPrj.ppath)[0]

    if _IS_WINDOWS:
        strippedpath = _normalize(path).strip(SEP)
    else:
        strippedpath = _normalize(path).rstrip(SEP)

    pathparts = strippedpath.split(SEP)
    all_custom_values = {}

    if pathparts[0] == "$DEFAULT":
        try:
            trail_begin = pathparts[1]
        except IndexError:
            trail_begin = ""

        # trail = SEP.join(pathparts[1:])
        # trail = opt.normpath(trail)

        if dtype is None:
            raise TypeError('"$DEFAULT" in path, but dtype not specified')
        elif dtype[0] != "$":
            dtype = "$" + dtype
        dtype = dtype.upper()

        if dtype in REQUIRES_INPUT and trail_begin in ("", "."):  # ,'..'):
            raise ValueError(
                "dtype {} requires $DEFAULT/{{..}} to be followed "
                "by nonempty path. got: {}".format(dtype, path)
            )

        path = dtype
        which_X_IN = SYMBOLS_MEANING_KEEP_ORIGINAL_INPUT_PATH[dtype]
        all_custom_values[which_X_IN] = SEP.join(pathparts[1:])
        all_custom_values.update(custom_param_values)

    else:
        all_custom_values = custom_param_values

    if _LOG:
        print(
            "replace_variables() path(temp): {}; all_custom_values: {}".format(
                path, all_custom_values
            )
        )

    third_replaced = _replace_default_variables(path, **all_custom_values)

    if aPrj is None:
        third_replaced = [
            x
            for x in third_replaced
            if not _contains_prj_variables(x, _normalized=True)
        ]

    if _LOG:
        print("replace_variables() third_replaced:", third_replaced)

    fully_replaced = []

    for third_rpl_pth in third_replaced:
        if _contains_prj_variables(third_rpl_pth):
            if aPrj is None:
                continue
            half_rpl_pth = _replace_prj_variables(
                third_rpl_pth, aPrj=aPrj, _normalized=True
            )
        else:
            half_rpl_pth = third_rpl_pth

        if _IS_WINDOWS:
            fully_replaced += _replace_drive_variable(half_rpl_pth, **drive_kwargs)
        else:
            fully_replaced += [half_rpl_pth]

    return fully_replaced


def _normalize(path):
    if _IS_WINDOWS:
        return path.replace("/", "\\").lstrip("\\")
    else:
        return path


def _defaultize(path, _normalized=False):
    if not _normalized:
        path = _normalize(path)

    if _IS_WINDOWS and ":" in path:
        return path
    if not _IS_WINDOWS and path[:1] in ("/", "~"):
        return path

    if path.split(SEP)[0] != "$DEFAULT":
        path = "$DEFAULT{}{}".format(SEP, path)

    return path


def _contains_prj_variables(path, _normalized=False):
    if not _normalized:
        path = _normalize(path)
    splitpath = path.split(SEP)

    return any(True for x in PRJ_VARIABLES if x in splitpath)


# returns PATH
def _replace_prj_variables(path, aPrj, _normalized=False):
    if not _normalized:
        path = _normalize(path)
    pathparts = path.split(SEP)

    projectdrive = opt.splitdrive(aPrj.ppath)[0]
    pairs = dict(
        [
            ["$PRJDRIVE:", projectdrive],
            ["$PRJPATH", aPrj.ppath],
            ["$PRJNAME", aPrj.name],
            ["$PRJDIRNAME", opt.basename(aPrj.ppath)],
        ]
    )

    path_replaced = SEP.join([pairs.get(x, x) for x in pathparts])

    return path_replaced


# returns LIST of paths
def _replace_default_variables(path, _r=0, **CUSTOM_VALUES):
    if not _r:
        path = _normalize(path)
        if len(CUSTOM_VALUES):
            PATHVAR_MAP = DEFAULT_PATHS.copy()
            for k, v in CUSTOM_VALUES.items():
                if isinstance(v, str):
                    CUSTOM_VALUES[k] = [v]
            PATHVAR_MAP.update(CUSTOM_VALUES)
        else:
            PATHVAR_MAP = DEFAULT_PATHS

    else:
        PATHVAR_MAP = _r

    pathparts = path.split(SEP)

    try:
        var = next(x for x in pathparts if x in PATHVAR_MAP)
    except StopIteration:
        return [path]

    replaced = []

    for replacement_path in PATHVAR_MAP[var]:
        new_pth = SEP.join([x if x != var else replacement_path for x in pathparts])
        plainpaths = _replace_default_variables(new_pth, PATHVAR_MAP)
        replaced.extend(plainpaths)

    return replaced


def _replace_drive_variable(path, start="$CURDRIVE:"):
    drives = []
    # Linux opt.splitdrive('a/b/c') -> ('','a/b/c')
    # Windows opt.splitdrive('a/b/c') -> ('','a/b/c')
    #            .splitdrive('C:/a/b/c') -> ('C:','/a/b/c')
    current_drive = opt.splitdrive(os.getcwd())[0] + SEP

    # start only included if path starts with $DRIVE
    include_start = False
    if start == "$CURDRIVE:":
        start = current_drive

    if path[:7] == "$DRIVE:":
        drives = get_drives()
        path = path[7:]
        include_start = True

    elif path[:8] in ("$2DRIVE:", "$3DRIVE:"):
        var = path[:8]
        path = path[8:]
        # C is preferred, since data may be kept on other disk
        # and when executing *it's* py files, C:\\ is sought first for prj
        drives = ["C:\\"]
        if current_drive != "C:\\":
            drives.append(current_drive)
        if var == "$3DRIVE:":
            include_start = True

    elif path[:10] == "$CURDRIVE:":
        pth2 = opt.join(current_drive, opt.normpath(path[10:]))
        return [pth2]

    else:
        return [path]

    if start is not None and include_start:
        start = fix_drive_letter(start)

        try:
            drives.remove(start)
        except ValueError:
            pass

        drives.insert(0, start)

    allpaths = [opt.join(drive, path) for drive in drives]

    return allpaths
