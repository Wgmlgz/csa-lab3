config = {
    'debug': False,
    'compile': False,
    'run': False,
    'interactive': False
}


def tab(s: str, tab='  ') -> str:
    return '\n'.join([tab + s for s in s.split('\n')])
