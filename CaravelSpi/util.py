import os, argparse
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

def parse_input() -> None:
    parser = argparse.ArgumentParser(description='Flash scipt for Caravel test harness', 
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file', action='store_false', help='Override supported file types')
    override = parser.parse_args(['-f', '--file'])
    print(override)
    
def get_input_type(input: str) -> str:
    file_type = input.partition('.')[2].lower()
    if file_type == 'hex' or file_type == 'bin':
        return  file_type
    else:
        raise RuntimeError('Invalid input file type. Needs to be .hex (verilog), .bin, or raw bytes')
    