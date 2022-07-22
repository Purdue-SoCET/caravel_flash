from enum import IntEnum

CARAVEL_FTDI_VPS = ((1027, 24596), )
CARAVEL_CS_COUNT = 2
FTDI_MAX_FREQ = 12E6  # Hz


# Commands recognized by Caravel HouseKeeping SPI
class HKCmd(IntEnum):
  Read = 0x40
  Write = 0x80
  MgtPass = Read | Write | 0x4
  UsrPass = Read | Write | 0x6


# Winbond Flash Constants
class FlashCmd(IntEnum):
  WriteEn = 0x06
  VolSRWriteEn = 0x50
  WriteDs = 0x04
  ReadSt1 = 0x05
  WriteSt1 = 0x01
  ReadSt2 = 0x35
  WriteSt2 = 0x31
  ReadSt3 = 0x15
  WriteSt3 = 0x11
  ChipErase = 0xC7
  _ChipErase = 0x60  # Equivalent to 0xC7
  EraseSuspend = 0x75
  EraseResume = 0x7A
  PowerDown = 0xB9
  RelPowerDown = 0xAB
  DeviceID = 0x90
  Jedec = 0x9F
  GlobalLock = 0x7E
  GlobalUnlock = 0x98
  EnterQPI = 0x38  # Probably should never use this
  ResetEn = 0x66
  Reset = 0x99
  UniqueID = 0x4B
  WritePage = 0x02
  QWritePage = 0x32
  EraseSector = 0x20
  EraseBlock32 = 0x52
  EraseBlock64 = 0xD8
  ReadData = 0x03
  FastRead = 0x0B
  FastReadD = 0x3B
  FastReadQ = 0x6B
  ReadSFDP = 0x5A
  EraseSec = 0x44
  WriteSec = 0x42
  ReadSec = 0x48
  BlockLock = 0x36
  BlockUnlock = 0x39
  RdBlockLock = 0x3D
  FastReadDIO = 0xBB
  DeviceIDDIO = 0x92
  SetBurst = 0x77
  FastReadQIO = 0xEB
  WordReadQIO = 0xE7
  OWordReadQIO = 0xE3
  DeviceIDQIO = 0x94

# Winbond Flash Status Register
class FlashStatus(IntEnum):
  St1Busy = 0b00000001 # Busy/Work-in-progress
  St1WEL = 0b00000010  # Write Enable Latch
  St1BP0 = 0b00000100  # Block Protect Bits 0
  St1BP1 = 0b00001000  # Block Protect Bits 1
  St1BP2 = 0b00010000  # Block Protect Bits 2
  St1TB = 0b00100000   # Top/Bottom Protect Bits
  St1SEC = 0b01000000  # Sector Protect Bit
  St1SRP = 0b10000000  # Status Register Protect 0
  
CmdResponseSize = {
    FlashCmd.Jedec: 3,
}

JEDEC_ID = 0xEF
