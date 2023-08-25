import ape
import pytest

from curve_dao.actions.whitelist import vecrv_whitelist_action
from curve_dao.addresses import CURVE_DAO_OWNERSHIP, SMARTWALLET_CHECKER, select_target
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def smartwallet_checker():
    yield ape.Contract(SMARTWALLET_CHECKER)


@pytest.fixture(scope="module")
def addr_to_whitelist():
    # cryptoriskteam msig:
    yield "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"


def test_whitelist(smartwallet_checker, addr_to_whitelist, vote_deployer):
    assert not smartwallet_checker.check(addr_to_whitelist)

    whitelist_action = vecrv_whitelist_action(addr_to_whitelist)
    target = select_target("ownership")
    vote_id = make_vote(
        target=target,
        actions=[whitelist_action],
        description="test",
        vote_creator=vote_deployer,
    )

    simulate_vote(
        vote_id=vote_id,
        voting_contract=target["voting"],
    )

    assert smartwallet_checker.check(addr_to_whitelist)
