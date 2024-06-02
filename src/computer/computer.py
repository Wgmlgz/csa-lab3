from computer.clock import Clock
from computer.io import Stream
from computer.mem import Memory
from computer.datapath import DataPath
# from computer.cache import Cache

# class IntegratedMemorySystem:
#     def __init__(
#         self, clock: Clock, memory_size: int, cache_size: int, block_size: int
#     ):
#         self.memory = Memory(memory_size)
#         self.cache = Cache(clock, self.memory, cache_size, block_size)

#     def get(self, address: int, size: int) -> bytes:
#         return self.cache.get(address, size)

#     def set(self, address: int, data: bytes):
#         self.cache.set(address, data)

#     def flush_cache(self):
#         self.cache.flush()


class Computer:
    name: str
    memory: Memory
    cpu: DataPath

    stdin: Stream
    stdout: Stream

    descriptors: dict[int, Stream]
    word_size: int

    def __init__(self, name="AmogusPC", mem_size: int = 0x3000, word_size=8) -> None:
        self.name = name
        self.clock = Clock(1 * 1000 * 1000 * 1)
        self.memory = Memory(mem_size)
        self.cpu = DataPath(mem_size)
        self.stdin = Stream()
        self.stdout = Stream()
        self.word_size = word_size

        self.descriptors = {0: self.stdin, 1: self.stdout}

    def __str__(self) -> str:
        s = ""
        # s += f"Machine({self.name}):\n"
        # s += "  " + "Memory at ip:\n"
        # s += tab(self.memory.to_str_chunk(int.from_bytes(self.cpu.ip)), "    ")
        # s += "\n  " + "Memory at ptr:\n"
        # s += tab(self.memory.to_str_chunk(int.from_bytes(self.cpu.ptr)), "    ")
        # s += "\n  " + "Memory at stack:\n"
        # s += tab(
        #     self.memory.to_str_chunk(int.from_bytes(self.cpu.stack) - 0x40),
        #     "    ",
        # )
        # s += "  " + "\nCPU:\n"
        s += str(self.cpu)
        # s += "  " + "\nstdin:\n"
        # s += tab(str(self.stdin), "    ")
        # s += "  " + "\nstdout:\n"
        # s += tab(str(self.stdout), "    ")

        return s
