#!/usr/bin/python

from .smbus import FakeSMBusDevice
from rpi_hardware.util.crc import crc8_value


class FakeDS28CM00(FakeSMBusDevice):
    """
    Fake Hardware for DS28CM00, to be talked to using DS28CM00 object for testing and simulation
    """

    _ADDRESS = 0b1010000

    def __init__(self, smbus, serial_number_byte_list):
        """
        Initalize object and give proper smbus to use.

        :param smbus: mock smbus object.
        :param serial_number_byte_list: 6 member list with bytes for serial number
        """
        if not len(serial_number_byte_list) == 6:
            raise ValueError('serial_number_byte_list must be a list of 6 byte integers.')
        if max(serial_number_byte_list) > 255 or min(serial_number_byte_list) < 0:
            raise ValueError('serial_number_byte_list contains values not within range(256)')

        # Memory is Family Code (0x70), 6 bytes of serial number, crc8, Control Register byte (0x01)
        data = [0x70] + serial_number_byte_list
        self._data = data + [crc8_value(data)] + [0x01]
        self._write_map = [False] * 8 + [True]
        self._index = 0
        super().__init__(smbus, self._ADDRESS)

    def _inc_index(self):
        self._index += 1
        if self._index > 8:
            self._index = 0

