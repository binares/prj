import sys, os

opt = os.path
import yaml

from .management import archive
from .pathfuncs import (
    search_path_in_drives,
    fix_drive_letter,
    get_drives,
    insert_paths,
    split_linux_path,
    _IS_WINDOWS,
)

from .pathvar import (
    replace_variables,
    _defaultize,
    _replace_default_variables,
    _replace_prj_variables,
    _replace_drive_variable,
)
from .settings import DEFAULT_PATHS, PRJ_FN

PPATHS = None
_IMPLEMENTED = []
KEYS_WITH_UTILITY = [
    "name",
    "version",
    "author",
    "srcDirs",
    "src",
    "extLibs",
    "ext",
    "path",
    "ppath",
    "dpath",
    "data",
    "mdpath",
    "myData",
]
INS_TO = "sys.path"
DELETE_SYS_PATH_INDEX = 0
_sys_path_index_deleted = False
SEP = os.sep
_LOG = 0


def _set_log(value=1):
    from . import pathvar

    pathvar._LOG = value
    global _LOG
    _LOG = value


set_logging = _set_log


def set_PRJ_FN(value):
    from . import settings

    settings.PRJ_FN = value
    # by default prj.yaml
    global PRJ_FN
    PRJ_FN = value


class Project:
    def __init__(
        self,
        path,
        name=None,
        version=None,
        author=None,
        dpath=None,
        mdpath=None,
        srcDirs=["$PRJPATH"],
        extLibs=None,
        attrs={},
        *,
        ins_to="sys.path",
        build=True
    ):
        assert isinstance(path, str)
        self.ppath = path
        self.version = version
        self.author = author
        self.ins_to = ins_to

        if name is None:
            self.name = opt.basename(path)
        else:
            self.name = name

        self.set_dpath(dpath)
        self.set_mdpath(mdpath)

        self.srcDirs = []
        self.extLibs = []

        if srcDirs is None:
            pass
        elif isinstance(srcDirs, str):
            self.add_src(srcDirs, build=False)
        else:
            [self.add_src(x, build=False) for x in srcDirs[::-1]]

        if extLibs is None:
            pass
        elif isinstance(extLibs, str):
            self.add_ext(extLibs, build=False)
        else:
            [self.add_ext(x, build=False) for x in extLibs[::-1]]

        self.attrs = attrs.copy()

        if build:
            self.build()

    def _set_datapath(self, path="$DEFAULT", pathtype="dpath"):
        if path is None:
            setattr(self, pathtype, None)
            return

        astype = "$" + pathtype.upper()
        realpths = resolve_path(
            path, op="isdir", select="first", astype=astype, parent_prj=self
        )

        try:
            datapath = realpths[0]
        except IndexError:
            raise FileNotFoundError(
                "{} not found with this path-variable: {}".format(pathtype, path)
            )

        setattr(self, pathtype, datapath)

    def set_dpath(self, path="$DEFAULT"):
        self._set_datapath(path, "dpath")

    def set_mdpath(self, path="$DEFAULT"):
        self._set_datapath(path, "mdpath")

    def _add_item(self, itm_type, item, op="insert"):
        attr = getattr(self, itm_type)

        if op == "append":
            attr.append(item)
        else:
            attr.insert(0, item)

    def add_src(self, path, op="insert", build=True):
        # $PRJPATH (or simply $PPATH) is the only allowed variable, but is not necessary
        # only relative paths to $PRJPATH are allowed (and not backwards, i.e. $PRJPATH\..)
        path = path.lstrip("/\\")
        contains_x = next(
            (x for x in ["$PRJPATH", "$PPATH"] if path.startswith(x)), None
        )
        if contains_x:
            path = path[len(contains_x) :]
        npth = opt.normpath(path).strip(SEP)
        srcpth = opt.normpath(opt.join(self.ppath, npth))

        if npth == ".." or npth[:3] == ".." + SEP:
            raise ValueError(
                "srcDir must be inside project dir tree, got: {}".format(npth)
            )
        elif opt.splitdrive(npth)[0] != "":
            raise ValueError("srcDirs must be relative, got: {}".format(path))
        elif not opt.isdir(srcpth):
            raise FileNotFoundError(
                'srcDir "{}" isn\'t part of the project'.format(path)
            )

        # srcDirsPaths.append(srcpth)
        self._add_item("srcDirs", srcpth, op=op)
        if build:
            self.build()

    def add_ext(self, path, op="insert", build=True):
        item = setup(
            path, astype="$EXTLIB", ins_to=self.ins_to, build=False, parent_prj=self
        )

        self._add_item("extLibs", item, op=op)
        if build:
            self.build()

    def build(self):
        if self.ins_to is None:
            return

        for x in self.extLibs[::-1]:
            if isinstance(x, Project):
                x.build()
            else:
                insert_paths(x, ins_to=self.ins_to)

        for x in self.srcDirs[::-1]:
            insert_paths(x, ins_to=self.ins_to)

    def archive(
        self,
        package=None,
        destination="$PRJPATH{}..{}_backup".format(SEP, SEP),
        compression="ZIP_DEFLATED",
        include_pycache=False,
        exists="rename",
    ):
        return archive(self, package, destination, compression, include_pycache, exists)

    def get(self, key, *default):
        if len(default) > 1:
            raise TypeError(
                "get expected at most 2 arguments, got %d" % len(default) + 1
            )
        default = default[0] if default else None
        if key in KEYS_WITH_UTILITY:
            return getattr(self, key)
        return self.attrs.get(key, default)

    def __getitem__(self, key):
        if key in KEYS_WITH_UTILITY:
            return getattr(self, key)
        return self.attrs[key]

    @property
    def path(self):
        return self.ppath

    @path.setter
    def path(self, value):
        self.ppath = value

    @property
    def data(self):
        return self.dpath

    @data.setter
    def data(self, value):
        self.dpath = value

    @property
    def myData(self):
        return self.mdpath

    @myData.setter
    def myData(self, value):
        self.mdpath = value

    @property
    def src(self):
        return self.srcDirs

    @src.setter
    def src(self, value):
        self.srcDirs = value

    @property
    def ext(self):
        return self.extLibs

    @ext.setter
    def ext(self, value):
        self.extLibs = value


