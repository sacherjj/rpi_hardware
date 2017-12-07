import pytest
from rpi_hardware.mocked import smbus
from rpi_hardware.mocked import FakeDS28CM00
from rpi_hardware import DS28CM00


@pytest.fixture
def smb():
    bus = smbus.SMBus(1)
    return bus


def test_bad_byte_values(smb):
    bad_number_values = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        ds = FakeDS28CM00(smb, bad_number_values)
    bad_values = [0, -1, 256, 3, 19, 43]
    with pytest.raises(ValueError):
        ds = FakeDS28CM00(smb, bad_values)


def test_straight_read(smb):
    serial_number = [15, 45, 120, 255, 0, 192]

    fds = FakeDS28CM00(smb, serial_number)
    rds = DS28CM00(smb)
    serial = 0
    for byte in serial_number:
        serial = (serial << 8) + byte
    assert hex(serial) == rds.serial_number
