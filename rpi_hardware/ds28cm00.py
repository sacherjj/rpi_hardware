#!/usr/bin/python

from .util.crc import crc8_check


class DS28CM00(object):
    """
    I2C driver for DS28CM00 silicon serial number

    This is a simple chip that only gives you a unique serial number.
    It is useful if you want to load the same software on multiple systems
    and still have them able to determine who they are.

    I use this serial as the primary key in the DB.  This allows the device to
    load config data from the DB at start up.
    """

    _ADDRESS = 0b1010000

    def __init__(self, smbus_ref):
        """
        Initalize object and give proper smbus to use.

        :param smbus_ref: smbus object, as create with smbus.Smbus(bus_number) or mock smbus object.
        """
        self._smbus = smbus_ref
        self._serial_number = None
        self._serial_hex = None

    @property
    def serial_number(self):
        """
        Read silicon serial number.

        :return: 48-bit serial number as hex value
        :raises: ValueError if CRC check fails
        """
        if not self._serial_number:
            # Load it once and cache it
            self._smbus.write_byte(self._ADDRESS, 0x00)
            data = [self._smbus.read_byte(self._ADDRESS) for _ in range(8)]
            if not crc8_check(data[:-1], data[-1]):
                raise ValueError('CRC validation failed for reading serial number.')
            self._serial_number = 0
            for byte_value in data[1:-1]:
                self._serial_number = (self._serial_number << 8) + byte_value
            self._serial_hex = hex(self._serial_number)
        return self._serial_hex
