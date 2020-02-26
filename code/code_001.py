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

mem.write_word(0x40A0, 0x7F9F)
code = [
    0x01, 0x34, 0x12,   # LD    BC,0x1234
    0x21, 0xA0, 0x40,   # LD    HL,0x40A0
    0x31, 0x89, 0x67,   # LD    SP,0x6789
    0x2A,               # LDI   A,(HL)
    0x2A,               # LDI   A,(HL)
    0xF9,               # LD    SP,HL
]