
from functools import wraps


class FakeSMBus(object):

    def __init__(self, channel):
        self.addr = channel
        self.fd = None  # We have no file descriptor, as no real device i2c file.
        self.pec = 0
        self._devices = {}

    def _register_fake_device(self, device):
        """
        Hook SMBus hardware simulating devices to FakeSMBus

        :param device: object inherited from FakeSMBusDevice
        """
        device_addr = device.smbus_addr
        if device_addr in self._devices.keys():
            raise ValueError('Device using smbus_addr: {} already registered.'.format(device_addr))
        self._devices[device_addr] = device

    def _get_device(self, smbus_addr):
        try:
            return self._devices[smbus_addr]
        except KeyError:
            raise ValueError('No device registered with smbus_addr: {}'.format(smbus_addr))

    def write_quick(self, smbus_addr):
        """ Send only the read / write bit as write. """
        self._get_device(smbus_addr).write_quick()

    def read_byte(self, smbus_addr):
        """ Read a single byte from a device, without specifying a device register. """
        self._get_device(smbus_addr).read_byte()

    def write_byte(self, smbus_addr, byte):
        """ Send a single byte to a device. """
        self._get_device(smbus_addr).write_byte(byte)

    def process_call(self, smbus_addr, register, value):
        """ Process Call transaction. """
        self._get_device(smbus_addr).process_call(register, value)

    def read_block_data(self, smbus_addr, register):
        """ Read Block Data transaction. """
        self._get_device(smbus_addr).read_block_data(register)

    def write_block_data(self, smbus_addr, register, value_list):
        """
        Write up to 32 bytes to a device.

        This function adds an initial byte indicating the length of the vals array before the vals array.

        Use write_i2c_block_data instead!
        """
        self._get_device(smbus_addr).write_block_data(register, value_list)

    def block_process_call(self, smbus_addr, register, value_list):
        """ Block Process Call transaction. """
        self._get_device(smbus_addr).block_process_call(register, value_list)

    def read_i2c_block_data(self, smbus_addr, register):
        """ Block Read transaction. """
        self._get_device(smbus_addr).read_i2c_block_data(register)

    def write_i2c_block_data(self, smbus_addr, register, value_list):
        """ Block Write transaction. """
        self._get_device(smbus_addr).write_i2c_block_data(register, value_list)

    def read_byte_data(self, smbus_addr, register):
        """ Read Byte Data transaction. """
        self._get_device(smbus_addr).read_byte(register)

    def read_word_data(self, smbus_addr, register):
        """ Read Word Data transaction. """
        self._get_device(smbus_addr).read_word(register)

    def write_byte_data(self, smbus_addr, register, value):
        """ Write Byte Data transaction. """
        self._get_device(smbus_addr).write_byte(register)

    def write_word_data(self, smbus_addr, register, value):
        """ Write Word Data transaction. """
        self._get_device(smbus_addr).write_word(register)


class FakeSMBusDevice(object):
    """
    Base object for FakeSMBus hardware objects.  
    
    These must be attached to FakeSMBus with _register_fake_device by calling super.__init__
    """
    def __init__(self, smbus, device_addr):
        self.device_addr = device_addr
        smbus._register_fake_device(self.device_addr)

    def write_quick(self, smbus_addr):
        raise NotImplementedError

    def read_byte(self, smbus_addr):
        raise NotImplementedError

    def write_byte(self, smbus_addr, byte):
        raise NotImplementedError

    def process_call(self, smbus_addr, register, value):
        raise NotImplementedError

    def read_block_data(self, smbus_addr, register):
        raise NotImplementedError

    def write_block_data(self, smbus_addr, register, value_list):
        raise NotImplementedError

    def block_process_call(self, smbus_addr, register, value_list):
        raise NotImplementedError

    def read_i2c_block_data(self, smbus_addr, register):
        raise NotImplementedError

    def write_i2c_block_data(self, smbus_addr, register, value_list):
        raise NotImplementedError

    def read_byte_data(self, smbus_addr, register):
        raise NotImplementedError

    def read_word_data(self, smbus_addr, register):
        raise NotImplementedError

    def write_byte_data(self, smbus_addr, register, value):
        raise NotImplementedError

    def write_word_data(self, smbus_addr, register, value):
        raise NotImplementedError
