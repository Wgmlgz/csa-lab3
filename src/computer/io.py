class Stream:
  data: str
  ptr: int
  
  def __init__(self, data = '', real=False) -> None:
    self.data = data
    self.ptr = 0
    
  def read(self, len = 1) -> bytes:
    res = bytes(self.data[self.ptr:self.ptr+len])
    return res
  
  def write(self, data: bytes):
    self.data += data
    self.ptr += len(data)
    
  def __str__(self) -> str:
    s = self.data
    s += '\n'
    s += ' ' * self.ptr + '^'
    return s