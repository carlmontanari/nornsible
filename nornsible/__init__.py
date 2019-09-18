"""nornir tag and host/group limit wrapper"""
import logging
from logging import NullHandler

from nornsible.nornsible import (
    InitNornsible,
    parse_cli_args,
    nornsible_task,
    patch_config,
    patch_inventory,
    nornsible_task_message,
)


__version__ = "2019.09.17"
__all__ = (
    "InitNornsible",
    "parse_cli_args",
    "nornsible_task",
    "patch_config",
    "patch_inventory",
    "nornsible_task_message",
)


# Setup logger
session_log = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(NullHandler())
