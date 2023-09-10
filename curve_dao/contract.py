import json

import boa
from vyper.semantics.types.function import ContractFunctionT

from curve_dao.etherscan import get_abi_from_etherscan


def get_contract(contract_address):
    """
    Creates contract instance given the address.

    Uses Etherscan to fetch the ABI.
    """
    abi_json = get_contract_abi_json(contract_address)
    abi_factory = boa.loads_abi(abi_json)
    contract = abi_factory.at(contract_address)

    abi = json.loads(abi_json)
    function_abi = []
    for entry in abi:
        if 'inputs' not in entry:
            continue
        if 'outputs' not in entry:
            continue
        if entry['type'] == 'constructor':
            continue
        function_type = ContractFunctionT.from_abi(entry)
        selector = list(function_type.method_ids.values())[0]
        entry["4bytes"] = selector.to_bytes(4, "big").hex()
        function_abi.append(entry)

    return contract, function_abi


def get_contract_abi_json(contract_address):
    """
    Creates contract instance given the address.

    Uses Etherscan to fetch the ABI.
    """
    if isinstance(contract_address, bytes):
        contract_address = "0x" + contract_address.hex()
    abi = get_abi_from_etherscan(contract_address)
    # XXX: kludge because titanoboa can't handle uint256[] abi type
    # XXX: it also can't handle python reserved keywords as event args
    new_abi = []
    skip = False
    abi = json.loads(abi)
    for entry in abi:
        if 'inputs' in entry:
            inputs = entry['inputs']
            for _input in inputs:
                if _input['type'] == 'uint256[]':
                    skip = True
                    break
                if _input['type'] == 'address[]':
                    skip = True
                    break
                if _input['name'] in ['from']:
                    skip = True
                    break
        if 'outputs' in entry:
            outputs = entry['outputs']
            for output in outputs:
                # ownership vote id 351, several more
                # if output['type'] == 'tuple':
                #     skip = True
                #     break
                if output['type'] == 'tuple[]':
                    skip=True
                    break
        # ownership vote id 394: vyper.exceptions.StructureException: '' contains invalid character(s)
        if skip:
            skip = False
            continue

        new_abi.append(entry)
    
    abi = json.dumps(new_abi)
    return abi


def get_abi_with_4bytes(contract_address):
    """
    Creates contract instance given the address.

    Uses Etherscan to fetch the ABI.
    """
    abi_json = get_contract_abi_json(contract_address)
    abi = json.loads(abi_json)
    function_abi = []
    for entry in abi:
        if 'inputs' not in entry:
            continue
        if 'outputs' not in entry:
            continue
        function_type = ContractFunctionT.from_abi(entry)
        selector = list(function_type.method_ids.values())[0]
        entry["4bytes"] = selector.to_bytes(4, "big").hex()
        function_abi.append(entry)

    return function_abi
