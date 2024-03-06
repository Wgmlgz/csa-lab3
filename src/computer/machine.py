from computer.io import Stream
from computer.mem import Memory
from computer.cpu import CPU
from utils import tab


class Machine:
    name: str
    memory: Memory
    cpu: CPU

    stdin: Stream
    stdout: Stream

    descriptors: dict[int, Stream]
    word_size: int
    
    def __init__(self, name="AmogusPC", mem_size: int = 0x10000, stack: int = 0x10000, word_size=8) -> None:
        self.name = name
        self.memory = Memory(mem_size)
        self.cpu = CPU(stack, main_ptr=0x0, reg_size=word_size)
        self.stdin = Stream('amogus test')
        self.stdout = Stream()
        self.word_size = word_size

        self.descriptors = {
            0: self.stdin,
            1: self.stdout
        }

    def __str__(self) -> str:
        s = ''
        s += f"Machine({self.name}):\n"
        s += '  ' + "Memory at ip:\n"
        s += tab(self.memory.to_str_chunk(int.from_bytes(self.cpu.ip)), '    ')
        s += '\n  ' + "Memory at ptr:\n"
        s += tab(self.memory.to_str_chunk(int.from_bytes(self.cpu.ptr)), '    ')
        s += '\n  ' + "Memory at stack:\n"
        s += tab(self.memory.to_str_chunk(int.from_bytes(self.cpu.stack) - 0x40), '    ')
        s += '  ' + "\nCPU:\n"
        s += tab(str(self.cpu))
        s += '  ' + "\nstdin:\n"
        s += tab(str(self.stdin), '    ')
        s += '  ' + "\nstdout:\n"
        s += tab(str(self.stdout), '    ')

        return s
