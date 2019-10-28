"""nornir tag and host/group limit wrapper"""
import logging
from logging import NullHandler

from nornsible.nornsible import (
    InitNornsible,
    nornsible_delegate,
    nornsible_task,
    nornsible_task_message,
    patch_inventory,
    parse_cli_args,
    patch_config,
    print_result,
)


__version__ = "2019.10.28"
__all__ = (
    "InitNornsible",
    "nornsible_delegate",
    "nornsible_task",
    "nornsible_task_message",
    "patch_inventory",
    "parse_cli_args",
    "patch_config",
    "print_result",
)


# Setup logger
session_log = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(NullHandler())
