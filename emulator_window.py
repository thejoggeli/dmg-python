import dlog
import lcd
import z80
import ctypes
import sdl2
import events
import gameboy
import time
import ztext

class Glob:
    renderer = None
    window = None
   #window_surface = None
    window_scale = 1
    window_rect = None
    screen_texture = None
    screen_rect = None
    screen_rect_dst = None
    exit_requested = False
    vblank_occured = False
glob = Glob()

def main(): 
    
    gameboy.init()
    events.subscribe(events.EVENT_SCANLINE_CHANGE, on_scanline_change)
    events.subscribe(events.EVENT_VIDEORAM_CHANGE, on_videoram_change)
    events.subscribe(events.EVENT_SPRITEMEM_CHANGE, on_spritemem_change)
    dlog.enable.errors();
   
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        
    # window rect
    glob.window_rect = sdl2.SDL_Rect(0, 0, 1280, 720) 
    
    # screen rect
    glob.screen_rect     = sdl2.SDL_Rect(0, 0, lcd.WIDTH, lcd.HEIGHT)
    glob.screen_rect_dst = sdl2.SDL_Rect(0, 0, lcd.WIDTH, lcd.HEIGHT)
    
    # window
    window_flags = 0
    window_flags |= sdl2.SDL_WINDOW_RESIZABLE
    window_flags |= sdl2.SDL_WINDOW_SHOWN
    glob.window = sdl2.SDL_CreateWindow(
        b"Dot Matrix Game",
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED,
        glob.window_rect.w,
        glob.window_rect.h,  
        window_flags
    )
    
    # renderer
    renderer_flags = sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_TARGETTEXTURE
    glob.renderer = sdl2.SDL_CreateRenderer(glob.window, -1, renderer_flags)

    # screen texture    
    glob.screen_texture = sdl2.SDL_CreateTexture(
        glob.renderer, 
        sdl2.SDL_PIXELFORMAT_RGBA8888, 
        sdl2.SDL_TEXTUREACCESS_STREAMING,
        glob.screen_rect.w,
        glob.screen_rect.h
    )
    
    # trigger resize
    on_window_resize()
    
    # ztext
    ztext.init(glob.renderer)    
    ztext.load_font("def", file="res/font.png", char_size=(14, 18))
    
    debug_texts = [None]*8
    for i in range(0, len(debug_texts)):
        debug_texts[i] = ztext.Text(ztext.get_font("def"), "test-"+str(i))
        debug_texts[i].set_position(4, 4+i*22)    
        debug_texts[i].set_scale(1)    
        
    # start main loop
    time_start = time.time()
    event = sdl2.SDL_Event()
    while(not glob.exit_requested):
    
        frame_start_time = time.time()
        
        # poll events
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                glob.exit_requested = True
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if(event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED):
                    on_window_resize()
                    
        # tick until vblank
        glob.vblank_occured = False
        while(not glob.vblank_occured):
            gameboy.tick()
                
        # render
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0x33, 0x33, 0x33, 0xFF)
        sdl2.SDL_RenderClear(glob.renderer)
        sdl2.SDL_UpdateTexture(
            glob.screen_texture, 
            glob.screen_rect,
            lcd.pixels,
            glob.screen_rect.w*4
        )
        sdl2.SDL_RenderCopy(
            glob.renderer, 
            glob.screen_texture, 
            glob.screen_rect, 
            glob.screen_rect_dst
        )
        
        real_time_passed = time.time() - time_start
        
        # window title
        title = b"Dot Matrix Game"
        # cpu time
        title += bytes(b" | Time: ")        
        title += bytes("{0:.1f}".format(round(z80.state.time_passed, 1)).encode("UTF-8"))
        # real time
        title += b" | Real: "
        title += bytes("{0:.1f}".format(round(real_time_passed, 1)).encode("UTF-8"))
        # registers
        title += b" | PC: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.pc, 4).encode("UTF-8"))
        title += b" | SP: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.sp, 4).encode("UTF-8"))
        title += b" | AF: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.get_af(), 4).encode("UTF-8"))
        title += b" | BC: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.get_bc(), 4).encode("UTF-8"))
        title += b" | DE: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.get_de(), 4).encode("UTF-8"))
        title += b" | HL: "
        title += bytes("0x{0:0{1}X}".format(z80.reg.get_hl(), 4).encode("UTF-8"))
        
        #sdl2.SDL_SetWindowTitle(glob.window, title)
        
        debug_texts[0].value = "T(Z80):" + "{0:.1f}".format(round(z80.state.time_passed, 1))
        debug_texts[1].value = "T(IRL):" + "{0:.1f}".format(round(real_time_passed, 1))
        debug_texts[2].value = "PC:" + "0x{0:0{1}X}".format(z80.reg.pc, 4)
        debug_texts[3].value = "SP:" + "0x{0:0{1}X}".format(z80.reg.sp, 4)
        debug_texts[4].value = "AF:" + "0x{0:0{1}X}".format(z80.reg.get_af(), 4)
        debug_texts[5].value = "BC:" + "0x{0:0{1}X}".format(z80.reg.get_bc(), 4)
        debug_texts[6].value = "DE:" + "0x{0:0{1}X}".format(z80.reg.get_de(), 4)
        debug_texts[7].value = "HL:" + "0x{0:0{1}X}".format(z80.reg.get_hl(), 4)
                
        for i in range(0, len(debug_texts)):
            debug_texts[i].update()
            debug_texts[i].render()        
        
        # present
        sdl2.SDL_RenderPresent(glob.renderer)
        
        # sleep
        frame_time_passed =  time.time() - frame_start_time
        sleep_duration = 1.0/60.0 - frame_time_passed
        if(sleep_duration > 0.0):
            sdl2.SDL_Delay(int(sleep_duration*1000.0))
    
    # shutdown
    sdl2.SDL_DestroyWindow(glob.window)
    sdl2.SDL_Quit()   
    return 0
    
def on_window_resize():
    w = ctypes.c_int()
    h = ctypes.c_int()
    sdl2.SDL_GetWindowSize(glob.window, w, h)
    glob.window_rect.w = w.value
    glob.window_rect.h = h.value
    window_wf = float(glob.window_rect.w)
    window_hf = float(glob.window_rect.h)
    window_af = window_wf/window_hf
    screen_wf = float(glob.screen_rect.w)
    screen_hf = float(glob.screen_rect.h)
    screen_af = screen_wf/screen_hf
    
    if(window_af > screen_af):
        glob.screen_rect_dst.h = glob.window_rect.h
        glob.screen_rect_dst.w = int(window_hf*screen_af)
        glob.screen_rect_dst.x = int(window_wf/2.0-window_hf*screen_af/2.0)
        glob.screen_rect_dst.y = 0
    else:    
        glob.screen_rect_dst.w = glob.window_rect.w
        glob.screen_rect_dst.h = int(window_wf/screen_af)
        glob.screen_rect_dst.x = 0
        glob.screen_rect_dst.y = int(window_hf/2.0-window_wf/screen_af/2.0)
        
def on_scanline_change(data):
    if(data == 0):
        glob.vblank_occured = True
def on_videoram_change(data):
    pass
def on_spritemem_change(data):   
    pass
