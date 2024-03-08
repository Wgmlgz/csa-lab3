
from enum import auto

class CS(enumerate):
    halt = auto()

    in_flags = auto()

    in_acc = auto()
    in_ptr = auto()
    in_cmd = auto()
    in_ip = auto()
    in_io = auto()
    in_io_status = auto()
    in_mem = auto()
    in_stack = auto()

    out_flags = auto()

    out_acc = auto()
    out_ptr = auto()
    out_cmd = auto()
    out_ip = auto()
    out_io = auto()
    out_mem = auto()
    out_stack = auto()

    inc = auto()
    inc_8 = auto()
    dec_8 = auto()
    dec = auto()
    add = auto()
    sub = auto()
    mul = auto()
    invert = auto()
    invert_bool = auto()
    neg = auto()
    
    if_out = auto()
    
    div = auto()
    rem = auto()
    
    
    s_8 = auto()
    s_4 = auto()
    s_2 = auto()
    s_1 = auto()
    

class Microcode:
    cs: list[list[int]]

    def __init__(self, cs: list[list[int]]) -> None:
        self.cs = cs
