class HCF4904Capture(object):
    """
    This class is used to emulate the data that is shifted to the HCF4904.

    A callback method is registered and will be called with a list of tuples (index, bit_state) for each
    output that has changed since last strobe.  This allows you to simulate hardware that occurs when the
    bit state changes.

    An example of this would be if the bit is controlling power to a device.  With a `1` bit state, you
    could simulate what actions occur when power is applied to the device.

    """

    def __init__(self, gpio_ref, data_gpio, clock_gpio, strobe_gpio, out_enable_gpio,
                 bits_list, callback):
        """
        Initialization

        Callback method details:

        One argument is given to callback method, a list of tuples (index, 0 or 1).
        index: index of bits_list which has changed since last strobe event.
        0 or 1: new state of bit.

        It is expected that you maintain old state to see if you need to trigger simulation events for what
        electrical event corresponds with that bit changing.

        :param gpio_ref:  reference to Mock.GPIO object
        :param data_gpio: data pin number
        :param clock_gpio: clock pin number
        :param strobe_gpio: strobe pin number
        :param out_enable_gpio: output enable pin number
        :param bits_list: list of bit states for current output, order is furthest to nearest bit.  As shifting
                          occurs at index 0 and finished at index ``n``.
                          This will determine initial state to trigger callbacks and bit length to maintain for data
                          Initial state usually all 0, so ``[0] * bit_depth`` might be easy initialization
        :param callback: method to call when bits change
        """
        self._gpio = gpio_ref
        self._data_pin = data_gpio
        self._clock_pin = clock_gpio
        self._strobe_pin = strobe_gpio
        self._out_enable_pin = out_enable_gpio

        test_list = [bit for bit in bits_list if bit not in (0, 1)]
        if len(test_list) != 0:
            raise ValueError('bits_list may only contain 0 or 1.  Found {}'.format(test_list))

        self._bit_count = len(bits_list)
        self.current_data = tuple(bits_list)
        self._buffered_data = []
        self._callback = callback

        # Register with Mock GPIO to call methods when clock or strobe occurs
        # We are using FALLING instead of RISING, because logic is backwards due to
        # MOSFET for output.
        self._gpio.add_event_callback(self._clock_pin, self._gpio.FALLING, self._clocked)
        self._gpio.add_event_callback(self._strobe_pin, self._gpio.FALLING, self._strobed)

    def _clocked(self):
        # Have to reverse data, as MOSFET output is backwards
        bit_value = (1, 0)[self._gpio._simulate_read_out_pin(self._data_pin)]
        self._buffered_data.append(bit_value)

    def _strobed(self):
        self._send_data()

    def _send_data(self):
        # Make list with last `self._bit_count` number of bits shifted.
        # May be called with only a few bits shifted, so need to include old data.
        new_data = (list(self.current_data) + self._buffered_data)[-self._bit_count:]
        changes = [(index, new)
                   for (index, (old, new)) in enumerate(zip(self.current_data, new_data))
                   if old != new]
        self.current_data = tuple(new_data)
        self._callback(changes)
