import pprint
import sys

import boa
from rich.console import Console as RichConsole

from curve_dao.contract import get_contract

from .addresses import CONVEX_VOTERPROXY

console = RichConsole(file=sys.stdout)


def simulate_vote(vote_id: int, voting_contract: str, debug=False):
    """Simulate passing vote on mainnet-fork"""
    console.log("--------- SIMULATE VOTE ---------")

    # aragon = ape.project.Voting.at(voting_contract)
    aragon, _ = get_contract(voting_contract)
    boa.env.set_balance(CONVEX_VOTERPROXY, 10 * 10**18)

    if debug:
        console.log("Vote stats before Convex Vote:")
        vote_stats = aragon.getVote(vote_id)
        console.log(pprint.pformat(vote_stats, indent=4))

    # vote
    console.log("Simulate Convex 'yes' vote")
    with boa.env.prank(CONVEX_VOTERPROXY):
        aragon.vote(vote_id, True, False)

    # sleep for a week so it has time to pass
    num_seconds = aragon.voteTime()
    boa.env.time_travel(seconds=num_seconds)

    if debug:
        console.log("Vote stats after 1 week:")
        vote_stats = aragon.getVote(vote_id)
        console.log(pprint.pformat(vote_stats, indent=4))

    # moment of truth - execute the vote!
    console.log("Simulate proposal execution")
    with boa.env.prank(CONVEX_VOTERPROXY):
        tx = aragon.executeVote(vote_id)
    console.log("Vote Executed!")

    # Return the transaction.
    # This lets us search event logs and assert things.
    return tx
