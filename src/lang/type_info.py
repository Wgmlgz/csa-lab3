class Type:
    id: str
    size: int

    def __init__(self, id: str = "()", size=0) -> None:
        self.id = id
        self.size = size

    def __str__(self) -> str:
        return f"{self.id}[{self.size}]"


class Struct(Type):
    members: dict[str, Type]
    name: str
    offsets: dict[str, int]

    def __init__(self, name: str, members: dict[str, Type]) -> None:
        self.name = name
        self.members = members

        offsets = {}
        base = 0
        for key, member in members.items():
            offsets[key] = base
            base += member.size
        size = base

        self.offsets = offsets

        args = " ".join(f"({key} {val.id})" for key, val in members.items())
        id = f"{name}({args})"

        super().__init__(id, size)


class Ptr(Type):
    base: Type

    def __init__(self, base: Type) -> None:
        self.base = base
        id = f"{base.id}*"
        super().__init__(id, 8)


class Callable(Type):
    args: list[Type]
    ret: Type

    def __init__(self, args: list[Type], ret: Type) -> None:
        self.args = args
        self.ret = ret
        s_args = " ".join(f"({arg.id})" for arg in args)
        id = f"({s_args}) -> {ret.id}"

        super().__init__(id, 8)


undefined_type = Type("undefined", 666)
void_type = Type("()", 0)
u8_type = Type("u8", 1)
int_type = Type("int", 8)
str_type = Struct("str", {"ptr": Ptr(u8_type), "len": int_type})
ints_type = Struct("ints", {"ptr": Ptr(int_type), "len": int_type})
