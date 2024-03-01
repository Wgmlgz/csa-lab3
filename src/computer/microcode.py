
from enum import auto

class CS(enumerate):
    halt = auto()

    in_flags = auto()

    in_acc = auto()
    in_ptr = auto()
    in_cmd = auto()
    in_ip = auto()
    in_io = auto()
    in_mem = auto()

    out_flags = auto()

    out_acc = auto()
    out_ptr = auto()
    out_cmd = auto()
    out_ip = auto()
    out_io = auto()
    out_mem = auto()

    inc = auto()
    inc_8 = auto()
    dec = auto()
    add_u64 = auto()


class Microcode:
    cs: list[list[CS]]

    def __init__(self, cs: list[list[CS]]) -> None:
        self.cs = cs
