from typing import Optional
from computer.instructions import any_to_arg, instructions
from lang.exp import Exp, IdLiteral, IntLiteral, Nested, ParseException, StrLiteral
import lang.module
from lang.scope import (
    Block,
    Constants,
    Entry,
    Instruction,
    Object,
    OffsetObject,
    Scope,
    ScopeEntry,
)
from lang.type_info import (
    Callable,
    Ptr,
    Struct,
    Type,
    int_type,
    void_type,
    str_type,
    undefined_type,
)


class Executable:
    def __init__(self, instructions: list["Instruction"]) -> None:
        self.instructions = instructions

    def to_dict(self):
        instructions = [
            (instr.to_list() if isinstance(instr, Instruction) else [instr])
            for instr in self.instructions
        ]
        res = {"instructions": instructions}
        return res


def compile_instr(exp: Exp, scope: Scope) -> Entry:
    if not isinstance(exp, Nested):
        raise ParseException("Expected expression in `( ... )`")

    if len(exp.children) < 1:
        raise ParseException("Unexpected empty expression", exp)
    id = exp.children[0]
    if not isinstance(id, IdLiteral):
        raise ParseException("Expected ", exp)

    instr = Instruction(id.val)
    if len(exp.children) > 2:
        raise ParseException("Unexpected arguments (expected 0 or)", exp)
    if len(exp.children) == 2:
        arg = exp.children[1]
        if isinstance(arg, IdLiteral):
            scope_entry = scope.get(arg.val, arg)
            instr.arg = scope_entry.obj
        elif isinstance(arg, IntLiteral) or isinstance(arg, StrLiteral):
            res = any_to_arg(arg.val)
            instr.arg = Object(res)
        else:
            raise ParseException("Expected string or int literal ", exp)

    return instr


