import pytest


from rpi_hardware import HCF4094
from rpi_hardware.mocked import (
    GPIO,
    HCF4094Capture,
)


OUT_EN = 20
STROBE = 19
CLOCK = 26
DATA = 21


@pytest.fixture
def capture(mocker):
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    callback = mocker.Mock()
    hcf_capture = HCF4094Capture(GPIO, DATA, CLOCK, STROBE, OUT_EN, [0]*16, callback)
    hcf = HCF4094(GPIO, DATA, CLOCK, STROBE, OUT_EN, True)
    return hcf_capture, hcf, callback


def test_buffer_length_maintained(capture):
    hcf_capture, hcf, callback = capture
    # Shift full set of 1's should get all changes
    hcf.shift_data([1]*16)
    assert len(hcf_capture._buffered_data) == 16
    hcf.shift_data([1] * 8)
    assert len(hcf_capture._buffered_data) == 16
