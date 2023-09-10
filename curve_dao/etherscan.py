import os

import requests

from curve_dao.exceptions import CurveDaoOperationsError

try:
    ETHERSCAN_API_KEY = os.environ["ETHERSCAN_API_KEY"]
except KeyError:
    raise CurveDaoOperationsError("Cannot find ETHERSCAN_API_KEY in env.")


def get_abi_from_etherscan(contract_address):
    etherscan_source_url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(etherscan_source_url)
    response.raise_for_status()
    resp_json = response.json()
    result = resp_json['result'][0]

    if 'Implementation' in result and result['Implementation']:
        contract_address = result['Implementation']

    etherscan_abi_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(etherscan_abi_url)
    response.raise_for_status()
    resp_json = response.json()

    result = resp_json['result']
    return result
