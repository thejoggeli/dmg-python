import dlog 

class Info:
    title = ""
    license = ""
    cgb = 0
    sgb = 0
    type = ""
    rom_size = 0
    ram_size = 0
info = Info()

class RomFile:
    bytes = None
rom_file = RomFile()    

# function pointers for memory
rom_0_read = None
rom_0_write = None
rom_0_name = None
rom_x_read = None
rom_x_write = None
rom_x_name = None
ram_read = None
ram_write = None
ram_name = None
mbc_state = None
    
def load_gb_file(file):
    with open(file, "rb") as fh:    
        rom_file.bytes = bytearray(fh.read())
    
    info.title = ""
    for i in range(0x0134, 0x0144):
        info.title += str(chr(rom_file.bytes[i]))        
    info.license = license_map[str(rom_file.bytes[0x0144]&0xF)+str(rom_file.bytes[0x0145]&0xF)]    
    info.cgb = rom_file.bytes[0x0143]
    info.sgb = rom_file.bytes[0x0146]    
    info.type = carttype = carttype_map[rom_file.bytes[0x0147]]    
    info.rom_size = rom_size_map[rom_file.bytes[0x0148]]
    info.ram_size = ram_size_map[rom_file.bytes[0x0149]]
   
    global rom_0_read, rom_0_write, rom_0_name
    global rom_x_read, rom_x_write, rom_x_name
    global ram_read,   ram_write,   ram_name
    global mbc_state
    
    rom_0_read  = mbc1_rom_0_read
    rom_0_write = mbc1_rom_0_write
    rom_0_name  = mbc1_rom_0_name
    rom_x_read  = mbc1_rom_x_read
    rom_x_write = mbc1_rom_x_write
    rom_x_name  = mbc1_rom_x_name
    ram_read    = mbc1_ram_read
    ram_write   = mbc1_ram_write
    ram_name    = mbc1_ram_name
    mbc_state   = MBC1_State()
    
    num_rom_banks = int(info.rom_size/16)
    num_ram_banks = int(info.ram_size/8)
    
    mbc_state.rom_banks = [None]*num_rom_banks
    for i in range(0, num_rom_banks):
        start = i*0x4000
        end = (i+1)*0x4000
        mbc_state.rom_banks[i] = rom_file.bytes[start:end]
    
    mbc_state.ram_banks = [None]*num_ram_banks
    for i in range(0, num_ram_banks):
        mbc_state.ram_banks[i] = [0]*0x2000
    
def print_info():    
    dlog.print_msg("CAR", "Title\t\t"+info.title)
    dlog.print_msg("CAR", "License\t\t"+info.license)
    dlog.print_msg("CAR", "SGB features\t"+str(info.sgb))
    dlog.print_msg("CAR", "Cartridge type\t"+info.type)
    dlog.print_msg("CAR", "ROM size\t"+str(info.rom_size)+"K" + "\t" + str(len(mbc_state.rom_banks)) + " banks")
    dlog.print_msg("CAR", "RAM size\t"+str(info.ram_size)+"K" + "\t" + str(len(mbc_state.ram_banks)) + " banks")

def print_state():
    mbc_state.print_state()

def update():
    if(dlog.enable.car_state):
        mbc_state.print_state()

class MBC1_State:
    rom_banks = []
    rom_bank_selected = 0
    ram_banks = []
    ram_bank_selected = 0
    rom_ram_mode = 0
    def print_state(self):
        dlog.print_msg(
            "CAR", 
            "cartridge" + "\t" +
            "ROM=" + "0x{0:0{1}X}".format(self.rom_bank_selected, 2) + "\t" +
            "RAM=" + "0x{0:0{1}X}".format(self.ram_bank_selected, 2) + "\t" +
            "Mode=" + ("ROM" if self.rom_ram_mode == 0 else "RAM")
        )

def mbc1_rom_0_read(addr):
    return mbc_state.rom_banks[0][addr]
