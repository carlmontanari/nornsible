"""ansible-like inventory utility for nornir"""
import logging
from logging import NullHandler

from nornsible.decorators import nornsible_delegate, nornsible_task

from nornsible.nornsible import InitNornsible
from nornsible.functions import print_result
from nornsible.inventory import AnsibleInventory


__version__ = "2020.01.11"
__all__ = (
    "AnsibleInventory",
    "InitNornsible",
    "nornsible_delegate",
    "nornsible_task",
    "print_result",
)


# Setup logger
session_log = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(NullHandler())
