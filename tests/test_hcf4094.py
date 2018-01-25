import mock
import pytest
import time

from rpi_hardware.mocked import GPIO
from rpi_hardware.mocked import HCF4094Capture
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
    hcf_capture = HCF4094Capture(GPIO, DATA, CLOCK, STROBE, OUT_EN, [0]*16, callback)
    hcf = HCF4094(GPIO, DATA, CLOCK, STROBE, OUT_EN, True)
    return hcf_capture, hcf, callback


@pytest.fixture
def hcf():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    hcf = HCF4094(GPIO, DATA, CLOCK, STROBE, OUT_EN, enable_output_immediate=False)
    return hcf


@pytest.fixture
def slow_hcf():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    callback = mock.Mock()
    hcf_capture = HCF4094Capture(GPIO, DATA, CLOCK, STROBE, OUT_EN, [0]*8, callback)
    hcf = HCF4094(GPIO, DATA, CLOCK, STROBE, OUT_EN,
                  enable_output_immediate=True,
                  data_pre_clock_sleep=0.05,
                  clock_high_sleep=0.1)
    return hcf_capture, hcf, callback


@pytest.mark.slow
def test_slow_hcf(slow_hcf):
    hcf_capture, hcf, callback = slow_hcf
    # Get time to see if we slowed
    start_time = time.time()
    # Shift full set of 1's should get all changes
    hcf.shift_data([1] * 8)
    end_time = time.time()
    # Verify that delays are working in HCF4094
    assert(end_time - start_time > (0.05 + 0.1) * 8)
    # Verify Operation with Delays
    callback.assert_called_with([(index, 1) for index in range(8)])


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


def test_hcf4904_pin_cycle(hcf):
    for pin, name, state in hcf.cycle_pins():
        assert state == GPIO._simulate_read_out_pin(pin)
