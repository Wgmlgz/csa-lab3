from pprint import pprint
from typing import Optional
from computer.instructions import any_to_arg, instructions
from lang.exp import Exp, IdLiteral, IntLiteral, Nested, ParseException, StrLiteral
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


class Type:
    id: str
    size: int

    def __init__(self, id: str = '()', size=0) -> None:
        self.id = id
        self.size = size

    def __str__(self) -> str:
        return f'{self.id}[{self.size}]'


void_type = Type('()', 0)
u64_type = Type('u64', 8)
built_in_types = {
    '()': void_type,  # basically `void`
    'u64': u64_type,
}


class ScopeEntry:
    type: Optional[Type]
    stack_offset: 'Object'

    def __init__(self, type: Type = None) -> None:
        self.type = type
        self.stack_offset = Object()

    def __str__(self) -> str:
        s = f'{str(self.type)} at {str(self.stack_offset)}'
        return s


class Scope:
    parent: Optional['Scope']
    definitions: dict[str, ScopeEntry]

    def __init__(self, parent: Optional['Scope'] = None) -> None:
        self.parent = parent
        self.definitions = {}

    def add(self, id: str, scope_entry: ScopeEntry, exp: Exp) -> Optional[str]:
        if id in self.definitions:
            raise ParseException(
                f'Variable {id} is already defined in this scope', exp)
        self.definitions[id] = scope_entry

    def __str__(self) -> str:
        if len(self.definitions) == 0:
            return 'EmptyScope'
        s = 'Scope:\n  '
        s += '\n  '.join(f'{key}: {val.type} at {val.stack_offset}' for key,
                         val in self.definitions.items())
        return s

    def resolve_offsets(self, offset: int):
        for entry in self.definitions.values():
            if entry.stack_offset.resolved is None:
                offset -= entry.type.size
                entry.stack_offset.resolved = offset.to_bytes(4, signed=True)
        return offset

    def get(self, id: str, exp: Exp) -> ScopeEntry:
        if id in self.definitions:
            return self.definitions[id]
        elif self.parent is not None:
            return self.parent.get(id, exp)
        else:
            raise ParseException(f'Undefined variable `{id}`', exp)


static_id = 1

# Compiled but not linked instruction arg


class Object:
    id: str
    resolved: Optional[bytes]

    def __init__(self, resolved=None) -> None:
        global static_id
        self.id = str(static_id)
        static_id = static_id + 1
        self.resolved = resolved

    def __str__(self) -> str:
        s = 'o.'
        s += f'{self.id}'
        if self.resolved is not None:
            s += f':{self.resolved}'
        return s

    def __repr__(self) -> str:
        return str(self)


class Instruction:
    id: str
    arg: Optional[Object]

    def __init__(self, id: str, arg: Optional[Object] = None) -> None:
        self.id = id
        self.arg = arg

    def __str__(self) -> str:
        s = ''
        s += self.id
        if self.arg is not None:
            s += f' {str(self.arg)}'
        return s

    def __repr__(self) -> str:
        return str(self)

    def to_list(self):
        res = [self.id]
        if self.arg is not None and self.arg.resolved is not None:
            res.append(int.from_bytes(self.arg.resolved))
        return res


class Block:
    scope: Scope
    ret: ScopeEntry
    content: list['Entry']

    def __init__(self, parent: Scope) -> None:
        self.scope = Scope(parent)
        self.content = []
        self.ret = ScopeEntry()

    def __str__(self) -> str:
        s = f'Block -> {self.ret}\n'
        s += tab(str(self.scope)) + '\n[\n'
        s += tab('\n'.join([str(instr) for instr in self.content]))
        s += '\n]'
        return s

    def resolve_offsets(self, base: int) -> list[Instruction]:
        if self.ret.stack_offset.resolved is None:
            base -= self.ret.type.size
            self.ret.stack_offset.resolved = base.to_bytes(4, signed=True)

        base = self.scope.resolve_offsets(base)

        for entry in self.content:
            if isinstance(entry, Block):
                base = entry.resolve_offsets(base)
        return base

    def flatten(self) -> list[Instruction | Object]:
        res = []
        for entry in self.content:
            if isinstance(entry, Instruction):
                res.append(entry)
            elif isinstance(entry, Block):
                res.extend(entry.flatten())
            elif isinstance(entry, Object):
                res.append(entry)
        return res


Entry = Instruction | Block | Object


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
            instr.arg = scope_entry.stack_offset
        elif isinstance(arg, IntLiteral) or isinstance(arg, StrLiteral):
            arg = any_to_arg(arg.val)
            instr.arg = Object(arg)
        else:
            raise ParseException('Expected string or int literal ', exp)

    return instr


# copy from a to b
def insert_copy(block: Block, a: ScopeEntry, b: ScopeEntry):
    if a.type.size != 0:
        block.content.append(Instruction('stack_get', a.stack_offset))
        block.content.append(Instruction('stack_set', b.stack_offset))


