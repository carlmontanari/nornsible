import argparse
from typing import List


def parse_cli_args(raw_args: List[str]) -> dict:
    """
    Parse CLI provided arguments; ignore unrecognized.

    Arguments:
        raw_args: List of CLI provided arguments

    Returns:
        cli_args: Processed CLI arguments

    Raises:
        N/A  # noqa

    """
    parser = argparse.ArgumentParser(description="Nornir Script Wrapper")
    parser.add_argument(
        "-w",
        "--workers",
        help="number of workers to set for global configuration",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-l",
        "--limit",
        help="limit to host or comma separated list of hosts",
        type=str.lower,
        default="",
    )
    parser.add_argument(
        "-g",
        "--groups",
        help="limit to group or comma separated list of groups",
        type=str.lower,
        default="",
    )
    parser.add_argument(
        "-t", "--tags", help="names of tasks to explicitly run", type=str.lower, default=""
    )
    parser.add_argument("-s", "--skip", help="names of tasks to skip", type=str.lower, default="")
    parser.add_argument(
        "-d", "--disable-delegate", help="disable adding delegate host", action="store_true"
    )
    args, _ = parser.parse_known_args(raw_args)
    cli_args = {
        "workers": args.workers if args.workers else False,
        "limit": set(args.limit.split(",")) if args.limit else False,
        "groups": set(args.groups.split(",")) if args.groups else False,
        "run_tags": set(args.tags.split(",")) if args.tags else [],
        "skip_tags": set(args.skip.split(",")) if args.skip else [],
        "disable_delegate": args.disable_delegate,
    }
    return cli_args
