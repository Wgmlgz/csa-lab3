config = {
    "debug": False,
    "debug-mem": False,
    "compile": False,
    "run": False,
    "interactive": False,
    "clear": False,
}


def tab(s: str, tab="  ") -> str:
    return "\n".join([tab + s for s in s.split("\n")])
