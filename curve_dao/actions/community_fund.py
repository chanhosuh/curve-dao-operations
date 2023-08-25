from curve_dao.addresses import COMMUNITY_FUND, CRV


def community_fund_action(recipient, amount, duration=365 * 86400, allow_disable=True):
    fund_action = (
        COMMUNITY_FUND,
        "deploy_vesting_contract",
        CRV,
        recipient,
        amount,
        allow_disable,  # allow the DAO to stop further vesting
        duration,  # in seconds, minimum one year
    )
    return fund_action
