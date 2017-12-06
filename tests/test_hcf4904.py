import mock
import pytest
from rpi_hardware.mocked import GPIO
from rpi_hardware.mocked import HCF4904Capture
from rpi_hardware import HCF4094

OUT_EN = 20
STROBE = 19
CLOCK = 26
DATA = 21


@pytest.fixture
def capture():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    callback = mock.Mock()
    hcf_capture = HCF4904Capture(GPIO, DATA, CLOCK, STROBE, OUT_EN, [0]*16, callback)
    hcf = HCF4094(GPIO, DATA, CLOCK, STROBE, OUT_EN, True)
    return hcf_capture, hcf, callback


def test_hcf_capture_send_data_internal(capture):
    hcf_capture, hcf, callback = capture
    hcf_capture._buffered_data = [1]
    hcf_capture._send_data()
    callback.assert_called_with([(15, 1)])

    hcf_capture._buffered_data = [1]*16
    hcf_capture._send_data()
    callback.assert_called_with([(index, 1) for index in range(15)])


def test_hcf4904_shift_data(capture):
    hcf_capture, hcf, callback = capture
    # Shift full set of 1's should get all changes
    hcf.shift_data([1]*16)
    callback.assert_called_with([(index, 1) for index in range(16)])
    # Partial shift
    hcf.shift_data([0, 1, 0, 1])
    callback.assert_called_with([(12, 0), (14, 0)])
