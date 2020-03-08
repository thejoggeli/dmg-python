import util_dlog as dlog
import util_events as events
import util_config as config
import hw_lcd as lcd
import hw_z80 as z80
import hw_gameboy as gameboy
import sdlboy_text
import sdlboy_input
import sdlboy_time
import sdlboy_console
import ctypes
import sdl2
import time

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
    in_console = False
glob = Glob()

def main(): 
    
    gameboy.init()
    events.subscribe(events.EVENT_SCANLINE_CHANGE, on_scanline_change)
    events.subscribe(events.EVENT_VIDEORAM_CHANGE, on_videoram_change)
    events.subscribe(events.EVENT_SPRITEMEM_CHANGE, on_spritemem_change)
    dlog.enable.errors();
   
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        
    # window rect
    glob.window_rect = sdl2.SDL_Rect(0, 0, 800, 600) 
    
    # screen rect
    glob.screen_rect     = sdl2.SDL_Rect(0, 0, lcd.WIDTH, lcd.HEIGHT)
    glob.screen_rect_dst = sdl2.SDL_Rect(0, 0, lcd.WIDTH, lcd.HEIGHT)
    
    # window
    window_flags = 0
    window_flags |= sdl2.SDL_WINDOW_RESIZABLE
    window_flags |= sdl2.SDL_WINDOW_SHOWN
    window_x = config.get("sdlboy_window_x", sdl2.SDL_WINDOWPOS_CENTERED)
    window_y = config.get("sdlboy_window_y", sdl2.SDL_WINDOWPOS_CENTERED)
    window_w = config.get("sdlboy_window_w", 640)
    window_h = config.get("sdlboy_window_h", 480)
    glob.window = sdl2.SDL_CreateWindow(
        b"Dot Matrix Game",
        window_x, window_y,
        window_w, window_h,
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
    
    # text
    sdlboy_text.init(glob.renderer)    
   #sdlboy_text.load_font("console", file="res/font.png", char_size=(7, 9))
    sdlboy_text.load_font("console", file="res/font_large.png", char_size=(14, 18))
           
    # input
    sdlboy_input.init()
    
    # console
    sdlboy_console.init()
    sdlboy_console.open()
            
    # trigger resize
    on_window_resize()
        
    # start main loop
    sdlboy_time.start()
    event = sdl2.SDL_Event()
    while(not glob.exit_requested):
    
        frame_start_time = time.time()
        sdlboy_time.update()
        sdlboy_input.clear_on_keys()
        
        # poll events
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if(event.type == sdl2.SDL_KEYDOWN):
                sdlboy_input.handle_key_down(event)
                # toggle console
                if(event.key.keysym.sym == 1073741882):
                    if(sdlboy_console.is_open):
                        sdlboy_console.close()
                    else:
                        sdlboy_console.open()                        
            elif(event.type == sdl2.SDL_KEYUP):
                sdlboy_input.handle_key_up(event)
            elif event.type == sdl2.SDL_QUIT:
                glob.exit_requested = True
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if(
                    event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED or
                    event.window.event == sdl2.SDL_WINDOWEVENT_MOVED      
                ):
                    on_window_resize()
            # let console handle events
            if(sdlboy_console.is_open):
                sdlboy_console.handle_event(event)                

        # update console
        if(sdlboy_console.is_open):
            sdlboy_console.update()
            
        if(not sdlboy_console.has_control):
            # tick until vblank
            glob.vblank_occured = False
            while(not glob.vblank_occured):
                gameboy.tick()
                    
        # render
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 0xFF)
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
                            
        """
        # window title
        title = b"Dot Matrix Game"
        # cpu time
        title += bytes(b" | Time: ")        
        title += bytes("{0:.1f}".format(round(z80.state.time_passed, 1)).encode("UTF-8"))
        # real time
        title += b" | Real: "
        title += bytes("{0:.1f}".format(round(real_time_passed, 1)).encode("UTF-8"))
        # set window title
        sdl2.SDL_SetWindowTitle(glob.window, title)
        """
                
        # render console        
        if(sdlboy_console.is_open):
            sdlboy_console.render()
        
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
    if(sdlboy_console.is_open):
        sdlboy_console.resize()
    # save window position
    x = ctypes.c_int()
    y = ctypes.c_int()
    sdl2.SDL_GetWindowPosition(glob.window, x, y)
    config.set("sdlboy_window_x", x.value)
    config.set("sdlboy_window_y", y.value)
    config.set("sdlboy_window_w", w.value)
    config.set("sdlboy_window_h", h.value)
    config.save()
        
def on_scanline_change(data):
    if(data == 0):
        glob.vblank_occured = True
def on_videoram_change(data):
    pass
def on_spritemem_change(data):   
    pass
