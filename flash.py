import sys
from CaravelSpi import CaravelSpi, Flasher, util

spi = CaravelSpi()
hk = spi.get_hk()
flash = spi.get_flash()
flasher = Flasher(spi)

mfg = int.from_bytes(hk.read_n(0x01, 2), 'big')
product = hk.read_b(0x03)
proj_id = int.from_bytes(hk.read_n(0x04, 4), 'big')

print(f'Caravel Data:')
print(f'  mfg    \t= {mfg:04x}')
print(f'  product\t= {product:02x}')
print(f'  proj ID\t= {proj_id:08x}\n')

print('Resetting Flash...')
flash.reset()

print(f'status = 0x{flash.read_st1():02x}\n')

jedec, mem_type, capacity = flash.read_jedec()
print(f'JEDEC info:')
print(f'manufacturer ID = 0x{jedec:02x}')
print(f'memory type = 0x{mem_type:02x}')
print(f'memory capacity = 0x{capacity:02x}\n')

print('Erasing chip...\n')
flasher.erase()

print('Writing...')
flasher.flash_hex(sys.argv[1])
print(f'Total Bytes: {util.from_hex(sys.argv[1])}\n')

print('Verifying...')
flasher.verify_hex(sys.argv[1])
    
print('Done\n')
print(f'status = 0x{flash.read_st1():02x}\n')