def compile_action(child: Nested, parent: Scope) -> Block:
    first_child = child.children[0]
    id = first_child.val
    if id in instructions.keys():
        entry = compile_instr(child, parent)
        return entry
    elif id == 'setq':
        if len(child.children) != 3:
            raise ParseException(
                f'Expected 2 arguments e.g. `setq x val`', child)
        if not isinstance(child.children[1], IdLiteral):
            raise ParseException(
                f'Expected identifier e.g. `setq x val`', child.children[1])
        var_name = child.children[1].val
        body = compile_block(child.children[2], parent)
        parent.add(var_name, body.ret, child.children[1])
        return body
    elif id == 'if':
        block = Block(parent)

        if len(child.children) != 4 or len(child.children) < 3:
            raise ParseException(
                f'Unexpected number of arguments ({len(child.children)}) in `if` e.g. `(if cond t f)`', child)
        cond = compile_block(child.children[1], parent)
        body = compile_block(child.children[2], parent)
        if len(child.children) == 4:
            f = compile_block(child.children[3], parent)
        else:
            f = Block(parent)
            f.ret.type = void_type

        if cond.ret.type.id != 'u64':
            raise ParseException(
                f'return type of `if` condition bust be `u64`', child.children[1])

        if body.ret.type.id != f.ret.type.id:
            raise ParseException(
                f'if types must match', child)

        block.ret.type = body.ret.type

        label_begin = Object()
        label_end = Object()
        block.content.append(cond)
        block.content.append(Instruction('stack_get', cond.ret.stack_offset))
        block.content.append(Instruction('jmp_if_false', label_begin))
        block.content.append(body)
        insert_copy(block, body.ret, block.ret)
        block.content.append(Instruction('jmp', label_end))
        block.content.append(label_begin)
        block.content.append(f)
        insert_copy(block, f.ret, block.ret)
        block.content.append(label_end)

        # block.content.append(Object)

        return block
    elif id == 'while':
        block = Block(parent)

        if len(child.children) != 3:
            raise ParseException(
                f'Unexpected number of arguments ({len(child.children)}) in `while` e.g. `(while cond body)`', child)
        cond = compile_block(child.children[1], parent)
        body = compile_block(child.children[2], parent)

        if cond.ret.type.id != 'u64':
            raise ParseException(
                f'return type of `while` condition bust be `u64`', child.children[1])

        block.ret.type = body.ret.type

        label_begin = Object()
        label_end = Object()
        block.content.append(label_begin)
        block.content.append(cond)
        block.content.append(Instruction('stack_get', cond.ret.stack_offset))
        block.content.append(Instruction('jmp_if_false', label_end))
        block.content.append(body)
        insert_copy(block, body.ret, block.ret)
        block.content.append(Instruction('jmp', label_begin))
        block.content.append(label_end)

        return block
    else:
        var = parent.get(id, child)
        block = Block(parent)
        block.ret.type = var.type
        if block.ret.type.size != 8:
            raise ParseException(f'only 8-byte fow now', child)
        insert_copy(block, var, block.ret)
        return block
        # raise ParseException(f'Unknown action `{id}`')


def compile_block(exp: Exp, parent: Scope) -> Block:
    block = Block(parent)
    if isinstance(exp, Nested):
        if len(exp.children) > 0 and isinstance(exp.children[0],  IdLiteral):
            entry = compile_action(exp, parent)
            block.content.append(entry)
        else:
            for child in exp.children:
                if isinstance(child, Nested) and len(child.children) > 0 and isinstance(child.children[0],  IdLiteral):
                    entry = compile_action(child, block.scope)
                    block.content.append(entry)
                else:
                    entry = compile_block(child, block.scope)
                    block.content.append(entry)
        if len(block.content) > 0:
            last = block.content[-1]
            if isinstance(last, Block) and last.ret.type.size > 0:
                block.ret.type = last.ret.type
                if last.ret.type.size != 8:
                    raise ParseException('only 8 bytes lololol', last)
                insert_copy(block, last.ret,
                            block.ret)
    elif isinstance(exp, IntLiteral):
        block.ret.type = u64_type

        block.content.append(Instruction(
            'cmd->acc', Object(exp.val.to_bytes(4))))
        block.content.append(Instruction(
            'stack_set', block.ret.stack_offset))

    elif isinstance(exp, IdLiteral):
        variable = block.scope.get(exp.val, exp)
        block.ret.type = variable.type

        block.content.append(Instruction(
            'cmd->acc', variable.stack_offset))
        block.content.append(Instruction('deref'))
        block.content.append(Instruction(
            'stack_set', block.ret.stack_offset))
    else:
        raise ParseException('Expected block', exp=exp)
    if block.ret.type is None:
        block.ret.type = void_type
    return block


def resolve_labels(list: list[Instruction | Object], base: int):
    res = []
    for entry in list:
        if isinstance(entry, Instruction):
            res.append(entry)
            base += 8
        elif isinstance(entry, Object):
            entry.resolved = base.to_bytes(4)
    return res

# def get_instr_functions(parent: Scope):
#   return [
#     Function(parent)
#   ]
