

class TMP275(object):
    """
    I2C driver for TMP275 temperature sensor
    """

    # Values to write to Pointer Register for Modes
    __TEMPERATURE_REGISTER = 0x0
    __CONFIGURATION_REGISTER = 0x1
    __T_LOW_REGISTER = 0x2
    __T_HIGH_REGISTER = 0x3

    # Config Register flags
    __CONFIG_SHUTDOWN_MODE = 0b00000001
    __CONFIG_THERMOSTAT_MODE = 0b00000010
    __CONFIG_ALERT_POLARITY = 0b00000100
    __CONFIG_CONSECUTIVE_FAULTS_MASK = 0b00011000
    __CONFIG_CONSECUTIVE_FAULTS = {
        1: 0b00000000,
        2: 0b00001000,
        4: 0b00010000,
        6: 0b00011000
    }
    __CONFIG_CONVERTER_RESOLUTION_MASK = 0b01100000
    __CONFIG_CONVERTER_RESOLUTION_BITS = {
        9:  0b00000000,
        10: 0b00100000,
        11: 0b01000000,
        12: 0b01100000
    }
    __CONFIG_ONE_SHOT = 0b1000000

    def __init__(self,
                 smbus_ref,
                 address=0x48,
                 debug=False):
        """
        Constructor

        :param smbus_ref: Reference to SMBus instance
        :param address: I2C Address of Chip
        :param debug: Boolean for debug
        :return: None
        """
        if not 0x48 <= address <= 0x4f:
            raise ValueError("Invalid address.  Valid value 0x48-0x4f.")

        self._smbus = smbus_ref
        self._address = address
        self._debug = debug
        self._config = 0
        # self._write_config()
        #

    @staticmethod
    def _temp_to_bit_int(celcius_temp):
        # Get number of 0.0625 degrees
        bit_temp = int(round(celcius_temp * 16, 0))
        if celcius_temp >= 0:
            # if temp over 127.9375, pull back to there
            bit_temp = min(0x7FF, bit_temp)
        else:
            # 2s complement value, bit_temp will be negative so adding
            bit_temp += 0x1000
            # if temp under -54.9375, pull up to there (higher is lower with 2s comp)
            bit_temp = max(bit_temp, 0xC90)
        # Value is 12 bits, MMMMMMMMLLLL
        # first_byte is MMMMMMMM, second is LLLL0000
        return bit_temp << 4

    @staticmethod
    def _bit_int_to_temp(temp_bytes):
        # Convert (MMMMMMMM, LLLL0000) to MMMMMMMMLLLL
        int_temp = temp_bytes >> 4
        if int_temp > 0x7ff:
            # 2s compliment conversion
            int_temp -= 0x1000
        return int_temp / 16.0

    def write_t_low_register(self, celcius_value):
        self._smbus.write_word_data(self._address, self.__T_LOW_REGISTER, self._temp_to_bit_int(celcius_value))

    def write_t_high_register(self, celcius_value):
        self._smbus.write_word_data(self._address, self.__T_HIGH_REGISTER, self._temp_to_bit_int(celcius_value))

    def _build_configuration(self, shutdown_mode, thermostat_mode, alert_polarity,
                             fault_queue, bit_resolution):
        """
        Builder method for configuration byte.

        """
        if shutdown_mode not in (0, 1):
            raise ValueError("Illegal shutdown_mode: {}. "
                             "Valid values 0 for Awake or 1 for Sleep.".format(shutdown_mode))
        if thermostat_mode not in (0, 1):
            raise ValueError("Illegal thermostat_mode: {}. "
                             "Valid values 0 for Comparator or 1 for Interrupt.".format(thermostat_mode))
        if alert_polarity not in (0, 1):
            raise ValueError("Illegal alert_polarity: {}. "
                             "Valid values 0 for Active Low or 1 for Active High.".format(alert_polarity))
        if fault_queue not in self.__CONFIG_CONSECUTIVE_FAULTS.keys():
            raise ValueError("Illegal fault_queue: {}.  Valid values {}.".
                             format(fault_queue, self.__CONFIG_CONSECUTIVE_FAULTS.keys()))
        if bit_resolution not in self.__CONFIG_CONVERTER_RESOLUTION_BITS.keys():
            raise ValueError("Invalid bit_resolution: {}.  "
                             "Valid values {}.".format(bit_resolution, self.__CONFIG_CONVERTER_RESOLUTION_BITS.keys()))

        config_value = 0
        if shutdown_mode:
            config_value |= self.__CONFIG_SHUTDOWN_MODE
        if thermostat_mode:
            config_value |= self.__CONFIG_THERMOSTAT_MODE
        if alert_polarity:
            config_value |= self.__CONFIG_ALERT_POLARITY
        config_value |= self.__CONFIG_CONSECUTIVE_FAULTS[fault_queue]
        config_value |= self.__CONFIG_CONVERTER_RESOLUTION_BITS[bit_resolution]
        return config_value

    def write_configuration(self, shutdown_mode=0, thermostat_mode=0, alert_polarity=0,
                            fault_queue=1, bit_resolution=9):
        """
        Update Configuration Register

        :param shutdown_mode: 0 = Stays Awake with Continuous Conversion, 1 = Shut down after current conversion
        :param thermostat_mode: 0 = Comparator Mode, 1 = Interrupt Mode.
        :param alert_polarity: Alert pin ACTIVE 0 = Low, 1 = High
        :param fault_queue: # of faults to generate alert: 1, 2, 4, 6
        :param bit_resolution: Conversion Resolution (bits): 9, 10, 11, 12
        :return: None
        """
        self._config = self._build_configuration(shutdown_mode, thermostat_mode, alert_polarity,
                                                 fault_queue, bit_resolution)
        self._smbus.write_byte_data(self._address, self.__CONFIGURATION_REGISTER, self._config)

    def one_shot(self):
        """
        Writes 1 to OS bit in configuration register to wake device and
        :return:
        """
        temp_config = self._config & self.__CONFIG_ONE_SHOT
        self._smbus.write_byte_data(self._address, self.__CONFIGURATION_REGISTER, temp_config)
        return self.read_temperature()

    def read_temperature(self):
        temp_bytes = self._smbus.read_word_data(self._address, self.__TEMPERATURE_REGISTER)
        return self._bit_int_to_temp(temp_bytes)
