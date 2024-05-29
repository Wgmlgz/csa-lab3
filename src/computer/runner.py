from computer.io import Stream
from computer.computer import Computer
from computer.microcode import CS, Microcode
from computer.instructions import opcode_by_tag, instructions
from utils import config
import logging
import os


def cls():
    os.system("cls" if os.name == "nt" else "clear")


class Runner:
    def __init__(self, m: Computer) -> None:
        self.m = m
        self.instructions = 0

    def int_ptr(self) -> int:
        return int.from_bytes(self.m.cpu.ptr)

    def get_stream(self) -> Stream:
        return self.m.descriptors[self.int_ptr()]

    def exec_tick(self, tick_cs: list[int]):
        if CS.halt in tick_cs:
            self.m.cpu.run = False
            return

        op_size = self.m.word_size
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
            input_list.append(self.m.cpu.acc)
        if CS.in_ptr in tick_cs:
            input_list.append(self.m.cpu.ptr)
        if CS.in_cmd in tick_cs:
            input_list.append(self.m.cpu.cmd[4:])
        if CS.in_ip in tick_cs:
            input_list.append(self.m.cpu.ip)
        if CS.in_io in tick_cs:
            input_list.append(self.get_stream().read(op_size))
        if CS.in_io_status in tick_cs:
            input_list.append(self.get_stream().status())
        if CS.in_mem in tick_cs:
            input_list.append(self.m.memory.get(self.int_ptr(), op_size))
        if CS.in_stack in tick_cs:
            input_list.append(self.m.cpu.stack)

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

        if (CS.if_acc in tick_cs and int.from_bytes(self.m.cpu.acc) != 0) or (
            CS.if_acc not in tick_cs
        ):
            bytes_res = res.to_bytes(op_size, signed=True)
            if CS.out_acc in tick_cs:
                self.m.cpu.acc = bytes_res
            if CS.out_ptr in tick_cs:
                self.m.cpu.ptr = bytes_res
            if CS.out_cmd in tick_cs:
                self.m.cpu.cmd = bytes_res
            if CS.out_ip in tick_cs:
                self.m.cpu.ip = bytes_res
            if CS.out_io in tick_cs:
                self.get_stream().write(bytes_res[-1:])
            if CS.out_mem in tick_cs:
                self.m.memory.set(self.int_ptr(), bytes_res)
            if CS.out_stack in tick_cs:
                self.m.cpu.stack = bytes_res

    def exec_instr(self, instr: Microcode):
        for tick_cs in instr.cs:
            self.m.clock.wait_cycles(1)
            self.exec_tick(tick_cs)
            if config["debug"]:
                if self.m.clock.ticks < 1000:
                  logging.info(self.m)
            if config["interactive"]:
                input()
            logging.debug(self.m.cpu)
        self.instructions += 1

    def run(self) -> None:
        self.m.cpu.run = True
        while self.m.cpu.run:
            if config["clear"]:
                cls()

            self.m.cpu.cmd = self.m.memory.get(
                int.from_bytes(self.m.cpu.ip, signed=True), 8
            )
            # self.exec_instr(instructions['load_cmd'])

            tag = int.from_bytes(self.m.cpu.cmd[:4])
            opcode = opcode_by_tag[tag]
            instr = instructions[opcode]

            logging.debug(opcode + str(int.from_bytes(self.m.cpu.cmd[-4:])))
            self.exec_instr(instr)
            self.m.cpu.ip = (int.from_bytes(self.m.cpu.ip, signed=True) + 8).to_bytes(
                8, signed=True
            )
            # self.exec_instr(instructions['inc_ip'])
