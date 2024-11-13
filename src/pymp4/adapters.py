from __future__ import annotations

from abc import ABC
from uuid import UUID

from construct import Adapter, int2byte, GreedyBytes


class ISO6392TLanguageCode(Adapter, ABC):
    def _decode(self, obj, context, path):
        return "".join([
            chr(bit + 0x60)
            for bit in (
                (obj >> 10) & 0b11111,
                (obj >> 5) & 0b11111,
                obj & 0b11111
            )
        ])

    def _encode(self, obj, context, path):
        bits = [ord(c) - 0x60 for c in obj]
        return (bits[0] << 10) | (bits[1] << 5) | bits[2]


class MaskedInteger(Adapter, ABC):
    def _decode(self, obj, context, path):
        return obj & 0x1F

    def _encode(self, obj, context, path):
        return obj & 0x1F


class UUIDBytes(Adapter, ABC):
    def _decode(self, obj, context, path):
        return UUID(bytes=obj)

    def _encode(self, obj, context, path):
        return obj.bytes


class VarBytesInteger(Adapter, ABC):
    def __init__(self, subcon=GreedyBytes, signed=True, swapped=False):
        super().__init__(subcon)
        self.signed = signed
        self.byteorder = 'little' if swapped else 'big'

    def _encode(self, obj, context, path):
        if self.signed:
            l = (8 + (obj + (obj < 0)).bit_length()) // 8
        else:
            l = max((obj.bit_length() + 7) // 8, 1)
        return obj.to_bytes(length=l, byteorder=self.byteorder, signed=self.signed)

    def _decode(self, obj, context, path):
        return int.from_bytes(obj, byteorder=self.byteorder, signed=self.signed)
