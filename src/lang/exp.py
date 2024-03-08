from typing import Optional

# from config import config
from lang.token import Token, TokenType
from utils import tab


class Exp:
    begin: int
    end: int

    def to_string(self) -> str:
        return "EmptyExp"


class Nested(Exp):
    children: list[Exp] = []

    def __init__(self) -> None:
        super().__init__()
        self.children = []

    def to_string(self) -> str:
        inner = "\n".join([tab(e.to_string()) for e in self.children])
        return f"Exp:\n{inner}"


class IntLiteral(Exp):
    val: int
    type: str

    def __init__(self, val: int, type: str) -> None:
        super().__init__()
        self.val = val
        self.type = type

    def to_string(self) -> str:
        return f"Int({self.val})"


class StrLiteral(Exp):
    val: str

    def __init__(self, val: str) -> None:
        super().__init__()
        self.val = val

    def to_string(self) -> str:
        return f"Str({self.val})"


class IdLiteral(Exp):
    val: str

    def __init__(self, val: str) -> None:
        super().__init__()
        self.val = val

    def to_string(self) -> str:
        return f"Id({self.val})"


class ParseException(Exception):
    token: Token
    msg: str

    def __init__(
        self, msg: str, pos=None, after=False, exp: Optional[Exp] = None
    ) -> None:
        super().__init__(msg, pos, after)
        self.msg = msg
        self.after = after
        self.exp = exp

        if isinstance(pos, Token):
            self.token = pos
        if isinstance(pos, Exp):
            self.exp = pos


def parse_exp(tokens: list[Token]) -> Exp:
    res = Nested()

    cursor = 0
    while cursor < len(tokens):
        exp, cursor = parse_general(tokens, cursor)
        res.children.append(exp)

        # raise ParseException('Unexpected (possibly extra `)`):', tokens[cursor])

    return res


def parse_atom(tokens: list[Token], cursor: int) -> tuple:
    if cursor >= len(tokens):
        raise ParseException("Expected `)`", tokens[-1])
    token = tokens[cursor]

    child: IdLiteral | IntLiteral | StrLiteral
    if token.type == TokenType.ID:
        child = IdLiteral(token.val)
    elif token.type == TokenType.INT:
        type = "int"
        val = token.val
        if "int" in val:
            type = "int"
        if "u32" in val:
            type = "u32"
        if "u16" in val:
            type = "u16"
        if "u8" in val:
            type = "u8"
        if "i64" in val:
            type = "i64"
        if "i32" in val:
            type = "i32"
        if "i16" in val:
            type = "i16"
        if "i8" in val:
            type = "i8"
        if type in val:
            val = val[: -(len(type))]

        res = eval(val)
        child = IntLiteral(res, type)
    elif token.type == TokenType.STR:
        escaped = eval(token.val)
        child = StrLiteral(escaped)
    else:
        raise ParseException("Unexpected token", token)
    child.begin = cursor
    child.end = cursor
    return child, cursor + 1


def parse_general(tokens: list[Token], cursor: int = 0) -> tuple:
    if cursor >= len(tokens):
        raise ParseException("Unexpected end of tokens", tokens[-1], after=True)

    token = tokens[cursor]
    if token.type == TokenType.OPEN:
        cursor += 1
        exp = Nested()
        exp.begin = cursor - 1

        while tokens[cursor].type != TokenType.CLOSE:
            child, cursor = parse_general(tokens, cursor)
            exp.children.append(child)
            if cursor >= len(tokens):
                raise ParseException("Expected `)`, found EOF", tokens[-1], after=True)

        exp.end = cursor
        return exp, cursor + 1
    elif token.type == TokenType.CLOSE:
        raise ParseException("Unexpected `)`", token)
    else:
        return parse_atom(tokens, cursor)
