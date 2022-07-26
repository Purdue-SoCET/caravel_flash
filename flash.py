from talk import CaravelSpi, Flasher

spi = CaravelSpi()
hk = spi.get_hk()
flash = spi.get_flash()
flasher = Flasher(spi)

mfg = int.from_bytes(hk.read_n(0x01, 2), 'big')
product = hk.read_b(0x03)
proj_id = int.from_bytes(hk.read_n(0x04, 4), 'big')

print(f'  mfg\t\t= {mfg:04x}')
print(f'  product\t= {product:02x}')
print(f'  proj ID\t= {proj_id:08x}\n')

print('Resetting Flash...')
flash.reset()

print(f'status = 0x{flash.read_st1():02x}\n')

jedec, mem_type, capacity = flash.read_jedec()
print(f'JEDEC = 0x{jedec:02x}')
print(f'memory type = {mem_type:02x}')
print(f'memory capacity = {capacity:02x}')

print('Erasing chip...')
flasher.erase()

print('Done')
print(f'status = 0x{flash.read_st1():02x}\n')
