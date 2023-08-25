import ape
import pytest

from curve_dao.addresses import (
    CONTROLLER_FACTORY,
    get_dao_voting_contract,
    select_target,
)
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def controller_factory():
    yield ape.Contract(CONTROLLER_FACTORY)


def test_change_pegkeeper_debt_ceiling(controller_factory, vote_deployer):
    # TUSD peg keeper
    pegkeeper_address = "0x1ef89ed0edd93d1ec09e4c07373f69c49f4dccae"
    new_ceiling = 1_000_000_000000000000000000

    current_ceiling = controller_factory.debt_ceiling(pegkeeper_address)
    assert (
        current_ceiling != new_ceiling
    ), "New debt ceiling is the same as current value"

    vote_type = "ownership"
    target = select_target(vote_type)

    set_ceiling_action = (
        controller_factory.address,
        "set_debt_ceiling",
        pegkeeper_address,
        new_ceiling,
    )
    actions = [set_ceiling_action]

    # burn excess crvUSD
    if new_ceiling < current_ceiling:
        burn_action = (
            controller_factory.address,
            "rug_debt_ceiling",
            pegkeeper_address,
        )
        actions.append(burn_action)

    vote_id = make_vote(
        target=target,
        actions=actions,
        description="test",
        vote_creator=vote_deployer,
    )

    voting_contract = get_dao_voting_contract(vote_type)
    simulate_vote(vote_id, voting_contract)
    assert (
        controller_factory.debt_ceiling(pegkeeper_address) == new_ceiling
    ), "Debt ceiling doesn't match expected new value."
