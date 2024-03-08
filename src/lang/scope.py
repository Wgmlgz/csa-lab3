from typing import Optional
from lang.exp import Exp, ParseException
from lang.types import Type, undefined_type
from utils import tab


class ScopeEntry:
    type: Type
    obj: "Object"

    def __init__(self, type: Type = undefined_type) -> None:
        self.type = type
        self.obj = Object()

    def __str__(self) -> str:
        s = f"{str(self.type)} at {str(self.obj)}"
        return s


class Scope:
    parent: Optional["Scope"]
    locals: dict[str, ScopeEntry]
    types: dict[str, Type]

    def __init__(self, parent: Optional["Scope"] = None) -> None:
        self.parent = parent
        self.locals = {}
        self.types = {}

    def add(self, id: str, scope_entry: ScopeEntry, exp: Exp):
        if id in self.locals:
            raise ParseException(
                f"Variable {id} is already defined in this scope", exp)
        self.locals[id] = scope_entry

    def get(self, id: str, exp: Exp) -> ScopeEntry:
        if id in self.locals:
            return self.locals[id]
        elif self.parent is not None:
            return self.parent.get(id, exp)
        else:
            raise ParseException(f"Undefined variable `{id}`", exp)

    def add_type(self, id: str, type_entry: Type, exp: Optional[Exp]):
        if id in self.types:
            raise ParseException(
                f"Type {id} is already defined in this scope", exp)
        self.types[id] = type_entry

    def get_type(self, id: str, exp: Exp) -> Type:
        if id in self.types:
            return self.types[id]
        elif self.parent is not None:
            return self.parent.get_type(id, exp)
        else:
            raise ParseException(f"Undefined type `{id}`", exp)

    def __str__(self) -> str:
        if len(self.locals) == 0 and len(self.types) == 0:
            return "EmptyScope"
        s = "Scope:\n  "
        if len(self.locals) != 0:
            s += "\n  ".join(
                f"{key}: {val.type} at {val.obj}" for key, val in self.locals.items()
            )
        if len(self.types) != 0:
            s += "\n  T: ".join(f"{key}: {str(val)}" for key,
                                val in self.types.items())
        return s

    def resolve_offsets(self, base: int):
        for entry in self.locals.values():
            if entry.obj.get() is None:
                base -= entry.type.size
                entry.obj.set(base)
        return base


static_id = 1

# Compiled but not linked instruction arg


class Object:
    id: str
    resolved: Optional[bytes]
    name: Optional[str]

    def __init__(self, resolved=None, name=None) -> None:
        global static_id
        self.id = str(static_id)
        static_id = static_id + 1
        self.resolved = resolved
        if isinstance(resolved, int):
            self.set(resolved)
        self.name = name

    def __str__(self) -> str:
        if self.name is not None:
            s = self.name + "."
        else:
            s = "o."
        s += f"{self.id}"
        if self.resolved is not None:
            s += f":{self.resolved!r}"
        return s

    def __repr__(self) -> str:
        return str(self)

    def set(self, val: int):
        resolved = int.to_bytes(val, 4, signed=True)
        self.resolved = resolved

    def get(self):
        return self.resolved


class OffsetObject:
    obj: Object
    offset: int

    def __init__(self, obj: Object, offset=0) -> None:
        self.obj = obj
        self.offset = offset

    def __str__(self) -> str:
        s = f"{str(self.obj)}{self.offset:+}"
        return s

    def __repr__(self) -> str:
        return str(self)

    def get(self):
        return (int.from_bytes(self.obj.resolved, signed=True) + self.offset).to_bytes(
            4, signed=True
        )


