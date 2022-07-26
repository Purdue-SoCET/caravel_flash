from pathlib import Path
from typing import Union, Tuple
from time import sleep

from pyftdi.ftdi import Ftdi
from pyftdi.spi import SpiController, SpiPort
from pyftdi.usbtools import UsbTools, UsbDeviceDescriptor

import constants
from constants import HKCmd, FlashCmd, FlashStatus, CmdResponseSize


class HKMaster:
  __slots__ = 'port'

  def __init__(self, port: SpiPort) -> None:
    self.port = port
    self.__verify()

  def __verify(self):
    mfg = int.from_bytes(self.read_n(0x01, 2), 'big')
    if mfg != constants.CARAVEL_MFG_ID:
      raise RuntimeError('Invalid Caravel manufacturer ID')

  @staticmethod
  def __build_cmd(op: int, addr: int, length: int = 0,
                  data: bytes = b'') -> bytes:
    cmd = op | (length << 3)
    return int.to_bytes(cmd, 1, 'big') + int.to_bytes(addr, 1, 'big') + data

  @staticmethod
  def __n_cmd(op: int, addr: int, length: int = 0, data: bytes = b'') -> bytes:
    if data:
      length = len(data)
    if not 0 < length < 8:
      raise RuntimeError('Invalid operation length')
    return HKMaster.__build_cmd(op, addr, length, data)

  @staticmethod
  def __s_cmd(op: int, addr: int, data: bytes = b'') -> bytes:
    return HKMaster.__build_cmd(op, addr, 0, data)

  def write_n(self, address: int, data: bytes) -> None:
    self.port.write(self.__n_cmd(HKCmd.Write, address, data=data))

  def read_n(self, address: int, length: int) -> bytes:
    return self.port.exchange(self.__n_cmd(HKCmd.Read, address, length),
                              length)

  def rw_n(self, address: int, data: bytes) -> bytes:
    return self.port.exchange(
        self.__n_cmd(HKCmd.Read | HKCmd.Write, address, data=data), len(data))

  def read_b(self, address: int) -> int:
    return self.read_n(address, 1)[0]

  def write_b(self, address: int, data: int) -> None:
    self.write_n(address, data.to_bytes(1, 'big'))

  def rw_b(self, address: int, data: int) -> int:
    return self.rw_n(address, data.to_bytes(1, 'big'))[0]

  def write_s(self, address: int, data: bytes) -> None:
    self.port.write(self.__s_cmd(HKCmd.Write, address, data))

  def read_s(self, address: int, length: int) -> bytes:
    return self.port.exchange(self.__s_cmd(HKCmd.Read, address), length)

  def rw_s(self, address: int, data: bytes) -> bytes:
    return self.port.exchange(
        self.__s_cmd(HKCmd.Read | HKCmd.Write, address, data), len(data))

  def mgt_pass(self, data: bytes, read_len: int) -> bytes:
    return self.port.exchange(
        int.to_bytes(HKCmd.MgtPass, 1, 'big') + data, read_len)

  def usr_pass(self, data: bytes, read_len: int) -> bytes:
    return self.port.exchange(
        int.to_bytes(HKCmd.UsrPass, 1, 'big') + data, read_len)


class FlashMaster:
  __slots__ = 'hk'

  def __init__(self, hk: HKMaster) -> None:
    self.hk = hk
    self.__verify()

  def __run_cmd(self, op: int, data: bytes = b''):
    readlen = CmdResponseSize.get(op, 0)
    return self.hk.mgt_pass(op.to_bytes(1, 'big') + data, readlen)

  def __verify(self) -> None:
    mfg, _, _ = self.read_jedec()
    if mfg != constants.JEDEC_ID:
      raise RuntimeError('Invalid flash manufacturer ID')
  
  def __wait(self) -> None:
    while self.is_busy():
      sleep(constants.POLL_WAIT)

  def read_jedec(self) -> Tuple[int, int, int]:
    return tuple(self.__run_cmd(FlashCmd.Jedec))

  def reset(self) -> None:
    self.__run_cmd(FlashCmd.ResetEn)
    self.__run_cmd(FlashCmd.Reset)

  def erase(self) -> None:
    self.__run_cmd(FlashCmd.WriteEn)
    self.__run_cmd(FlashCmd.ChipErase)
    self.__wait()

  def read_st1(self) -> int:
    return self.__run_cmd(FlashCmd.ReadSt1)[0]

  def read_st2(self) -> int:
    return self.__run_cmd(FlashCmd.ReadSt2)[0]

  def read_st3(self) -> int:
    return self.__run_cmd(FlashCmd.ReadSt3)[0]

  def is_busy(self) -> bool:
    return bool(self.read_st1() & FlashStatus.St1Busy)
  
  def write_page(self, addr: int, data : bytes) -> None:
    self.__run_cmd(FlashCmd.WriteEn)
    self.__run_cmd(FlashCmd.WritePage, addr.to_bytes(3, 'big') + data)
    self.__wait()


class CaravelSpi(SpiController):
  def __init__(self) -> None:
    device = self.get_device()
    url = UsbTools.build_dev_strings('ftdi', Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS,
                                     [device])[0][0]
    super().__init__(constants.CARAVEL_CS_COUNT)
    self.configure(url)

    self._hk = HKMaster(self.get_port(cs=1, freq=12E6))
    self._flash = FlashMaster(self._hk)

  @staticmethod
  def get_device() -> Tuple[UsbDeviceDescriptor, int]:
    devs = Ftdi.find_all(constants.CARAVEL_FTDI_VPS)
    if not devs:
      raise RuntimeError('No board found')
    elif len(devs) > 1:
      raise RuntimeError('Multiple valid devices found')
    return devs[0]

  def get_hk(self) -> HKMaster:
    return self._hk

  def get_flash(self) -> FlashMaster:
    return self._flash


class Flasher:
  __slots__ = 'spi', 'hk', 'flash'

  def __init__(self, spi: CaravelSpi) -> None:
    self.spi = spi
    self.hk = spi.get_hk()
    self.flash = spi.get_flash()

  def __reset(self, state: int) -> None:
    self.hk.write_b(0x0b, state)
  
  def __flush(self, addr: int, buf: bytes) -> None:
    while buf:
      self.flash.write_page(addr, buf[:256])
      addr += 256
      buf = buf[256:]
  
  def erase(self) -> None:
    self.__reset(1)
    self.flash.erase()
    self.__reset(0)

  def flash_bytes(self, data: bytes) -> None:
    self.__reset(1)
    self.__reset(0)

  def flash_bin(self, path: Union[str, Path]) -> None:
    pass

  def flash_hex(self, path: Union[str, Path]) -> None:
    self.__reset(1)

    addr = 0
    buf = b''
    with open(path) as f:
      for line in f:
        if line[0] == '@':
          self.__flush(buf, addr)
          buf = b''
          addr = int(line[1:], 16)
        else:
          buf += bytes.fromhex(line)
    self.__flush(buf, addr)
    
    self.__reset(0)
    
  def verify_flash(self, path: Union[str, Path]) -> None:
    pass
