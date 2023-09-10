from typing import Any, Dict, List, Tuple, Union

from eth_abi.exceptions import InsufficientDataBytes
from eth_utils import humanize_hash, is_hex_address, to_checksum_address

try:
    from eth_abi import decode_abi
except ImportError:
    from eth_abi import decode as decode_abi


def decode_input(abi_with_4bytes, calldata: Union[str, bytes]) -> Tuple[str, Any]:
    selector = calldata[:4].hex()
    raw_data = calldata[4:]

    abi = None
    for entry in abi_with_4bytes:
        if entry["4bytes"] == selector:
            abi = entry

    if abi is None:
        raise ValueError(
            "Four byte selector does not match the ABI for this contract"
        )

    decoded_data = decode_calldata(abi, raw_data)
    return abi, decoded_data


def decode_calldata(
    abi_entry,
    raw_data: bytes,
) -> List:
    input_types = [i['type'] for i in abi_entry['inputs']]

    try:
        raw_input_values = decode_abi(input_types, raw_data)
        input_values = [decode_value(v) for v in raw_input_values]
    except InsufficientDataBytes:
        input_values = ["<?>" for _ in input_types]

    return input_values


def decode_value(value):
    if isinstance(value, str) and is_hex_address(value):
        return to_checksum_address(value)

    elif value and isinstance(value, str):
        # Surround non-address strings with quotes.
        return f'"{value}"'

    elif isinstance(value, (list, tuple)):
        decoded_values = [decode_value(v) for v in value]
        return decoded_values

    return value
