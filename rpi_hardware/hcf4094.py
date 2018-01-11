class HCF4094(object):
    """
    Drives HCF4094 shift register with external pull up resistors
    to high voltage and N-MOSFET pulling down to ground.

    HCF4094 is capable of higher voltages than RPi interface (I'm using 12V.)
    This allows a more robust signal line, but requires isolation with RPi.

    I'm driving base of DMN3404 N-MOSFET through 100R resistor.
    Base is pulled to Ground via 10K resistor.
    Drain is connected directly to output for each of the 4 pins and via 4.7K resistor to 12V.
    Source is connected to ground.

    I am chaining 6 boards with each having 6 HCF4094 devices.  This allows 288 outputs.
    Chaining HCF4094 requires nothing different in software, with exception of larger data for shift_data.
    """

    # Due to N-MOSFET Pulling down, logic is reversed
    _OUTPUT_HIGH = 0
    _OUTPUT_LOW = 1

    def __init__(self, gpio_ref, data_gpio, clock_gpio, strobe_gpio, out_enable_gpio,
                 enable_output_immediate=False):
        """
        Initialization

        :param gpio_ref:  reference to RPi.GPIO object
        :param data_gpio: data pin number
        :param clock_gpio: clock pin number
        :param strobe_gpio: strobe pin number
        :param out_enable_gpio: output enable pin number
        :return:
        """
        self._gpio = gpio_ref
        self._data_pin = data_gpio
        self._clock_pin = clock_gpio
        self._strobe_pin = strobe_gpio
        self._out_enable_pin = out_enable_gpio

        self._gpio.setup(self._data_pin, self._gpio.OUT, initial=self._OUTPUT_LOW)
        self._gpio.setup(self._clock_pin, self._gpio.OUT, initial=self._OUTPUT_LOW)
        self._gpio.setup(self._out_enable_pin, self._gpio.OUT, initial=self._OUTPUT_LOW)
        self._gpio.setup(self._strobe_pin, self._gpio.OUT, initial=self._OUTPUT_LOW)

        if enable_output_immediate:
            self.set_output_enable(True)

    def cycle_pins(self):
        """
        Iterate this method and add print out and delays to cycle output for the pins on and off.

        :return: Yields (name, pin state)
        """
        pins = ((self._data_pin, 'Data', self._OUTPUT_HIGH),
                (self._data_pin, 'Data', self._OUTPUT_LOW),
                (self._clock_pin, 'Clock', self._OUTPUT_HIGH),
                (self._clock_pin, 'Clock', self._OUTPUT_LOW),
                (self._strobe_pin, 'Strobe', self._OUTPUT_HIGH),
                (self._strobe_pin, 'Strobe', self._OUTPUT_LOW),
                (self._out_enable_pin, 'Enable', self._OUTPUT_HIGH),
                (self._out_enable_pin, 'Enable', self._OUTPUT_LOW))
        for _ in range(5):
            for pin, name, state in pins:
                self._gpio.output(pin, state)
                yield pin, name, state

    def set_output_enable(self, enable):
        """
        Set output enable pin

        :param enable: State of pin
        :return: None
        """
        output_val = self._OUTPUT_LOW
        if enable:
            output_val = self._OUTPUT_HIGH
        self._gpio.output(self._out_enable_pin, output_val)

    def shift_data(self, data):
        """
        Shifts data out, in order of the list.

        :param data: Data to be shifted as list or tuple
        :return: Bits shifted count
        """
        shift_count = 0
        self._gpio.output(self._strobe_pin, self._OUTPUT_LOW)
        for bit_value in data:
            # Inverting due to N-MOSFET inversion, also error if not 0/1.
            value = (HCF4094._OUTPUT_LOW, HCF4094._OUTPUT_HIGH)[bit_value]
            self._gpio.output(self._data_pin, value)
            self._gpio.output(self._clock_pin, self._OUTPUT_HIGH)
            self._gpio.output(self._clock_pin, self._OUTPUT_LOW)
            shift_count += 1
        self._gpio.output(self._strobe_pin, self._OUTPUT_HIGH)
        return shift_count
