from computer.io import Stream
from computer.machine import Machine
from computer.microcode import CS, Microcode
from computer.instructions import opcode_by_tag, instructions


class Runner:
    def __init__(self, m: Machine) -> None:
        self.m = m

    def int_ptr(self) -> int:
      return int.from_bytes(self.m.cpu.ptr)
    
    def get_stream(self) -> Stream:
      return self.m.descriptors.get(self.int_ptr())
    
    def exec_tick(self, tick_cs: list[CS]):
        if CS.halt in tick_cs:
            self.m.cpu.run = False
            return

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
            input_list.append(self.get_stream())
        if CS.in_mem in tick_cs:
            input_list.append(self.m.memory.get(self.int_ptr()))
        int_list = [int.from_bytes(i) for i in input_list]

        res = 0
        
        res = sum(int_list)
        # if CS.add_u64 in tick_cs:
        if CS.inc in tick_cs:
            res += 1
        if CS.inc_8 in tick_cs:
            res += 8
        if CS.dec in tick_cs:
            res -= 1

        bytes_res = res.to_bytes(8)
        if CS.out_acc in tick_cs:
            self.m.cpu.acc = bytes_res
        if CS.out_ptr in tick_cs:
            self.m.cpu.ptr = bytes_res
        if CS.out_cmd in tick_cs:
            self.m.cpu.cmd = bytes_res
        if CS.out_ip in tick_cs:
            self.m.cpu.ip = bytes_res
        if CS.out_io in tick_cs:
            self.get_stream().write(chr(bytes_res[-1]))
        if CS.out_mem in tick_cs:
            self.m.memory.set(self.int_ptr(), bytes_res)


    def exec_instr(self, instr: Microcode):
      for tick_cs in instr.cs:
        self.exec_tick(tick_cs)
        
    def run(self) -> None:
        self.m.cpu.run = True
        while self.m.cpu.run:
          self.exec_instr(instructions['load_cmd'])
          tag = int.from_bytes(self.m.cpu.cmd[:4])
          opcode = opcode_by_tag.get(tag)
          instr = instructions.get(opcode)
          self.exec_instr(instr)
          self.exec_instr(instructions['inc_ip'])
          