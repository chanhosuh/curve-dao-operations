import boa

from curve_dao.etherscan import get_abi_from_etherscan


def get_contract(contract_address):
    """
    Creates contract instance given the address.

    Uses Etherscan to fetch the ABI.
    """
    abi = get_abi_from_etherscan(contract_address)
    abi_factory = boa.loads_abi(abi)
    contract = abi_factory.at(contract_address)
    return contract