def mbc1_rom_0_write(addr, byte):
    if(addr >= 0 and addr <= 0x1FFF):
        # RAM enable/disable
        if(byte&0x0A):
            if(dlog.enable.car_ram_enable):
                dlog.print_msg("CAR", "RAM Enable")
            # nothing else to do?
        else: 
            if(dlog.enable.car_ram_enable):
                dlog.print_msg("CAR", "RAM Disable")
            # nothing else to do?
    elif(addr >= 0x2000 and addr <= 0x3FFF):
        # ROM bank select bits 0-4
        x = byte&0x1F 
        if(x == 0x00):
            x |= 0x01
        mbc_state.rom_bank_selected = (mbc_state.rom_bank_selected&0x60)|x
        if(dlog.enable.car_banking):
            dlog.print_msg("CAR", "select_rom_0_4" + "\t" + "Bank " + "0x{0:0{1}X}".format(mbc_state.selected_bank, 2))
def mbc1_rom_0_name():
    return "ROM Bank 0x00"
def mbc1_rom_x_read(addr):
    return mbc_state.rom_banks[mbc_state.rom_bank_selected][addr-0x4000]
def mbc1_rom_x_write(addr, byte):
    if(addr >= 0x4000 and addr <= 0x5FFF):
        x = byte&0x03
        if(mbc_state.rom_ram_mode == 0):
            # ROM bank select bits 5-6
            mbc_state.rom_bank_selected = (x<<5)|(mbc_state.rom_bank_selected&0x1F)
            x = (byte>>5)&0x03
            if(dlog.enable.car_banking):
                dlog.print_msg("CAR", "select_rom_5_6" + "\t" + "Bank " + "0x{0:0{1}X}".format(mbc_state.ram_bank_selected, 2))
        else:
            # RAM bank select
            mbc_state.ram_bank_selected = x
            if(dlog.enable.car_banking):
                dlog.print_msg("CAR", "select_ram" + "\t" + "Bank " + "0x{0:0{1}X}".format(mbc_state.ram_bank_selected, 2))
    elif(addr >= 0x6000 and addr <= 0x7FFF):        
        # ROM/RAM Mode Select
        mbc_state.rom_ram_mode = byte&0x01
        if(mbc_state.rom_ram_mode == 0):
            # only RAM Bank 00h can be used during Mode 0
            mbc_state.ram_bank_selected = 0
        else:   
            # only ROM Banks 0x00-0x1F can be used during Mode 1
            mbc_state.rom_bank_selected = mbc_state.rom_bank_selected&0x1F
        if(dlog.enable.car_banking):
            dlog.print_msg("CAR", "select_mode\t" + "ROM/RAM mode set to " + str(mbc_state.rom_ram_mode))
def mbc1_rom_x_name():
    return "ROM Bank " + "0x{0:0{1}X}".format(mbc_state.rom_bank_selected, 2)
def mbc1_ram_read(addr):
    return mbc_state.ram_banks[mbc_state.ram_bank_selected][addr-0xA000]
def mbc1_ram_write(addr, byte):
    mbc_state.ram_banks[mbc_state.ram_bank_selected][addr-0xA000] = byte
def mbc1_ram_name():   
    return "RAM Bank " + "0x{0:0{1}X}".format(mbc_state.ram_bank_selected, 2)

def mbc2_rom_0_read(addr):
    dlog.print_error("CAR", "mbc2_rom_0_read not implemented")
def mbc2_rom_0_write(addr, byte):
    dlog.print_error("CAR", "mbc2_rom_0_write() can't write to ROM")
def mbc2_rom_0_name():
    dlog.print_error("CAR", "mbc2_rom_0_name not implemented")
def mbc2_rom_x_read(addr):
    dlog.print_error("CAR", "mbc2_rom_x_read not implemented")
def mbc2_rom_x_write(addr, byte):
    dlog.print_error("CAR", "mbc2_rom_x_write() can't write to ROM")
def mbc2_rom_x_name():
    dlog.print_error("CAR", "mbc2_rom_x_name not implemented")
def mbc2_ram_read(addr):
    dlog.print_error("CAR", "mbc2_ram_read not implemented")
def mbc2_ram_write(addr, byte):
    dlog.print_error("CAR", "mbc2_ram_write not implemented")
def mbc2_ram_name():
    dlog.print_error("CAR", "mbc2_ram_name not implemented")

def mbc3_rom_0_read(addr):
    dlog.print_error("CAR", "mbc3_rom_0_read not implemented")
def mbc3_rom_0_write(addr, byte):
    dlog.print_error("CAR", "mbc3_rom_0_write() can't write to ROM")
