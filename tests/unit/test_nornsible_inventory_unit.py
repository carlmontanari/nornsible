from pathlib import Path

import pytest
import ruamel.yaml

import nornsible
from nornsible.inventory import AnsibleInventory, NornirNoValidInventoryError, ScriptParser


NORNSIBLE_DIR = nornsible.__file__
TEST_DIR = f"{Path(NORNSIBLE_DIR).parents[1]}/tests/"


def read(hosts_file, groups_file, defaults_file):
    yml = ruamel.yaml.YAML(typ="safe")
    with open(hosts_file, "r") as f:
        hosts = yml.load(f)
    with open(groups_file, "r") as f:
        groups = yml.load(f)
    with open(defaults_file, "r") as f:
        defaults = yml.load(f)
    return hosts, groups, defaults


def test_no_nornir_valid_inventory_exception():
    #  test import try/except in inventory
    pass


def test_script_parser_verify_file_valid():
    parser = ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py")
    assert parser.hostsfile == f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py"


def test_script_parser_verify_file_invalid_not_executable():
    with pytest.raises(TypeError):
        ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/non_executable.py")


def test_script_parser_verify_file_invalid_no_shebang():
    with pytest.raises(TypeError):
        ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/no_shebang.py")


def test_script_parser_verify_file_invalid_non_zero_exit():
    with pytest.raises(OSError):
        ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/non_zero_exit.py")


def test_script_parser_load_hosts_original_data():
    parser = ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py")
    assert parser.original_data == {
        "all": {
            "children": {
                "defaults": {
                    "vars": {
                        "ansible_connection": "network_cli",
                        "ansible_network_os": "ios",
                        "ansible_python_interpreter": "python",
                        "ansible_ssh_common_args": '-o ProxyCommand="ssh -W %h:%p -p 10000 guest@10.105.152.50"',
                        "env": "staging",
                    }
                },
                "virl": {"vars": {}, "children": {"asa": {}, "ios": {}}, "hosts": {}},
                "asa": {
                    "vars": {
                        "ansible_become": "yes",
                        "ansible_become_method": "enable",
                        "ansible_network_os": "asa",
                        "ansible_persistent_command_timeout": 30,
                        "cisco_asa": True,
                        "network_os": "asa",
                    },
                    "children": {},
                    "hosts": {"asa1": {"ansible_host": "10.255.0.2", "dot1x": True}},
                },
                "ios": {
                    "vars": {"network_os": "ios", "nornir_nos": "ios", "platform": "ios"},
                    "children": {"access": {}, "dist": {}, "routers": {}},
                    "hosts": {},
                },
                "access": {
                    "vars": {},
                    "children": {},
                    "hosts": {"access1": {"ansible_host": "10.255.0.6"}},
                },
                "dist": {
                    "vars": {},
                    "children": {},
                    "hosts": {
                        "dist1": {"ansible_host": "10.255.0.5"},
                        "dist2": {"ansible_host": "10.255.0.11"},
                    },
                },
                "routers": {
                    "vars": {},
                    "children": {},
                    "hosts": {
                        "iosv-1": {"ansible_host": "10.255.0.12"},
                        "iosv-2": {"ansible_host": "10.255.0.13"},
                    },
                },
            }
        }
    }


def test_script_parser_normalize():
    parser = ScriptParser(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py")
    assert isinstance(parser.original_data["all"], dict)
    assert isinstance(parser.original_data["all"]["children"], dict)
    assert "_meta" not in parser.original_data["all"]["children"].keys()
    assert all(
        i in parser.original_data["all"]["children"].keys()
        for i in ["virl", "asa", "ios", "access", "dist", "routers"]
    )


def test_script_parser_normalize_all_in_keys():
    parser = ScriptParser(
        f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success_all_in_keys.py"
    )
    assert isinstance(parser.original_data["all"], dict)
    assert isinstance(parser.original_data["all"]["children"], dict)
    assert "_meta" not in parser.original_data["all"]["children"].keys()
    assert all(
        i in parser.original_data["all"]["children"].keys()
        for i in ["virl", "asa", "ios", "access", "dist", "routers"]
    )


def test_ansible_inventory_invalid_hash():
    with pytest.raises(ValueError):
        AnsibleInventory(f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py", "blah")


def test_ansible_inventory_basic_script():
    hosts_file = f"{TEST_DIR}_test_nornir_inventory/basic_script/expected/hosts.yaml"
    groups_file = f"{TEST_DIR}_test_nornir_inventory/basic_script/expected/groups.yaml"
    defaults_file = f"{TEST_DIR}_test_nornir_inventory/basic_script/expected/defaults.yaml"
    expected_hosts, expected_groups, expected_defaults = read(
        hosts_file, groups_file, defaults_file
    )
    inv = AnsibleInventory.deserialize(
        inventory=f"{TEST_DIR}_test_nornir_inventory/basic_script/source/success.py",
        hash_behavior="merge",
    )
    inv_serialized = AnsibleInventory.serialize(inv).dict()
    assert inv_serialized["hosts"] == expected_hosts
    assert inv_serialized["groups"] == expected_groups
    assert inv_serialized["defaults"] == expected_defaults


@pytest.mark.parametrize("case", ["no_source", "parse_error"])
def test_ansible_inventory_no_valid_inventory(case):
    with pytest.raises(NornirNoValidInventoryError):
        AnsibleInventory(f"{TEST_DIR}_test_nornir_inventory/{case}/")


@pytest.mark.parametrize("case", ["multiple_sources", "multiple_sources_2"])
@pytest.mark.parametrize("hash_behavior", ["replace", "merge"])
def test_inventory_multiple_source(case, hash_behavior):
    hosts_file = f"{TEST_DIR}_test_nornir_inventory/{case}/expected/{hash_behavior}/hosts.yaml"
    groups_file = f"{TEST_DIR}_test_nornir_inventory/{case}/expected/{hash_behavior}/groups.yaml"
    defaults_file = (
        f"{TEST_DIR}_test_nornir_inventory/{case}/expected/{hash_behavior}/defaults.yaml"
    )
    expected_hosts, expected_groups, expected_defaults = read(
        hosts_file, groups_file, defaults_file
    )

    inventory_sources = (
        f"{TEST_DIR}_test_nornir_inventory/{case}/source/source1,"
        f"{TEST_DIR}_test_nornir_inventory/{case}/source/source2"
    )

    inv = AnsibleInventory.deserialize(inventory=inventory_sources, hash_behavior=hash_behavior)
    inv_serialized = AnsibleInventory.serialize(inv).dict()

    assert inv_serialized["hosts"] == expected_hosts
    assert inv_serialized["groups"] == expected_groups
    assert inv_serialized["defaults"] == expected_defaults
