config = {
    'debug': False,
    'compile': True,
    'run': False
}


def tab(s: str, tab='  ') -> str:
    return '\n'.join([tab + s for s in s.split('\n')])
