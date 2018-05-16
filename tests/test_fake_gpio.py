import mock
import pytest

from rpi_hardware.mocked import GPIO

# Note GPIO works like RPi.GPIO.  It is a singleton and only one is allowed.
# All test methods will alter it.
# Using fixtures with .cleanup() to restore.


@pytest.fixture
def raw():
    GPIO.cleanup()


@pytest.fixture
def bcm():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)


@pytest.fixture
def board():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)


def test_pin_mode_not_set(raw):
    with pytest.raises(ValueError):
        GPIO.gpio_function(3)
    with pytest.raises(ValueError):
        GPIO.input(3)
    with pytest.raises(ValueError):
        GPIO.output(3, GPIO.HIGH)


def test_pin_is_input(bcm):
    assert GPIO._pin_is_input(4) is True
    GPIO.setup(4, GPIO.OUT)
    assert GPIO._pin_is_input(4) is False


def test_mode(raw):
    assert GPIO.getmode() == GPIO.UNKNOWN
    GPIO.setmode(GPIO.BOARD)
    assert GPIO.getmode() == GPIO.BOARD
    GPIO.setmode(GPIO.BCM)
    assert GPIO.getmode() == GPIO.BCM


def test_gpio_function(bcm):
    assert GPIO.gpio_function(5) == GPIO.IN
    GPIO.setup(5, GPIO.OUT)
    assert GPIO.gpio_function(5) == GPIO.OUT


def test_gpio_setup_initial(bcm):
    assert GPIO.gpio_function(7) == GPIO.IN
    GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH)
    assert GPIO.gpio_function(7) == GPIO.OUT
    assert GPIO._simulate_read_out_pin(7) == GPIO.HIGH


def test_validate_edge_type(bcm):
    GPIO._validate_edge_type(GPIO.RISING)
    GPIO._validate_edge_type(GPIO.FALLING)
    with pytest.raises(ValueError):
        GPIO._validate_edge_type(GPIO.IN)


def test_input(board):
    # Should be default state.
    GPIO.setup(40, GPIO.IN)
    assert GPIO.input(40) == GPIO.LOW
    GPIO._simulate_set_pin(40, GPIO.HIGH)
    assert GPIO.input(40) == GPIO.HIGH
    GPIO._simulate_set_pin(40, GPIO.LOW)
    assert GPIO.input(40) == GPIO.LOW


def test_validate_output(bcm):
    pin = 4
    GPIO.setup(pin, GPIO.IN)
    with pytest.raises(ValueError):
        # Setup as input error
        GPIO._validate_output(pin, GPIO.HIGH)
    GPIO.setup(pin, GPIO.OUT)
    with pytest.raises(ValueError):
        not_high_or_low = 2
        GPIO._validate_output(pin, not_high_or_low)


def test_output(bcm):
    GPIO.setup(0, GPIO.OUT, initial=GPIO.HIGH)
    assert GPIO._simulate_read_out_pin(0) == GPIO.HIGH
    GPIO.output(0, GPIO.LOW)
    assert GPIO._simulate_read_out_pin(0) == GPIO.LOW
    GPIO.output(0, GPIO.HIGH)
    assert GPIO._simulate_read_out_pin(0) == GPIO.HIGH


def test_rising_callback(board):
    func = mock.Mock()
    GPIO.setup(38, GPIO.OUT, initial=GPIO.LOW)
    GPIO.add_event_callback(38, GPIO.RISING, func)
    GPIO.output(38, GPIO.HIGH)
    func.assert_called_with()


def test_falling_callback(bcm):
    func = mock.Mock()
    GPIO.setup(6, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.add_event_callback(6, GPIO.FALLING, func)
    GPIO.output(6, GPIO.LOW)
    func.assert_called_with()
