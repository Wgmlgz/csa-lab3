import json
from computer.instructions import any_to_arg, tag_by_opcode


class Memory:
    content: bytearray
    n: int

    def __init__(self, len: int) -> None:
        self.n = len
        self.content = bytearray(len)

    def load_instructions(self, instructions: list[list], word_size):
        idx = 0
        for j_instruction in instructions:
            entry = j_instruction[0]
            if isinstance(entry, str):
                tag = tag_by_opcode[entry]
                int_arg = 0
                if len(j_instruction) > 1:
                    int_arg = j_instruction[1]
                arg = any_to_arg(int_arg)

                instruction = tag.to_bytes(4) + arg
                self.set(idx, instruction)
                idx += word_size
            else:
                self.set(idx, int.to_bytes(entry, 1, signed=True))
                idx += 1

    def load_json(self, p: str):
        with open(p) as f:
            data = json.load(f)
            instructions = data['instructions']
            self.load_instructions(instructions, 8)

    def get(self, idx: int, size) -> bytes:
        if idx + size > self.n:
            raise Exception('reach outside memory')
        res = self.content[idx: idx + size]
        return res

    def set(self, idx: int, val: bytes):
        if idx + len(val) > self.n:
            raise Exception('reach outside memory')
        self.content[idx:idx+len(val)] = val

    def to_str_chunk(self, begin=0, len=0x40) -> str:
        s = ""
        chunk = 8
        s += '\n'.join([f'{hex(begin + i * chunk):6}' + ':' + self.content[begin + i * chunk: begin + (i + 1) * chunk].hex()
                        for i in range(len // chunk)])
        return s

    def __str__(self) -> str:
        return self.to_str_chunk(0, len(self.content))
