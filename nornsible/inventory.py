import configparser as cp
from collections import defaultdict
from copy import deepcopy
import json
from json.decoder import JSONDecodeError
import logging
import os
from pathlib import Path
import subprocess
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    MutableMapping,
    Tuple,
)

from nornir.core.deserializer.inventory import Inventory

# Support Nornir 2.2.0 -> 2.3.0
try:
    from nornir.core.exceptions import NornirNoValidInventoryError
except ImportError:

    class NornirNoValidInventoryError(Exception):  # type: ignore
        pass


from nornir.plugins.inventory.ansible import (
    AnsibleParser,
    INIParser,
    YAMLParser,
    VARS_FILENAME_EXTENSIONS,
)
from ruamel.yaml.composer import ComposerError
from ruamel.yaml.scanner import ScannerError

NORNIR_LOGGER = logging.getLogger("nornir")
VARS_FILENAME_EXTENSIONS.append(".py")


class ScriptParser(AnsibleParser):
    def verify_file(self) -> bool:
        with open(self.hostsfile, "rb") as inv_file:
            initial_chars = inv_file.read(2)
            if initial_chars.startswith(b"#!") and os.access(self.hostsfile, os.X_OK):
                return True
        return False

    def load_hosts_file(self) -> None:
        if not self.verify_file():
            raise TypeError(f"AnsibleInventory: invalid script file {self.hostsfile}")

        proc = subprocess.Popen(
            [self.hostsfile, "--list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        std_out, std_err = proc.communicate()

        if proc.returncode != 0:
            raise OSError(f"AnsibleInventory: {self.hostsfile} exited with non-zero return code")

        processed = json.loads(std_out.decode())
        self.original_data = self.normalize(processed)

    @staticmethod
    def normalize(data: Dict[str, Any]) -> Dict[str, Any]:
        groups: DefaultDict[str, Dict[str, Any]] = defaultdict(dict)
        result: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {"all": {"children": groups}}

        # hostvars are stored in ["_meta"]["hostvars"] if present
        hostvars = data.get("_meta", {}).get("hostvars", None)

        if "all" in data.keys():
            data = data["all"]
        if "vars" in data.keys():
            groups["defaults"]["vars"] = data.pop("vars")

        for group, gdata in data.items():
            if "vars" in gdata.keys():
                groups[group]["vars"] = gdata["vars"]
            if "children" in gdata.keys():
                groups[group]["children"] = {}
                for child in gdata["children"]:
                    groups[group]["children"][child] = {}
            if "hosts" in gdata.keys():
                groups[group]["hosts"] = {}
                for host in gdata["hosts"]:
                    groups[group]["hosts"][host] = hostvars.get(host, None)
        return result


class AnsibleInventory(Inventory):
    def __init__(self, inventory: str = "", hash_behavior: str = "replace", **kwargs: Any,) -> None:
        """
        Ansible Inventory plugin supporting ini, yaml, and dynamic inventory sources.

        Arguments:
            inventory: Comma separated list of valid Ansible inventory sources
            hash_behavior: Determines behavior of how duplicate dicts vars in inventory are handled.
                With 'replace' (default), highest priority (first file parsed) dicts are retained
                and subsequent dicts ignored. With 'merge', subsequent dicts are merged into any
                higher priority dicts in inventory. This is intended to duplicate Ansible
                "hash_behaviour" setting.
            **kwargs: keyword arguments to pas to super

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        if hash_behavior.lower() not in ("replace", "merge"):
            raise ValueError(
                f"'hash_behavior' value {hash_behavior} is invalid, must be replace|merge"
            )
        hosts, groups, defaults = self.parse(inventory, hash_behavior)
        super().__init__(hosts=hosts, groups=groups, defaults=defaults, **kwargs)

    def combine_inventory(
        self, inventory_one: Dict[str, Any], inventory_two: Dict[str, Any], hash_behavior: str
    ) -> Dict[str, Any]:
        """
        Parent method for combining inventory based on hash_behavior

        Arguments:
            inventory_one: TODO
            inventory_two: TODO
            hash_behavior: see init method

        Returns:
            inventory_update: updated inventory based on hash_behavior

        Raises:
            N/A  # noqa

        """
        if hash_behavior == "merge":
            return self._merge_inventory(inventory_one, inventory_two)
        return self._replace_inventory(inventory_one, inventory_two)

    def _merge_inventory(
        self, inventory_one: Dict[str, Any], inventory_two: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge inventory data

        Arguments:
            inventory_one: TODO
            inventory_two: TODO

        Returns:
            inventory_update: updated inventory based on hash_behavior

        Raises:
            N/A  # noqa

        """
        # if inventory_one is empty or inventories are equal, return copy of inventory_two
        if not inventory_one or inventory_one == inventory_two:
            return deepcopy(inventory_two)

        # deepcopy original (inventory_one) to new dict (inventory_update)
        inventory_update = deepcopy(inventory_one)

        # iterate through inventory_two k,v
        for k, v in inventory_two.items():
            # if inventory_two k is already in new dict (inventory_update) and the value in both
            # original dicts (inventory_one copy as inventory_update, and inventory_two that we are
            # currently iterating over) is a mapping (dict), create new value as dict of
            # inventory_two value. pass back to this merge method to merge the child dict
            if (
                k in inventory_update.keys()
                and isinstance(inventory_update[k], MutableMapping)
                and isinstance(v, MutableMapping)
            ):
                updated_value: Dict[str, Any] = dict(v)
                inventory_update[k] = self._merge_inventory(inventory_update[k], updated_value)
            # otherwise, simply assign value to key in new dict (inventory_update)
            else:
                inventory_update[k] = v
        return inventory_update

    @staticmethod
    def _replace_inventory(
        inventory_one: Dict[str, Any], inventory_two: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace inventory data

        Arguments:
            inventory_one: TODO
            inventory_two: TODO

        Returns:
            inventory_update: updated inventory based on hash_behavior

        Raises:
            N/A  # noqa

        """
        # deepcopy original (inventory_one) to new dict (inventory_update)
        inventory_update = deepcopy(inventory_one)
        # update new dict (inventory_update) w/ inventory_two
        inventory_update.update(inventory_two)
        return inventory_update

    @staticmethod
    def _gather_possible_inventory_sources(inventory: str) -> List[str]:
        possible_sources: List[str] = []
        inventory_locations = inventory.split(",")

        for location in inventory_locations:
            inv: Path = Path(location).expanduser()
            if inv.is_dir():
                files = Path(location).glob("*")
                possible_sources.extend(
                    [
                        str(f.resolve())
                        for f in files
                        if f.suffix in VARS_FILENAME_EXTENSIONS and not f.is_dir()
                    ]
                )
            elif inv.is_file():
                possible_sources.append(str(inv.resolve()))
        return possible_sources

    @staticmethod
    def _gather_valid_inventory_sources(possible_sources: List[str]) -> List[AnsibleParser]:
        valid_sources: List[AnsibleParser] = []
        for possible_source in possible_sources:
            try:
                parser: AnsibleParser = INIParser(possible_source)
                valid_sources.append(parser)
                continue
            except cp.Error:
                NORNIR_LOGGER.info(
                    "AnsibleInventory: file %r is not INI file, moving to next parser...",
                    possible_source,
                )
            try:
                parser = YAMLParser(possible_source)
                valid_sources.append(parser)
                continue
            except (ScannerError, ComposerError):
                NORNIR_LOGGER.info(
                    "AnsibleInventory: file %r is not YAML file, moving to next parser...",
                    possible_source,
                )
            try:
                parser = ScriptParser(possible_source)
                valid_sources.append(parser)
                continue
            except (TypeError, OSError, JSONDecodeError) as e:
                NORNIR_LOGGER.info(
                    "AnsibleInventory: file %r is not executable Python file. "
                    "Error: %r no more parsers to try...",
                    possible_source,
                    e,
                )
        return valid_sources

    def parse(
        self, inventory: str, hash_behavior: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Merge inventory data

        Arguments:
            inventory: Comma separated list of valid Ansible inventory sources
            hash_behavior: see init method

        Returns:
            hosts: dict of all hosts parsed in inventory source(s)
            groups: dict of all groups parsed in inventory source(s)
            defaults: dict of all defaults parsed in inventory source(s)

        Raises:
            NornirNoValidInventoryError: if no valid inventory sources to parse

        """
        possible_sources: List = self._gather_possible_inventory_sources(inventory)
        valid_sources: List[AnsibleParser] = self._gather_valid_inventory_sources(possible_sources)

        if not valid_sources:
            raise NornirNoValidInventoryError(
                f"AnsibleInventory: no valid inventory source(s). Tried: {possible_sources}"
            )

        hosts: Dict[str, Any] = {}
        groups: Dict[str, Any] = {}
        defaults: Dict[str, Any] = {}

        for source in valid_sources:
            source.parse()
            hosts = self.combine_inventory(hosts, source.hosts, hash_behavior)
            groups = self.combine_inventory(groups, source.groups, hash_behavior)
            defaults = self.combine_inventory(defaults, source.defaults, hash_behavior)

        return hosts, groups, defaults
