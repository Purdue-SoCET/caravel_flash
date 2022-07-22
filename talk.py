from pathlib import Path
from typing import Union, Tuple

from pyftdi.ftdi import Ftdi
from pyftdi.spi import SpiController, SpiPort
from pyftdi.usbtools import UsbTools, UsbDeviceDescriptor

import constants
from constants import HKCmd, FlashCmd


class HKMaster:
  __slots__ = 'port'

  def __init__(self, port: SpiPort) -> None:
    self.port = port

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

  def write_n(self, data: bytes, address: int) -> None:
    self.port.write(self.__n_cmd(HKCmd.Write, address, data=data))

  def read_n(self, length: int, address: int) -> bytes:
    return self.port.exchange(self.__n_cmd(HKCmd.Read, address, length),
                              length)

  def rw_n(self, data: bytes, address: int) -> bytes:
    return self.port.exchange(
        self.__n_cmd(HKCmd.Read | HKCmd.Write, address, data=data), len(data))

  def write_s(self, data: bytes, address: int) -> None:
    self.port.write(self.__s_cmd(HKCmd.Write, address, data))

  def read_s(self, length: int, address: int) -> bytes:
    return self.port.exchange(self.__s_cmd(HKCmd.Read, address), length)

  def rw_s(self, data: bytes, address: int) -> bytes:
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

  def __run_cmd(self, op: int, read: int, data: bytes = b''):
    return self.hk.mgt_pass(op.to_bytes(1, 'big') + data, read)

  def __verify(self) -> None:
    mfg, _, _ = self.read_jedec()
    if mfg != constants.JEDEC_ID:
      raise RuntimeError('Invalid Manufacturer ID')

  def read_jedec(self) -> Tuple[int, int, int]:
    return tuple(self.__run_cmd(FlashCmd.Jedec, 3))


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
  def get_device() -> tuple[UsbDeviceDescriptor, int]:
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
  __slots__ = 'spi', 'hk'

  def __init__(self, spi: CaravelSpi) -> None:
    self.spi = spi
    self.hk = spi.get_hk()

  def __verify(self) -> None:
    pass

  def flash_bytes(self, data: bytes) -> None:
    pass

  def flash_file(self, path: Union[str, Path]) -> None:
    pass