# copy from a to b
def insert_copy(
    block: Block, a: ScopeEntry, b: ScopeEntry, exp: Exp, deref=False, ptr_write=False
):
    type_a = a.type
    type_b = b.type

    if deref:
        if not isinstance(type_a, Ptr):
            raise ParseException(f"Expected pointer, but found `{type_a.id}`", exp)
        type_a = type_a.base

    if ptr_write:
        if not isinstance(type_b, Ptr):
            raise ParseException(f"Expected pointer, but found `{type_b.id}`", exp)
        type_b = type_b.base

    if type_a.id != type_b.id:
        raise ParseException(f"Types don't match `{type_a.id}` and `{type_b.id}`", exp)
    if a.obj.id == b.obj.id:
        return
    if type_a.size != b.type.size:
        raise ParseException("lol")
    size = type_b.size
    done = 0

    for shift in range((size - done) // 8):
        if deref:
            block.content.append(Instruction("local_get", a.obj))
            block.content.append(Instruction("add_cmd", Object(done)))
            block.content.append(Instruction("deref"))
        else:
            block.content.append(Instruction("local_get", OffsetObject(a.obj, done)))

        if ptr_write:
            if done != 0:
                raise ParseException(
                    "Can only copy types of sizes 8, 4, 2, 1 by pointer", exp
                )
            block.content.append(Instruction("write_by_local", b.obj))
        else:
            block.content.append(Instruction("local_set", OffsetObject(b.obj, done)))
        done += 8

    for shift in range((size - done) // 4):
        if deref:
            block.content.append(Instruction("local_get", a.obj))
            block.content.append(Instruction("add_cmd", Object(done)))
            block.content.append(Instruction("deref_4"))
        else:
            block.content.append(Instruction("local_get_4", OffsetObject(a.obj, done)))
        if ptr_write:
            if done != 0:
                raise ParseException(
                    "Can only copy types of sizes 8, 4, 2, 1 by pointer", exp
                )
            block.content.append(Instruction("write_by_local", b.obj))
        else:
            block.content.append(Instruction("local_set_4", OffsetObject(b.obj, done)))
        done += 4
    for shift in range((size - done) // 2):
        if deref:
            block.content.append(Instruction("local_get", a.obj))
            block.content.append(Instruction("add_cmd", Object(done)))
            block.content.append(Instruction("deref_2"))
        else:
            block.content.append(Instruction("local_get_2", OffsetObject(a.obj, done)))

        if ptr_write:
            if done != 0:
                raise ParseException(
                    "Can only copy types of sizes 8, 4, 2, 1 by pointer", exp
                )
            block.content.append(Instruction("write_by_local", b.obj))
        else:
            block.content.append(Instruction("local_set_2", OffsetObject(b.obj, done)))
        done += 2
    for shift in range((size - done) // 1):
        if deref:
            block.content.append(Instruction("local_get", a.obj))
            block.content.append(Instruction("add_cmd", Object(done)))
            block.content.append(Instruction("deref_1"))
        else:
            block.content.append(Instruction("local_get_1", OffsetObject(a.obj, done)))

        if ptr_write:
            if done != 0:
                raise ParseException(
                    "Can only copy types of sizes 8, 4, 2, 1 by pointer", exp
                )
            block.content.append(Instruction("write_by_local", b.obj))
        else:
            block.content.append(Instruction("local_set_1", OffsetObject(b.obj, done)))
        done += 1


# copy from *a to b
# def insert_deref(block: Block, a: ScopeEntry, b: ScopeEntry, exp: Exp):
#     if not isinstance(a.type, Ptr):
#         raise ParseException(f'Expected pointer but found `{a.type.id}`', exp)

#     if a.type.base.id != b.type.id:
#         raise ParseException(f'Types don\'t match {a.type.base.id} {b.type.id}', exp)
#     if a.obj.id == b.obj.id:
#         return
#     if a.type.size != b.type.size:
#         raise ParseException('lol')
#     size = a.type.size
#     done = 0
#     # if block.ret.type.size != 8:
#     #     raise ParseException(f'only 8-byte fow now', child)
#     # if a.type.size != 0:
#     # size =

#     for shift in range((size - done) // 8):
#         block.content.append(Instruction('local_get', OffsetObject(a.obj, done)))
#         block.content.append(Instruction('local_set', OffsetObject(b.obj, done)))
#         done += 8

#     for shift in range((size - done) // 4):
#         block.content.append(Instruction('local_get_4', OffsetObject(a.obj, done)))
#         block.content.append(Instruction('local_set_4', OffsetObject(b.obj, done)))
#         done += 4
#     for shift in range((size - done) // 2):
#         block.content.append(Instruction('local_get_2', OffsetObject(a.obj, done)))
#         block.content.append(Instruction('local_set_2', OffsetObject(b.obj, done)))
#         done += 2
#     for shift in range((size - done) // 1):
#         block.content.append(Instruction('local_get_1', OffsetObject(a.obj, done)))
#         block.content.append(Instruction('local_set_1', OffsetObject(b.obj, done)))
#         done += 1


def compile_if(
    child: Nested,
    parent: Scope,
    mod: lang.module.Module,
    ret: Optional[ScopeEntry] = None,
) -> Block:
    block = Block(parent, ret)
    if len(child.children) != 4 or len(child.children) < 3:
        raise ParseException(
            f"Unexpected number of arguments ({len(child.children)}) in `if` e.g. `(if cond t f)`",
            child,
        )
    cond = compile_block(child.children[1], parent, mod)
    t = compile_block(child.children[2], parent, mod, block.ret)
    if len(child.children) == 4:
        f = compile_block(child.children[3], parent, mod, block.ret)
    else:
        f = Block(parent)
        f.ret.type = void_type

    if cond.ret.type.id != "int":
        raise ParseException(
            "return type of `if` condition bust be `int`", child.children[1]
        )

    if t.ret.type.id != f.ret.type.id:
        raise ParseException("if types must match", child)

    block.ret.type = t.ret.type

    label_begin = Object()
    label_end = Object()
    block.content.append(cond)
    block.content.append(Instruction("local_get", cond.ret.obj))
    block.content.append(Instruction("jmp_if_false", label_begin))
    block.content.append(t)
    insert_copy(block, t.ret, block.ret, child)
    block.content.append(Instruction("jmp", label_end))
    block.content.append(label_begin)
    block.content.append(f)
    insert_copy(block, f.ret, block.ret, child)
    block.content.append(label_end)
    return block


def compile_while(
    child: Nested,
    parent: Scope,
    mod: lang.module.Module,
    ret: Optional[ScopeEntry] = None,
) -> Block:
    block = Block(parent, ret)

    if len(child.children) != 3:
        raise ParseException(
            f"Unexpected number of arguments ({len(child.children)}) in `while` e.g. `(while cond body)`",
            child,
        )
    cond = compile_block(child.children[1], parent, mod)
    body = compile_block(child.children[2], parent, mod, ret)

    if cond.ret.type.id != "int":
        raise ParseException(
            "return type of `while` condition bust be `int`", child.children[1]
        )

    block.ret.type = body.ret.type

    label_begin = Object()
    label_end = Object()
    block.content.append(label_begin)
    block.content.append(cond)
    block.content.append(Instruction("local_get", cond.ret.obj))
    block.content.append(Instruction("jmp_if_false", label_end))
    block.content.append(body)
    insert_copy(block, body.ret, block.ret, child)
    block.content.append(Instruction("jmp", label_begin))
    block.content.append(label_end)
    return block


def compile_get(
    action: str,
    child: Nested,
    parent: Scope,
    mod: lang.module.Module,
    ret: Optional[ScopeEntry] = None,
) -> Block:
    deref = False
    if action == ".":
        deref = True

    block = Block(parent, ret)

    if len(child.children) != 3:
        raise ParseException(
            f"Unexpected number of arguments ({len(child.children)}) in `{action}` e.g. `({action} ptr id)`",
            child,
        )
    ptr = compile_block(child.children[1], parent, mod)
    if not isinstance(ptr.ret.type, Ptr) or not isinstance(ptr.ret.type.base, Struct):
        raise ParseException(
            f"Expected pointer to struct, found `{ptr.ret.type.id}`", child.children[1]
        )
    struct = ptr.ret.type.base
    if not isinstance(child.children[2], IdLiteral):
        raise ParseException(
            "Expected id",
            child.children[2],
        )

    id = child.children[2].val
    if id not in struct.offsets:
        raise ParseException(
            f"Unknown member `{id}` of struct `{struct.name}`",
            child.children[2],
        )
    offset = struct.offsets[id]
    block.content.append(ptr)

    if deref:
        block.ret.type = struct.members[id]
        dereferenced = ScopeEntry(Ptr(struct.members[id]))
        block.scope.add("__dereferenced", dereferenced, child)
        block.content.append(Instruction("local_get", ptr.ret.obj))
        block.content.append(Instruction("add_cmd", Object(offset)))
        block.content.append(Instruction("local_set", dereferenced.obj))

        insert_copy(block, dereferenced, block.ret, child, deref=True)
    else:
        block.ret.type = Ptr(struct.members[id])
        block.content.append(Instruction("local_get", ptr.ret.obj))
        block.content.append(Instruction("add_cmd", Object(offset)))
        block.content.append(Instruction("local_set", block.ret.obj))

    return block


def compile_let(
    child: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(child.children) != 3:
        raise ParseException("Expected 3 arguments e.g. `let x val`", child)
    if not isinstance(child.children[1], IdLiteral):
        raise ParseException("Expected identifier e.g. `let x val`", child.children[1])
    var_name = child.children[1].val
    body = compile_block(child.children[2], parent, mod, ret)
    parent.add(var_name, body.ret, child.children[1])
    return body


def compile_def(
    child: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(child.children) != 2:
        raise ParseException("Expected 2 arguments e.g. `def (x type)`", child)
    var_name, type = compile_typed(child.children[1], parent)
    entry = ScopeEntry(type)
    parent.add(var_name, entry, child.children[1])
    return Block(parent)


def compile_set(
    child: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(child.children) != 3:
        raise ParseException("Expected 2 arguments e.g. `set x val`", child)
    if not isinstance(child.children[1], IdLiteral):
        raise ParseException("Expected identifier e.g. `set x val`", child.children[1])
    var_name = child.children[1].val
    var = parent.get(var_name, child.children[1])
    body = compile_block(child.children[2], parent, mod, var)
    return body


def compile_pset(
    exp: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(exp.children) != 3:
        raise ParseException("Expected 2 arguments e.g. `pset ptr val`", exp)
    block = Block(parent)

    ptr_calc = compile_block(exp.children[1], parent, mod)
    val_calc = compile_block(exp.children[2], parent, mod)
    block.scope.add("__tmp_ptr", ptr_calc.ret, exp)
    block.scope.add("__tmp_val", val_calc.ret, exp)

    block.content.append(ptr_calc)
    block.content.append(val_calc)

    if not isinstance(ptr_calc.ret.type, Ptr):
        raise ParseException("Expected ptr", exp.children[1])

    if ptr_calc.ret.type.base.id != val_calc.ret.type.id:
        raise ParseException("types don't match", exp.children[1])

    block.ret.type = void_type

    insert_copy(block, val_calc.ret, ptr_calc.ret, exp, ptr_write=True)
    return block


def compile_type(exp: Exp, scope: Scope) -> tuple[str, Type]:
    if not (
        isinstance(exp, Nested)
        and len(exp.children) == 2
        and isinstance(exp.children[0], IdLiteral)
        and isinstance(exp.children[1], IdLiteral)
    ):
        raise ParseException("Invalid typed declaration, expected `(name type)`", exp)
    name = exp.children[0].val
    type = scope.get_type(exp.children[1].val, exp.children[1])
    return name, type


def compile_typed(exp: Exp, scope: Scope) -> tuple[str, Type]:
    if not (
        isinstance(exp, Nested)
        and len(exp.children) == 2
        and isinstance(exp.children[0], IdLiteral)
        and isinstance(exp.children[1], IdLiteral)
    ):
        raise ParseException("Invalid typed declaration, expected `(name type)`", exp)
    name = exp.children[0].val
    type = scope.get_type(exp.children[1].val, exp.children[1])
    return name, type


def compile_fn(
    exp: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(exp.children) < 3:
        raise ParseException(
            f"Expected at least 3 arguments e.g. `fn name (body)`, found({len(exp.children)})",
            exp,
        )

    if not isinstance(exp.children[1], IdLiteral):
        raise ParseException(
            "Expected function name e.g. `fn name ((arg1 type1)...) (body)``",
            exp.children[1],
        )
    fn_name = exp.children[1].val

    signature_def = exp.children[2:-1]
    if len(signature_def) > 0:
        if isinstance(signature_def[-1], IdLiteral):
            ret_type = parent.get_type(signature_def[-1].val, signature_def[-1])
            args_def = signature_def[:-1]
        else:
            ret_type = void_type
            args_def = signature_def
    else:
        ret_type = void_type
        args_def = []

    block = Block(parent)
    block.ret.type = ret_type
    ret_entry = ScopeEntry(int_type)
    block.scope.add("ret_addr", ret_entry, exp)

    for child in args_def:
        name, type = compile_typed(child, parent)
        block.scope.add(name, ScopeEntry(type), child)
    fn_type = Callable(
        [val.type for key, val in block.scope.locals.items() if key != "ret_addr"],
        ret_type,
    )
    fn_label = ScopeEntry(fn_type)
    fn_label.obj.name = fn_name
    mod.global_scope.add(fn_name, fn_label, exp)

    # if not isinstance(exp.children[], Nested):
    #     raise ParseException(
    #         f'Expected nested args declaration e.g. `((arg1 type1)...)`', exp.children[2])

    body = compile_block(exp.children[-1], block.scope, mod, block.ret)
    block.content.append(body)

    if block.ret.type.id != ret_type.id:
        raise ParseException(
            f"Body return type `{body.ret.type.id}` don't match declaration type `{ret_type.id}`",
            exp.children[-1],
        )

    insert_copy(block, body.ret, block.ret, exp)
    block.content.append(Instruction("local_get", ret_entry.obj))
    block.content.append(Instruction("jmp_acc"))
    block.resolve_offsets(0)

    ret_block = Block(parent)
    ret_block.ret.type = void_type
    # ret_block.content.append(Instruction("load", fn_label.obj))
    # ret_block.content.append(Instruction("local_set", ret_block.ret.obj))

    ret_block.global_entries.append(fn_label.obj)
    ret_block.global_entries.append(block)

    return ret_block


binary_operators = ["+", "-", "*", "/", "%", "=", "!=", "<=", ">=", "<"]
unary_operators = ["*"]
operators = binary_operators + unary_operators


def compile_operator(
    op: str,
    exp: Nested,
    parent: Scope,
    mod: lang.module.Module,
    ret: ScopeEntry | None = None,
) -> Block:
    block = Block(parent, ret)
    if op in binary_operators and len(exp.children) == 3:
        # if :
        #     raise ParseException(
        #         f'Expected 2 arguments `({op} a b)`, found({len(exp.children)})', exp)
        ptr = ScopeEntry(int_type)
        b_ret = ScopeEntry(int_type)
        block.scope.add("__arg_a", ptr, exp)
        block.scope.add("__arg_b", b_ret, exp)
        a = compile_block(exp.children[1], block.scope, mod, ptr)
        b = compile_block(exp.children[2], block.scope, mod, b_ret)

        # only int operations for now
        if not (isinstance(a.ret.type, Ptr) or a.ret.type.id == int_type.id):
            raise ParseException("Expected 64 bit int type", exp.children[1])
        if not (isinstance(b.ret.type, Ptr) or b.ret.type.id == int_type.id):
            raise ParseException("Expected 64 bit int type", exp.children[2])

        # if a.ret.type != b.ret.type:
        #     raise ParseException(f"types, don' match", exp.children[0])
        # if b.ret.type != int_type:

        block.content.append(a)
        block.content.append(b)
        block.content.append(Instruction("local_get", a.ret.obj))
        if op == "+":
            block.content.append(Instruction("add_local", b.ret.obj))
        elif op == "-":
            block.content.append(Instruction("sub_local", b.ret.obj))
        elif op == "*":
            block.content.append(Instruction("mul_local", b.ret.obj))
        elif op == "/":
            block.content.append(Instruction("div_local", b.ret.obj))
        elif op == "%":
            block.content.append(Instruction("rem_local", b.ret.obj))
        elif op == "=":
            block.content.append(Instruction("sub_local", b.ret.obj))
            block.content.append(Instruction("invert_bool"))
        elif op == "!=":
            block.content.append(Instruction("sub_local", b.ret.obj))
        elif op == "<":
            block.content.append(Instruction("sub_local", b.ret.obj))
            block.content.append(Instruction("is_neg"))
        else:
            raise ParseException(f"Unhandled operator ({op})`", exp)
        block.content.append(Instruction("local_set", block.ret.obj))
        block.ret.type = a.ret.type
    elif op in unary_operators and len(exp.children) == 2:
        if op == "*":
            # ptr = ScopeEntry(int_type)
            # block.scope.add("ptr", ptr, exp)
            a = compile_block(exp.children[1], block.scope, mod)
            block.content.append(a)
            if not isinstance(a.ret.type, Ptr):
                raise ParseException(
                    f"Expected pointer, but found `{a.ret.type.id}`", exp.children[1]
                )
            block.ret.type = a.ret.type.base
            insert_copy(block, a.ret, block.ret, exp, deref=True)
        else:
            raise ParseException(f"Unhandled operator ({op})`", exp)
    else:
        raise ParseException(f"Unhandled operator `{op}`", exp)
    return block


def compile_import(exp: Nested, mod: lang.module.Module) -> Block:
    if len(exp.children) != 2 or not isinstance(exp.children[1], StrLiteral):
        raise ParseException(
            'Invalid import statement e.g. `(import "./path/to/file")`'
        )
    path = exp.children[1].val
    res = lang.module.Module(path, mod)
    if res.block is None:
        raise Exception("No block")
    return res.block


def compile_mem(
    exp: Nested, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    if len(exp.children) < 3:
        raise ParseException(
            f"Expected at least 3 arguments e.g. `mem type N`, found({len(exp.children)})",
            exp,
        )

    if not isinstance(exp.children[1], IdLiteral):
        raise ParseException("Expected type literal", exp.children[1])

    if not isinstance(exp.children[2], IntLiteral):
        raise ParseException("Expected int literal", exp.children[2])

    type = parent.get_type(exp.children[1].val, exp.children[1])
    length = exp.children[2].val

    block = Block(parent, ret)

    block.ret.type = Ptr(type)
    begin_ptr = Object()
    block.global_entries.append(begin_ptr)
    bytes_str = str.encode("\0" * length * type.size)
    block.global_entries.append(Constants(bytes_str))

    block.content.append(Instruction("load", begin_ptr))
    block.content.append(Instruction("local_set", block.ret.obj))

    return block


# def compile_var()
def compile_action(
    id,
    child: Nested,
    parent: Scope,
    mod: lang.module.Module,
    ret: ScopeEntry | None = None,
) -> Entry:
    if id in instructions.keys():
        return compile_instr(child, parent)
    elif id == "let":
        return compile_let(child, parent, mod, ret)
    elif id == "def":
        return compile_def(child, parent, mod, ret)
    elif id == "set":
        return compile_set(child, parent, mod, ret)
    elif id == "pset":
        return compile_pset(child, parent, mod, ret)
    elif id == "if":
        return compile_if(child, parent, mod, ret)
    elif id == "while":
        return compile_while(child, parent, mod, ret)
    elif id == "fn":
        return compile_fn(child, parent, mod, ret)
    elif id == "mem":
        return compile_mem(child, parent, mod, ret)
    elif id == "." or id == "->":
        return compile_get(id, child, parent, mod, ret)
    elif id in operators:
        return compile_operator(id, child, parent, mod, ret)
    elif id == "import":
        return compile_import(child, mod)
    else:
        # compile_var(block, )
        # else:
        var = parent.get(id, child)
        if len(child.children) == 1 and not isinstance(var.type, Callable):
            block = Block(parent)
            block.ret.type = var.type
            insert_copy(block, var, block.ret, child)
            return block
        else:
            if not isinstance(var.type, Callable):
                raise ParseException(f"Type `{var.type.id}` is not callable", child)

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
            ret_addr_var = ScopeEntry(int_type)
            ret_addr_label = Object()

            block.scope.add("ret_addr", ret_addr_var, child)

            block.content.append(Instruction("load", ret_addr_label))
            block.content.append(Instruction("local_set", ret_addr_var.obj))

            if len(child.children[1:]) != len(var.type.args):
                raise ParseException(
                    f"Number of arguments don't match: {len(child.children[1:])} {len(var.type.args)}",
                    child,
                )
            for idx, exp in enumerate(child.children[1:]):
                arg_scope_entry = ScopeEntry(var.type.args[idx])

                arg_block = compile_block(exp, block.scope, mod, arg_scope_entry)

                if arg_block.ret.type.id != var.type.args[idx].id:
                    raise ParseException(
                        f"types don't match: {arg_block.ret.type.id } {var.type.args[idx].id}",
                        exp,
                    )
                block.scope.add(f"_arg{idx}", arg_scope_entry, child)
                block.content.append(arg_block)
                insert_copy(block, arg_block.ret, arg_scope_entry, exp)

            block.content.append(Instruction("shift_stack", block.before_ret))
            block.content.append(Instruction("jmp", var.obj))
            block.content.append(ret_addr_label)
            block.content.append(Instruction("unshift_stack", block.before_ret))

            # ret_addr = Object()
            # block.scope.add('ret_ptr', ScopeEntry())
            # call_stack_begin = Object()

            # block.content.append(call_stack_begin)
            # for arg_block in args_blocks:
            #     block.content.append(arg_block)

            # block.ret.type = var.type
            return block


def compile_block(
    exp: Exp, parent: Scope, mod: lang.module.Module, ret: ScopeEntry | None = None
) -> Block:
    block = Block(parent, ret)
    if isinstance(exp, Nested):
        if len(exp.children) > 0 and isinstance(exp.children[0], IdLiteral):
            entry = compile_action(exp.children[0].val, exp, parent, mod, block.ret)
            block.content.append(entry)
        else:
            for idx, child in enumerate(exp.children):
                if idx == len(exp.children) - 1:
                    child_ret = block.ret
                else:
                    child_ret = None
                if (
                    isinstance(child, Nested)
                    and len(child.children) > 0
                    and isinstance(child.children[0], IdLiteral)
                ):
                    entry = compile_action(
                        child.children[0].val, child, block.scope, mod, child_ret
                    )
                    block.content.append(entry)
                else:
                    entry = compile_block(child, block.scope, mod, child_ret)
                    block.content.append(entry)
        if len(block.content) > 0:
            last = block.content[-1]
            if isinstance(last, Block):
                block.ret.type = last.ret.type
                insert_copy(block, last.ret, block.ret, exp)
    elif isinstance(exp, IntLiteral):
        type = parent.get_type(exp.type, exp)
        block.ret.type = type

        block.content.append(Instruction("load", Object(exp.val.to_bytes(4))))
        if type.size == 8:
            block.content.append(Instruction("local_set", block.ret.obj))
        elif type.size == 4:
            block.content.append(Instruction("local_set_4", block.ret.obj))
        elif type.size == 2:
            block.content.append(Instruction("local_set_2", block.ret.obj))
        elif type.size == 1:
            block.content.append(Instruction("local_set_1", block.ret.obj))

    elif isinstance(exp, IdLiteral):
        compile_var(block, exp)

    elif isinstance(exp, StrLiteral):
        block.ret.type = str_type
        begin_ptr = Object()
        block.global_entries.append(begin_ptr)
        bytes_str = str.encode(exp.val)
        block.global_entries.append(Constants(bytes_str))

        block.content.append(Instruction("load", begin_ptr))
        block.content.append(Instruction("local_set", block.ret.obj))

        block.content.append(Instruction("load", Object(len(bytes_str).to_bytes(4))))
        block.content.append(Instruction("local_set", OffsetObject(block.ret.obj, 8)))
        # compile_var(block, exp)
    else:
        raise ParseException("Expected block", exp=exp)
    if block.ret.type.id == undefined_type.id:
        block.ret.type = void_type
    return block


def compile_var(block: Block, exp: IdLiteral):
    var_name = exp.val
    ref = False
    if var_name.startswith("'"):
        var_name = var_name[1:]
        ref = True

    variable = block.scope.get(var_name, exp)
    if ref:
        block.ret.type = Ptr(variable.type)
        block.content.append(Instruction("local_ptr", variable.obj))
        block.content.append(Instruction("local_set", block.ret.obj))
    else:
        block.ret.type = variable.type
        insert_copy(block, variable, block.ret, exp)


def resolve_labels(
    input: list[Instruction | Object | int], base: int, word_size: int
) -> tuple[list[Instruction | int], int]:
    res: list[Instruction | int] = []
    for entry in input:
        if isinstance(entry, Instruction):
            res.append(entry)
            base += word_size
        elif isinstance(entry, int):
            res.append(entry)
            base += 1
        elif isinstance(entry, Object):
            entry.set(base)
    return res, base


# def get_instr_functions(parent: Scope):
#   return [
#     Function(parent)
#   ]
