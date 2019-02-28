# -*- coding:utf8 -*-
from ctypes import c_uint

class Number(object):

    def __init__(self, value):
        self.value = c_uint(value)

    @property
    def val(self):
        return self.value.value

    def __add__(self, other):
        """ self + other """
        return Number(self.val + other.val)

    def __sub__(self, other):
        """ self - other """
        return Number(self.val - other.val)

    def __mul__(self, other):
        """ self * other """
        return Number(self.val * other.val)

    def __truediv__(self, other):
        """ self / other """
        return Number(self.val // other.val)

    def __mod__(self, other):
        """ self % other """
        return Number(self.val % other.val)

    def __gt__(self, other):
        """ self > other """
        return Number(int(self.val > other.val))

    def __ge__(self, other):
        """ self >= other """
        return Number(int(self.val >= other.val))

    def __lt__(self, other):
        """ self < other """
        return Number(int(self.val < other.val))

    def __le__(self, other):
        """ self <= other """
        return Number(int(self.val <= other.val))

    def __eq__(self, other):
        """ self == other """
        return Number(int(self.val == other.val))

    def __ne__(self, other):
        """ self != other """
        return Number(int(self.val != other.val))

    def __iadd__(self, other):
        """ self += other """
        result = self.val + other.val
        return Number(result)

    def __isub__(self, other):
        """ self -= other """
        result = self.val - other.val
        return Number(result)

    def __imul__(self, other):
        """ self *= other """
        result = self.val * other.val
        return Number(result)

    def __itruediv__(self, other):
        """ self /= other """
        result = self.val / other.val
        return Number(result)

    def __and__(self, other):
        """ self & other """
        return Number(int(self.val & other.val))

    def __or__(self, other):
        """ self | other """
        return Number(int(self.val | other.val))

    def __xor__(self, other):
        """ self ^ other """
        return Number(int(self.val ^ other.val))


    def __bool__(self):
        return bool(self.value)

    def _not(self):
        return Number(0) if self.value else Number(1)

    def __repr__(self):
        return 'int ({})'.format(
            self.value
        )

    def __str__(self):
        return self.__repr__()
