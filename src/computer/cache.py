# import logging
# from typing import Optional
# from computer.clock import Clock
# from computer.mem import Memory
# from utils import config


# class CacheBlock:
#     def __init__(self, data: bytearray, tag: int):
#         self.data = data
#         self.tag = tag
#         self.dirty = False
#         self.last_used = 0


# class Cache:
#     def __init__(
#         self, clock: Clock, memory: Memory, cache_size: int = 1024, block_size: int = 64
#     ):
#         self.clock = clock
#         self.memory = memory
#         self.cache_size = cache_size
#         self.block_size = block_size
#         self.num_blocks = cache_size // block_size
#         self.cache: list[Optional[CacheBlock]] = [None] * self.num_blocks
#         self.hits = 0
#         self.misses = 0

#     def __str__(self):
#         total_memory_blocks = self.memory.n // self.block_size
#         representation = [" "] * total_memory_blocks

#         for block in self.cache:
#             if block is not None:
#                 block_index = (block.tag * self.block_size) // self.block_size
#                 representation[block_index] = "|"

#         # if total_memory_blocks > 100:
#         #     compact_representation = ""
#         #     scale_factor = total_memory_blocks // 100
#         #     for i in range(0, total_memory_blocks, scale_factor):
#         #         if "|" in representation[i : i + scale_factor]:
#         #             compact_representation += "|"
#         #         else:
#         #             compact_representation += "."
#         #     return compact_representation

#         return "".join(representation)

#     def get_block(self, address: int) -> Optional[CacheBlock]:
#         tag = address // self.block_size
#         for block in self.cache:
#             if block is not None and block.tag == tag:
#                 return block
#         return None

#     def get(self, address: int, size: int) -> bytes:
#         result = bytearray()
#         while size > 0:
#             block = self.get_block(address)

#             offset = address % self.block_size
#             bytes_to_read = min(self.block_size - offset, size)

#             if block is not None:
#                 if config["debug-mem"]:
#                     logging.debug("hit")
#                 self.hits += 1
#                 self.clock.wait_cycles(1)
#                 result.extend(block.data[offset : offset + bytes_to_read])
#             else:
#                 if config["debug-mem"]:
#                     logging.info("miss")
#                 self.misses += 1
#                 self.clock.wait_cycles(10)

#                 start_address = (address // self.block_size) * self.block_size
#                 block_data = self.memory.get(start_address, self.block_size)
#                 self.set(start_address, block_data)
#                 block = self.get_block(address)
#                 if block is None:
#                     raise Exception("block is none")
#                 result.extend(block.data[offset : offset + bytes_to_read])

#             address += bytes_to_read
#             size -= bytes_to_read

#         return bytes(result)

#     def set(self, address: int, data: bytes):
#         data_index = 0
#         size = len(data)

#         while size > 0:
#             current_block = self.get_block(address)
#             offset = address % self.block_size
#             bytes_to_write = min(self.block_size - offset, size)

#             if current_block is not None:
#                 if config["debug-mem"]:
#                     logging.info("hit")
#                 self.hits += 1
#                 self.clock.wait_cycles(1)
#             else:
#                 if config["debug-mem"]:
#                     logging.info("miss")
#                 self.misses += 1
#                 self.clock.wait_cycles(10)

#                 lru_index = self.find_lru_block_index()
#                 lru_block = self.cache[lru_index]
#                 # If the current block is dirty, flush it to memory before overwriting
#                 if lru_block is not None and lru_block.dirty:
#                     self.flush_block(lru_index)

#                 # Load the block from memory if it's a miss or the block is not present
#                 block_data = self.memory.get(address - offset, self.block_size)

#                 tag = address // self.block_size
#                 current_block = CacheBlock(block_data, tag)  # Initially not dirty
#                 current_block.last_used = self.clock.ticks
#                 self.cache[lru_index] = current_block

#             # Update the block with new data and mark it as dirty
#             end_offset = offset + bytes_to_write
#             current_block.data[offset:end_offset] = data[
#                 data_index : data_index + bytes_to_write
#             ]
#             current_block.dirty = True

#             address += bytes_to_write
#             data_index += bytes_to_write
#             size -= bytes_to_write

#     def find_lru_block_index(self) -> int:
#         lru_index = 0
#         min_last_used = float("inf")
#         for i, block in enumerate(self.cache):
#             if block is None:
#                 return i
#             if block and block.last_used < min_last_used:
#                 lru_index = i
#                 min_last_used = block.last_used
#         return lru_index

#     def flush_block(self, block_index: int):
#         block = self.cache[block_index]
#         if block and block.dirty:
#             start_address = (block.tag * self.block_size) % self.memory.n
#             self.memory.set(start_address, block.data)
#             block.dirty = False
#         if config["debug-mem"]:
#             print(self)

#     def flush(self):
#         for i in range(self.num_blocks):
#             self.flush_block(i)
