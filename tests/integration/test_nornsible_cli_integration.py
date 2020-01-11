from pathlib import Path
import sys
from unittest.mock import patch

from nornir import InitNornir

import nornsible
from nornsible import InitNornsible, nornsible_delegate, nornsible_task


NORNSIBLE_DIR = nornsible.__file__
TEST_DIR = f"{Path(NORNSIBLE_DIR).parents[1]}/tests/"


@nornsible_task
def custom_task_example(task):
    return "Hello, world!"


@nornsible_task
def custom_task_example_2(task):
    return "Hello, world!"


@nornsible_delegate
def custom_task_example_3(task):
    return "Hello, world!"


def test_nornsible_task_skip_task():
    testargs = ["somescript", "-l", "localhost", "-s", "custom_task_example"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        task_result = nr.run(task=custom_task_example)
        assert set(task_result.keys()) == {"delegate", "localhost"}
        assert task_result["localhost"].result == "Task skipped!"
        assert task_result["delegate"].result == "Task skipped, delegate host!"


def test_nornsible_task_skip_task_disable_delegate():
    testargs = ["somescript", "-l", "localhost", "-s", "custom_task_example", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        task_result = nr.run(task=custom_task_example)
        assert set(task_result.keys()) == {"localhost"}
        assert task_result["localhost"].result == "Task skipped!"


def test_nornsible_task_explicit_task():
    testargs = ["somescript", "-l", "localhost", "-t", "custom_task_example_2"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        print(nr.inventory.hosts)
        tasks = [custom_task_example, custom_task_example_2]
        task_results = []
        for task in tasks:
            task_results.append(nr.run(task=task))

        assert task_results[0]["localhost"].result == "Task skipped!"
        assert task_results[1]["localhost"].result == "Hello, world!"
        assert task_results[0]["delegate"].result == "Task skipped, delegate host!"
        assert task_results[1]["delegate"].result == "Task skipped, delegate host!"


def test_nornsible_task_no_tags():
    testargs = ["somescript", "-l", "localhost"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        print(nr.inventory.hosts)
        tasks = [custom_task_example, custom_task_example_2]
        task_results = []
        for task in tasks:
            task_results.append(nr.run(task=task))

        assert task_results[0]["localhost"].result == "Hello, world!"
        assert task_results[1]["localhost"].result == "Hello, world!"


def test_nornsible_delegate():
    testargs = ["somescript", "-l", "localhost"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        print(nr.inventory.hosts)
        tasks = [custom_task_example_3]
        task_results = []
        for task in tasks:
            task_results.append(nr.run(task=task))

        assert task_results[0]["localhost"].result == "Task skipped, non-delegate host!"


def test_nornsible_delegate_disable_delegate():
    testargs = ["somescript", "-l", "localhost", "-d"]
    with patch.object(sys, "argv", testargs):
        nr = InitNornir(
            inventory={
                "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                "options": {
                    "host_file": f"{TEST_DIR}_test_nornir_inventory/basic/hosts.yaml",
                    "group_file": f"{TEST_DIR}_test_nornir_inventory/basic/groups.yaml",
                },
            },
            logging={"enabled": False},
        )
        nr = InitNornsible(nr)
        print(nr.inventory.hosts)
        tasks = [custom_task_example_3]
        task_results = []
        for task in tasks:
            task_results.append(nr.run(task=task))

        assert task_results[0]["localhost"].result == "Task skipped, delegate host!"
