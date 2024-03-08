from computer.clock import Clock
from computer.io import Stream
from computer.mem import Memory
from computer.cpu import CPU
from computer.cache import Cache
from utils import tab

class IntegratedMemorySystem:
    def __init__(self, clock: Clock, memory_size: int, cache_size: int, block_size: int):
        self.memory = Memory(memory_size)
        self.cache = Cache(clock, self.memory, cache_size, block_size)

    def get(self, address: int, size: int) -> bytes:
        return self.cache.get(address, size)

    def set(self, address: int, data: bytes):
        self.cache.set(address, data)

    def flush_cache(self):
        self.cache.flush()


class Machine:
    name: str
    memory: IntegratedMemorySystem
    cpu: CPU

    stdin: Stream
    stdout: Stream

    descriptors: dict[int, Stream]
    word_size: int

    
    def __init__(self, name="AmogusPC", mem_size: int = 0x1000, stack: int = 0x1000, word_size=8) -> None:
        self.name = name
        self.clock = Clock(1 * 1000 * 1000 * 1)
        self.memory = IntegratedMemorySystem(self.clock, mem_size, 64 * 8, 64)
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
        s += tab(self.memory.memory.to_str_chunk(int.from_bytes(self.cpu.ip)), '    ')
        s += '\n  ' + "Memory at ptr:\n"
        s += tab(self.memory.memory.to_str_chunk(int.from_bytes(self.cpu.ptr)), '    ')
        s += '\n  ' + "Memory at stack:\n"
        s += tab(self.memory.memory.to_str_chunk(int.from_bytes(self.cpu.stack) - 0x40), '    ')
        s += '  ' + "\nCPU:\n"
        s += tab(str(self.cpu))
        s += '  ' + "\nstdin:\n"
        s += tab(str(self.stdin), '    ')
        s += '  ' + "\nstdout:\n"
        s += tab(str(self.stdout), '    ')

        return s
