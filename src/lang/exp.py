from enum import Enum
import re
# from config import config
from lang.token import Token, TokenType
from utils import tab

class Exp:
  aaa = 228
  pass


class Nested(Exp):
  aaa = 111
  children: list[Exp] = []

  def __init__(self) -> None:
    super().__init__()
    self.children = []
    
    
  def to_string(self) -> str:
    inner = '\n'.join([tab(e.to_string()) for e in self.children])
    return f'Exp:\n{inner}'
  
class IntLiteral(Exp):
  val_int: int
  def __init__(self, val: int) -> None:
    super().__init__()
    self.val_int  = val
  def to_string(self) -> str:
    return f'Int({self.val_int})'
  
class StrLiteral(Exp):
  val_str: str
  def __init__(self, val: str) -> None:
    super().__init__()
    self.val_str  = val
    
  def to_string(self) -> str:
    return f'Str({self.val_str})'
  
class IdLiteral(Exp):
  val_id: str
  
  def __init__(self, val: str) -> None:
    super().__init__()
    self.val_id  = val
    
  def to_string(self) -> str:
    return f'Id({self.val_id})'

class ParseException(Exception):
  token: Token
  msg: str
  
  def __init__(self, msg: str, token: Token = None, after = False) -> None:
    super().__init__(msg, token, after)
    self.msg = msg
    self.token = token
    self.after = after
    
def parse_exp(tokens: list[Token]) -> Exp:
  exp, cursor = parse_general(tokens)
  if cursor < len(tokens):
    raise ParseException('Unexpected (possibly extra `)`):', tokens[cursor])
    
  return exp

def parse_atom(tokens: list[Token], cursor: int) -> tuple:
    if cursor >= len(tokens):
        raise ParseException('Expected `)`', tokens[-1])
    token = tokens[cursor]
  
    if token.type == TokenType.ID:
        child = IdLiteral(token.val)
    elif token.type == TokenType.INT:
        child = IntLiteral(token.val)
    elif token.type == TokenType.STR:
        child = StrLiteral(token.val)
    else:
        raise ParseException('Unexpected token', token)
  
    return child, cursor + 1

def parse_general(tokens: list[Token], cursor: int = 0) -> tuple:
    if cursor >= len(tokens):
        raise ParseException('Unexpected end of tokens', tokens[-1], after=True)
    
    token = tokens[cursor]
    if token.type == TokenType.OPEN:
        cursor += 1
        exp = Nested()
        
        while tokens[cursor].type != TokenType.CLOSE:
            child, cursor = parse_general(tokens, cursor)
            exp.children.append(child)
            if cursor >= len(tokens):
                raise ParseException('Expected `)`, found EOF', tokens[-1], after=True)
        
        return exp, cursor + 1
    elif token.type == TokenType.CLOSE:
        raise ParseException('Unexpected `)`', token)
    else:
        return parse_atom(tokens, cursor)




       

# `(` is parsed, `)` is handled here 
# def parse_nested(tokens: list[Token], last: Token) -> Exp:
#   exp = Nested()
  
#   while True:
#     print(exp)
#     print(tokens)
    
#     if len(tokens) == 0:
#       raise ParseException('Expected `)`', last, after=True)
#     token = tokens[0]
#     if token.type == TokenType.CLOSE:
#       return exp, tokens[1:]
#     else:
#       child, tokens = parse_general(tokens)
#       exp.children.append(child)