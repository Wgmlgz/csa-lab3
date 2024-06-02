from computer.microcode import Microcode, CS


def any_to_arg(arg: int | str = 0) -> bytes:
    if isinstance(arg, int):
        res = arg.to_bytes(4, signed=True)
    elif isinstance(arg, str):
        if len(arg) < 4:
            t = (4 - len(arg)) * "\0" + arg
        s = t[:4]
        res = str.encode(s)
    return res


instructions = {
    # does nothing
    "nop": Microcode([[]]),
    # exit(0)
    "halt": Microcode([[CS.halt]]),
    # acc = *acc
    "deref": Microcode([[CS.in_acc, CS.out_ptr], [CS.in_mem, CS.out_acc]]),
    "deref_4": Microcode([[CS.in_acc, CS.out_ptr], [CS.in_mem, CS.s_4, CS.out_acc]]),
    "deref_2": Microcode([[CS.in_acc, CS.out_ptr], [CS.in_mem, CS.s_2, CS.out_acc]]),
    "deref_1": Microcode([[CS.in_acc, CS.out_ptr], [CS.in_mem, CS.s_1, CS.out_acc]]),
    "write_by_local": Microcode(
        [
            [CS.in_stack, CS.in_cmd, CS.out_ptr],
            [CS.in_mem, CS.out_ptr],
            [CS.in_acc, CS.out_mem],
        ]
    ),
    "write_by_local_4": Microcode(
        [
            [CS.in_stack, CS.in_cmd, CS.out_ptr],
            [CS.in_mem, CS.out_ptr],
            [CS.in_acc, CS.s_4, CS.out_mem],
        ]
    ),
    "write_by_local_2": Microcode(
        [
            [CS.in_stack, CS.in_cmd, CS.out_ptr],
            [CS.in_mem, CS.out_ptr],
            [CS.in_acc, CS.s_2, CS.out_mem],
        ]
    ),
    "write_by_local_1": Microcode(
        [
            [CS.in_stack, CS.in_cmd, CS.out_ptr],
            [CS.in_mem, CS.out_ptr],
            [CS.in_acc, CS.s_1, CS.out_mem],
        ]
    ),
    # 'set': Microcode([[CS.in_acc, CS.out_mem]]),
    # acc = io
    # 'read': Microcode([[CS.in_io, CS.out_acc]]),
    # 'write': Microcode([[CS.in_acc, CS.out_io]]),
    "load": Microcode([[CS.in_cmd, CS.out_acc]]),
    # 'cmd->ptr': Microcode([[CS.in_cmd, CS.out_ptr]]),
    # 'jump': Microcode([[CS.in_cmd, CS.dec, CS.out_ip]]),
    "ptr_acc": Microcode([[CS.in_acc, CS.out_ptr]]),
    "ptr_ip": Microcode([[CS.in_acc, CS.in_ip, CS.out_ptr]]),
    # ptr = acc
    "acc->ptr": Microcode([[CS.in_acc, CS.out_ptr]]),
    # stack = acc
    "acc->stack": Microcode([[CS.in_acc, CS.out_stack]]),
    "stack->acc": Microcode([[CS.in_acc, CS.out_stack]]),
    # `acc = cmd + stack`
    "stack_offset": Microcode([[CS.in_stack, CS.in_cmd, CS.out_acc]]),
    "stack_-offset": Microcode(
        [[CS.in_cmd, CS.neg, CS.out_acc], [CS.in_stack, CS.in_acc, CS.out_acc]]
    ),
    "shift_stack": Microcode([[CS.in_stack, CS.in_cmd, CS.out_stack]]),
    "unshift_stack": Microcode(
        [[CS.in_cmd, CS.neg, CS.out_acc], [CS.in_stack, CS.in_acc, CS.out_stack]]
    ),
    # `acc = (cmd + stack)`
    "local_ptr": Microcode([[CS.in_stack, CS.in_cmd, CS.out_acc]]),
    # `*(cmd + stack) = acc`
    "local_set": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_mem]]
    ),
    # `acc = *(cmd + stack)`
    "local_get": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.in_mem, CS.out_acc]]
    ),
    "local_set_4": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_4, CS.in_acc, CS.out_mem]]
    ),
    "local_get_4": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_4, CS.in_mem, CS.out_acc]]
    ),
    "local_set_2": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_2, CS.in_acc, CS.out_mem]]
    ),
    "local_get_2": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_2, CS.in_mem, CS.out_acc]]
    ),
    "local_set_1": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_1, CS.in_acc, CS.out_mem]]
    ),
    "local_get_1": Microcode(
        [[CS.in_stack, CS.in_cmd, CS.out_ptr], [CS.s_1, CS.in_mem, CS.out_acc]]
    ),
    # `*(cmd) = acc`
    "global_set": Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_mem]]),
    # `acc = *(cmd)`
    "global_get": Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_mem, CS.out_acc]]),
    # ++acc
    "inc": Microcode([[CS.in_acc, CS.inc, CS.out_acc]]),
    # ++acc
    "inc8": Microcode([[CS.in_acc, CS.inc_8, CS.out_acc]]),
    # --acc
    "dec": Microcode([[CS.in_acc, CS.dec, CS.out_acc]]),
    # --acc
    "dec8": Microcode([[CS.in_acc, CS.dec_8, CS.out_acc]]),
    "inc_ip": Microcode([[CS.in_ip, CS.inc_8, CS.out_ip]]),
    "load_cmd": Microcode([[CS.in_ip, CS.out_ptr], [CS.in_mem, CS.out_cmd]]),
    # io[cmd] += acc & 0xff
    "out": Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_acc, CS.out_io]]),
    "in": Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_io, CS.s_1, CS.out_acc]]),
    "io_status": Microcode([[CS.in_cmd, CS.out_ptr], [CS.in_io_status, CS.out_acc]]),
    # jump
    "jmp_acc": Microcode([[CS.in_acc, CS.dec_8, CS.out_ip]]),
    "jmp": Microcode([[CS.in_cmd, CS.dec_8, CS.out_ip]]),
    "jmp_if": Microcode([[CS.in_cmd, CS.dec_8, CS.if_acc, CS.out_ip]]),
    "jmp_if_false": Microcode(
        [
            [CS.in_acc, CS.invert_bool, CS.out_acc],
            [CS.in_cmd, CS.dec_8, CS.if_acc, CS.out_ip],
        ]
    ),
    # math
    "add_cmd": Microcode([[CS.in_cmd, CS.in_acc, CS.out_acc]]),
    "add_local": Microcode(
        [[CS.in_cmd, CS.in_stack, CS.out_ptr], [CS.in_acc, CS.in_mem, CS.out_acc]]
    ),
    "sub_local": Microcode(
        [
            [CS.in_cmd, CS.in_stack, CS.out_ptr],
            [CS.in_acc, CS.in_mem, CS.sub, CS.out_acc],
        ]
    ),
    "mul_local": Microcode(
        [
            [CS.in_cmd, CS.in_stack, CS.out_ptr],
            [CS.in_acc, CS.in_mem, CS.mul, CS.out_acc],
        ]
    ),
    "div_local": Microcode(
        [
            [CS.in_cmd, CS.in_stack, CS.out_ptr],
            [CS.in_acc, CS.in_mem, CS.div, CS.out_acc],
        ]
    ),
    "rem_local": Microcode(
        [
            [CS.in_cmd, CS.in_stack, CS.out_ptr],
            [CS.in_acc, CS.in_mem, CS.rem, CS.out_acc],
        ]
    ),
    "invert_bool": Microcode([[CS.in_acc, CS.invert_bool, CS.out_acc]]),
    "is_neg": Microcode([[CS.in_acc, CS.is_neg, CS.out_acc]]),
}

opcode_by_tag = {idx: opcode for idx, opcode in enumerate(instructions.keys())}
tag_by_opcode = {opcode: idx for idx, opcode in enumerate(instructions.keys())}
