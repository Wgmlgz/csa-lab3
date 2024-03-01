import json
from computer.instructions import tag_by_opcode

class Memory:
    content: bytes
    n: int

    def __init__(self, len: int) -> None:
        self.n = len
        self.content = bytearray(len)

    def load_json(self, p: str):
        with open(p) as f:
            data = json.load(f)  # ok
            instructions = data['instructions']
            
            idx = 0
            for j_instruction in instructions:
                tag = tag_by_opcode.get(j_instruction[0])
                arg = 0
                if len(j_instruction) > 1:
                    arg = j_instruction[1]
                if isinstance(arg, int):
                    arg = arg.to_bytes(4)
                if isinstance(arg, str):
                    if len(arg) < 4: arg = (4 - len(arg)) * '\0' + arg
                    arg = arg[:4]
                    arg = str.encode(arg)
                instruction = tag.to_bytes(4) + arg
                self.set(idx, instruction)
                idx += 8
            
    def get(self, idx: int, size=8) -> bytes:
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
        s += '\n'.join([f'{hex(begin + i * chunk):6}' + ':' + self.content[begin + i * chunk: (i + 1) * chunk].hex()
                        for i in range(len // chunk)])
        return s
        # return f"MEM:{self.content}"
    def __str__(self) -> str:
        return self.to_str_chunk(0, len(self.content))
        # return f"MEM:{self.content}"
