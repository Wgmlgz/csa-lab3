from pprint import pprint
from lang.scope import Block, Instruction
from lang.token import Token, tokenize
from typing import Optional
from pathlib import Path
from lang.exp import Exp, ParseException, parse_exp
from lang.types import void_type, u64_type, u8_type, str_type
from utils import config


class Module:
    base_path: str
    path: Path
    source: Optional[str]
    tokens: Optional[list[Token]]

    exp: Optional[Exp]
    # exe: Optional["Executable"]
    # global_scope: Optional["Scope"]
    parent: Optional["Module"]
    block: Optional[Block]

    def __init__(self, base_path: str, parent: Optional["Module"] = None) -> None:
        from lang.compiler import Executable, Scope, compile_block, resolve_labels
        self.exe: Optional[Executable]
        self.global_scope: Scope
        try:
            self.parent = parent
            if parent is None:
                global_scope = Scope()
                global_scope.add_type("()", void_type, None)
                global_scope.add_type("u64", u64_type, None)
                global_scope.add_type("u8", u8_type, None)
                global_scope.add_type("str", str_type, None)
                self.global_scope = global_scope
            else:
                self.global_scope = parent.global_scope

            self.base_path = base_path
            self.resolve_path()
            self.init_source()
            self.tokenize()
            self.parse_exp()
            self.compile()

        except ParseException as e:
            msg = self.handle_parse_exception(e)

            raise Exception(msg)

    def handle_parse_exception(self, e: ParseException) -> str:
        if self.source is None:
            raise Exception('No source')
        lines = self.source.split("\n")

        if e.exp is not None or e.token is not None:
            if e.exp is not None:
                if self.tokens is None:
                    raise Exception("No tokens")
                token = self.tokens[e.exp.begin]
                end_token = self.tokens[e.exp.end]
                pos = token.pos
                end_pos = end_token.pos + len(end_token.val)
                l = end_pos - pos
                line_n = 1
                while pos > len(lines[line_n - 1]):
                    pos -= len(lines[line_n - 1]) + 1
                    line_n += 1
                # pos += 1

            elif e.token is not None:
                pos = e.token.pos
                line_n = 1
                l = len(e.token.val)
                while pos > len(lines[line_n - 1]):
                    pos -= len(lines[line_n - 1]) + 1
                    line_n += 1
        else:
            line_n = len(lines)
            pos = 0
            l = 1

        l = min(l, len(lines[line_n - 1]) - pos)
        # pos += 1
        msg = f"ParseError: {e.msg}\n"
        msg += f"at file {self.path}:{line_n} {pos + 1} \n"
        msg += lines[line_n - 1] + "`"
        msg += "\n"
        msg += " " * pos + (" " * l + "^" if e.after else "^" * l)
        return msg

    def resolve_path(self):
        if self.parent is not None:
            fin_path = Path(self.parent.path).parent.joinpath(self.base_path)
        else:
            fin_path = Path(self.base_path)
        self.path = fin_path

    def init_source(this):
        try:
            file_path = this.path.with_suffix('.lsp')
            with open(file_path, "r") as file:
                this.source = file.read()
        except:
            raise Exception(f"Failed to resolve file {file_path}")

    def tokenize(self) -> None:
        if self.source is None:
            raise Exception('No source')
        self.tokens = tokenize(self.source)

    def parse_exp(self) -> None:
        if self.tokens is None:
            raise Exception(f"No tokens")
            
        self.exp = parse_exp(self.tokens)
        if config["debug"]:
            print(self.exp.to_string())

    def compile(self):
        if self.exp is None:
            raise Exception(f"No exp")
        from lang.compiler import Executable, Scope, compile_block, resolve_labels

        exp = self.exp

        scope = Scope(self.global_scope)
        block = compile_block(exp, scope, self)
        if config["debug"]:
            print("compiled, unresolved:")
            print(block)
        self.block = block

    def link(self):
        from lang.compiler import Executable, Scope, compile_block, resolve_labels

        word_size = 8
        instructions = []
        self.block.resolve_offsets(0)
        if config["debug"]:
            print("compiled, resolved:")
            print(self.block)

        unlinked_main, unlinked_global = self.block.flatten()
        unlinked_main.append(Instruction("halt"))

        unlinked = unlinked_main + unlinked_global

        if config["debug"]:
            print("compiled, resolved, unlinked:")
            pprint(unlinked)
        instructions, base = resolve_labels(unlinked, 0, word_size)
        if config["debug"]:
            print(
                f"compiled, resolved to instructions ({hex(len(instructions) * word_size)}):"
            )
            pprint(instructions)
        executable = Executable(instructions)
        self.exe = executable


#  def compile(self):
#         instructions = []

#         exp = self.exp

#         global_scope = Scope()
#         block = Block(global_scope)
#         block.ret.type = void_type
#         global_scope.add_type('()', void_type, None)
#         global_scope.add_type('u64', u64_type, None)

#         main_block = compile_block(exp, global_scope, global_scope)
#         block.content.append(main_block)
#         if config['debug']:
#             print('compiled, unresolved:')
#             print(block)

#         block.resolve_offsets(0)
#         if config['debug']:
#             print('compiled, resolved:')
#             print(block)

#         unlinked_main = block.flatten()
#         unlinked_global = block.flatten_global()
#         unlinked = unlinked_main + unlinked_global

#         if config['debug']:
#             print('compiled, resolved, unlinked:')
#             pprint(unlinked)
#         instructions, base = resolve_labels(unlinked, 0)

#         if config['debug']:
#             print('compiled, resolved to instructions:')
#             pprint(instructions)
#         executable = Executable(instructions)
#         self.exe = executable
