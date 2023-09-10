import ape
import click
from ape.api import accounts
from ape.cli.choices import AccountAliasPromptChoice
from ape.cli.options import _account_callback
from ape.logging import logger

from curve_dao import make_vote
from curve_dao.actions.community_fund import community_fund_action
from curve_dao.actions.kill_gauge import kill_gauge_action
from curve_dao.actions.whitelist import vecrv_whitelist_action
from curve_dao.addresses import (
    CONTROLLER_FACTORY,
    CRYPTOSWAP_FACTORY_OWNER,
    STABLESWAP_FACTORY_OWNER,
    STABLESWAP_GAUGE_OWNER,
    STABLESWP_OWNER,
    get_dao_voting_contract,
    select_target,
)
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import decode_vote_script, get_vote_script
from scripts.decode import console


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
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation (default is False)",
)
def whitelist(network, account, addr, description, simulate):

    vote_type = "ownership"
    target = get_dao_voting_contract(vote_type)
    vote_id = make_vote(
        target=target,
        actions=[vecrv_whitelist_action(addr)],
        description=description,
        vote_creator=account,
    )
    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")

    if simulate:
        script = get_vote_script(vote_id, "ownership")
        votes = decode_vote_script(script)
        for vote in votes:
            formatted_output = vote["formatted_output"]
            console.log(formatted_output)
        voting_contract = get_dao_voting_contract(vote_type)
        simulate_vote(vote_id, voting_contract)


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
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation (default is False)",
)
def kill_gauge(
    network,
    account,
    address,
    kill,
    gauge_type,
    description,
    simulate,
):
    """
    ape run set_vote kill_gauge --address 0x762648808ef8b25c6d92270b1c84ec97df3bed6b --gauge-type crypto_factory -d 'Kill the whatever gauge'  --account test_account --network :mainnet-fork
    """
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    kill_action = kill_gauge_action(gauge_type, address, kill)
    vote_type = "ownership"
    target = select_target(vote_type)
    vote_id = make_vote(
        target=target,
        actions=[kill_action],
        description=description,
        vote_creator=account,
    )
    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")

    if simulate:
        script = get_vote_script(vote_id, "ownership")
        votes = decode_vote_script(script)
        for vote in votes:
            formatted_output = vote["formatted_output"]
            console.log(formatted_output)
        voting_contract = get_dao_voting_contract(vote_type)
        simulate_vote(vote_id, voting_contract)


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
    type=click.Choice(
        ["stableswap", "stableswap_factory", "crypto_factory", "tricrypto_ng"]
    ),
    required=True,
)
@click.option(
    "--parameter",
    "-p",
    required=True,
    multiple=True,
    type=(str, int),
)
@click.option("--description", "-d", type=str, required=True)
def change_parameters(
    network,
    account,
    address,
    pool_type,
    parameter,
    description,
):
    """
    ape run set_vote kill_gauge --address 0x762648808ef8b25c6d92270b1c84ec97df3bed6b --gauge-type crypto_factory -d 'Kill the whatever gauge'  --account test_account --network :mainnet-fork
    """
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    valid_parameters = set(
        "A",
        "gamma",
        "fee",
        "admin_fee",
        "mid_fee",
        "out_fee",
        "fee_gamma",
        "allowed_extra_profit",
        "adjustment_step",
        "ma_time",
        "future_time",
    )
    parameters = dict(parameter)
    validate_pool_parameters(valid_parameters, pool_type)

    if pool_type == "crypto_factory":
        ramp_action = (
            CRYPTOSWAP_FACTORY_OWNER,
            "ramp_A_gamma",
            address,
            future_A,
            future_gamma,
            future_time,
        )
        parameter_action = (
            CRYPTOSWAP_FACTORY_OWNER,
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
    if pool_type in ["stableswap", "stableswap_factory"]:
        if pool_type == "stableswap":
            owner_proxy = STABLESWP_OWNER
        if pool_type == "stableswap_factory":
            owner_proxy = STABLESWAP_FACTORY_OWNER

        actions = []
        if "A" in parameters:
            future_A = parameters["A"]
            default_future_time = ape.chain.pending_timestamp + 7 * 86400
            future_time = parameters.get("future_time", default_future_time)
            ramp_action = (
                owner_proxy,
                "ramp_A",
                address,
                future_A,
                future_time,
            )
            actions.append(ramp_action)
        if "fee" in parameters:
            new_fee = parameters["fee"]
            fee_action = (
                owner_proxy,
                "commit_new_fee",
                address,
                new_fee,
            )
            actions.append(fee_action)

    target = select_target("ownership")
    vote_id = make_vote(
        target=target,
        actions=actions,
        description=description,
        vote_creator=account,
    )
    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="pegkeeper_debt_ceiling",
    short_help="Set the pegkeeper debt ceiling",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option("--address", "-a", type=str, required=True, help="Pegkeeper address")
@click.option("--ceiling", "-c", type=int, required=True, help="New debt ceiling")
@click.option("--description", "-d", type=str, required=True)
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation (default is False)",
)
def pegkeeper_debt_ceiling(
    network,
    account,
    address,
    ceiling,
    description,
    simulate,
):
    """
    ape run pegkeeper_debt_ceiling --account <account index or alias> --network <network>
    """
    pegkeeper_address = address

    if "mainnet-fork" in network:
        # Override account with a properly setup user
        logger.info("Using test user account")
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    vote_type = "ownership"
    target = select_target(vote_type)

    set_ceiling_action = (
        CONTROLLER_FACTORY,
        "set_debt_ceiling",
        address,
        ceiling,
    )
    actions = [set_ceiling_action]

    # burn excess crvUSD
    factory = ape.Contract(CONTROLLER_FACTORY)
    current_ceiling = factory.debt_ceiling(pegkeeper_address)
    if ceiling < current_ceiling:
        burn_action = (factory.address, "rug_debt_ceiling", pegkeeper_address)
        actions.append(burn_action)

    vote_id = make_vote(
        target=target,
        actions=actions,
        description=description,
        vote_creator=account,
    )
    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")

    if simulate:
        script = get_vote_script(vote_id, vote_type)
        votes = decode_vote_script(script)
        for vote in votes:
            formatted_output = vote["formatted_output"]
            console.log(formatted_output)
        voting_contract = get_dao_voting_contract(vote_type)
        simulate_vote(vote_id, voting_contract)


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="community_fund",
    short_help="Receive linearly vesting funds from the DAO Community Fund",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option("--recipient", "-r", type=str, required=True, help="Recipient address")
