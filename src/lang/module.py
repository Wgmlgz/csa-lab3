from lang.token import Token, tokenize
from typing import Optional
from os import path
from lang.exp import Exp, ParseException, parse_exp
from utils import config

class Module:
  path: str
  source: Optional[str]
  tokens: Optional[list[Token]]
  
  exp: Optional[Exp]
  
  
  def __init__(this, path: str) -> None:
    try:
      this.path = path
      this.init_source()
      this.tokenize()
      this.parse_exp()
      if config['debug']:
        print('module exp:')
        print(this.exp.to_string())
        
    except ParseException as e:
      lines = this.source.split('\n')
      
      token = e.token
      if token is None:
        line_n = len(lines)
        pos = 0
        l = 1
      else:
        pos = e.token.pos
        line_n = 1
        l = len(e.token.val)
        while pos > len(lines[0]):
          pos -= len(lines[0])
          lines = lines[1:]
          line_n = line_n + 1
        
      msg = f'ParseError: {e.msg}\n'
      msg += f'at file {this.path}:{line_n} {pos + 1} \n'
      msg += lines[0]
      msg += "\n"
      msg += ' ' * pos + (' ' * l + '^' if e.after else '^' * l)
      msg += "\n"
      raise Exception(msg)
      
  
  def resolve(this, relative_path: str) -> str:
    fin_path = path.join(this.path, relative_path)
    return fin_path

  def init_source(this):
    try:
      with open(this.path, 'r') as file:
        this.source = file.read()
    except:
      raise Exception(f'Failed to resolve file {this.path}')
    
  def tokenize(this) -> None:
    this.tokens = tokenize(this.source)
    
  def parse_exp(self) -> None:
    self.exp = parse_exp(self.tokens)