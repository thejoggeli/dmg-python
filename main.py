import dlog
import z80
import mem
import code_loader as cld

z80.init()

mem.write_byte(0x8000, 0x20)
mem.write_byte(0x8001, 0x40)
cld.add_instruction([0x3E, 0xFC])       # LD    A,n
cld.add_instruction([0x31, 0xF0, 0xFF]) # LD    SP,nn    
cld.add_instruction([0xCD, 0x08, 0xA0]) # CALL  nn

cld.load_into_memory(0)
cld.print_code_lines()

for i in range(0, len(cld.instructions)+2):
    dlog.print_msg("SYS", "========================================================================================")
    z80.execute()
dlog.print_msg("SYS", "========================================================================================")


z80.exit()