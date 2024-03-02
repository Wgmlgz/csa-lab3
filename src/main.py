from typing import Optional
from computer.runner import Runner
from lang.module import Module
from computer.machine import Machine
from utils import config
import sys

class Susser:    
  def run(entry_path: str):
    pass

USAGE_STR = '''
Usage: python <script-path> <input-file> [-d/--debug] [-r/--run] [-c/--run]
  Flags:
    -d/--debug enables debug output
'''

def main():
  if len(sys.argv) < 2:
    print(USAGE_STR)
    exit(1)
  if ('-d' in sys.argv) or ('--debug' in sys.argv):
    print('Debug output enabled.')
    config['debug'] = True
  if ('-r' in sys.argv) or ('--run' in sys.argv):
    config['run'] = True
  if ('-c' in sys.argv) or ('--compile' in sys.argv):
    config['compile'] = True
  if ('-i' in sys.argv) or ('--interactive' in sys.argv):
    config['interactive'] = True
  
  if config['debug']:
    print('argument list', sys.argv)
  
  file_path = sys.argv[1]
  
  try:
    machine = Machine()
    machine.memory.set(0, 0x00_00_00_01_00_00_00_00.to_bytes(8))
    
    if config['compile']:
      mod = Module(file_path)
      executable = mod.exe
      dict = executable.to_dict()
      machine.memory.load_instructions(dict['instructions'])
      
    elif config['run']:
      machine.memory.load_json(file_path)
    
  
      
    if config['run']:
      if config['debug']:
        print(machine)
      runner = Runner(machine)
      runner.run()
      print(runner.m.stdout.data)
      if config['debug']:
        print(machine)
    
  except Exception as err:
    print(f'Compilation failed occurred:')
    print(err)
    if config['debug']:
      print(err.with_traceback())
    exit(1)
    
    
  

if __name__ == '__main__':
  main()