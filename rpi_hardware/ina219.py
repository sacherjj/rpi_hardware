#!/usr/bin/python

from collections import namedtuple


BusVoltage = namedtuple('BusVoltage', 'voltage overflow')


class INA219(object):
    """
    I2C driver for INA219 power monitor
    """

    __REGISTER_CONFIG = 0x0
    __REGISTER_SHUNT = 0x1
    __REGISTER_BUS = 0x2
    __REGISTER_POWER = 0x3
    __REGISTER_CURRENT = 0x4
    __REGISTER_CALIBRATION = 0x5

    __REG_RESET_SHIFT = 15

    __REG_BUS_VOLT_SHIFT = 13

    BUS_VOLTAGE_LOOKUP = {
        16: 0,
        32: 1
    }

    __REG_GAIN_SHIFT = 12

    GAIN_LOOKUP = {
        1: 0x0,
        2: 0x1,
        4: 0x2,
        8: 0x3
    }

    __REG_ADC_BUS_SHIFT = 7
    __REG_ADC_SHUNT_SHIFT = 3

    ADC_BIT_LOOKUP = {
        9: 0x0,
        10: 0x1,
        11: 0x2,
        12: 0x3
    }

    ADC_12BIT_SAMPLE_LOOKUP = {
        1: 0x8,
        2: 0x9,
        4: 0xa,
        8: 0xb,
        16: 0xc,
        32: 0xd,
        64: 0xe,
        128: 0xf
    }

    __REG_MODE_POWER_DOWN = 0x0
    __REG_MODE_SHUNT_VOLTAGE_TRIGGERED = 0x1
    __REG_MODE_BUS_VOLTAGE_TRIGGERED = 0x2
    __REG_MODE_BUS_SHUNT_AND_BUS_TRIGGERED = 0x3
    __REG_MODE_ADC_OFF = 0x4
    __REG_MODE_SHUNT_VOLTAGE_CONTINUOUS = 0x5
    __REG_MODE_BUS_VOLTAGE_CONTINUOUS = 0x6
    __REG_MODE_SHUNT_AND_BUS_CONTINUOUS = 0x7

    def __init__(self, smbus_ref,
                 address=0x40,
                 bus_voltage_range=BUS_VOLTAGE_LOOKUP[32],
                 pga_gain=GAIN_LOOKUP[1],
                 bus_adc=ADC_12BIT_SAMPLE_LOOKUP[4],
                 shunt_adc=ADC_12BIT_SAMPLE_LOOKUP[4],
                 operating_mode=__REG_MODE_BUS_SHUNT_AND_BUS_TRIGGERED,
                 debug=False):
        """

        :param address: I2C address 0x40-0x4f
        :param bus_number: RPi bus number (default 0x1)
        :param bus_voltage_range: Voltage Range - use BUS_VOLTAGE_LOOKUP with 16 or 32
        :param pga_gain: ADC Gain - use GAIN_LOOKUP with 1 (40mV), 2 (80mV), 4 (160mV), 8 (320mV)
        :param bus_adc: Bus ADC - use ADC_BIT_LOOKUP for single or ADC_12BIT_SAMPLE_LOOKUP for multiple sample avg.
        :param shunt_adc: Shunt ADC - use ADC_BIT_LOOKUP for single or ADC_12BIT_SAMPLE_LOOKUP for multiple sample avg.
        :param operating_mode: Use __REG_MODE_ values for operation mode.
        :param debug: Defaults to False
        """

        if not 0x40 <= address <= 0x4f:
            raise ValueError("Invalid address.  Valid value 0x40-0x4f.")
        if not 0x0 <= bus_voltage_range <= 0x1:
            raise ValueError("Invalid bus_voltage_range.  Valid values 0-1.")
        if not 0x0 <= pga_gain <= 0x3:
            raise ValueError("Invalid pga_gain.  Valid values 0-3.")
        if not 0x0 <= bus_adc <= 0xf:
            raise ValueError("Invalid bus_adc.  Valid values 0x0-0xf.")
        if not 0x0 <= shunt_adc <= 0xf:
            raise ValueError("Invalid shunt_adc.  Valid values 0x0-0xf.")
        if not 0x0 <= operating_mode <= 0x7:
            raise ValueError("Invalid operating_mode.  Valid values 0x0-0x7.")

        if not smbus_ref:
            raise ValueError('smbus_ref is required.')
        self._smbus = smbus_ref
        self.reset = 0
        self.address = address
        self.bus_voltage_range = bus_voltage_range
        self.pga_gain = pga_gain
        self.bus_adc = bus_adc
        self.shunt_adc = shunt_adc
        self.operating_mode = operating_mode
        self.debug = debug
        self._write_config()
        # For some reason I need to read to get things going with this guy.
        self._read_config()

    def _write_config(self):
        """
        Writes current values to config register
        :return: None
        """
        config = self._build_config()
        if self.debug:
            print("Config: %s " % bin(config))
        self._smbus.write_word_data(self.address, self.__REGISTER_CONFIG, config)

    def _build_config(self):
        """
        Builds configuration bytes
        :return: 16 bit configuration integer
        """
        config_value = 0
        config_value |= self.reset << self.__REG_RESET_SHIFT
        config_value |= self.bus_voltage_range << self.__REG_BUS_VOLT_SHIFT
        config_value |= self.pga_gain << self.__REG_GAIN_SHIFT
        config_value |= self.bus_adc << self.__REG_ADC_BUS_SHIFT
        config_value |= self.shunt_adc << self.__REG_ADC_SHUNT_SHIFT
        config_value |= self.operating_mode
        return config_value

    def _read_config(self):
        config_value = self._smbus.read_word_data(self.address, self.__REGISTER_CONFIG)
        return config_value

    def shunt_voltage(self):
        """
        Gets the shunt voltage

        :return: shunt voltage in millivolts
        """
        value = self._smbus.read_word_data(self.address, self.__REGISTER_SHUNT)
        print('value', value)
        # Get sign from top bit
        sign = value & 0x8000
        print('sign', sign)
        # Make bit resolution based sign clearing mask
        sign_clear_mask = 0x7fff >> 12 - self._shunt_bit_resolution()
        print('sign_clear_mask', sign_clear_mask)
        # Clear out sign bits
        value &= sign_clear_mask
        print(value)
        # Convert to mV and apply sign
        if sign:
            return value / -100
        return value / 100

    def bus_voltage(self):
        """
        Gets the bus voltage
        :return: bus voltage in millivolts
        """
        value = self._smbus.read_word_data(self.address, self.__REGISTER_BUS)
        print('value', value)
        # shift voltage down to 1
        voltage = (value & 0xfff8) >> 3
        print('voltage', voltage)
        # convert into mV
        voltage /= 4
        print('voltage', voltage)
        overflow = (value & 1)
        print('overflow', overflow)
        return BusVoltage(voltage, overflow)

    def power(self):
        value = self._smbus.read_word_data(self.address, self.__REGISTER_POWER)
        return value

    def current(self):
        value = self._smbus.read_word_data(self.address, self.__REGISTER_CURRENT)
        return value

    def _shunt_bit_resolution(self):
        return self._bit_resolution(self.shunt_adc)

    def _bus_bit_resolution(self):
        return self._bit_resolution(self.bus_adc)

    @staticmethod
    def _bit_resolution(bit_setting):
        if bit_setting > 0x3:
            return 12
        return (9, 10, 11, 12)[bit_setting]
