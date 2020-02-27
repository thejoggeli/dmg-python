import dlog
import z80
import mem
import code_loader as cld

z80.init()

cld.add_instruction([0x3E, 0x40])       # LD    A,n
cld.add_instruction([0x21, 0x04, 0x80]) # LD    HL,nn
cld.add_instruction([0x77])             # LD    (HL),A
cld.add_instruction([0xCB, 0x16])       # RL,   (HL)
cld.add_instruction([0xCB, 0x16])       # RL,   (HL)
cld.add_instruction([0xCB, 0x16])       # RL,   (HL)
cld.add_instruction([0xCB, 0x16])       # RL,   (HL)
cld.add_instruction([0xCB, 0x1E])       # RR,   (HL)
cld.add_instruction([0xCB, 0x1E])       # RR,   (HL)
cld.add_instruction([0xCB, 0x1E])       # RR,   (HL)

cld.load_into_memory(0)
cld.print_code_lines()

for i in range(0, len(cld.instructions)):
    dlog.print_msg("SYS", "========================================================================================")
    z80.execute()
dlog.print_msg("SYS", "========================================================================================")


z80.exit()