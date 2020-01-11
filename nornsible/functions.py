import logging
import threading
from typing import List, Optional

from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir.plugins.functions.text import _print_result


LOCK = threading.Lock()


def print_result(
    result: Result,
    host: Optional[str] = None,
    nr_vars: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
) -> None:
    updated_agg_result = AggregatedResult(result.name)
    for hostname, multi_result in result.items():
        updated_multi_result = MultiResult(result.name)
        for r in multi_result:
            if isinstance(r.result, str) and r.result.startswith("Task skipped"):
                continue
            updated_multi_result.append(r)
        if updated_multi_result:
            updated_agg_result[hostname] = updated_multi_result  # noqa

    if not updated_agg_result:
        return

    LOCK.acquire()
    try:
        _print_result(updated_agg_result, host, nr_vars, failed, severity_level)
    finally:
        LOCK.release()
