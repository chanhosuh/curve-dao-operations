import sys
import warnings

import ape
import click
from ape.exceptions import ChainError
from curve_dao.decoder_utils import decode_input
from curve_dao.ipfs import get_description_from_vote_id
from curve_dao.vote_utils import decode_vote_script, get_vote_script
from rich.console import Console as RichConsole

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)


@click.group(
    short_help="Curve DAO proposal decoder",
)
def cli():
    """
    Command-line helper for managing Smartwallet Checker
    """


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="decode",
    short_help="Decode Curve DAO proposal by Vote ID",
)
@ape.cli.network_option()
@click.option(
    "--vote-type",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--vote-id", "-v", type=int, default=0)
def decode(network, vote_type: str, vote_id: int):

    RICH_CONSOLE.log(f"Decoding {vote_type} VoteID: {vote_id}")

    # get script from voting data:
    script = get_vote_script(vote_id, vote_type)
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return

    description = get_description_from_vote_id(vote_id, vote_type)
    RICH_CONSOLE.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="decode_add_gauge",
    short_help="Decode Curve DAO proposal by Vote ID",
)
@ape.cli.network_option()
def decode_add_gauge(network):
    vote_type = "ownership"
    vote_id = 409

    gauge_type_counts = {}
    gauge_type_addresses = {}
    while vote_id >= 0:
        # get script from voting data:
        script = get_vote_script(vote_id, vote_type)

        if not script:
            RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
            vote_id -= 1
            continue

        try:
            votes = decode_vote_script(script)
        except ChainError as e:
            RICH_CONSOLE.log(e)
            vote_id -= 1
            continue

        for vote in votes:
            if vote["function"] == "add_gauge":
                RICH_CONSOLE.log(f"Decoding {vote_type} VoteID: {vote_id}")
                description = get_description_from_vote_id(vote_id, vote_type)
                RICH_CONSOLE.log(description)

                formatted_output = vote["formatted_output"]
                # RICH_CONSOLE.log(formatted_output)
                gauge_address = vote["inputs"][0][1]
                gauge_type = vote["inputs"][1][1]
                RICH_CONSOLE.log(f"gauge address: {gauge_address}")
                RICH_CONSOLE.log(f"gauge type: {gauge_type}")
                gauge_type_counts[gauge_type] = gauge_type_counts.get(gauge_type, 0) + 1
                gauge_type_addresses.setdefault(gauge_type, []).append(gauge_address)
        vote_id -= 1
        print(gauge_type_counts)
    print(gauge_type_addresses)