def mbc3_rom_0_name():
    dlog.print_error("CAR", "mbc3_rom_0_name not implemented")
def mbc3_rom_x_read(addr):
    dlog.print_error("CAR", "mbc3_rom_x_read not implemented")
def mbc3_rom_x_write(addr, byte):
    dlog.print_error("CAR", "mbc3_rom_x_write() can't write to ROM")
def mbc3_rom_x_name():
    dlog.print_error("CAR", "mbc3_rom_x_name not implemented")
def mbc3_ram_read(addr):
    dlog.print_error("CAR", "mbc3_ram_read not implemented")
def mbc3_ram_write(addr, byte):
    dlog.print_error("CAR", "mbc3_ram_write not implemented")
def mbc3_ram_name():
    dlog.print_error("CAR", "mbc3_ram_name not implemented")

rom_size_map = [32, 64, 128, 256, 512, 1024, 2048, 4196]
ram_size_map = [0, 2, 8, 32]

carttype_map = [None]*0x100
carttype_map[0x00] = "ROM"
carttype_map[0x03] = "MBC1+RAM+BATTERY"
carttype_map[0x08] = "ROM+RAM"
carttype_map[0x0C] = "MMM01+RAM"
carttype_map[0x10] = "MBC3+TIMER+RAM+BATTERY"
carttype_map[0x13] = "MBC3+RAM+BATTERY"
carttype_map[0x17] = "MBC4+RAM+BATTERY"
carttype_map[0x1B] = "MBC5+RAM+BATTERY"
carttype_map[0x1E] = "MBC5+RUMBLE+RAM+BATTERY"
carttype_map[0xFE] = "HuC3"
carttype_map[0x01] = "MBC1"
carttype_map[0x05] = "MBC2"
carttype_map[0x09] = "ROM+RAM+BATTERY"
carttype_map[0x0D] = "MMM01+RAM+BATTERY"
carttype_map[0x11] = "MBC3"
carttype_map[0x15] = "MBC4"
carttype_map[0x19] = "MBC5"
carttype_map[0x1C] = "MBC5+RUMBLE"
carttype_map[0xFC] = "POCKET CAMERA"
carttype_map[0xFF] = "HuC1+RAM+BATTERY"
carttype_map[0x02] = "MBC1+RAM"
carttype_map[0x06] = "MBC2+BATTERY"
carttype_map[0x0B] = "MMM01"
carttype_map[0x0F] = "MBC3+TIMER+BATTERY"
carttype_map[0x12] = "MBC3+RAM"
carttype_map[0x16] = "MBC4+RAM"
carttype_map[0x1A] = "MBC5+RAM"
carttype_map[0x1D] = "MBC5+RUMBLE+RAM"
carttype_map[0xFD] = "Bandai TAMA5"

