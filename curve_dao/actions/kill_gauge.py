from curve_dao.addresses import (
    CRYPTOSWAP_FACTORY_OWNER,
    STABLESWAP_FACTORY_OWNER,
    STABLESWAP_GAUGE_OWNER,
)


def kill_gauge_action(gauge_type, address, kill):
    if gauge_type == "crypto_factory":
        kill_action = (
            CRYPTOSWAP_FACTORY_OWNER,
            "set_killed",
            address,
            kill,
        )
    if gauge_type == "tricrypto_ng":
        # tricrypto-ng factory admin is OWNERSHIP agent already,
        # rather than an owner proxy
        kill_action = (
            address,
            "set_killed",
            kill,
        )
    if gauge_type == "stableswap":
        # The OG stableswap pools like 3Pool, sUSD, Compound, etc.
        # do not have any kill functionality for their gauges.
        #
        # Somewhat newer, pre-factory ones have a `kill_me`
        # and are controlled by EOA.
        #
        # Even newer pre-factory ones have a `set_killed` but
        # are controlled by a gauge owner contract.
        kill_action = (
            STABLESWAP_GAUGE_OWNER,
            "set_killed",
            address,
            kill,
        )
    if gauge_type == "stableswap_factory":
        kill_action = (
            STABLESWAP_FACTORY_OWNER,
            "set_killed",
            address,
            kill,
        )
    return kill_action
