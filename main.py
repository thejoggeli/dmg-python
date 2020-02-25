import dlog
import z80
import mem

z80.init()


code = [
    0x3E, 0x42,         # LD    A,0x42
    0xEA, 0x00, 0x40,   # LD    (0x4000),A
    0x26, 0x40,         # LD    H,(0x40)
    0x2E, 0x00,         # LD    L,(0x00)
    0x46,               # LD    B,(HL)
    0x3E, 0x10,         # LD    A,0x10
    0x32,               # LDD   (HL),A
    0x3E, 0x20,         # LD    A,0x20
    0x32,               # LDD   (HL),A
    0x26, 0xFF,         # LD    H,(0xFF)
    0x2E, 0xFE,         # LD    L,(0xFE)
    0x22,               # LDI   (HL),A
    0x22,               # LDI   (HL),A
    0x22,               # LDI   (HL),A
    0x32,               # LDD   (HL),A
    0x32,               # LDD   (HL),A
    0x32,               # LDD   (HL),A
    0x3E, 0xFF,         # LD    A,0xFF
    0x0E, 0x77,         # LD    C,0x77
    0xE2,               # LD    (0xFF00+C),A
    0x3E, 0x20,         # LD    A,0x20
    0xF2,               # LD    A,(0xFF00+C)
    0x3E, 0x20,         # LD    A,0x20
    0xF0, 0x77,         # LD    A,(0xFF00+n)
    0xE0, 0x78,         # LD    (0xFF00+n),A
    0x26, 0xFF,         # LD    H,(0xFF)
    0x2E, 0x76,         # LD    L,(0xFE)
    0x2A,               # LDI   A,(HL)
    0x2A,               # LDI   A,(HL)
    0x2A,               # LDI   A,(HL)
    0x2A,               # LDI   A,(HL)
]

for i in range(len(code)):
    mem.write_byte(i, code[i])

for i in range(0, 31):
    dlog.print_msg("SYS", "====================================================================================")
    z80.execute()
dlog.print_msg("SYS", "====================================================================================")


z80.exit()

