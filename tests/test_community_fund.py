import ape
import pytest

from curve_dao.addresses import (
    COMMUNITY_FUND,
    CONTROLLER_FACTORY,
    get_dao_voting_contract,
    select_target,
)
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def community_fund():
    yield ape.Contract(COMMUNITY_FUND)


def test_vest_from_community_fund(community_fund, vote_deployer):
    vote_type = "ownership"
    target = select_target(vote_type)

    amount = 1_000_000_000000000000000000
    recipient = "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"  # LlamaRisk msig
    fund_action = (
        community_fund.address,
        "deploy_vesting_contract",
        "0xd533a949740bb3306d119cc777fa900ba034cd52",  # CRV
        recipient,
        amount,
        True,  # allow disable
        365 * 86400,  # duration; minimum one year
    )
    actions = [fund_action]

    vote_id = make_vote(
        target=target,
        actions=actions,
        description="test",
        vote_creator=vote_deployer,
    )

    voting_contract = get_dao_voting_contract(vote_type)
    tx = simulate_vote(vote_id, voting_contract)

    logs = tx.decode_logs()
    # logs[0]  # Approval
    # logs[1]  # Transfer
    # logs[2]  # Fund
    # logs[3]  # ScriptResult
    # logs[4]  # ExecuteVote
    transfer_log = logs[1]
    transfer_amount = transfer_log.event_arguments["_value"]
    assert amount == transfer_amount

    vesting_contract_address = transfer_log.event_arguments["_to"]
    vesting_contract = ape.Contract(vesting_contract_address)
    assert vesting_contract.lockedOf(recipient) == amount
