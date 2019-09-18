![](https://github.com/carlmontanari/nornsible/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/nornsible.svg)](https://badge.fury.io/py/nornsible)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

nornsible
=======

Wrap Nornir with Ansible-like host/group limits and tagging!

The idea behind nornsible is to allow for Nornir scripts to be written to operate on an entire environment, and then limited to a subset of host(s) based on simple command line arguments. Of course you can simply do this yourself, but why not let nornsible handle it for you!

Nornsible provides the ability to -- via command line arguments -- filter Nornir inventories by hostname or group name, or both. There is also a handy flag to set the number of workers; quite useful for setting workers equal to 1 for troubleshooting purposes.

Lastly, nornsible supports the concept of tags. Tags correspond to the name of *custom* tasks and operate very much like tags in Ansible. Provide a list of tags to execute, and Nornsible will ensure that Nornir only runs those tasks. Provide a list of tags to skip, and Nornsible will ensure that Nornir only runs those not in that list. Easy peasy.


# How does nornsible work?

Nornsible accepts an instantiated Nornir object as an argument and returns a slightly modified Nornir object. Nornsible sets the desired number of workers if applicable, and adds an attribute for "run_tags" and "skip_tags" based on your command line input.

To take advantage of the tags feature Nornsible provides a decorator that you can use to wrap your custom tasks. This decorator inspects the task being ran and checks the task name against the lists of run and skip tags. If the task is allowed, Nornsible simply allows the task to run as per normal, if it is *not* allowed, Nornsible will print a pretty message and move on.


# Caveats

Nornsible breaks some things! Most notably it breaks "normal" Nornir filtering *after* the Nornir object is "nornsible-ified". This can probably be fixed but at the moment it doesn't seem like that big a deal, so I'm not bothering!

If you want to do "normal" Nornir filtering -- do this *before* passing the nornir object to Nornsible.

Nornsible, at the moment, can only wrap custom tasks. This can probably be improved upon as well, but at the moment the decorator wrapping custom tasks solution seems to work pretty well.


# Installation

Installation via pip:

```
pip install nornsible
```

To install from this repository:

```
pip install git+https://github.com/carlmontanari/nornsible
```

To install from source:

```
git clone https://github.com/carlmontanari/nornsible
cd nornsible
python setup.py install
```


# Usage

Import stuff:

```
from nornsible import InitNornsible, nornsible_task
```

Decorate custom tasks with `nornsible_task` if desired:

```
@nornsible_task
def my_custom_task(task):
```

Create your Nornir object and then pass it through InitNornsible:

```
nr = InitNornir(config_file="config.yaml")
nr = InitNornsible(nr)
```

Run a custom task wrapped by `nornsible_task`:

```
nr.run(task=my_custom_task)
```

Run your script with any of the following command line switches:

| Purpose          | Short Flag    | Long Flag  | Allowed Options
| -----------------|---------------|------------|-------------------|
| set num_workers  | -w            | --workers  | integer           |
| limit host(s)    | -l            | --limit    | comma sep string  |
| limit group(s)   | -g            | --groups   | comma sep string  |
| run tag(s)       | -t            | --tags     | comma sep string  |
| skip tag(s)      | -s            | --skip     | comma sep string  |

To set number of workers to 1 for troubleshooting purposes:

```
python my_nornir_script.py -w 1
```

To limit to the "sea" group (from your Nornir inventory):

```
python my_nornir_script.py -g sea
```

To run only the tasks named "create_configs" and "deploy_configs" (assuming you've wrapped all of your tasks with `nornsible_task`!):

```
python my_nornir_script.py -t create_configs,deploy_configs
```

To run only the tasks named "create_configs" and "deploy_configs" against the "sea-eos-1" host:

```
python my_nornir_script.py -t create_configs,deploy_configs -l sea-eos-1
```


# FAQ

TBA, probably things though!

# Linting and Testing

## Linting

This project uses [black](https://github.com/psf/black) for auto-formatting. In addition to black, tox will execute [pylama](https://github.com/klen/pylama), and [pydocstyle](https://github.com/PyCQA/pydocstyle) for linting purposes. I've also added docstring linting with [darglint](https://github.com/terrencepreilly/darglint) which has been quite handy! Finally, I've been playing with type hints and have added mypy to the test/lint suite as well.

## Testing

I broke testing into two main categories -- unit and integration. Unit is what you would expect -- unit testing the code. Integration testing is for things that test more than one "unit" (generally function) at a time.


# To Do

- Add handling for "not" in host/group limit; i.e.: "-t !localhost" to run against all hosts *not* localhost.
