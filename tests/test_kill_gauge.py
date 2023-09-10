import ape
import pytest

from curve_dao.actions.kill_gauge import kill_gauge_action
from curve_dao.addresses import (
    CRYPTOSWAP_FACTORY_OWNER,
    CURVE_DAO_OWNERSHIP,
    STABLESWAP_FACTORY_OWNER,
    STABLESWAP_GAUGE_OWNER,
)
from curve_dao.simulate import simulate_vote
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def crypto_factory_gauge():
    # JPEGpETH gauge
    yield ape.Contract("0x839d92046f1e62a51a2b5705ecae41df152545ec")


@pytest.fixture(scope="module")
def tricrypto_ng_gauge():
    # TriCryptoINV gauge
    yield ape.Contract("0x4fc86cd0f9b650280fa783e3116258e0e0496a2c")


@pytest.fixture(scope="module")
def stableswap_gauge():
    # USDP metapool (pre-factory)
    yield ape.Contract("0x055be5ddb7a925bfef3417fc157f53ca77ca7222")


@pytest.fixture(scope="module")
def stableswap_factory_gauge():
    # BUSD-FRAXBP
    yield ape.Contract("0xAeac6Dcd12CC0BE74c8f99EfE4bB5205a1f9A608")


def test_kill_crypto_factory_gauge(vote_deployer, crypto_factory_gauge):
    assert crypto_factory_gauge.is_killed() is False

    kill_action = kill_gauge_action(
        "crypto_factory", crypto_factory_gauge.address, True
    )

    vote_id = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[kill_action],
        description="test",
        vote_creator=vote_deployer,
    )

    # this advances the chain one week from vote creation
    simulate_vote(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert crypto_factory_gauge.is_killed() is True


def test_kill_ng_gauge(vote_deployer, tricrypto_ng_gauge):
    assert tricrypto_ng_gauge.is_killed() is False

    kill_action = kill_gauge_action("tricrypto_ng", tricrypto_ng_gauge.address, True)

    vote_id = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[kill_action],
        description="test",
        vote_creator=vote_deployer,
    )

    # this advances the chain one week from vote creation
    simulate_vote(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert tricrypto_ng_gauge.is_killed() is True


def test_kill_stableswap_gauge(vote_deployer, stableswap_gauge):
    assert stableswap_gauge.is_killed() is False

    kill_action = kill_gauge_action("stableswap", stableswap_gauge.address, True)

    vote_id = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[kill_action],
        description="test",
        vote_creator=vote_deployer,
    )

    # this advances the chain one week from vote creation
    simulate_vote(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert stableswap_gauge.is_killed() is True


def test_kill_stableswap_factory_gauge(vote_deployer, stableswap_factory_gauge):
    assert stableswap_factory_gauge.is_killed() is False

    kill_action = kill_gauge_action(
        "stableswap_factory", stableswap_factory_gauge.address, True
    )

    vote_id = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[kill_action],
        description="test",
        vote_creator=vote_deployer,
    )

    # this advances the chain one week from vote creation
    simulate_vote(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert stableswap_factory_gauge.is_killed() is True
