import logging
from lang.scope import Block, Instruction
from lang.token import Token, tokenize
from typing import Optional
from pathlib import Path
from lang.exp import Exp, ParseException, parse_exp
from lang.type_info import void_type, int_type, char_type, str_type, ints_type
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
        from lang.compiler import Executable, Scope

        self.exe: Optional[Executable]
        self.global_scope: Scope
        try:
            self.parent = parent
            if parent is None:
                global_scope = Scope()
                global_scope.add_type("()", void_type, None)
                global_scope.add_type("int", int_type, None)
                global_scope.add_type("char", char_type, None)
                global_scope.add_type("str", str_type, None)
                global_scope.add_type("ints", ints_type, None)
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
            raise Exception("No source")
        lines = self.source.split("\n")

        if e.exp is not None or e.token is not None:
            if e.exp is not None:
                if self.tokens is None:
                    raise Exception("No tokens")
                token = self.tokens[e.exp.begin]
                end_token = self.tokens[e.exp.end]
                pos = token.pos
                end_pos = end_token.pos + len(end_token.val)
                length = end_pos - pos
                line_n = 1
                while pos > len(lines[line_n - 1]):
                    pos -= len(lines[line_n - 1]) + 1
                    line_n += 1
                # pos += 1

            elif e.token is not None:
                pos = e.token.pos
                line_n = 1
                length = len(e.token.val)
                while pos > len(lines[line_n - 1]):
                    pos -= len(lines[line_n - 1]) + 1
                    line_n += 1
        else:
            line_n = len(lines)
            pos = 0
            length = 1

        length = min(length, len(lines[line_n - 1]) - pos)
        # pos += 1
        msg = f"ParseError: {e.msg}\n"
        msg += f"at file {self.path}:{line_n} {pos + 1} \n"
        msg += lines[line_n - 1] + "`"
        msg += "\n"
        msg += " " * pos + (" " * length + "^" if e.after else "^" * length)
        return msg

    def resolve_path(self):
        if self.parent is not None:
            fin_path = Path(self.parent.path).parent.joinpath(self.base_path)
        else:
            fin_path = Path(self.base_path)
        self.path = fin_path

    def init_source(this):
        file_path = this.path.with_suffix(".lsp")
        with open(file_path, "r") as file:
            this.source = file.read()

    def tokenize(self) -> None:
        if self.source is None:
            raise Exception("No source")
        self.tokens = tokenize(self.source)

    def parse_exp(self) -> None:
        if self.tokens is None:
            raise Exception("No tokens")

        self.exp = parse_exp(self.tokens)
        logging.debug(self.exp.to_string())

    def compile(self):
        if self.exp is None:
            raise Exception("No exp")
        from lang.compiler import Scope, compile_block

        exp = self.exp

        scope = Scope(self.global_scope)
        block = compile_block(exp, scope, self)
        logging.debug("compiled, unresolved:")
        logging.debug(block)
        self.block = block

    def link(self):
        from lang.compiler import Executable, resolve_labels

        word_size = 8
        instructions = []
        self.block.resolve_offsets(0)

        logging.debug("compiled, resolved:")
        logging.debug(self.block)

        unlinked_main, unlinked_global = self.block.flatten()
        unlinked_main.append(Instruction("halt"))

        unlinked = unlinked_main + unlinked_global

        if config["debug"]:
            logging.debug("compiled, resolved, unlinked:")
            logging.debug(unlinked)
        instructions, base = resolve_labels(unlinked, 0, word_size)
        logging.debug(
            f"compiled, resolved to instructions ({hex(len(instructions) * word_size)}):"
        )
        logging.debug(instructions)
        executable = Executable(instructions)
        self.exe = executable
