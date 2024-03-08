from enum import Enum
import logging
import re
import pprint
from utils import config


class TokenType(Enum):
    OPEN = 1
    CLOSE = 2
    STR = 3
    INT = 4
    ID = 5
    COMMENT = 6


class Token:
    val: str
    type: TokenType
    pos: int

    def __str__(self) -> str:
        return f"`{self.val}`.{self.type}@{self.pos}"

    def __repr__(self) -> str:
        return self.__str__()


tokens_def = [
    (r"\(", TokenType.OPEN),
    (r"\)", TokenType.CLOSE),
    (r"\"[^\"]*\"", TokenType.STR),
    (r"\d+(?:(?:u|i)(?:8|16|32|64))?", TokenType.INT),
    (r";;.*", TokenType.COMMENT),
    (r"[^\s\(\)\d][^\s\(\)]*", TokenType.ID),
]
tokens_pattern = "|".join([f"({p})" for p, _ in tokens_def])


def displaymatch(match):
    if match is None:
        return None
    return "<Match: %r, groups=%r>" % (match.group(), match.groups())


def tokenize(s: str) -> list[Token]:
    logging.debug(f"Tokenizing: {s}")

    cur = 0
    search = True
    tokens = []

    while search:
        match = re.search(tokens_pattern, s[cur:])
        if match is None:
            break

        token = Token()
        token.pos = cur + match.span()[0]
        token.val = match.group()

        token.type = [
            val[1]
            for idx, val in enumerate(tokens_def)
            if match.groups()[idx] is not None
        ][0]
        cur += match.span()[1]

        if token.type == TokenType.COMMENT:
            continue
        tokens.append(token)

    if config["debug"]:
        pprint.pprint(tokens)

    return tokens
