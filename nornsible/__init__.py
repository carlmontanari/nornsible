"""nornir tag and host/group limit wrapper"""
import logging
from logging import NullHandler

from nornsible.nornsible import (
    Init_Nornsible,
    parse_cli_args,
    process_tags,
    patch_config,
    patch_inventory,
)


__version__ = "2019.09.16"
__all__ = ("Init_Nornsible", "parse_cli_args", "process_tags", "patch_config", "patch_inventory")


# Setup logger
session_log = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(NullHandler())
