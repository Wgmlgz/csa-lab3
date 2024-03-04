from pprint import pprint
from typing import Optional
from computer.instructions import any_to_arg, instructions
from lang.exp import Exp, IdLiteral, IntLiteral, Nested, ParseException, StrLiteral
from lang.scope import Block, Callable, Entry, Instruction, Object, Scope, ScopeEntry, Type, void_type, u64_type
from utils import tab, config


class Executable:
    def __init__(self, instructions: list['Instruction']) -> None:
        self.instructions = instructions

    def to_dict(self):
        instructions = [instr.to_list() for instr in self.instructions]
        res = {
            'instructions': instructions
        }
        return res

# class Callable:


# class Function:
#     ret: Type
#     args: Scope

#     body: Block

#     def get_type(self) -> str:
#         args_str = ', '.join(
#             [f'{id}: {type}' for id, type in self.args.definitions.items()])
#         return f'fn ({args_str}) -> {self.ret.id}'

#     def __init__(self, parent: Scope) -> None:
#         self.args = Scope(parent)
#         self.body = Block(self.args)
#         self.ret = Type()

#     def resolve_call():
#         pass


# class

# class SyntaxTree:
# instructions:
# symbols:

# def __init__(self) -> None:
#   pass

# def compile_call(exp: Exp) -> Block:

def compile_instr(exp: Exp, scope: Scope) -> Entry:
    if not isinstance(exp, Nested):
        raise ParseException('Expected expression in `( ... )`')

    if len(exp.children) < 1:
        raise ParseException('Unexpected empty expression', exp)
    id = exp.children[0]
    if not isinstance(id, IdLiteral):
        raise ParseException('Expected ', exp)

    instr = Instruction(id.val)
    if len(exp.children) > 2:
        raise ParseException('Unexpected arguments (expected 0 or)', exp)
    if len(exp.children) == 2:
        arg = exp.children[1]
        if isinstance(arg, IdLiteral):
            scope_entry = scope.get(arg.val, arg)
            instr.arg = scope_entry.obj
        elif isinstance(arg, IntLiteral) or isinstance(arg, StrLiteral):
            arg = any_to_arg(arg.val)
            instr.arg = Object(arg)
        else:
            raise ParseException('Expected string or int literal ', exp)

    return instr


# copy from a to b
def insert_copy(block: Block, a: ScopeEntry, b: ScopeEntry, exp: Exp):
    if a.type.id != b.type.id:
        raise ParseException(f'Types don\'t match {a.type.id} {b.type.id}', exp)
    if a.obj.id == b.obj.id:
        return
    if a.type.size != 0:
        block.content.append(Instruction('local_get', a.obj))
        block.content.append(Instruction('local_set', b.obj))


