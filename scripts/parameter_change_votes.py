import ape
import click
from ape.api import accounts
from ape.logging import logger

from curve_dao import make_vote, select_target


@click.command(
    cls=ape.cli.NetworkBoundCommand,
    short_help="Change parameters for a pool",
)
@ape.cli.network_option()
@ape.cli.account_option()
def cli(
    network,
    account,
):
    """
    ape run parameter_change_votes --account <account index or alias> --network <network>

    TriCryptoINV
    A: 1707629
    gamma: 11809167828997
    mid_fee: 3000000
    out_fee: 30000000
    fee_gamma: 500000000000000
    new_allowed_extra_profit: 2000000000000
    new_adjustment_step: 490000000000000
    new_ma_time: 1801

    TriCRV
    A: 2700000
    gamma: 1300000000000
    mid_fee: 2999999
    out_fee: 80000000
    fee_gamma: 350000000000000
    new_allowed_extra_profit: 100000000000
    new_adjustment_step: 100000000000
    new_ma_time: 600
    """
    # new
    new_mid_fee = 2000000
    new_out_fee = 4500000
    # same as TriCRV
    future_A = 2700000
    future_gamma = 1300000000000
    future_time = 1692386521 + 10 * 86400
    new_fee_gamma = 350000000000000
    new_allowed_extra_profit = 100000000000
    new_adjustment_step = 100000000000
    new_ma_time = 600

    address = "0x5426178799ee0a0181a89b4f57efddfab49941ec"
    description = "fill this in!"

    print("NETWORK:", network)
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        logger.info("Using test user account")
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    target = select_target("ownership")

    ramp_action = (
        address,
        "ramp_A_gamma",
        future_A,
        future_gamma,
        future_time,
    )

    commit_action = (
        address,
        "commit_new_parameters",
        new_mid_fee,
        new_out_fee,
        new_fee_gamma,
        new_allowed_extra_profit,
        new_adjustment_step,
        new_ma_time,
    )

    tx = make_vote(
        target=target,
        actions=[ramp_action, commit_action],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")
