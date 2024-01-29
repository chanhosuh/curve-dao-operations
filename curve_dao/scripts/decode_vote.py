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

console = RichConsole(file=sys.stdout)


@click.command(
    cls=NetworkBoundCommand,
    short_help="Decode Curve DAO proposal by Vote Type and ID",
)
@network_option()
@click.option(
    "--type",
    "-t",
    "_type",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--id", "-i", "_id", type=int, required=True)
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation (default is False)",
)
def cli(network, _type: str, _id: int, simulate: bool):
    console.log(f"Decoding {_type.title()} Vote: {_id}")

    try:
        script = get_vote_script(_id, _type)
    except MissingVote:
        console.log(f"[red] VoteID not found in the {_type} DAO voting contract [/red]")
        return

    description = get_description_from_vote_id(_id, _type)
    console.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        console.log(formatted_output)

    data = get_vote_data(_id, _type)
    results = decode_vote_data(data, _type)
    console.log(results["formatted_output"])

    if simulate:
        voting_contract = get_dao_voting_contract(_type)
        simulate_vote(_id, voting_contract)
