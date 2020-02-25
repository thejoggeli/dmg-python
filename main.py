import dlog
import z80
import mem

z80.init()

mem.write_word(0x40A0, 0x7F9F)
code = [
    0x01, 0x34, 0x12,   # LD    BC,0x1234
    0x21, 0xA0, 0x40,   # LD    HL,0x40A0
    0x31, 0x89, 0x67,   # LD    SP,0x6789
    0x2A,               # LDI   A,(HL)
    0x2A,               # LDI   A,(HL)
    0xF9,               # LD    SP,HL
]

for i in range(len(code)):
    mem.write_byte(i, code[i])

for i in range(0, 6):
    dlog.print_msg("SYS", "====================================================================================")
    z80.execute()
dlog.print_msg("SYS", "====================================================================================")


z80.exit()

