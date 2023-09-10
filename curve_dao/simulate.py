import pprint

from .addresses import CONVEX_VOTERPROXY

# import ape
# from ape.logging import logger



def simulate_vote(vote_id: int, voting_contract: str):
    """Simulate passing vote on mainnet-fork"""
    logger.info("--------- SIMULATE VOTE ---------")

    # aragon = ape.project.Voting.at(voting_contract)
    aragon = get_contract(voting_contract)
    voter_proxy = ape.accounts[CONVEX_VOTERPROXY]
    voter_proxy.balance += 10 * 10**18

    # print vote details to console first:
    logger.debug("Vote stats before Convex Vote:")
    vote_stats = aragon.getVote(vote_id)
    logger.debug(pprint.pformat(vote_stats, indent=4))

    # vote
    logger.info("Simulate Convex 'yes' vote")
    aragon.vote(vote_id, True, False, sender=voter_proxy)

    # sleep for a week so it has time to pass
    num_seconds = aragon.voteTime()
    ape.chain.mine(deltatime=num_seconds)

    # get vote stats:
    logger.debug("Vote stats after 1 week:")
    vote_stats = aragon.getVote(vote_id)
    logger.debug(pprint.pformat(vote_stats, indent=4))

    # moment of truth - execute the vote!
    logger.info("Simulate proposal execution")
    enacter = voter_proxy
    tx = aragon.executeVote(vote_id, sender=enacter)
    logger.info("Vote Executed!")

    # Return the transaction.
    # This lets us search event logs and assert things.
    return tx
