
from typing import Optional
from lang.exp import Exp, ParseException
from utils import tab


class Type:
    id: str
    size: int

    def __init__(self, id: str = '()', size=0) -> None:
        self.id = id
        self.size = size

    def __str__(self) -> str:
        return f'{self.id}[{self.size}]'
      
class Callable(Type):
    args: list[Type]
    ret: Type
    
    def __init__(self, args: list[Type], ret: Type) -> None:
      self.args = args
      self.ret = ret
      args = ' '.join(f'({arg.id})' for arg in args)
      id = f'({args}) -> {ret.id}'
          
      super().__init__(id, 8)

    def __str__(self) -> str:
        return f'{self.id}[{self.size}]'

class ScopeEntry:
    type: Optional[Type]
    obj: 'Object'

    def __init__(self, type: Type = None) -> None:
        self.type = type
        self.obj = Object()

    def __str__(self) -> str:
        s = f'{str(self.type)} at {str(self.obj)}'
        return s


void_type = Type('()', 0)
u64_type = Type('u64', 8)


class Scope:
    parent: Optional['Scope']
    locals: dict[str, ScopeEntry]
    types: dict[str, Type]

    def __init__(self, parent: Optional['Scope'] = None) -> None:
        self.parent = parent
        self.locals = {}
        self.types = {}

    def add(self, id: str, scope_entry: ScopeEntry, exp: Exp) -> Optional[str]:
        if id in self.locals:
            raise ParseException(
                f'Variable {id} is already defined in this scope', exp)
        self.locals[id] = scope_entry

    def get(self, id: str, exp: Exp) -> ScopeEntry:
        if id in self.locals:
            return self.locals[id]
        elif self.parent is not None:
            return self.parent.get(id, exp)
        else:
            raise ParseException(f'Undefined variable `{id}`', exp)

    def add_type(self, id: str, type_entry: Type, exp: Exp) -> Optional[str]:
        if id in self.types:
            raise ParseException(
                f'Type {id} is already defined in this scope', exp)
        self.types[id] = type_entry

    def get_type(self, id: str, exp: Exp) -> ScopeEntry:
        if id in self.types:
            return self.types[id]
        elif self.parent is not None:
            return self.parent.get_type(id, exp)
        else:
            raise ParseException(f'Undefined type `{id}`', exp)

    def __str__(self) -> str:
        if len(self.locals) == 0 and len(self.types) == 0:
            return 'EmptyScope'
        s = 'Scope:\n  '
        if len(self.locals) != 0:
            s += '\n  '.join(f'{key}: {val.type} at {val.obj}' for key,
                             val in self.locals.items())
        if len(self.types) != 0:
            s += '\n  T: '.join(f'{key}: {str(val)}' for key,
                                val in self.types.items())
        return s

    def resolve_offsets(self, base: int):
        for entry in self.locals.values():
            if entry.obj.resolved is None:
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
        self.name = name

    def __str__(self) -> str:
        if self.name is not None:
          s = self.name + '.'
        else:
          s = 'o.'
        s += f'{self.id}'
        if self.resolved is not None:
            s += f':{self.resolved}'
        return s

    def __repr__(self) -> str:
        return str(self)
    
    def set(self, val: int):
        resolved = int.to_bytes(val, 4, signed=True)
        self.resolved = resolved
      

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
    before_ret: Object
    ret: ScopeEntry
    content: list['Entry']
    global_entries: list['Entry']

    def __init__(self, parent: Scope) -> None:
        self.scope = Scope(parent)
        self.content = []
        self.global_entries = []
        self.ret = ScopeEntry()
        self.before_ret = Object()

    def __str__(self) -> str:
        s = f'Block -> {self.ret}\n'
        s += tab(str(self.scope)) + '\n[\n'
        s += tab('\n'.join([str(instr) for instr in self.content]))
        s += '\n]'
        if len(self.global_entries) != 0:
          s += ' glob code: [\n'
          s += tab('\n'.join([str(instr) for instr in self.global_entries]))
          s += '\n]'
        return s

    def resolve_offsets(self, base: int) -> int:
        if self.ret.obj.resolved is None:
            self.before_ret.set(base)
            base -= self.ret.type.size
            self.ret.obj.set(base)
        after_ret = base
        base = self.scope.resolve_offsets(base)

        for entry in self.content:
            if isinstance(entry, Block):
                entry.resolve_offsets(base)
        return after_ret
    
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
    
    def flatten_global(self) -> list[Instruction | Object]:
        res = []
        for entry in self.global_entries:
            if isinstance(entry, Instruction):
                res.append(entry)
            elif isinstance(entry, Block):
                res.extend(entry.flatten())
            elif isinstance(entry, Object):
                res.append(entry)
        for entry in self.content:
          if isinstance(entry, Block):
              res.extend(entry.flatten_global())
        return res


Entry = Instruction | Block | Object