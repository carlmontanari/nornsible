# Nornsible Example

This directory contains a hosts, groups, and config file for Nornir. All of the hosts are simply set to use 127.0.0.1 as a hostname so you should be able to test nornsible out using these files quite easily! Ensure you've installed nornsible and the requirements.txt file before proceeding.


## Executing Normally

Without nornsible the two custom tasks execute against all three hosts (sea-eos-1, sea-nxos-1, and localhost) as you'd expect, nice and easy Nornir stuff.


## Limit Workers

```
$ python try_me.py -w 1
1
[SNIP]
```


## Limit Host(s)

```
$ python try_me.py -l sea-eos-1
my_custom_task_1****************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_1 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
---- command ** changed : False ------------------------------------------------ INFO
hello, world!

hello, world!

^^^^ END my_custom_task_1 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
my_custom_task_10***************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_10 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
---- command ** changed : False ------------------------------------------------ INFO
hello, from task 10!

hello, from task 10!

^^^^ END my_custom_task_10 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

## Limit host(s) and task(s)

```
$ python try_me.py -l sea-eos-1 -t custom_task_1
---- sea-eos-1 skipping task my_custom_task_1 ----------------------------------
my_custom_task_1****************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_1 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Task skipped!
^^^^ END my_custom_task_1 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
---- sea-eos-1 skipping task my_custom_task_10 ---------------------------------
my_custom_task_10***************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_10 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Task skipped!
^^^^ END my_custom_task_10 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

## Limit host(s) and skip task(s)

```
$ python try_me.py -l sea-eos-1 -s my_custom_task_1
20
---- sea-eos-1 skipping task my_custom_task_1 ----------------------------------
my_custom_task_1****************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_1 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Task skipped!
^^^^ END my_custom_task_1 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
my_custom_task_10***************************************************************
* sea-eos-1 ** changed : False *************************************************
vvvv my_custom_task_10 ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
---- command ** changed : False ------------------------------------------------ INFO
hello, from task 10!

hello, from task 10!

^^^^ END my_custom_task_10 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```
