from typing import Tuple

from pyftdi.ftdi import Ftdi
from pyftdi.spi import SpiController, SpiPort
from pyftdi.usbtools import UsbTools, UsbDeviceDescriptor

import constants
from constants import HKCmd


def get_device() -> tuple(UsbDeviceDescriptor, int):
  devs = Ftdi.find_all(constants.CARAVEL_FTDI_VPS)
  if not devs:
    raise RuntimeError('No board found')
  elif len(devs) > 1:
    raise RuntimeError('Multiple valid devices found')
  return devs[0]


def desc_to_url(desc: tuple[UsbDeviceDescriptor, int]) -> str:
  return UsbTools.build_dev_strings('ftdi', Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS,
                                    [desc])[0][0]


def connectconfig_spi(url: str) -> SpiController:
  spi = SpiController(cs_count=constants.CARAVEL_CS_COUNT)
  spi.configure(url)
  return spi


def do_the_thing():
  desc = get_device()
  url = desc_to_url(desc)
  return connectconfig_spi(url)


class HKMaster:
  __slots__ = 'port'

  def __init__(self, port: SpiPort) -> None:
    self.port = port

  @staticmethod
  def __build_cmd(op: int, addr: int, length: int = 0, data: bytes = b''):
    cmd = op | (length << 3)
    return int.to_bytes(cmd, 1, 'big') + int.to_bytes(addr, 1, 'big') + data

  @staticmethod
  def __n_cmd(op: int, addr: int, length: int = 0, data: bytes = b''):
    if data:
      length = len(data)
    if not 0 < length < 8:
      raise RuntimeError('Invalid operation length')
    return HKMaster.__build_cmd(op, addr, length, data)

  @staticmethod
  def __s_cmd(op: int, addr: int, data: bytes = b''):
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


spi = do_the_thing()
gpio = spi.get_gpio()
port = spi.get_port(cs=1, freq=12E6, mode=0)
cmd = HKMaster(port)