@click.option(
    "--amount", "-a", type=int, required=True, help="Amount of CRV (18 decimals)"
)
@click.option("--description", "-d", type=str, required=True)
@click.option(
    "--duration",
    type=int,
    required=False,
    default=86400 * 365,
    show_default=True,
    help="Vesting duration in seconds.  Minimum of 1 year.",
)
@click.option(
    "--allow-disable",
    type=bool,
    required=False,
    default=True,
    show_default=True,
    help="Allow DAO to terminate unvested funds.",
)
@click.option("--description", "-d", type=str, required=True)
@click.option(
    "--simulate",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Check validity via fork simulation",
)
def community_fund(
    network,
    account,
    recipient,
    amount,
    description,
    duration,
    allow_disable,
    simulate,
):
    if "mainnet-fork" in network:
        # Override account with a properly setup user
        logger.info("Using test user account")
        account = ape.accounts["0x9c5083dd4838E120Dbeac44C052179692Aa5dAC5"]

    vote_type = "ownership"
    target = select_target(vote_type)
    fund_action = community_fund_action(recipient, amount, duration, allow_disable)
    vote_id = make_vote(
        target=target,
        actions=[fund_action],
        description=description,
        vote_creator=account,
    )
    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")

    if simulate:
        script = get_vote_script(vote_id, vote_type)
        votes = decode_vote_script(script)
        for vote in votes:
            formatted_output = vote["formatted_output"]
            console.log(formatted_output)
        voting_contract = get_dao_voting_contract(vote_type)
        simulate_vote(vote_id, voting_contract)
