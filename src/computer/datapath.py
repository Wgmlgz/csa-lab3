from computer.clock import Clock
from computer.io import Stream
from computer.mem import Memory
from computer.microcode import CS, Microcode
from computer.instructions import opcode_by_tag, instructions
from utils import config
import logging
import os


def cls():
    os.system("cls" if os.name == "nt" else "clear")

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


class DataPath:
    name: str
    memory: Memory

    stdin: Stream
    stdout: Stream

    descriptors: dict[int, Stream]
    word_size: int
    
    acc: bytes
    ip: bytes
    ptr: bytes
    cmd: bytes
    stack: bytes

    # flags
    run: bool

    def regs_str(self) -> str:
        return f"acc:{self.acc.hex()} ptr:{self.ptr.hex()} cmd:{self.cmd.hex()} ip:{self.ip.hex() } stack:{self.stack.hex()}"

    def __init__(
        self, name="AmogusPC", mem_size: int = 0x3000, stack: int = 0x3000, word_size=8
    ) -> None:
        self.name = name
        self.clock = Clock(1 * 1000 * 1000 * 1)
        self.memory = Memory(mem_size)
        
        self.acc = int(0).to_bytes(word_size)
        self.ip = int(0).to_bytes(word_size)
        self.ptr = int(0).to_bytes(word_size)
        self.cmd = int(0).to_bytes(word_size)
        self.stack = stack.to_bytes(word_size)
        self.run = False
        self.stdin = Stream()
        self.stdout = Stream()
        self.word_size = word_size

        self.descriptors = {0: self.stdin, 1: self.stdout}
    

    def __str__(self) -> str:
        s = ""
        # s += f"Machine({self.name}):\n"
        # s += "  " + "Memory at ip:\n"
        # s += tab(self.memory.to_str_chunk(int.from_bytes(self.ip)), "    ")
        # s += "\n  " + "Memory at ptr:\n"
        # s += tab(self.memory.to_str_chunk(int.from_bytes(self.ptr)), "    ")
        # s += "\n  " + "Memory at stack:\n"
        # s += tab(
        #     self.memory.to_str_chunk(int.from_bytes(self.stack) - 0x40),
        #     "    ",
        # )
        # s += "  " + "\nCPU:\n"
        s += self.regs_str()
        # s += "  " + "\nstdin:\n"
        # s += tab(str(self.stdin), "    ")
        # s += "  " + "\nstdout:\n"
        # s += tab(str(self.stdout), "    ")

        return s

    def int_ptr(self) -> int:
        return int.from_bytes(self.ptr)

    def get_stream(self) -> Stream:
        return self.descriptors[self.int_ptr()]

    def exec_tick(self, tick_cs: list[int]):
        if CS.halt in tick_cs:
            self.run = False
            return

        op_size = self.word_size
        if CS.s_8 in tick_cs:
            op_size = 8
        if CS.s_4 in tick_cs:
            op_size = 4
        if CS.s_2 in tick_cs:
            op_size = 4
        if CS.s_1 in tick_cs:
            op_size = 1

        input_list: list[bytes] = []
        if CS.in_acc in tick_cs:
            input_list.append(self.acc)
        if CS.in_ptr in tick_cs:
            input_list.append(self.ptr)
        if CS.in_cmd in tick_cs:
            input_list.append(self.cmd[4:])
        if CS.in_ip in tick_cs:
            input_list.append(self.ip)
        if CS.in_io in tick_cs:
            input_list.append(self.get_stream().read(op_size))
        if CS.in_io_status in tick_cs:
            input_list.append(self.get_stream().status())
        if CS.in_mem in tick_cs:
            input_list.append(self.memory.get(self.int_ptr(), op_size))
        if CS.in_stack in tick_cs:
            input_list.append(self.stack)

        input_list = [i[-op_size:] for i in input_list]
        int_list = [int.from_bytes(i, signed=True) for i in input_list]

        if (
            CS.div in tick_cs
            or CS.rem in tick_cs
            or CS.sub in tick_cs
            or CS.mul in tick_cs
        ):
            if int_list[1] == 0:
                pass

            if len(int_list) != 2:
                raise RuntimeError(
                    "you have destroyed and betrayed yourself for nothing"
                )
            if CS.div in tick_cs:
                res = int_list[0] // int_list[1]
            if CS.rem in tick_cs:
                res = int_list[0] % int_list[1]
            if CS.sub in tick_cs:
                res = int_list[0] - int_list[1]
            if CS.mul in tick_cs:
                res = int_list[0] * int_list[1]
        else:
            res = 0
            res = sum(int_list)
            # if CS.add_int in tick_cs:
            if CS.inc in tick_cs:
                res += 1
            if CS.inc_8 in tick_cs:
                res += 8
            if CS.dec_8 in tick_cs:
                res -= 8
            if CS.dec in tick_cs:
                res -= 1
            if CS.invert in tick_cs:
                res = ~res
            if CS.neg in tick_cs:
                res = -res
            if CS.invert_bool in tick_cs:
                res = res == 0
            if CS.is_neg in tick_cs:
                res = int(res < 0)

        if (CS.if_acc in tick_cs and int.from_bytes(self.acc) != 0) or (
            CS.if_acc not in tick_cs
        ):
            bytes_res = res.to_bytes(op_size, signed=True)
            if CS.out_acc in tick_cs:
                self.acc = bytes_res
            if CS.out_ptr in tick_cs:
                self.ptr = bytes_res
            if CS.out_cmd in tick_cs:
                self.cmd = bytes_res
            if CS.out_ip in tick_cs:
                self.ip = bytes_res
            if CS.out_io in tick_cs:
                self.get_stream().write(bytes_res[-1:])
            if CS.out_mem in tick_cs:
                self.memory.set(self.int_ptr(), bytes_res)
            if CS.out_stack in tick_cs:
                self.stack = bytes_res

    def exec_instr(self, instr: Microcode):
        for tick_cs in instr.cs:
            self.clock.wait_cycles(1)
            self.exec_tick(tick_cs)
            if config["interactive"]:
                logging.debug(self)
                input()
            logging.debug(self)

    def power_on(self) -> None:
        self.run = True
        while self.run:
            if config["clear"]:
                cls()

            self.cmd = self.memory.get(
                int.from_bytes(self.ip, signed=True), 8
            )
            # self.exec_instr(instructions['load_cmd'])

            tag = int.from_bytes(self.cmd[:4])
            opcode = opcode_by_tag[tag]
            instr = instructions[opcode]

            logging.debug(opcode + str(int.from_bytes(self.cmd[-4:])))
            self.exec_instr(instr)  
            self.ip = (int.from_bytes(self.ip, signed=True) + 8).to_bytes(
                8, signed=True
            )
            # self.exec_instr(instructions['inc_ip'])
