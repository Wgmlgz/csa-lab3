from computer.microcode import Microcode, CS


def any_to_arg(arg=0) -> bytes:
    if isinstance(arg, int):
        arg = arg.to_bytes(4)
    elif isinstance(arg, str):
        if len(arg) < 4:
            arg = (4 - len(arg)) * '\0' + arg
        arg = arg[:4]
        arg = str.encode(arg)
    return arg


instructions = {
    # does nothing
    'nop': Microcode([[]]),
    # exit(0)
    'halt': Microcode([[CS.halt]]),

    # acc = *acc
    'deref': Microcode([[CS.in_acc, CS.out_ptr], [CS.in_mem, CS.out_acc]]),

    # 'set': Microcode([[CS.in_acc, CS.out_mem]]),

    # acc = io
    # 'read': Microcode([[CS.in_io, CS.out_acc]]),
    # 'write': Microcode([[CS.in_acc, CS.out_io]]),

    'cmd->acc': Microcode([[CS.in_cmd, CS.out_acc]]),
    # 'cmd->ptr': Microcode([[CS.in_cmd, CS.out_ptr]]),
    # 'jump': Microcode([[CS.in_cmd, CS.dec, CS.out_ip]]),

    'ptr_acc': Microcode([[CS.in_acc, CS.out_ptr]]),
    'ptr_ip': Microcode([[CS.in_acc, CS.in_ip, CS.out_ptr]]),

    # ptr = acc
    'acc->ptr': Microcode([[CS.in_acc, CS.out_ptr]]),
    # stack = acc
    'acc->stack': Microcode([[CS.in_acc, CS.out_stack]]),
    'stack->acc': Microcode([[CS.in_acc, CS.out_stack]]),

    # `acc = cmd + stack`
    'stack_offset': Microcode([[CS.in_stack, CS.in_cmd, CS.out_acc]]),
    'stack_-offset': Microcode([[CS.in_cmd, CS.neg, CS.out_acc], [CS.in_stack, CS.in_acc, CS.out_acc]]),
    
    'shift_stack': Microcode([[CS.in_stack, CS.in_cmd, CS.out_stack]]),
    'unshift_stack': Microcode([[CS.in_cmd, CS.neg, CS.out_acc], [CS.in_stack, CS.in_acc, CS.out_stack]]),
  
    # `*(cmd + stack) = acc`
    'local_set': Microcode([[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_mem]]),
    # `acc = *(cmd + stack)`
    'local_get': Microcode([[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.in_mem, CS.out_acc]]),
    
    # `*(cmd) = acc`
    'global_set': Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_mem]]),
    # `acc = *(cmd)`
    'global_get': Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_mem, CS.out_acc]]),

    # ++acc
    'inc': Microcode([[CS.in_acc, CS.inc, CS.out_acc]]),
    # ++acc
    'inc8': Microcode([[CS.in_acc, CS.inc_8, CS.out_acc]]),
    # --acc
    'dec': Microcode([[CS.in_acc, CS.dec, CS.out_acc]]),
    # --acc
    'dec8': Microcode([[CS.in_acc, CS.dec_8, CS.out_acc]]),

    'inc_ip': Microcode([[CS.in_ip, CS.inc_8, CS.out_ip]]),
    'load_cmd': Microcode([[CS.in_ip, CS.out_ptr], [CS.in_mem, CS.out_cmd]]),

    # io[cmd] += acc & 0xff
    'out': Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_io]]),

    # jump
    'jmp_acc': Microcode([[CS.in_acc, CS.dec_8, CS.out_ip]]),
    'jmp': Microcode([[CS.in_cmd, CS.dec_8, CS.out_ip]]),
    'jmp_if': Microcode([[CS.in_cmd, CS.dec_8, CS.if_out, CS.out_ip]]),
    'jmp_if_false': Microcode([[CS.in_acc, CS.invert_bool, CS.out_acc], [CS.in_cmd, CS.dec_8, CS.if_out, CS.out_ip]]),

    # math
    'add_local': Microcode([[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.out_acc] ]),
    'sub_local': Microcode([[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.sub, CS.out_acc] ]),
    'mul_local': Microcode([[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.mul, CS.out_acc] ]),
    'div_local': Microcode([[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.div, CS.out_acc] ]),
    'rem_local': Microcode([[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.rem, CS.out_acc] ]),
    'invert_bool': Microcode([[CS.in_acc, CS.invert_bool, CS.out_acc]]),
}

opcode_by_tag = {idx: opcode for idx, opcode in enumerate(instructions.keys())}
tag_by_opcode = {opcode: idx for idx, opcode in enumerate(instructions.keys())}
