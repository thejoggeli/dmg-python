import util_dlog as dlog
import hw_cartridge as car

read_map = [None]*0x10000
write_map = [None]*0x10000
name_map = [None]*0x10000

def init():
    # load bios
    global bios
    with open("bios.gb", "rb") as bios_fh:    
        bios = bytearray(bios_fh.read())
    # load memory functions
    for i in range(0x0000, 0x0100):
        read_map [i]    = bios_read
        write_map[i]    = bios_write
        name_map [i]    = bios_name
    for i in range(0xC000, 0xE000):
        read_map [i]    = intram_read
        write_map[i]    = intram_write
        name_map [i]    = intram_name
    for i in range(0xE000, 0xFE00):
        read_map [i]    = intramecho_read
        write_map[i]    = intramecho_write
        name_map [i]    = intramecho_name
    for i in range(0xFEA0, 0xFF00):
        read_map [i]    = unused_read
        write_map[i]    = unused_write
        name_map [i]    = unused_name
    for i in range(0xFF00, 0xFF80):
        read_map [i]    = iomem_read
        write_map[i]    = iomem_write
        name_map [i]    = iomem_name
    for i in range(0xFF4C, 0xFF80):
        read_map [i]    = unused_read
        write_map[i]    = unused_write
        name_map [i]    = unused_name
    for i in range(0xFF80, 0x10000):
        read_map [i]    = zeropage_read
        write_map[i]    = zeropage_write
        name_map [i]    = zeropage_name
    
    # 0xFF50
    write_map[0xFF50] = write_0xFF50
    name_map [0xFF50] = lambda: "END OF BIOS"
    
    # 0xFFFF
    name_map [0xFFFF] = lambda: "RAM (zero page): IE - Interrupt Enable (R/W)"
    
    # 0xFF0F
    read_map [0xFF0F] = read_0xFF0F
    write_map[0xFF0F] = write_0xFF0F
    name_map [0xFF0F] = lambda: "IF - Interrupt Flags (R/W)"
    
        
bios_running = True
def write_0xFF50(addr, byte):
    # end bios
    global bios_running, read_map, write_map
    if(not bios_running):
        dlog.print_error("MEM", "BIOS already ended")
        return
    bios_running = False
    car.map_memory_bios()
        
def read_0xFF0F(addr):
    return iomem[0x0F]
def write_0xFF0F(addr, byte):
    iomem[0x0F] = byte

# bios
bios = None
def bios_read(addr):
    return bios[addr]
def bios_write(addr, byte):
    dlog.print_error("MEM", "can't write to bios")
    pass
def bios_name():
    return "BIOS"
    
# internal ram
intram = [0]*0x2000
def intram_read(addr):
    return intram[addr-0xC000]
def intram_write(addr, byte):
    intram[addr-0xC000] = byte
def intram_name():
    return "RAM (internal)"
    
# echo of internal ram
def intramecho_read(addr):
    return intram[addr-0xE000]
def intramecho_write(addr, byte):
    intram[addr-0xE000] = byte
def intramecho_name():
    return "RAM (echo)"

# empty but unusable for I/O
def unused_read(addr):
    dlog.print_error("MEM", "unused_read not implemented")
    pass
def unused_write(addr, byte):
    # don't write anything
    # super mario land 1 seems to be writing to this address
    # NOT SURE IF THIS BEHAVIOR IS CORRECT
    pass
def unused_name():
    return "Unused"

# I/O ports
iomem = [0]*0x4C
def iomem_read(addr):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("MEM", "iomem_read not implemented: " + "0x{0:0{1}X}".format(addr, 4))
    return iomem[addr-0xFF00]
def iomem_write(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("MEM", "iomem_write not implemented: " + "0x{0:0{1}X}".format(addr, 4))    
    iomem[addr-0xFF00] = byte
def iomem_name():
    return "I/O ports: not implemented"

# zero page
zeropage = [0]*0x80
def zeropage_read(addr):
    return zeropage[addr-0xFF80]
def zeropage_write(addr, byte):
    zeropage[addr-0xFF80] = byte
def zeropage_name():
    return "RAM (zero page)"
    
def read_byte_silent(addr):
    return read_map[addr](addr)

def write_byte_silent(addr):
    write_map[addr](addr, byte)    

def read_byte(addr):
    if(dlog.enable.mem_read):
        byte = read_map[addr](addr)        
        dlog.print_msg(
            "MEM",
            "0x{0:0{1}X}".format(addr, 4) + "\t" +
            "0x{0:0{1}X}".format(byte, 2) + "\t" +
            name_map[addr](),
            cat="read_byte"
        )
        return byte
    return read_map[addr](addr)

def write_byte(addr, byte):
    if(dlog.enable.mem_write):        
        dlog.print_msg(
            "MEM", 
            "0x{0:0{1}X}".format(addr, 4) + "\t" +
            "0x{0:0{1}X}".format(byte, 2) + "\t" +
            name_map[addr](),
            cat="writ_byte"
        )
    write_map[addr](addr, byte)
    
def read_word(addr):
    return (read_byte(addr+1)<<8)|read_byte(addr)

def write_word(addr, word):
    write_byte(addr+1, (word>>8)&0xFF)
    write_byte(addr, word&0xFF)