license_map = {}
license_map["00"] = "none"
license_map["09"] = "hot-b"
license_map["0C"] = "elite systems"
license_map["19"] = "itc entertainment"
license_map["1F"] = "virgin"
license_map["25"] = "san-x"
license_map["30"] = "infogrames"
license_map["33"] = "GBC - see above"
license_map["38"] = "Capcom"
license_map["3E"] = "gremlin"
license_map["44"] = "Malibu"
license_map["49"] = "irem"
license_map["4F"] = "u.s. gold"
license_map["52"] = "activision"
license_map["55"] = "park place"
license_map["59"] = "milton bradley"
license_map["5C"] = "naxat soft"
license_map["61"] = "virgin"
license_map["6E"] = "elite systems"
license_map["71"] = "Interplay"
license_map["75"] = "the sales curve"
license_map["7A"] = "triffix entertainment"
license_map["80"] = "misawa entertainment"
license_map["8B"] = "bullet-proof software"
license_map["8F"] = "i'max"
license_map["93"] = "tsuburava"
license_map["97"] = "kaneko"
license_map["9B"] = "Tecmo"
license_map["9F"] = "nova"
license_map["A4"] = "Konami"
license_map["A9"] = "technos japan"
license_map["AD"] = "toho"
license_map["B1"] = "ascii or nexoft"
license_map["B6"] = "HAL"
license_map["BA"] = "*culture brain o"
license_map["BF"] = "sammy"
license_map["C3"] = "Squaresoft"
license_map["C6"] = "tonkin house"
license_map["CA"] = "ultra"
license_map["CD"] = "meldac"
license_map["D0"] = "Taito"
license_map["D3"] = "sigma enterprises"
license_map["D7"] = "copya systems"
license_map["DB"] = "ljn"
license_map["DF"] = "altron"
license_map["E2"] = "uutaka"
license_map["E7"] = "athena"
license_map["EA"] = "king records"
license_map["EE"] = "igs"
license_map["FF"] = "ljn"
license_map["01"] = "nintendo"
license_map["0A"] = "jaleco"
license_map["13"] = "electronic arts"
license_map["1A"] = "yanoman"
license_map["20"] = "KSS"
license_map["28"] = "kotobuki systems"
license_map["31"] = "nintendo"
license_map["34"] = "konami"
license_map["39"] = "Banpresto"
license_map["41"] = "Ubisoft"
license_map["46"] = "angel"
license_map["4A"] = "virgin"
license_map["50"] = "absolute"
license_map["53"] = "american sammy"
license_map["56"] = "ljn"
license_map["5A"] = "mindscape"
license_map["5D"] = "tradewest"
license_map["67"] = "ocean"
license_map["6F"] = "electro brain"
license_map["72"] = "broderbund"
license_map["78"] = "t*hq"
license_map["7C"] = "microprose"
license_map["83"] = "lozc"
license_map["8C"] = "vic tokai"
license_map["91"] = "chun soft"
license_map["95"] = "varie"
license_map["99"] = "arc"
license_map["9C"] = "imagineer"
license_map["A1"] = "Hori electric"
license_map["A6"] = "kawada"
license_map["AA"] = "broderbund"
license_map["AF"] = "Namco"
license_map["B2"] = "Bandai"
license_map["B7"] = "SNK"
license_map["BB"] = "Sunsoft"
license_map["C0"] = "Taito"
license_map["C4"] = "tokuma shoten intermedia"
license_map["C8"] = "koei"
license_map["CB"] = "vap"
license_map["CE"] = "*pony canyon or"
license_map["D1"] = "sofel"
license_map["D4"] = "ask kodansha"
license_map["D9"] = "Banpresto"
license_map["DD"] = "ncs"
license_map["E0"] = "jaleco"
license_map["E3"] = "varie"
license_map["E8"] = "asmik"
license_map["EB"] = "atlus"
license_map["F0"] = "a wave"
license_map["08"] = "capcom"
license_map["0B"] = "coconuts"
license_map["18"] = "hudsonsoft"
license_map["1D"] = "clary"
license_map["24"] = "pcm complete"
license_map["29"] = "seta"
license_map["32"] = "bandai"
license_map["35"] = "hector"
license_map["3C"] = "*entertainment i"
license_map["42"] = "Atlus"
license_map["47"] = "spectrum holoby"
license_map["4D"] = "malibu"
license_map["51"] = "acclaim"
license_map["54"] = "gametek"
license_map["57"] = "matchbox"
license_map["5B"] = "romstar"
license_map["60"] = "titus"
license_map["69"] = "electronic arts"
license_map["70"] = "Infogrammes"
license_map["73"] = "sculptered soft"
license_map["79"] = "accolade"
license_map["7F"] = "kemco"
license_map["86"] = "tokuma shoten intermedia"
license_map["8E"] = "ape"
license_map["92"] = "video system"
license_map["96"] = "yonezawa/s'pal"
license_map["9A"] = "nihon bussan"
license_map["9D"] = "Banpresto"
license_map["A2"] = "Bandai"
license_map["A7"] = "takara"
license_map["AC"] = "Toei animation"
license_map["B0"] = "Acclaim"
license_map["B4"] = "Enix"
license_map["B9"] = "pony canyon"
license_map["BD"] = "Sony imagesoft"
license_map["C2"] = "Kemco"
license_map["C5"] = "data east"
license_map["C9"] = "ufl"
license_map["CC"] = "use"
license_map["CF"] = "angel"
license_map["D2"] = "quest"
license_map["D6"] = "naxat soft"
license_map["DA"] = "tomy"
license_map["DE"] = "human"
license_map["E1"] = "towachiki"
license_map["E5"] = "epoch"
license_map["E9"] = "natsume"
license_map["EC"] = "Epic/Sony records"
license_map["F3"] = "extreme entertainment"