class AlreadyImplemented(Exception):
    def __init__(self, prj, path_tried=None):
        self.prj = prj
        self.path_tried = path_tried


def set_delete_sys_path_index(value):
    global DELETE_SYS_PATH_INDEX
    DELETE_SYS_PATH_INDEX = value


# returns LIST of paths
def resolve_path(path, astype="$PPATH", op="isdir", select="all", parent_prj=None):
    realop = getattr(os.path, op)

    # among other operations the path is defaultized (_defaultize(path))
    # thus for this function to include the possibility of 'path' being completely arbitrary,
    # must ensure that DEFAULT_PATHS[dtype] contains PARAM_MAP[dtype]
    defaultized = _defaultize(path)
    if _LOG:
        print("resolve_path() defaultized:", defaultized)

    paths = replace_variables(defaultized, dtype=astype, aPrj=parent_prj)
    if _LOG:
        print("resolve_path() paths:", paths)
    # if astype == '$EXTLIB': print(paths)
    paths = [
        opt.normpath(x.strip(SEP) if _IS_WINDOWS else x.rstrip(SEP)) for x in paths
    ]

    # drop relative paths (due to our os.getcwd() being uncertain; prj.yaml isn't necessarily in the project root dir)
    if _IS_WINDOWS:
        abs_paths = [opt.realpath(x) for x in paths if opt.splitdrive(x)[0] != ""]
    else:
        abs_paths = [
            opt.realpath(opt.expanduser(x)) for x in paths if x[0] in (SEP, "~")
        ]  # expanduser() bc opt.isdir() doesn't undertand '~'

    if _LOG:
        print("resolve_path() abs_paths:", abs_paths)

    opfilter = filter(realop, abs_paths)

    if select == "first":
        try:
            return [next(opfilter)]  # [opt.realpath( next(opfilter) )]
        except StopIteration:
            return []

    return list(opfilter)


def find_prj_file(path, procedure="search", astype="$PPATH", parent_prj=None):
    response = {"dir": None, "error": None}

    if procedure == "search":
        if _IS_WINDOWS:
            drive, trail = opt.splitdrive(opt.realpath(path))
            drive += "\\"
            pathparts = trail.split("\\")[1:]
            len_path = len(pathparts)

            n_first_parts_only = lambda i: opt.join(
                drive, *pathparts[: len_path - i], PRJ_FN
            )
            prjfilepaths = map(n_first_parts_only, list(range(len_path + 1)))
        else:
            split = split_linux_path(path)
            n_first_parts_only = lambda i: opt.join(*split[: len(split) - i], PRJ_FN)
            prjfilepaths = map(n_first_parts_only, list(range(len(split) + 1)))

        # print(list(prjfilepaths))
        # print(list(filter(opt.isfile, prjfilepaths)))
        try:
            response["dir"] = opt.dirname(next(filter(opt.isfile, prjfilepaths)))
        except StopIteration:
            response["error"] = FileNotFoundError(
                'Project file could not be found in backward-search from path: "{}"'.format(
                    path
                )
            )

    else:
        prjdirpaths = resolve_path(path, astype=astype, parent_prj=parent_prj)
        prjfilepaths = map(lambda x: opt.join(x, PRJ_FN), prjdirpaths)

        try:
            response["dir"] = opt.dirname(next(filter(opt.isfile, prjfilepaths)))
        except StopIteration:
            response["error"] = FileNotFoundError(
                'Project file could not be found with path provided: "{}"'.format(path)
            )

            if astype != "$PPATH" and len(prjdirpaths):
                response["dir"] = prjdirpaths[0]

    return response


def read_prj_file(path):
    with open(path, encoding="utf-8") as f:
        prj_instr = yaml.safe_load(f)

    # empty file
    if prj_instr is None:
        prj_instr = {}

    prj_instr["path"] = opt.dirname(path)

    return prj_instr