class Instruction:
    id: str
    arg: Optional[Object | OffsetObject]

    def __init__(self, id: str, arg: Optional[Object | OffsetObject] = None) -> None:
        self.id = id
        self.arg = arg

    def __str__(self) -> str:
        s = ""
        s += self.id
        if self.arg is not None:
            s += f" {str(self.arg)}"
        return s

    def __repr__(self) -> str:
        return str(self)

    def to_list(self):
        res = [self.id]
        if self.arg is not None and self.arg.get() is not None:
            res.append(int.from_bytes(self.arg.get(), signed=True))
        return res


class Constants:
    constant: bytes

    def __init__(self, val: bytes) -> None:
        self.constant = val

    def __str__(self) -> str:
        s = "const."
        s += f"{self.constant!r}"
        return s

    def __repr__(self) -> str:
        return str(self)

    def flatten(self) -> list[int]:
        res = []
        for byte in self.constant:
            res.append(byte)
        return res


# def flatten_entries(content: list["Entry"]):
#     res = []
#     for entry in content:
#         if isinstance(entry, Instruction):
#             res.append(entry)
#         elif isinstance(entry, Block):
#             res.extend(entry.flatten())
#         elif isinstance(entry, Object):
#             res.append(entry)
#         if isinstance(entry, Constants):
#             res.extend(entry.flatten())
#     return res


class Block:
    scope: Scope
    before_ret: Optional[Object]
    ret: ScopeEntry
    content: list["Entry"]
    global_entries: list["Entry"]

    def __init__(self, parent: Scope, ret: Optional[ScopeEntry] = None) -> None:
        self.scope = Scope(parent)
        self.content = []
        self.global_entries = []
        if ret is not None:
            self.ret = ret
        else:
            self.ret = ScopeEntry()
            self.before_ret = Object()

    def __str__(self) -> str:
        s = f"Block -> {self.ret}\n"
        s += tab(str(self.scope)) + "\n[\n"
        s += tab("\n".join([str(instr) for instr in self.content]))
        s += "\n]"
        if len(self.global_entries) != 0:
            s += " glob code: [\n"
            s += tab("\n".join([str(instr) for instr in self.global_entries]))
            s += "\n]"
        return s

    def resolve_offsets(self, base: int) -> int:
        if self.ret.obj.get() is None:
            if self.before_ret is not None:
                self.before_ret.set(base)
            base -= self.ret.type.size
            self.ret.obj.set(base)
        after_ret = base
        base = self.scope.resolve_offsets(base)

        for entry in self.content:
            if isinstance(entry, Block):
                entry.resolve_offsets(base)
        return after_ret

    def flatten(self) -> tuple[list[Instruction | Object | int], list[Instruction | Object | int]]:
        local: list[Instruction | Object | int] = []
        glob: list[Instruction | Object | int] = []
        after_global: list[Instruction | Object | int] = []
        for entry in self.content:
            if isinstance(entry, Instruction):
                local.append(entry)
            elif isinstance(entry, Block):
                child_local, child_glob = entry.flatten()
                local.extend(child_local)
                glob.extend(child_glob)
            elif isinstance(entry, Object):
                local.append(entry)
            if isinstance(entry, Constants):
                local.extend(entry.flatten())

        for entry in self.global_entries:
            if isinstance(entry, Instruction):
                glob.append(entry)
            elif isinstance(entry, Block):
                child_local, child_glob = entry.flatten()
                glob.extend(child_local)
                after_global.extend(child_glob)
            elif isinstance(entry, Object):
                glob.append(entry)
            if isinstance(entry, Constants):
                glob.extend(entry.flatten())
        glob.extend(after_global)
        return local, glob
        # local = flatten_entries(self.content)
        # glob = flatten_entries(self.global_entries)
        # for entry in self.content:
        #     if isinstance(entry, Block):
        #         res.extend(entry.flatten())
        # return flatten_entries(self.content)

    # def flatten_global(self) -> list[Instruction | Object | int]:
    #     res = flatten_entries(self.global_entries)
    #     for entry in self.content:
    #         if isinstance(entry, Block):
    #             res.extend(entry.flatten())
    #     return res


Entry = Instruction | Block | Object | Constants
