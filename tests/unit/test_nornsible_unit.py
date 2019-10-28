import sys
from pathlib import Path
from unittest.mock import patch

from nornir import InitNornir
from nornir.core.task import AggregatedResult, MultiResult, Result

import nornsible
from nornsible import (
    InitNornsible,
    nornsible_task_message,
    parse_cli_args,
    patch_config,
    patch_inventory,
    print_result,
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
        "--disable-delegate",
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
        },
        logging={"enabled": False},
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    print(nr.inventory.hosts.keys())
    assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_patch_inventory_limit_host_ignore_case():
    args = ["-l", "UPPER-HOST"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        },
        logging={"enabled": False},
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == {"UPPER-HOST"}


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
        },
        logging={"enabled": False},
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == {"sea-eos-1"}


def test_patch_inventory_limit_group_ignore_case():
    args = ["-g", "UPPER"]
    args = parse_cli_args(args)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
            },
        },
        logging={"enabled": False},
    )
    nr.inventory = patch_inventory(args, nr.inventory)
    assert set(nr.inventory.hosts.keys()) == {"UPPER-HOST"}


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
        },
        logging={"enabled": False},
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
        },
        logging={"enabled": False},
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
        },
        logging={"enabled": False},
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
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"delegate", "sea-eos-1"}


def test_set_nornsible_limit_host_disable_delegate():
    testargs = ["somescript", "-l", "sea-eos-1", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            },
            logging={"enabled": False},
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
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"delegate", "sea-eos-1"}


def test_set_nornsible_limit_group_disable_delegate():
    testargs = ["somescript", "-g", "eos", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            },
            logging={"enabled": False},
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
            },
            logging={"enabled": False},
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
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"delegate"}


def test_set_nornsible_limithost_invalid_disable_delegate():
    testargs = ["somescript", "-l", "sea-eos-1234", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            },
            logging={"enabled": False},
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
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        assert set(nr.inventory.hosts.keys()) == {"delegate"}


def test_set_nornsible_limit_group_invalid_disable_delegate():
    testargs = ["somescript", "-g", "eos1234", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            },
            logging={"enabled": False},
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
            },
            logging={"enabled": False},
        )
        nornsible_nr = InitNornsible(initial_nr)
        assert nornsible_nr == initial_nr


def test_set_nornsible_do_nothing_disable_delegate():
    testargs = ["somescript", "-d"]
    with patch.object(sys, "argv", testargs):
        initial_nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nornsible_nr = InitNornsible(initial_nr)
        assert nornsible_nr == initial_nr
        assert "delegate" not in nornsible_nr.inventory.hosts.keys()


def test_process_tags_messages(capfd):
    nornsible_task_message("this is a test message")
    std_out, std_err = capfd.readouterr()
    assert "this is a test message" in std_out


def test_nornsible_print_task_no_results():
    test_result = AggregatedResult("testresult")
    test_result["localhost"] = MultiResult("testresult")
    test_result["localhost"].append(
        Result(host="localhost", result="Task skipped", failed=False, changed=False)
    )
    output = print_result(test_result)
    assert output is None


def test_nornsible_print_task_results(capfd):
    test_result = AggregatedResult("testresult")
    test_result["localhost"] = MultiResult("testresult")
    test_result["localhost"].append(
        Result(host="localhost", result="stuff happening!", failed=False, changed=False)
    )
    print_result(test_result)
    std_out, std_err = capfd.readouterr()
    assert "stuff happening" in std_out
