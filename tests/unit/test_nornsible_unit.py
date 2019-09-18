from pathlib import Path
import sys
import threading
from unittest.mock import patch

from nornir import InitNornir

import nornsible
from nornsible import (
    InitNornsible,
    parse_cli_args,
    patch_config,
    patch_inventory,
    nornsible_task_message,
)


NORNSIBLE_DIR = nornsible.__file__
TEST_DIR = f"{Path(NORNSIBLE_DIR).parents[1]}/tests/"


def test_parse_cli_args_basic_short():
    args = [
        "-l",
        "sea-eos-1",
        "-g",
        "sea",
        "-s",
        "deploy_configs",
        "-t",
        "render_configs",
        "-w",
        "10",
    ]
    args = parse_cli_args(args)
    assert args["limit"] == {"sea-eos-1"}
    assert args["groups"] == {"sea"}
    assert args["skip_tags"] == {"deploy_configs"}
    assert args["run_tags"] == {"render_configs"}
    assert args["workers"] == 10


def test_parse_cli_args_basic_long():
    args = [
        "--limit",
        "sea-eos-1",
        "--groups",
        "sea",
        "--skip",
        "deploy_configs",
        "--tags",
        "render_configs",
        "--workers",
        "10",
    ]
    args = parse_cli_args(args)
    assert args["limit"] == {"sea-eos-1"}
    assert args["groups"] == {"sea"}
    assert args["skip_tags"] == {"deploy_configs"}
    assert args["run_tags"] == {"render_configs"}
    assert args["workers"] == 10


def test_parse_cli_args_basic_none():
    args = ["somethingelse", "notrelevant"]
    args = parse_cli_args(args)
    assert args["limit"] is False
    assert args["groups"] is False
    assert args["skip_tags"] == []
    assert args["run_tags"] == []
    assert args["workers"] is False


def test_patch_inventory_basic_limit_host():
    args = ["-l", "sea-eos-1"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        }
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_patch_inventory_basic_limit_group():
    args = ["-g", "eos"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        }
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_patch_config_basic_limit_workers():
    args = ["-w", "10"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        }
    )
    nr.config = patch_config(args, nr.config)
    assert nr.config.core.num_workers == 10


def test_patch_inventory_basic_limit_host_invalid():
    args = ["-l", "sea-1234"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        }
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == set()


def test_patch_inventory_basic_limit_group_invalid():
    args = ["-g", "eos1234"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        }
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == set()


def test_set_nornsible_limit_host():
    testargs = ["somescript", "-l", "sea-eos-1"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_set_nornsible_limit_group():
    testargs = ["somescript", "-g", "eos"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_set_nornsible_workers():
    testargs = ["somescript", "-w", "10"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nr = InitNornsible(nr)
        assert nr.config.core.num_workers == 10


def test_set_nornsible_limithost_invalid():
    testargs = ["somescript", "-l", "sea-eos-1234"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == set()


def test_set_nornsible_limit_group_invalid():
    testargs = ["somescript", "-g", "eos1234"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == set()


def test_set_nornsible_do_nothing():
    testargs = ["somescript"]
    with patch.object(sys, "argv", testargs):
        initial_nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            }
        )
        nornsible_nr = InitNornsible(initial_nr)
        assert nornsible_nr == initial_nr


def test_process_tags_messages(capfd):
    nornsible_task_message("this is a test message")
    std_out, std_err = capfd.readouterr()
    assert "this is a test message" in std_out
