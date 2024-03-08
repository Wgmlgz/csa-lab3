class Stream:
  data: bytes
  ptr: int
  
  def __init__(self, data = bytearray(), real=False) -> None:
    self.data = data
    self.ptr = 0
    
  def read(self, len = 1) -> bytes:
    res = bytes(self.data[self.ptr:self.ptr+len])
    self.ptr += len
    return res
  
  def status(self) -> bytes:
    if len(self.data) == self.ptr:
      return b'\0'
    return b'\1'

  def write(self, data: bytes):
    self.data += data
    self.ptr += len(data)
    
  def __str__(self) -> str:
    s = str(self.data)
    s += '\n'
    s += ' ' * self.ptr + '^'
    return s