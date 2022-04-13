from decimal import Decimal


class Preset(dict):
    def __init__(self, data, khz=False):

        # Convert frequency to Decimal
        data['frequency'] = Decimal(str(data['frequency']))

        super().__init__(data)
        self.__dict__['_khz'] = khz

    def __setattr__(self, key, value):

        if not isinstance(value, Decimal):
            value = Decimal(value)

        if self._khz:
            value /= 1000
        self[key] = value

    def __getattr__(self, key):
        """
        We use getattr and will transpose the raw data to display data
        """
        try:
            return self.__dict__[key]
        except KeyError:
            pass

        if key in self:
            return self[key]*1000 if self._khz else self[key]
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, key))
