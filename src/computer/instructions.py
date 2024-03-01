from computer.microcode import Microcode, CS

instructions = {
    'nop': Microcode([[]]),
    'halt': Microcode([[CS.halt]]),

    'get': Microcode([[CS.in_mem, CS.out_acc]]),
    'set': Microcode([[CS.in_acc, CS.out_mem]]),

    'read': Microcode([[CS.in_io, CS.out_acc]]),
    'write': Microcode([[CS.in_acc, CS.out_io]]),

    'load_acc': Microcode([[CS.in_cmd, CS.out_acc]]),
    'jump': Microcode([[CS.in_cmd, CS.dec, CS.out_ip]]),

    'ptr_acc': Microcode([[CS.in_acc, CS.out_ptr]]),
    'ptr_ip': Microcode([[CS.in_acc, CS.in_ip, CS.add_u64, CS.out_ptr]]),

    'inc': Microcode([[CS.in_acc, CS.inc, CS.out_acc]]),
    'dec': Microcode([[CS.in_acc, CS.dec, CS.out_acc]]),

    'inc_ip': Microcode([[CS.in_ip, CS.inc_8, CS.out_ip]]),
    'load_cmd': Microcode([[CS.in_ip, CS.out_ptr], [CS.in_mem, CS.out_cmd]]),

    'out': Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_io]])
}

opcode_by_tag = {idx: opcode for idx, opcode in enumerate(instructions.keys())}
tag_by_opcode = {opcode: idx for idx, opcode in enumerate(instructions.keys())}
