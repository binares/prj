__version__ = "0.4.0"

from .management import archive, zip_contents
from .prj import (
    Project,
    setup,
    qs,
    get_prj,
    set_delete_sys_path_index,
    _set_log,
    set_logging,
)

from .deprecated import find_paths

__all__ = [
    "archive",
    "zip_contents",
    "Project",
    "setup",
    "qs",
    "get_prj",
    "set_delete_sys_path_index",
]
