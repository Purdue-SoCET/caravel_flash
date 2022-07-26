import os
from pathlib import Path
from typing import Union

def from_hex(path: Union[str, Path]) -> int:
    total_bytes = 0
    with open(path) as f:
        for line in f:
            if not line[0] == '@':
                total_bytes += len(bytes.fromhex(line))
    return total_bytes

def from_bytes(data: bytes) -> int:
    return len(data)

def from_bin(path: Union[str, Path]) -> int:
    return os.path.getsize(path)