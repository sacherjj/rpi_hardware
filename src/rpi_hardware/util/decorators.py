import time
from functools import wraps


def simple_decorator(decorator):
    """
    This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.
    """
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


def cached_with_immediate(call_time):
    """
    Decorator that only calls expensive operations if past last call time.

    Can specify immediate=True to make a call ignoring cached condition.

    This is useful for using value of long running hardware processes when immediate value is not normally
    needed.  Such as a temperature conversion that can only vary much slower than code may call it.  So a
    few millisecond hardware process returns much faster if called often, as the hardware query and conversion
    is skipped.

    Using property of default _cached dictionary staying with the function definition.

    Example:
    @decorators.cached_with_immediate(call_time=30)
    def long_time_to_run_normally():
        return something_that_took_a_long_time_to_get

    call function with immediate=True to ignore caching
    """
    @simple_decorator
    def _cached_with_immediate(main_func):
        def _decorator(*args, _cached={'last_call': 0, 'value': None}, immediate=False, **kwargs):
            cur_time = time.time()
            if immediate or (cur_time - _cached['last_call']) > call_time:
                _cached['last_call'] = cur_time
                _cached['value'] = main_func(*args, **kwargs)
            return _cached['value']
        return wraps(main_func)(_decorator)
    return _cached_with_immediate
