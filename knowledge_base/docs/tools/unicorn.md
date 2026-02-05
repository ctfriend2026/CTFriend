# Unicorn

## Example Template
```python
from unicorn import *
from unicorn.x86_const import *

# Machine code
mc = bytes.fromhex('BYTES FROM GHIDRA HERE')

# Setup Emulator
emu = unicorn.Uc(UC_ARCH_X86, UC_MODE_64)

# Define and Map Stack
stack_addr = 0x0002000
stack_size = 0x0001000
emu.mem_map(stack_addr, stack_size)

# Write ESP to middle of stack to prevent potential errors
reg_esp = stack_addr + stack_size // 2
emu.reg_write(UC_X86_REG_ESP,reg_esp)

# Map a code segment for machine code
code_addr = 0x0005000
code_size = 0x0001000
emu.mem_map(code_addr, code_size)

# Write code to memory
emu.mem_write(code_addr, mc)

# Setup fs_address if stack canary is present
# FS segment base address (arbitrarily chosen in this example)
fs_base = 0x100000
fs_size = 0x1000  # Size large enough to cover offset 0x28
emu.mem_map(fs_base, fs_size)

# Set FS base (Unicorn API for setting FS base may vary based on the architecture)
emu.reg_write(UC_X86_REG_FS_BASE, fs_base)

# Load the passed parameter
emu.reg_write(UC_X86_REG_RDI, 0x664e3128) # system_time parameter

# Write a value to the FS:[0x28] address
fs_offset = 0x28
value_to_write = 0x123456789ABCDEF0  # Example value
emu.mem_write(fs_base + fs_offset, value_to_write.to_bytes(8, byteorder="little"))

# Track last instruction
last_instr_address = None
last_instr_size = None

# Define addresses and sizes for the heap and stack
heap_base = 0x200000
heap_size = 0x10000  # 64 KB
emu.mem_map(heap_base, heap_size)
next_free_address = heap_base

# Define the callback function to capture instructions
def track_instructions(mu, address, size, user_data):
    global last_instr_address, last_instr_size
    last_instr_address = address
    last_instr_size = size

# Track allocations
def mock_malloc(size):
    global next_free_address
    if next_free_address + size > heap_base + heap_size:
        raise MemoryError("Out of emulated heap memory.")
    allocated_address = next_free_address
    next_free_address += size
    return allocated_address

# Hook to intercept and handle malloc calls
def hook_code(emu, address, size, user_data):
    # Check if the instruction is a call to `malloc`
    # You may need to set the address of `malloc` here.
    malloc_addr = 0x5151  # Example address where malloc is located
    if address == malloc_addr:
        # Intercepting the malloc call
        size_to_allocate = emu.reg_read(UC_X86_REG_RDI)  # Read size from RDI
        malloc_return = mock_malloc(size_to_allocate)  # Call our mock malloc

        # Set RAX (return register) to our allocated address
        emu.reg_write(UC_X86_REG_RAX, malloc_return)

        # Skip the actual malloc call in emulation
        emu.reg_write(UC_X86_REG_RIP, emu.reg_read(UC_X86_REG_RIP) + size)

# Add the hook for all instructions
#emu.hook_add(UC_HOOK_CODE, track_instructions)
emu.hook_add(UC_HOOK_CODE, hook_code)

# Emulate and catch errors
try:
    start_addr = code_addr
    end_addr = code_addr + len(mc)
    emu.emu_start(start_addr, end_addr)

    rax_pointer = emu.reg_read(UC_X86_REG_RAX)
    for i in range(11):
        # Read the address at encrypted_buffer[i]
        address = emu.mem_read(rax_pointer + i * 8, 8)  # 4 bytes for a long address
        address = int.from_bytes(address, 'little')  # Convert bytes to integer (address)

        # Now read the value at this address
        value = emu.mem_read(address, 8)  # Assuming the value is also a long (4 bytes)
        value = int.from_bytes(value, 'little')  # Convert bytes to integer (value)

        print(f'Address: {hex(address)}, Value: {value}')
except UcError as e:
    print(f"Emulation error: {e}")
    if last_instr_address is not None:
        # Get the opcode that caused the issue
        faulty_instr = emu.mem_read(last_instr_address, last_instr_size)
        print(f"Last instruction address: 0x{last_instr_address:X}")
        print(f"Faulty instruction opcode: {faulty_instr.hex()}")
```