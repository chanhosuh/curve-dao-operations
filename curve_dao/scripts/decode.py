import os
import sys
import warnings

import boa
import click
from rich.console import Console as RichConsole

from curve_dao.addresses import get_dao_voting_contract
from curve_dao.exceptions import CurveDaoOperationsError
from curve_dao.ipfs import get_description_from_vote_id
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import decode_vote_script, get_vote_script

try:
    WEB3_ALCHEMY_PROJECT_ID = os.environ["WEB3_ALCHEMY_PROJECT_ID"]
except KeyError:
    raise CurveDaoOperationsError("Cannot find WEB3_ALCHEMY_PROJECT_ID in env.")

boa.env.fork(url=f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}")

warnings.filterwarnings("ignore")

console = RichConsole(file=sys.stdout)


@click.command(
    short_help="Decode Curve DAO proposal by Vote Type and ID",
)
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
def cli(vote_type: str, vote_id: int, simulate: bool):

    console.log(f"Decoding {vote_type} VoteID: {vote_id}")

    # get script from voting data:
    script = get_vote_script(vote_id, vote_type)
    if not script:
        console.log("[red] VoteID not found in any DAO voting contract [/red]")
        return

    # FIXME: need to retrieve the event data using web3 or something like that
    # description = get_description_from_vote_id(vote_id, vote_type)
    # console.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        console.log(formatted_output)

    if simulate:
        voting_contract = get_dao_voting_contract(vote_type)
        tx = simulate_vote(vote_id, voting_contract)
        # logs = tx.decode_logs()
        # print(logs)


if __name__ == '__main__':
    cli()
