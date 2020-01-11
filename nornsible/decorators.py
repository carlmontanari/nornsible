import threading
from typing import Dict, List, Any, Union, Callable, Optional

from colorama import Back, Fore, init, Style
from nornir.core.task import Result, Task


init(autoreset=True, strip=False)
LOCK = threading.Lock()


def nornsible_task_message(msg: str, critical: Optional[bool] = False) -> None:
    """
    Handle printing pretty messages for nornsible_task decorator

    Args:
        msg: message to beautifully print to stdout
        critical: (optional) message is critical

    Returns:
         N/A

    Raises:
        N/A  # noqa

    """
    if critical:
        back = Back.RED
        fore = Fore.WHITE
    else:
        back = Back.CYAN
        fore = Fore.WHITE

    LOCK.acquire()
    try:
        print(f"{Style.BRIGHT}{back}{fore}{msg}{'-' * (80 - len(msg))}")
    finally:
        LOCK.release()


def nornsible_task(wrapped_func: Callable) -> Callable:
    """
    Decorate an "operation" -- execute or skip the operation based on tags

    Args:
        wrapped_func: function to wrap in tag processor

    Returns:
        tag_wrapper: wrapped function

    Raises:
        N/A  # noqa

    """

    def tag_wrapper(
        task: Task, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> Union[Callable, Result]:
        if task.host.name == "delegate":
            return Result(
                host=task.host, result="Task skipped, delegate host!", failed=False, changed=False
            )
        if {wrapped_func.__name__}.intersection(task.nornir.skip_tags):
            msg = f"---- {task.host} skipping task {wrapped_func.__name__} "
            nornsible_task_message(msg)
            return Result(host=task.host, result="Task skipped!", failed=False, changed=False)
        if not task.nornir.run_tags:
            return wrapped_func(task, *args, **kwargs)
        if {wrapped_func.__name__}.intersection(task.nornir.run_tags):
            return wrapped_func(task, *args, **kwargs)
        msg = f"---- {task.host} skipping task {wrapped_func.__name__} "
        nornsible_task_message(msg)
        return Result(host=task.host, result="Task skipped!", failed=False, changed=False)

    tag_wrapper.__name__ = wrapped_func.__name__
    return tag_wrapper


def nornsible_delegate(wrapped_func: Callable) -> Callable:
    """
    Decorate an "operation" -- execute only on "delegate" (localhost)

    Args:
        wrapped_func: function to wrap in delegate_wrapper

    Returns:
        tag_wrapper: wrapped function

    Raises:
        N/A  # noqa

    """

    def delegate_wrapper(
        task: Task, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> Union[Callable, Result]:
        if "delegate" not in task.nornir.inventory.hosts.keys():
            msg = f"---- WARNING no delegate available for task {wrapped_func.__name__} "
            nornsible_task_message(msg, critical=True)
            return Result(
                host=task.host, result="Task skipped, delegate host!", failed=False, changed=False
            )
        if task.host.name != "delegate":
            return Result(
                host=task.host,
                result="Task skipped, non-delegate host!",
                failed=False,
                changed=False,
            )
        return wrapped_func(task, *args, **kwargs)

    delegate_wrapper.__name__ = wrapped_func.__name__
    return delegate_wrapper
