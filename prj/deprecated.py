import os, sys

opt = os.path
from collections import OrderedDict, namedtuple
import traceback

from .pathfuncs import get_drives
from .settings import DEPRECATED_PYPROJECTS as PYPROJECTS


def qs():
    return find_paths(ins_to="sys.path")


# Returns namedtuple(prj=...,data=...,src...) with its values being the paths to the
#   corresponding folders under the specified project 'projectname'
#   set go = field_name to change opt.curdir() to the resulting path under the field
# Returns str path if which is assigned to one of the fields of the namedtuple above
#   in that case option to just set go=True
# If projectname not specified, returns (None,None,None,mainLib=...,myData=...) only


def find_paths(
    projectname=None, which=None, go=False, ins_to="sys.path", ins_these=None
):
    # ins_these are dir_names with their (determined) path
    # later inserted to ins_to (e.g. sys.path, if given)
    if ins_to == "sys.path":
        ins_to = sys.path

    if ins_these is None:
        ins_these = ("src", "mainLib")
    else:
        seen = set()
        ins_these = [x for x in ins_these if not (x in seen or seen.add(x))]

    c_tree = [
        {"d": PYPROJECTS, "f": None, "s": [{"d": "mainLib"}, {"d": "myData"}]},
        {"d": "PData", "f": None, "s": []},
    ]

    if projectname:
        # PyProjects -> cur_project -> src
        # mainLib and myData paths are preferred if found inside prj folder
        # (not overwritten with (PyProjects -> x)
        c_tree[0]["s"].insert(
            0,
            {
                "d": projectname,
                "f": "prj",
                "s": [{"d": "src"}, {"d": "mainLib"}, {"d": "myData"}],
            },
        )

        c_tree[1]["s"].append({"d": projectname, "f": "data"})

    FIELDS = ["prj", "data", "src", "mainLib", "myData"]

    names = namedtuple("Project", FIELDS)
    paths = OrderedDict(zip(names._fields, [None] * len(names._fields)))

    _go = None

    drives = get_drives()

    for X in drives:
        outer_path = opt.join(X, "PProjects")
        try:
            _path_inserter(outer_path, c_tree, paths)
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        except Exception:
            traceback.print_exc()

    if which is not None:
        assert paths[which] is not None
        output = paths[which]

        if go is True:
            _go = which

    else:
        any_paths = any(True for x in paths.values() if x is not None)
        assert any_paths

        paths_tuple = names(**paths)
        output = paths_tuple

    for GO in (go, _go):
        if isinstance(GO, str):
            try:
                go_to = paths[GO]
                os.chdir(go_to)
            except Exception:
                traceback.print_exc()
                print(
                    'WARNING: chdir() failed, possibly writing instead\
                                            to curdir(): "'
                    + os.getcwd()
                    + '"'
                )
            else:
                break

    i = 0

    if ins_to:
        assert isinstance(ins_to, list)
        for field in ins_these:
            if paths.get(field) is None:
                continue
            pth = paths[field]
            while True:
                if pth not in ins_to:
                    break
                ind = ins_to.index(pth)
                if ind < i:
                    i -= 1
                del ins_to[ind]

            ins_to.insert(i, pth)
            i += 1

    return output


def _path_inserter(outer_path, contents, p_holder, overwrite=False):
    for c_dict in contents:
        i_path = opt.join(outer_path, c_dict["d"])

        if not opt.isdir(i_path):
            continue

        field = c_dict.get("f", c_dict.get("d"))
        if field is None:
            pass
        elif overwrite or p_holder.get(field) is None:
            p_holder[field] = i_path

        sub = c_dict.get("s")
        if sub is not None:
            _path_inserter(i_path, sub, p_holder, overwrite=overwrite)


def _construct_pPaths(**kw):
    FIELDS = ["prj", "data", "src", "mainLib", "myData", "_name"]

    paths = OrderedDict(zip(FIELDS, [None] * len(FIELDS)))  # PPaths._fields)))
    paths["srcDirs"] = []
    paths["extLibs"] = []
    paths.update(kw)

    PPaths = namedtuple("PPaths", FIELDS)
    pPaths = PPaths(**paths)

    return pPaths
