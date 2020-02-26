import dlog
import z80
import mem
import code_loader as cld

z80.init()

cld.add_instruction([0x11, 0xFE, 0xFF]) # LD    DE,nn
cld.add_instruction([0x13])             # INC   DE
cld.add_instruction([0x13])             # INC   DE
cld.add_instruction([0x13])             # INC   DE
cld.add_instruction([0x1B])             # DEC   DE
cld.add_instruction([0x1B])             # DEC   DE
cld.add_instruction([0x1B])             # DEC   DE

cld.load_into_memory(0)
cld.print_code_lines()

for i in range(0, len(cld.instructions)):
    dlog.print_msg("SYS", "========================================================================================")
    z80.execute()
dlog.print_msg("SYS", "========================================================================================")


z80.exit()
