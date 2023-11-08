from prj.prj import _IS_WINDOWS, resolve_path, set_PRJ_FN, set_logging
import os

set_PRJ_FN("_prj.yaml")
set_logging()


if _IS_WINDOWS:
    paths = [
        ["test\\test_mgmt_folder", "$PPATH"],
        ["\\test\\", "$PPATH"],
        ["\\test\\", "$SRCDIR"],
        ["test\\", "$SRCDIR"],
        # '.' # error
    ]
else:
    paths = [
        ["test/username", "$PPATH"],
        # ['', '$PPATH'],
    ]


def test_resolve_path():
    for path, astype in paths:
        print(os.path.isdir(path))
        print(path, astype, resolve_path(path, astype), "\n")


# def test_resolve_path
