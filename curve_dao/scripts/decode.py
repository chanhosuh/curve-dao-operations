import sys
import warnings

import ape
import click
from ape.cli import NetworkBoundCommand, network_option
from rich.console import Console as RichConsole

from curve_dao.addresses import get_dao_voting_contract
from curve_dao.ipfs import get_description_from_vote_id
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import (
    MissingVote,
    decode_vote_data,
    decode_vote_script,
    get_vote_data,
    get_vote_script,
)

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)


@click.command(
    cls=NetworkBoundCommand,
    short_help="Decode Curve DAO proposal by Vote Type and ID",
)
@network_option()
@click.option(
    "--vote-type",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--vote-id", "-v", type=int, required=True)
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation (default is False)",
)
def cli(network, vote_type: str, vote_id: int, simulate: bool):
    RICH_CONSOLE.log(f"Decoding {vote_type} VoteID: {vote_id}")

    try:
        script = get_vote_script(vote_id, vote_type)
    except MissingVote:
        RICH_CONSOLE.log(
            f"[red] VoteID not found in the {vote_type} DAO voting contract [/red]"
        )
        return

    description = get_description_from_vote_id(vote_id, vote_type)
    RICH_CONSOLE.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)

    data = get_vote_data(vote_id, vote_type)
    results = decode_vote_data(data, vote_type)
    RICH_CONSOLE.log(results["formatted_output"])

    if simulate:
        voting_contract = get_dao_voting_contract(vote_type)
        simulate_vote(vote_id, voting_contract)
