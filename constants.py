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
CMD_READ_STATUS = 0x05  # Read status register
CMD_WRITE_ENABLE = 0x06  # Write enable
CMD_WRITE_DISABLE = 0x04  # Write disable
CMD_PROGRAM_PAGE = 0x02  # Write page
CMD_EWSR = 0x50  # Enable write status register
CMD_WRSR = 0x01  # Write status register
CMD_ERASE_SUBSECTOR = 0x20
CMD_ERASE_HSECTOR = 0x52
CMD_ERASE_SECTOR = 0xD8
# CMD_ERASE_CHIP = 0xC7
CMD_ERASE_CHIP = 0x60
CMD_RESET_CHIP = 0x99
CMD_JEDEC_DATA = 0x9f

CMD_READ_LO_SPEED = 0x03  # Read @ low speed
CMD_READ_HI_SPEED = 0x0B  # Read @ high speed
ADDRESS_WIDTH = 3

JEDEC_ID = 0xEF
