from pprint import pprint
from lang.compiler import Executable, Scope, compile_block, resolve_labels
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
    exe: Optional[Executable]

    def __init__(this, path: str) -> None:
        try:
            this.path = path
            this.init_source()
            this.tokenize()
            this.parse_exp()
            this.compile()
            if config['debug']:
                print('module exp:')
                print(this.exp.to_string())

        except ParseException as e:
            lines = this.source.split('\n')
            
            if e.exp is not None:
                token = this.tokens[e.exp.begin]
                end_token = this.tokens[e.exp.end]
                pos = token.pos
                end_pos = end_token.pos + len(end_token.val)
                l = end_pos - pos
                line_n = 1
                while pos > len(lines[0]):
                    pos -= len(lines[0]) + 1
                    lines = lines[1:]
                    line_n = line_n + 1
                pos += 1
                
            elif e.token is not None:
                pos = e.token.pos
                line_n = 1
                l = len(e.token.val)
                while pos > len(lines[0]):
                    pos -= len(lines[0]) + 1
                    lines = lines[1:]
                    line_n = line_n + 1
            else:
                line_n = len(lines)
                pos = 0
                l = 1
                
            # pos += 1
            msg = f'ParseError: {e.msg}\n'
            msg += f'at file {this.path}:{line_n} {pos + 1} \n'
            msg += lines[0]
            msg += "\n"
            msg += ' ' * pos + (' ' * l + '^' if e.after else '^' * l)
                            
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
        if config['debug']:
            print(self.exp.to_string())

    def compile(self):
        instructions = []

        exp = self.exp

        scope = Scope()
        # scope.
        block = compile_block(exp, scope)
        if config['debug']:
            print('compiled, unresolved:')
            print(block)

        block.resolve_offsets(0)
        if config['debug']:
            print('compiled, resolved:')
            print(block)

        unlinked = block.flatten()
        
        if config['debug']:
            print('compiled, resolved, unlinked:')
            pprint(unlinked)
        instructions = resolve_labels(unlinked, 0)
        
        if config['debug']:
            print('compiled, resolved to instructions:')
            pprint(instructions)
        executable = Executable(instructions)
        self.exe = executable
