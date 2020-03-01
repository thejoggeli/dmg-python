import dlog
import cartridge as car

read_map = [None]*0x10000
write_map = [None]*0x10000
name_map = [None]*0x10000

def init():
    # load bios
    global bios_mem
    with open("bios.gb", "rb") as bios_fh:    
        bios_mem = bytearray(bios_fh.read())
    # load memory functions
    for i in range(0x0000, 0x0100):
        read_map[i]     = bios_read
        write_map[i]    = bios_write
        name_map[i]     = bios_name
    for i in range(0x0100, 0x4000):
        read_map[i]     = car.rom_0_read
        write_map[i]    = car.rom_0_write
        name_map[i]     = car.rom_0_name
    for i in range(0x4000, 0x8000):
        read_map[i]     = car.rom_x_read
        write_map[i]    = car.rom_x_write
        name_map[i]     = car.rom_x_name
    for i in range(0x8000, 0xA000):
        read_map[i]     = videoram_read
        write_map[i]    = videoram_write
        name_map[i]     = videorame_name
    for i in range(0xA000, 0xC000):
        read_map[i]     = car.ram_read
        write_map[i]    = car.ram_write
        name_map[i]     = car.ram_name
    for i in range(0xC000, 0xE000):
        read_map[i]     = intram_read
        write_map[i]    = intram_write
        name_map[i]     = intram_name
    for i in range(0xE000, 0xFE00):
        read_map[i]     = intramecho_read
        write_map[i]    = intramecho_write
        name_map[i]     = intramecho_name
    for i in range(0xFE00, 0xFEA0):
        read_map[i]     = spritemem_read
        write_map[i]    = spritemem_write
        name_map[i]     = spritemem_name
    for i in range(0xFEA0, 0xFF00):
        read_map[i]     = empty_read
        write_map[i]    = empty_wirte
        name_map[i]     = empty_name
    for i in range(0xFF00, 0xFF4C):
        read_map[i]     = io_read
        write_map[i]    = io_write
        name_map[i]     = io_name
    for i in range(0xFF4C, 0xFF80):
        read_map[i]     = empty_read
        write_map[i]    = empty_wirte
        name_map[i]     = empty_name
    for i in range(0xFF80, 0xFFFF):
        read_map[i]     = zeropage_read
        write_map[i]    = zeropage_write
        name_map[i]     = zeropage_name
        
bios_running = True
def end_bios():
    global bios_running, read_map, write_map
    bios_running = False
    dlog.print_message("MEM", "end of bios")
    for i in range(0, 0x100):
        read_map[i] = car.rom_0_read
        write_map[i] = car.rom_0_write
        name_map[i] = car.rom_0_name

# bios
bios_mem = None
def bios_read(addr):
    return bios_mem[addr]
def bios_write(addr, byte):
    dlog.print_error("MEM", "can't write to bios")
    pass
def bios_name():
    return "BIOS"
    
# video ram
videoram_mem = [0]*0x2000
def videoram_read(addr):
    return videoram_mem[addr-0x8000]
def videoram_write(addr, byte):
    videoram_mem[addr-0x8000] = byte
def videorame_name():
    return "Video RAM"
    
# internal ram
intram_mem = [0]*0x2000
def intram_read(addr):
    return intram_mem[addr-0xC000]
def intram_write(addr, byte):
    intram_mem[addr-0xC000] = byte
def intram_name():
    return "RAM (internal)"
    
# echo of internal ram
def intramecho_read(addr):
    return intram_mem[addr-0xE000]
def intramecho_write(addr, byte):
    intram_mem[addr-0xE000] = byte
def intramecho_name():
    return "RAM (echo)"
    
# sprite attrib memory
def spritemem_read(addr):
    # addr-0xFE00
    dlog.print_error("MEM", "spritemem_read not implemented")
    pass
def spritemem_write(addr, byte):
    # addr-0xFE00
    dlog.print_error("MEM", "spritemem_write not implemented")
    pass
def spritemem_name():
    return "Sprite Attribute Memory"

# empty but unusable for I/O
def empty_read(addr):
    dlog.print_error("MEM", "empty_read not implemented")
    pass
def empty_wirte():
    dlog.print_error("MEM", "empty_wirte not implemented")
    pass
def empty_name():
    return "I/O ports (unusable)"

# I/O ports
io_mem = [0]*0x4C
def io_read(addr):
    dlog.print_warning("MEM", "io_read not complete")
    return io_mem[addr-0xFF00]
def io_write(addr, byte):
    dlog.print_warning("MEM", "io_write not complete")
    io_mem[addr-0xFF00] = byte
def io_name():
    return "I/O ports"

# zero page
mem_zeropage = [0]*0x100
def zeropage_read(addr):
    return mem_zeropage[addr-0xFF80]
def zeropage_write(addr, byte):
    mem_zeropage[addr-0xFF80] = byte
def zeropage_name():
    return "RAM (zero page)"

def read_byte(addr):
    if(dlog.enable_mem_read):
        byte = read_map[addr](addr)
        dlog.print_mem("read_byte", addr, byte, name_map[addr]())
        return byte
    return read_map[addr](addr)

def write_byte(addr, byte):
    if(dlog.enable_mem_write):
        dlog.print_mem("write_byte ", addr, byte, name_map[addr]())
    write_map[addr](addr, byte)
    
def read_word(addr):
    return (read_byte(addr+1)<<8)|read_byte(addr)

def write_word(addr, word):
    write_byte(addr+1, (word>>8)&0xFF)
    write_byte(addr, word&0xFF)

