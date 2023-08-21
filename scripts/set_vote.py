import ape
import click
from ape.api import accounts
from ape.cli.choices import AccountAliasPromptChoice
from ape.cli.options import _account_callback
from ape.logging import logger

from curve_dao import make_vote
from curve_dao.addresses import get_dao_voting_contract
from curve_dao.modules.smartwallet_checker import whitelist_vecrv_lock
from curve_dao.simulate import simulate


# Missing name issue for AccountAliasPromptChoice is not fixed until
# version 0.6.11, see PR: https://github.com/ApeWorX/ape/pull/1486
#
# Our workaround is to just monkey-patch the init as in their fix.
# This also allows us to customize `account_option` a bit.
def __monkey_patch_init__(
    self,
    account_type=None,
    prompt_message=None,
    name="account",
):
    # NOTE: we purposely skip the constructor of `PromptChoice`
    self._account_type = account_type
    self._prompt_message = prompt_message or "Select an account"
    self.name = name


AccountAliasPromptChoice.__init__ = __monkey_patch_init__


def account_option():
    """
    A CLI option that accepts either the account alias or the account number.
    If not given anything, it will prompt the user to select an account.
    """

    return click.option(
        "--account",
        type=AccountAliasPromptChoice(),
        help="Account index or alias",
        callback=_account_callback,
    )


@click.group(short_help="Create a Curve DAO vote")
def cli():
    """Cammand-line helper for creating different DAO votes"""
    pass


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="whitelist",
    short_help="Whitelist proposed contract to lock veCRV",
)
@ape.cli.network_option()
@account_option()
@click.option("--addr", "-a", type=str, required=True)
@click.option("--description", "-d", type=str, required=True)
def whitelist(network, account, addr, description):

    target = get_dao_voting_contract("ownership")
    tx = make_vote(
        target=target,
        actions=[whitelist_vecrv_lock(addr)],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="kill_gauge",
    short_help="Kill or unkill the specified gauge",
)
@ape.cli.network_option()
@account_option()
@click.option("--address", "-a", type=str, required=True, help="Gauge address")
@click.option(
    "--kill",
    "-k",
    is_flag=True,
    default=True,
    show_default=True,
    help="Toggle kill/unkill (default is True/kill)",
)
@click.option(
    "--gauge-type",
    "-t",
    type=click.Choice(["stableswap", "crypto_factory", "tricrypto_ng"]),
    required=True,
)
@click.option("--description", "-d", type=str, required=True)
def kill_gauge(
    network,
    account,
    address,
    kill,
    gauge_type,
    description,
):
    """
    ape run set_vote kill_gauge --address 0x762648808ef8b25c6d92270b1c84ec97df3bed6b --gauge-type crypto_factory -d 'Kill the whatever gauge'  --account test_account --network :mainnet-fork
    """
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    if gauge_type == "crypto_factory":
        kill_action = (
            CRYPTOSWAP_OWNER_PROXY,
            "set_killed",
            address,
            True,
        )
    if gauge_type == "tricrypto_ng":
        kill_action = (
            address,
            "set_killed",
            True,
        )
    if gauge_type == "stableswap":
        kill_action = (
            CURVE_DAO_OWNERSHIP["agent"],
            "set_killed",
            address,
            True,
        )

    target = select_target("ownership")
    tx = make_vote(
        target=target,
        actions=[kill_action],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="change_parameters",
    short_help="Change parameters for a pool",
)
@ape.cli.network_option()
@account_option()
@click.option("--address", "-a", type=str, required=True, help="Pool address")
@click.option(
    "--pool-type",
    "-t",
    type=click.Choice(["stableswap", "crypto_factory", "tricrypto_ng"]),
    required=True,
)
@click.option(
    "--parameter-action",
    "-p",
    type=click.Choice(["ramp", "commit"]),
    required=True,
)
@click.option("--description", "-d", type=str, required=True)
def change_parameters(
    network,
    account,
    address,
    kill,
    pool_type,
    description,
):
    """
    ape run set_vote kill_gauge --address 0x762648808ef8b25c6d92270b1c84ec97df3bed6b --gauge-type crypto_factory -d 'Kill the whatever gauge'  --account test_account --network :mainnet-fork
    """
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    if pool_type == "crypto_factory":
        raise Exception("Not supported yet.")
        ramp_action = (
            CRYPTOSWAP_OWNER_PROXY,
            "ramp_A_gamma",
            address,
            future_A,
            future_gamma,
            future_time,
        )
        parameter_action = (
            CRYPTOSWAP_OWNER_PROXY,
            "commit_new_parameters",
            crypto_factory_pool.address,
            new_mid_fee,
            new_out_fee,
            new_admin_fee,
            new_fee_gamma,
            new_allowed_extra_profit,
            new_adjustment_step,
            new_ma_time,
        )
    if pool_type == "tricrypto_ng":
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
    if pool_type == "stableswap":
        raise Exception("Not supported yet.")

    target = select_target("ownership")
    tx = make_vote(
        target=target,
        actions=[kill_action],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="pegkeeper_debt_ceiling",
    short_help="Set the pegkeeper debt ceiling",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option("--address", "-a", type=str, required=True, help="Pegkeeper address")
@click.option("--ceiling", "-c", type=str, required=True, help="New debt ceiling")
@click.option("--description", "-d", type=str, required=True)
def pegkeeper_debt_ceiling(
    network,
    account,
    address,
    ceiling,
    description,
):
    """
    ape run pegkeeper_debt_ceiling --account <account index or alias> --network <network>
    """

    # Controller factory
    factory_address = "0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC"
    # TUSD peg keeper
    pegkeeper_address = "0x1ef89ed0edd93d1ec09e4c07373f69c49f4dccae"
    # pegkeeper_address = address
    # current debt ceiling: 25000000000000000000000000
    new_debt_ceiling = 1_000_000_000000000000000000
    description = "fill this in!"

    if "mainnet-fork" in network:
        # Override account with a properly setup user
        logger.info("Using test user account")
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    factory = ape.Contract(factory_address)
    current_ceiling = factory.debt_ceiling(pegkeeper_address)
    assert current_ceiling != ceiling, "New debt ceiling is the same as current value"

    target = select_target("ownership")

    set_ceiling_action = (
        factory_address,
        "set_debt_ceiling",
        pegkeeper_address,
        new_debt_ceiling,
    )
    actions = [set_ceiling_action]

    # burn excess crvUSD
    if ceiling < current_ceiling:
        burn_action = (factory_address, "rug_debt_ceiling", pegkeeper_address)
        actions.append(burn_action)

    tx = make_vote(
        target=target,
        actions=actions,
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")

    # For testing, since malformed script can be set in vote, we need to
    # execute to double-check everything really works.
    simulate(vote_id, CURVE_DAO_OWNERSHIP["voting"])
    assert (
        factory.debt_ceiling(pegkeeper_address) == new_debt_ceiling
    ), "Debt ceiling doesn't match expected new value."
