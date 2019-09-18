from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks import commands

from nornsible import InitNornsible, nornsible_task


@nornsible_task
def my_custom_task_1(task):
    task.run(task=commands.command, command="echo 'hello, world!'")


"""
MOAR CUSTOM TASKS MAYBE?!
"""


@nornsible_task
def my_custom_task_10(task):
    task.run(task=commands.command, command="echo 'hello, from task 10!'")


def main():
    nr = InitNornir(config_file="config.yaml")
    nr = InitNornsible(nr)
    print(nr.config.core.num_workers)
    agg_result = nr.run(task=my_custom_task_1)
    print_result(agg_result)
    agg_result = nr.run(task=my_custom_task_10)
    print_result(agg_result)


if __name__ == "__main__":
    main()
