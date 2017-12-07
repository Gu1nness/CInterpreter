class Number(object):
    types = dict(char=int, int=int, float=float, double=float)
    order = ('char', 'int', 'float', 'double')

    def __init__(self, ttype, value):
        self.type = ttype
        self.value = value

    def _calc_type(self, other):
        left_order = Number.order.index(self.type)
        right_order = Number.order.index(other.type)
        return Number.order[max(left_order, right_order)]

    def __add__(self, other):
        ttype = self._calc_type(other)
        ctype = Number.types[ttype]
        return Number(ttype, ctype(self.value) + ctype(other.value))

    def __sub__(self, other):
        ttype = self._calc_type(other)
        ctype = Number.types[ttype]
        return Number(ttype, ctype(self.value) - ctype(other.value))

    def __mul__(self, other):
        ttype = self._calc_type(other)
        ctype = Number.types[ttype]
        return Number(ttype, ctype(self.value) * ctype(other.value))

    def __truediv__(self, other):
        ttype = self._calc_type(other)
        ctype = Number.types[ttype]

        if ctype == int:
            return Number(ttype, ctype(self.value) // ctype(other.value))
        return Number(ttype, ctype(self.value) / ctype(other.value))

    def __mod__(self, other):
        ttype = self._calc_type(other)
        ctype = Number.types[ttype]
        if ctype != int:
            raise TypeError("invalid operands of types '{}' and '{}' to binary ‘operator %’".format(
                self.type,
                other.type
            ))
        return Number(ttype, ctype(self.value) % ctype(other.value))

    def __repr__(self):
        return '{} ({})'.format(
            self.type,
            self.value
        )

    def __str__(self):
        return self.__repr__()
#
#
# a = Number('char', 1)
# b = Number('int', 2)
# c = Number('float', 3.0)
# d = Number('double', 4.1)
#
# print(b % a)

def asd():
    print("asd")

import math

print(callable(math))