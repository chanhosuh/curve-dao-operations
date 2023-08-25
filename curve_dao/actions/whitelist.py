from curve_dao.addresses import SMARTWALLET_CHECKER


def vecrv_whitelist_action(address):
    """Get the action type for approving a smart contract for veCRV."""
    return (SMARTWALLET_CHECKER, "approveWallet", address)