def implement_prj_file(
    path, ins_to="sys.path", build=True, replace_null_srcDirs=["$PRJPATH"]
):
    instr = read_prj_file(path)
    project = _implement_prj_instructions(
        instr, ins_to=ins_to, build=build, replace_null_srcDirs=replace_null_srcDirs
    )

    return project


def _implement_prj_instructions(
    prj_instr, ins_to="sys.path", build=True, replace_null_srcDirs=["$PRJPATH"]
):
    projectdir = prj_instr["path"]
    projectname = opt.basename(projectdir)

    if "name" in prj_instr:
        projectname = prj_instr["name"]

    try:
        prev_implemented_prj = get_prj(path=projectdir)
    except ValueError:
        pass
    else:
        raise AlreadyImplemented(prev_implemented_prj, path_tried=projectdir)

    datadir = prj_instr.get("dpath", prj_instr.get("data"))
    mydatadir = prj_instr.get("mdpath", prj_instr.get("myData"))
    srcDirs = prj_instr.get("srcDirs", prj_instr.get("src"))
    extLibs = prj_instr.get("extLibs", prj_instr.get("ext"))
    attrs = {k: v for k, v in prj_instr.items() if k not in KEYS_WITH_UTILITY}

    if srcDirs is None:
        srcDirs = replace_null_srcDirs

    P = Project(
        name=projectname,
        version=prj_instr.get("version"),
        path=projectdir,
        dpath=datadir,
        mdpath=mydatadir,
        srcDirs=srcDirs,
        extLibs=extLibs,
        attrs=attrs,
        ins_to=ins_to,
        build=build,
    )

    _IMPLEMENTED.append(P)

    return P


def get_prj(name=None, path=None):
    path2 = opt.realpath(path) if path else None
    # is_implem = False

    try:
        return next(X for X in _IMPLEMENTED if X.ppath == path2)
    except StopIteration:
        pass

    try:
        return next(X for X in _IMPLEMENTED if X.name == name)
    except StopIteration:
        pass

    """for imppath in X.srcDirs:
        if path2 == imppath:
            return True
    for imppath in X.extLibs:
        if path2 == imppath:
            return True"""

    raise ValueError(
        "Cannot find prj with parameters path={}, name={}".format(path, name)
    )


# may rely on os.getcwd(), therefore should be placed at the top of a script
# (sub modules can still be imported at random time without worrying about cwd,
#  since their setup() [if added] won't renew the paths)


def qs(
    _file_,
    ins_to="sys.path",
    build="if_not_implemented",
    replace_null_srcDirs=["$PRJPATH"],
):
    """qs - quick setup. Typical usage: P = prj.qs(__file__)
    Searches upstream from _file_ parameter until prj.yaml is found.
    (_file_ is a path, normally use module's __file__ variable;
     searched like this: [_file_\prj.yaml, _file_\..\prj.yaml, ...])
    Should be called at the top of the script."""

    return setup(
        opt.realpath(_file_),
        procedure="search",
        astype="$PPATH",
        ins_to=ins_to,
        build=build,
        replace_null_srcDirs=replace_null_srcDirs,
    )


def setup(
    path,
    procedure="from_defaults",
    astype="$PPATH",
    ins_to="sys.path",
    build=True,
    parent_prj=None,
    replace_null_srcDirs=["$PRJPATH"],
):
    """Sets up project by the `path` to prj.yaml's directory. Alternatively set `procedure` to
    'search' in order to use it as `qs(path)`. `build=True` forces the project to "build" its paths
    (insert them into `ins_to`). Returns: Project object."""

    global _sys_path_index_deleted
    # If this is the first time setup() is called, delete sys.path[0]
    # Make sure though that there are no manually inserted paths;
    if (
        DELETE_SYS_PATH_INDEX is not None
        and not _sys_path_index_deleted
        and (ins_to == "sys.path" or ins_to is sys.path)
    ):
        del sys.path[DELETE_SYS_PATH_INDEX]
    _sys_path_index_deleted = True

    if isinstance(build, str):
        if build == "if_not_implemented":
            build_bool = True
        else:
            raise ValueError(build)
    else:
        build_bool = bool(build)

    response = find_prj_file(
        path, procedure=procedure, astype=astype, parent_prj=parent_prj
    )
    # build = True if parent_prj is None else False

    if not response["dir"]:
        raise response["error"]
    elif astype == "$PPATH" and response["error"]:
        raise response["error"]

    if not response["error"]:
        fpath = opt.join(response["dir"], PRJ_FN)

        try:
            """if procedure == 'search' and ins_to == 'sys.path':
            try: sys.path.remove(opt.realpath(path))
            except ValueError: pass"""

            project = implement_prj_file(
                fpath,
                ins_to=ins_to,
                build=build_bool,
                replace_null_srcDirs=replace_null_srcDirs,
            )

        except AlreadyImplemented as e:
            project = e.prj
            if build_bool and build != "if_not_implemented":
                project.build()

        return project

    else:
        if ins_to is not None:
            insert_paths([response["dir"]], ins_to=ins_to)

        return response["dir"]
