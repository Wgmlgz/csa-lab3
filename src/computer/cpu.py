
class CPU:
    acc: bytes
    ip: bytes
    ptr: bytes
    cmd: bytes
    stack: bytes
    
    # flags
    run: bool
    
    def __init__(self, stack: int, main_ptr = 0x00) -> None:
        self.acc = int(0).to_bytes(8)
        self.ip = main_ptr.to_bytes(8)
        self.ptr = int(0).to_bytes(8)
        self.cmd = int(0).to_bytes(8)
        self.stack = stack.to_bytes(8)
        self.run = False
        
    # def __str__(self) -> str:
    #     s = ''
    #     s += '    acc: ' + self.acc.hex() + '\n'
    #     s += '    ptr: ' + self.ptr.hex() + '\n'
    #     s += '    cmd: ' + self.cmd.hex() + '\n'
    #     s += '     ip: ' + self.ip.hex() + '\n'
    #     # s += '     ip: ' + self.cmd.hex() + '\n'
    #     return s
    def __str__(self) -> str:
        s = ''
        # s = f'{"acc":16} {"ptr":16} {"cmd":16} {"ip":16} \n'
        s += f'acc:{self.acc.hex()}   ptr:{self.ptr.hex()} cmd:{self.cmd.hex()}\n'
        s += f' ip:{self.ip.hex() } stack:{self.stack.hex()} '
        
        return s