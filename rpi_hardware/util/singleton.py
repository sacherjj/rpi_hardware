class Singleton(object):
    """
    Use to create a singleton
    """
    def __new__(cls, *args, **kwds):
        self = "__self__"
        if not hasattr(cls, self):
            instance = object.__new__(cls)
            instance._init(*args, **kwds)
            setattr(cls, self, instance)
        return getattr(cls, self)

    def _init(self, *args, **kwargs):
        raise NotImplementedError('must implement init method')

    @classmethod
    def destroy(cls):
        """
        Kills Singleton object, but objects holding reference will still have old object.

        This is mainly used to break down between tests, to assure no held common_data.
        """
        self = '__self__'
        if hasattr(cls, self):
            instance = getattr(cls, self)
            del instance
            delattr(cls, self)

