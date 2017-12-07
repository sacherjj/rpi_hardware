# This is to fake Raspberry Pi GPIO for simulation and testing.
from collections import defaultdict, deque

from rpi_hardware.util.singleton import Singleton


class FakeGPIO(Singleton):
    """
    This object can replace RPi.GPIO for testing GPIO based objects and simulating GPIO use when not on a RPi.

    Recommend designing objects to allow GPIO reference to be passed in on creation, so this can be swapped with
    GPIO reference easily.
    """
    # Constants defined in GPIO
    BCM = 11
    BOARD = 10
    BOTH = 33
    FALLING = 32
    HARD_PWM = 43
    HIGH = 1
    I2C = 42
    IN = 1
    LOW = 0
    OUT = 0
    PUD_DOWN = 21
    PUD_OFF = 20
    PUD_UP = 22
    RISING = 31
    SERIAL = 40
    SPI = 41
    UNKNOWN = -1
    VERSION = '0.6.3'  # When I developed the mock, it was against this version.

    _board_to_bcm = {3: 2,
                     5: 3,
                     7: 4,
                     8: 14,
                     10: 15,
                     11: 17,
                     12: 18,
                     13: 27,
                     15: 22,
                     16: 23,
                     18: 24,
                     19: 10,
                     21: 9,
                     22: 25,
                     23: 11,
                     24: 8,
                     26: 7,
                     27: 0,
                     28: 1,
                     29: 5,
                     31: 6,
                     32: 12,
                     33: 13,
                     35: 19,
                     36: 16,
                     37: 26,
                     38: 20,
                     40: 21}

    _valid_pins = {
        UNKNOWN: (),
        BCM: _board_to_bcm.values(),
        BOARD: _board_to_bcm.keys()
    }

    def _init(self):
        """
        This is different from __init__, it is called when singleton object creation
        starts or from cleanup to reset object.
        """
        self._mode = self.UNKNOWN
        # list: [dir, value]
        self._pins = {}
        for pin in self._board_to_bcm.values():
            self._pins[pin] = [self.IN, self.LOW]
        self._edge_callback = defaultdict(list)
        self._show_warnings = True

    def cleanup(self):
        self.destroy()

    def _validate_edge_type(self, edge_type):
        if edge_type not in (self.RISING, self.FALLING):
            raise ValueError('edge_type should be RISING or FALLING.')

    def add_event_callback(self, pin_number, edge_type, callback):
        pin = self._translate_pin(pin_number)
        self._validate_edge_type(edge_type)
        self._edge_callback[pin].append((edge_type, callback))

    def add_event_detect(self):
        raise NotImplementedError

    def event_detected(self):
        raise NotImplementedError

    def remove_event_detect(self):
        raise NotImplementedError

    def getmode(self):
        return self._mode

    def _translate_pin(self, pin_number):
        if self._mode == self.UNKNOWN:
            raise ValueError('mode has not been set.')
        if pin_number not in self._valid_pins[self._mode]:
            raise ValueError('pin_number {} is invalid for mode: {}'
                             .format(pin_number, self._mode))
        if self._mode == self.BOARD:
            return self._board_to_bcm[pin_number]
        return pin_number

    def gpio_function(self, pin_number):
        pin = self._translate_pin(pin_number)
        return self._pins[pin][0]

    def input(self, pin_number):
        pin = self._translate_pin(pin_number)
        if self._pins[pin][0] == self.OUT:
            raise ValueError('pin {} is an OUT state.'.format(pin_number))
        return self._pins[pin][1]

    def _test_edge_callback(self, pin, old_value, new_value):
        if old_value == new_value:
            return
        if old_value == self.HIGH:
            edge_type = self.FALLING
        else:
            edge_type = self.RISING

        # Perform edge callback
        for callpair in self._edge_callback[pin]:
            if callpair[0] == edge_type:
                callpair[1]()

    def _simulate_set_pin(self, pin_number, value):
        """
        Allows setting pin value even if it is an IN pin for use in simulation.

        :param pin_number: BCM or BOARD pin number, based on mode
        :param value: value of pin 0 or 1
        """
        if value not in (self.HIGH, self.LOW):
            raise ValueError('Illegal value. {} or {}'.format(self.LOW, self.HIGH))
        pin = self._translate_pin(pin_number)
        if self._pins[pin][0] == self.OUT:
            raise ValueError('pin {} is in an OUT state and should be changed with `output`, not a hidden method.'.format(pin_number))
        old_value = self._pins[pin][1]
        self._pins[pin][1] = value
        self._test_edge_callback(pin, old_value, value)

    def _simulate_read_out_pin(self, pin_number):
        """
        Allows reading of an OUT pin value, for simulation.

        :param pin_number: BCM or BOARD pin number, based on mode
        :return: value of pin 0 or 1
        """
        pin = self._translate_pin(pin_number)
        if self._pins[pin][0] == self.IN:
            raise ValueError('pin {} is in an IN state and should be read with `input`, not a hidden method.'.format(pin_number))
        return self._pins[pin][1]

    def output(self, pin_number, value):
        if value not in (self.HIGH, self.LOW):
            raise ValueError('Illegal value. {} or {}'.format(self.LOW, self.HIGH))
        pin = self._translate_pin(pin_number)
        if self._pins[pin][0] == self.IN:
            raise ValueError('pin {} is an IN state.'.format(pin_number))
        old_value = self._pins[pin][1]
        self._pins[pin][1] = value
        self._test_edge_callback(pin, old_value, value)

    def setwarnings(self, show_warnings):
        self._show_warnings = show_warnings

    def setmode(self, pin_numbering_style):
        if pin_numbering_style not in (self.BCM, self.BOARD):
            raise ValueError('mode should be BCM or BOARD.')
        self._mode = pin_numbering_style

    def setup(self, pin_number, direction, initial=None):
        pin = self._translate_pin(pin_number)
        if direction not in (self.IN, self.OUT):
            raise ValueError('direction should be IN or OUT.')
        self._pins[pin][0] = direction
        if initial:
            self._pins[pin][1] = initial

    def wait_for_edge(self, edge_type):
        # Hard to simulate this, as it is blocking.
        # Assume RISING or FALLING happens
        self._validate_edge_type(edge_type)


# Created to allow import like RPi.GPIO import.
GPIO = FakeGPIO()
