import sys

from nornir.core import Nornir, Config, Inventory
from nornir.core.inventory import Host

from nornsible.cli import parse_cli_args


def patch_inventory(cli_args: dict, inv: Inventory) -> Inventory:
    """
    Patch nornir inventory configurations per cli arguments.

    Arguments:
        cli_args: Updates from CLI to update in Nornir objects
        inv: nornir.core.inventory.Inventory object; Initialized Nornir Inventory object

    Returns:
        inv: nornir.core.inventory.Inventory object; Updated Nornir Inventory object

    Raises:
        N/A  # noqa

    """
    if cli_args["limit"]:
        lower_hosts = [h.lower() for h in inv.hosts.keys()]
        valid_hosts = []
        invalid_hosts = []
        for host in cli_args["limit"]:
            if host in lower_hosts:
                valid_hosts.append(host)
            else:
                invalid_hosts.append(host)
        if invalid_hosts:
            print(f"Host limit contained invalid host(s), ignoring: {invalid_hosts}")
        inv = inv.filter(filter_func=lambda h: h.name.lower() in valid_hosts)

    elif cli_args["groups"]:
        lower_groups = [g.lower() for g in inv.groups.keys()]
        valid_groups = [g for g in cli_args["groups"] if g in lower_groups]
        invalid_groups = [g for g in cli_args["groups"] if g not in lower_groups]
        if invalid_groups:
            print(f"Group limit contained invalid group(s), ignoring: {invalid_groups}")
        inv = inv.filter(
            filter_func=lambda h: any(
                True for g in valid_groups for hg in h.groups if g == hg.lower()
            )
        )

    return inv


def patch_inventory_delegate(inv: Inventory) -> Inventory:
    """
    Patch nornir inventory configurations per cli arguments.

    Arguments:
        inv: nornir.core.inventory.Inventory object; Initialized Nornir Inventory object

    Returns:
        inv: nornir.core.inventory.Inventory object; Updated Nornir Inventory object

    Raises:
        N/A  # noqa

    """
    inv.hosts["delegate"] = Host(name="delegate")

    return inv


def patch_config(cli_args: dict, conf: Config) -> Config:
    """
    Patch nornir core configurations per cli arguments.

    Arguments:
        cli_args: Updates from CLI to update in Nornir objects
        conf: nornir.core.configuration.Config object; Initialized Nornir Config object

    Returns:
        conf: nornir.core.configuration.Config object; Updated Nornir Config object

    Raises:
        N/A  # noqa

    """
    if cli_args["workers"]:
        conf.core.num_workers = cli_args["workers"]

    return conf


def InitNornsible(nr: Nornir) -> Nornir:
    """
    Patch nornir object based on cli arguments

    Arguments:
        nr: Nornir object

    Returns:
        nr: Nornir object; modified if cli args dictate the need to do so; otherwise passed as is

    Raises:
        N/A  # noqa

    """
    cli_args = parse_cli_args(sys.argv[1:])

    nr.run_tags = cli_args.pop("run_tags")
    nr.skip_tags = cli_args.pop("skip_tags")

    if any(a for a in cli_args.values()):
        nr.config = patch_config(cli_args, nr.config)
        nr.inventory = patch_inventory(cli_args, nr.inventory)

    if not cli_args["disable_delegate"]:
        nr.inventory = patch_inventory_delegate(nr.inventory)

    return nr
