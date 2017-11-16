# This is to fake Raspberry Pi GPIO for simulation and testing.
from collections import defaultdict, deque

from ..util.singleton import Singleton


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

    # list: [dir, value]
    _pins = {2: [IN, 0],
             3: [IN, 0],
             4: [IN, 0],
             14: [IN, 0],
             15: [IN, 0],
             17: [IN, 0],
             18: [IN, 0],
             27: [IN, 0],
             22: [IN, 0],
             23: [IN, 0],
             24: [IN, 0],
             10: [IN, 0],
             9: [IN, 0],
             25: [IN, 0],
             11: [IN, 0],
             8: [IN, 0],
             7: [IN, 0],
             0: [IN, 0],
             1: [IN, 0],
             5: [IN, 0],
             6: [IN, 0],
             13: [IN, 0],
             19: [IN, 0],
             16: [IN, 0],
             26: [IN, 0],
             20: [IN, 0],
             21: [IN, 0]}

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

    _show_warnings = True

    _call_count = 0

    _valid_pins = {
        UNKNOWN: (),
        BCM: _pins.keys(),
        BOARD: _board_to_bcm.keys()
    }

    _mode = UNKNOWN
    _pin_dir = {}

    def _init(self):
        """ This is different from __init__, it is called when singleton object creation starts. """
        self._edge_callback = defaultdict(list)

    def _test_for_warning(self):
        # TODO: Add this to function calls to simulate multiple opening of GPIO
        if self._call_count > 1:
            if self._show_warnings:
                raise RuntimeWarning('This channel is already in use, continuing anyway. '
                                     'Use GPIO.setwarnings(False) to disable warnings.')

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
            raise ValueError('invalid pin number: {}'.format(pin_number))
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
        if old_value - new_value == 1:
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
        return self._pins[pin][1]

    def output(self, pin_number, value):
        if value not in (self.HIGH, self.LOW):
            raise ValueError('Illegal value. {} or {}'.format(self.LOW, self.HIGH))
        pin = self._translate_pin(pin_number)
        if self._pins[pin][0] == self.IN:
            raise ValueError('pin {} is an IN state.'.format(pin_number))
        old_value = self._pins[pin][1]
        self._pins[pin][1] = value
        # Can the callback be triggered for outputs?
        self._test_edge_callback(pin, old_value, value)

    def setwarnings(self, show_warnings):
        self._show_warnings = show_warnings

    def setmode(self, pin_numbering_style):
        if pin_numbering_style not in (self.BCM, self.BOARD):
            raise ValueError('mode should be BCM or BOARD.')
        self._call_count += 1
        self._mode = pin_numbering_style

    def setup(self, pin_number, direction):
        if pin_number not in self._valid_pins[self._mode]:
            raise ValueError('pin_number invalid.')
        if direction not in (self.IN, self.OUT):
            raise ValueError('direction should be IN or OUT.')
        self._pins[pin_number][0] = direction

    def cleanup(self, ):
        self._mode = self.UNKNOWN
        self._call_count -= 1

    def wait_for_edge(self, edge_type):
        # Hard to simulate this, as it is blocking.
        # Assume RISING or FALLING
        self._validate_edge_type(edge_type)


# class ShiftIOCapture(Component):
#     """
#     This class is used to emulate the data that is shifted to the HCF4904 boards to power
#     tablets and press button in cart.
#
#     We will send power and button events via the circuits interface.  This must be created
#     somewhere that it can be registered into the circuits tree.   Currently being created
#     in cart_hardware.py
#     """
#
#     # From cart_hardware, can I import to here without going circular?
#     SR_OUT_EN_GPIO = 20
#     SR_STROBE_GPIO = 19
#     SR_CLOCK_GPIO = 26
#     SR_DATA_GPIO = 21
#
#     def __init__(self, gpio):
#         self.gpio = gpio
#         self.shift_data = PowerShiftData()
#         self.shift_bits = deque(self.shift_data.data_bits(), maxlen=288)
#         self.gpio.add_event_callback(self.SR_CLOCK_GPIO, self.gpio.RISING, self.clocked)
#         self.gpio.add_event_callback(self.SR_STROBE_GPIO, self.gpio.RISING, self.strobed)
#
#     def clocked(self):
#         self.shift_bits.append(self.gpio._simulate_read_out_pin(self.SR_DATA_GPIO))
#         strobe = self.gpio._simulate_read_out_pin(self.SR_STROBE_GPIO)
#         if strobe == self.gpio.HIGH:
#             self.send_data()
#
#     def strobed(self):
#         self.send_data()
#
#     def send_data(self):
#         call_map = {PowerShiftData.POWER_TYPE: events.simulation_tablet_power,
#                     PowerShiftData.BUTTON_TYPE: events.simulation_tablet_button}
#         for key, value in self.shift_data._get_differences_and_update(self.shift_bits):
#             method = call_map[key.shift_mode]
#             self.fire(method(key.tablet_index, value))
#             print('Send Data: {} {}'.format(key, value))

