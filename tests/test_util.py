import pytest
import time

from src.rpi_hardware.util.singleton import Singleton
from src.rpi_hardware.util.decorators import cached_with_immediate


class SingletonTest(Singleton):
    def _init(self, store_value):
        """ Run when singleton is created.  We can use to test if run only once. """
        self.store_value = store_value


def test_multiple_singleton_are_same():
    """
    Verify that singleton returns the same object for multiple instantiations.
    """
    single_a = SingletonTest('Loaded with A')
    single_b = SingletonTest('Loaded with B')
    assert single_a is single_b
    assert single_b.store_value == 'Loaded with A'


@cached_with_immediate(call_time=1)  # Will cache for 2 seconds
def get_time():
    time.sleep(0.01)  # Assure time changes between calls
    return float(time.time())


@pytest.mark.slow
def test_cached_with_immediate():
    time_a = get_time()  # Should be current
    time_b = get_time()  # Should be cached time_a
    assert time_a == time_b

    # Sleep past cache and see value change
    time.sleep(1)
    time_c = get_time()
    assert time_c > time_a

    # Ignore cache and get current value
    time_d = get_time(immediate=True)
    assert time_d > time_c