def compile_if(child: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    block = Block(parent, ret)
    if len(child.children) != 4 or len(child.children) < 3:
        raise ParseException(
            f'Unexpected number of arguments ({len(child.children)}) in `if` e.g. `(if cond t f)`', child)
    cond = compile_block(child.children[1], parent, glob)
    t = compile_block(child.children[2], parent, glob, block.ret)
    if len(child.children) == 4:
        f = compile_block(child.children[3], parent, glob, block.ret)
    else:
        f = Block(parent)
        f.ret.type = void_type

    if cond.ret.type.id != 'u64':
        raise ParseException(
            f'return type of `if` condition bust be `u64`', child.children[1])

    if t.ret.type.id != f.ret.type.id:
        raise ParseException(
            f'if types must match', child)

    block.ret.type = t.ret.type

    label_begin = Object()
    label_end = Object()
    block.content.append(cond)
    block.content.append(Instruction('local_get', cond.ret.obj))
    block.content.append(Instruction('jmp_if_false', label_begin))
    block.content.append(t)
    insert_copy(block, t.ret, block.ret, child)
    block.content.append(Instruction('jmp', label_end))
    block.content.append(label_begin)
    block.content.append(f)
    insert_copy(block, f.ret, block.ret, child)
    block.content.append(label_end)
    return block


def compile_while(child: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    block = Block(parent, ret)

    if len(child.children) != 3:
        raise ParseException(
            f'Unexpected number of arguments ({len(child.children)}) in `while` e.g. `(while cond body)`', child)
    cond = compile_block(child.children[1], parent, glob)
    body = compile_block(child.children[2], parent, glob, ret)

    if cond.ret.type.id != 'u64':
        raise ParseException(
            f'return type of `while` condition bust be `u64`', child.children[1])

    block.ret.type = body.ret.type

    label_begin = Object()
    label_end = Object()
    block.content.append(label_begin)
    block.content.append(cond)
    block.content.append(Instruction('local_get', cond.ret.obj))
    block.content.append(Instruction('jmp_if_false', label_end))
    block.content.append(body)
    insert_copy(block, body.ret, block.ret, child)
    block.content.append(Instruction('jmp', label_begin))
    block.content.append(label_end)
    return block


def compile_let(child: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    if len(child.children) != 3:
        raise ParseException(
            f'Expected 2 arguments e.g. `let x val`', child)
    if not isinstance(child.children[1], IdLiteral):
        raise ParseException(
            f'Expected identifier e.g. `let x val`', child.children[1])
    var_name = child.children[1].val
    body = compile_block(child.children[2], parent, glob, ret)
    parent.add(var_name, body.ret, child.children[1])
    return body


def compile_set(child: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    if len(child.children) != 3:
        raise ParseException(
            f'Expected 2 arguments e.g. `set x val`', child)
    if not isinstance(child.children[1], IdLiteral):
        raise ParseException(
            f'Expected identifier e.g. `set x val`', child.children[1])
    var_name = child.children[1].val
    var = parent.get(var_name, child.children[1])
    body = compile_block(child.children[2], parent, glob, var)
    return body


def compile_typed(exp: Exp, scope: Scope) -> tuple[str, Type]:
    if not (isinstance(exp, Nested)
            and len(exp.children) == 2
            and isinstance(exp.children[0], IdLiteral)
            and isinstance(exp.children[1], IdLiteral)):
        raise ParseException(
            f'Invalid typed declaration, expected `(name type)`', exp)
    name = exp.children[0].val
    type = scope.get_type(exp.children[1].val, exp.children[1])
    return name, type


def compile_fn(exp: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    if len(exp.children) < 3:
        raise ParseException(
            f'Expected at least 3 arguments e.g. `fn name (body)`, found({len(exp.children)})', exp)

    if not isinstance(exp.children[1], IdLiteral):
        raise ParseException(
            f'Expected function name e.g. `fn name ((arg1 type1)...) (body)``', exp.children[1])
    fn_name = exp.children[1].val

    signature_def = exp.children[2:-1]
    if len(signature_def) > 0:
        if isinstance(signature_def[-1], IdLiteral):
            ret_type = parent.get_type(
                signature_def[-1].val, signature_def[-1])
            args_def = signature_def[:-1]
        else:
            ret_type = void_type
            args_def = signature_def

    block = Block(glob)
    block.ret.type = ret_type
    ret_entry = ScopeEntry(u64_type)
    block.scope.add('ret_addr', ret_entry, exp)

    for child in args_def:
        name, type = compile_typed(child, parent)
        block.scope.add(name, ScopeEntry(type), child)
    fn_type = Callable(
        [val.type for key, val in block.scope.locals.items() if key != 'ret_addr'], ret_type)
    fn_label = ScopeEntry(fn_type)
    fn_label.obj.name = fn_name
    glob.add(fn_name, fn_label, exp)

    # if not isinstance(exp.children[], Nested):
    #     raise ParseException(
    #         f'Expected nested args declaration e.g. `((arg1 type1)...)`', exp.children[2])

    body = compile_block(exp.children[-1], block.scope, glob, block.ret)
    block.content.append(body)

    if block.ret.type != ret_type:
        raise ParseException(
            f'Body return type `{body.ret.type.id}` don\'t match declaration type `{block.ret.type.id}`',
            exp.children[-1])

    insert_copy(block, body.ret, block.ret, child)
    block.content.append(Instruction('local_get', ret_entry.obj))
    block.content.append(Instruction('jmp_acc'))
    block.resolve_offsets(0)

    ret_block = Block(parent)
    ret_block.ret.type = fn_type
    ret_block.content.append(Instruction('cmd->acc', fn_label.obj))
    ret_block.content.append(Instruction('local_set', ret_block.ret.obj))

    ret_block.global_entries.append(fn_label.obj)
    ret_block.global_entries.append(block)

    return ret_block


binary_operators = ['+', '-', '*', '/', '%', '=', '!=', '<=', '>=']
unary_operators = ['neg', 'inv', '!']
operators = binary_operators + unary_operators


def compile_operator(exp: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    block = Block(parent, ret)
    op = exp.children[0].val
    if op in binary_operators:
        if len(exp.children) != 3:
            raise ParseException(
                f'Expected 2 arguments `({op} a b)`, found({len(exp.children)})', exp)
        a_ret = ScopeEntry(u64_type)
        b_ret = ScopeEntry(u64_type)
        block.scope.add('a', a_ret, exp)
        block.scope.add('b', b_ret, exp)
        a = compile_block(exp.children[1], block.scope, glob, a_ret)
        b = compile_block(exp.children[2], block.scope, glob, b_ret)
        if a.ret.type != u64_type:
            raise ParseException(
                f'Expected u64', exp.children[1])
        if b.ret.type != u64_type:
            raise ParseException(
                f'Expected u64', exp.children[2])
        block.content.append(a)
        block.content.append(b)
        block.content.append(Instruction('local_get', a.ret.obj))
        if op == '+':
            block.content.append(Instruction('add_local', b.ret.obj))
        elif op == '-':
            block.content.append(Instruction('sub_local', b.ret.obj))
        elif op == '*':
            block.content.append(Instruction('mul_local', b.ret.obj))
        elif op == '/':
            block.content.append(Instruction('div_local', b.ret.obj))
        elif op == '%':
            block.content.append(Instruction('rem_local', b.ret.obj))
        elif op == '=':
            block.content.append(Instruction('sub_local', b.ret.obj))
            block.content.append(Instruction('invert_bool'))
        elif op == '!=':
            block.content.append(Instruction('sub_local', b.ret.obj))
        else:
            raise ParseException(
                f'Unhandled operator ({op})`', exp)
        block.content.append(Instruction('local_set', block.ret.obj))
        block.ret.type = u64_type
    elif op in unary_operators:
        raise ParseException(
            f'Unhandled operator ({op})`', exp)
        if len(exp.children) != 2:
            raise ParseException(
                f'Expected 1 argument `({op} a)`, found({len(exp.children)})', exp)
    else:
        raise ParseException(
            f'Unhandled operator ({op})`', exp)
    return block


def compile_action(child: Nested, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    first_child = child.children[0]
    id = first_child.val
    if id in instructions.keys():
        return compile_instr(child, parent)
    elif id == 'let':
        return compile_let(child, parent, glob, ret)
    elif id == 'set':
        return compile_set(child, parent, glob, ret)
    elif id == 'if':
        return compile_if(child, parent, glob, ret)
    elif id == 'while':
        return compile_while(child, parent, glob, ret)
    elif id == 'fn':
        return compile_fn(child, parent, glob, ret)
    elif id in operators:
        return compile_operator(child, parent, glob, ret)
    else:
        # else:
        var = parent.get(id, child)
        if len(child.children) == 1 and not isinstance(var.type, Callable):
            block = Block(parent)
            block.ret.type = var.type
            if block.ret.type.size != 8:
                raise ParseException(f'only 8-byte fow now', child)
            insert_copy(block, var, block.ret, child)
            return block
        else:
            if not isinstance(var.type, Callable):
                raise ParseException(
                    f'Type `{var.type.id}` is not callable', child)

            # call stack_mem
            #
            #  ____old___
            #  PhantomBlock() ret <- stack_ptr
            #  PhantomBlock() scope ret_addr
            #  PhantomBlock() arg1
            #  PhantomBlock() arg2
            #  fn_local_block

            # call convetiont
            #
            # __old_code__
            # arg1_block
            # arg1_copy
            # arg2_block
            # arg2_copy

            block = Block(parent)
            block.ret.type = var.type.ret
            ret_addr_var = ScopeEntry(u64_type)
            ret_addr_label = Object()

            block.scope.add('ret_addr', ret_addr_var, child)

            block.content.append(Instruction('cmd->acc', ret_addr_label))
            block.content.append(Instruction('local_set', ret_addr_var.obj))

            if len(child.children[1:]) != len(var.type.args):
                raise ParseException(
                        f'Number of arguments don\'t match: {len(child.children[1:])} {len(var.type.args)}', child)
            for idx, exp in enumerate(child.children[1:]):
                arg_scope_entry = ScopeEntry(var.type.args[idx])

                arg_block = compile_block(
                    exp, block.scope, glob, arg_scope_entry)

                if arg_block.ret.type.id != arg_scope_entry.type.id:
                    raise ParseException(
                        f'types don\'t match: {arg_block.ret.type.id } {arg_scope_entry.type.id}', exp)
                block.scope.add(f'_arg{idx}', arg_scope_entry, child)
                block.content.append(arg_block)
                insert_copy(block, arg_block.ret, arg_scope_entry, exp)

            block.content.append(Instruction('shift_stack', block.before_ret))
            block.content.append(Instruction('jmp', var.obj))
            block.content.append(ret_addr_label)
            block.content.append(Instruction(
                'unshift_stack', block.before_ret))

            # ret_addr = Object()
            # block.scope.add('ret_ptr', ScopeEntry())
            # call_stack_begin = Object()

            # block.content.append(call_stack_begin)
            # for arg_block in args_blocks:
            #     block.content.append(arg_block)

            # block.ret.type = var.type
            return block


def compile_block(exp: Exp, parent: Scope, glob: Scope, ret: ScopeEntry = None) -> Block:
    block = Block(parent, ret)
    if isinstance(exp, Nested):
        if len(exp.children) > 0 and isinstance(exp.children[0],  IdLiteral):
            entry = compile_action(exp, parent, glob, block.ret)
            block.content.append(entry)
        else:
            for idx, child in enumerate(exp.children):
                if idx == len(exp.children) - 1:
                    child_ret = block.ret
                else:
                    child_ret = None
                if isinstance(child, Nested) and len(child.children) > 0 and isinstance(child.children[0],  IdLiteral):
                    entry = compile_action(child, block.scope, glob, child_ret)
                    block.content.append(entry)
                else:
                    entry = compile_block(child, block.scope, glob, child_ret)
                    block.content.append(entry)
        if len(block.content) > 0:
            last = block.content[-1]
            if isinstance(last, Block):
                block.ret.type = last.ret.type
                insert_copy(block, last.ret,
                            block.ret, exp)
    elif isinstance(exp, IntLiteral):
        block.ret.type = u64_type

        block.content.append(Instruction(
            'cmd->acc', Object(exp.val.to_bytes(4))))
        block.content.append(Instruction(
            'local_set', block.ret.obj))

    elif isinstance(exp, IdLiteral):
        variable = block.scope.get(exp.val, exp)
        block.ret.type = variable.type

        insert_copy(block, variable, block.ret, exp)
    else:
        raise ParseException('Expected block', exp=exp)
    if block.ret.type is None:
        block.ret.type = void_type
    return block


def resolve_labels(list: list[Instruction | Object], base: int) -> tuple[Instruction, int]:
    res = []
    for entry in list:
        if isinstance(entry, Instruction):
            res.append(entry)
            base += 8
        elif isinstance(entry, Object):
            entry.set(base)
    return res, base

# def get_instr_functions(parent: Scope):
#   return [
#     Function(parent)
#   ]
