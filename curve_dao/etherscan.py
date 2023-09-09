import os

import requests

from curve_dao.exceptions import CurveDaoOperationsError

try:
    ETHERSCAN_API_KEY = os.environ["ETHERSCAN_API_KEY"]
except KeyError:
    raise CurveDaoOperationsError("Cannot find ETHERSCAN_API_KEY in env.")


def get_abi_from_etherscan(contract_address):
    etherscan_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(etherscan_url)
    response.raise_for_status()
    resp_json = response.json()
    return resp_json
