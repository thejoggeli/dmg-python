import util_dlog as dlog
import util_events as events
import util_config as config
import hw_lcd as lcd
import hw_z80 as z80
import hw_gameboy as gameboy
import hw_mem as mem
import hw_joypad as joy
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
    background_texture  = None
    lcd_texture_background  = None
    background_rect_src = None
    
    lcd_texture_background = None
    lcd_texture_sprites_p1 = None
    lcd_texture_sprites_p0 = None
    lcd_rect_tex = None
    lcd_rect_src = None
    lcd_rect_dst = None
    
    exit_requested = False
    vblank_occured = False
    in_console = False
    cycle_limiter = 0
    speed_estimate = 0
glob = Glob()

def reset():
    gameboy.init()

def main(): 

    dlog.enable.errors()
    
    gameboy.init()
   #gameboy.run_for_n_seconds(5)
    events.subscribe(events.EVENT_SCANLINE_CHANGE, on_scanline_change)
    events.subscribe(events.EVENT_VIDEORAM_CHANGE, on_videoram_change)
    events.subscribe(events.EVENT_SPRITEMEM_CHANGE, on_spritemem_change)
   
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        
    # window rect
    glob.window_rect = sdl2.SDL_Rect(0, 0, 800, 600) 
        
    # window
    window_flags = 0
    window_flags |= sdl2.SDL_WINDOW_RESIZABLE
    # window_flags |= sdl2.SDL_WINDOW_SHOWN
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
    sdl2.SDL_SetRenderDrawBlendMode(glob.renderer, sdl2.SDL_BLENDMODE_BLEND)

    # lcd buffer
    glob.lcd_rect_tex = sdl2.SDL_Rect(0, 0,  176, 176)
    glob.lcd_rect_src = sdl2.SDL_Rect(8, 16, 160, 144)
    glob.lcd_rect_dst = sdl2.SDL_Rect(0, 0,  160, 144)
    
    # background
    glob.lcd_texture_background = sdl2.SDL_CreateTexture(
        glob.renderer, 
        sdl2.SDL_PIXELFORMAT_ARGB8888, 
        sdl2.SDL_TEXTUREACCESS_STREAMING,
        glob.lcd_rect_tex.w,
        glob.lcd_rect_tex.h,
    )
    sdl2.SDL_SetTextureBlendMode(glob.lcd_texture_background, sdl2.SDL_BLENDMODE_BLEND)
    
    # sprites p1
    glob.lcd_texture_sprites_p1 = sdl2.SDL_CreateTexture(
        glob.renderer, 
        sdl2.SDL_PIXELFORMAT_ARGB8888, 
        sdl2.SDL_TEXTUREACCESS_STREAMING,
        glob.lcd_rect_tex.w,
        glob.lcd_rect_tex.h,
    )
    sdl2.SDL_SetTextureBlendMode(glob.lcd_texture_sprites_p1, sdl2.SDL_BLENDMODE_BLEND)
    
    # sprites p0
    glob.lcd_texture_sprites_p0 = sdl2.SDL_CreateTexture(
        glob.renderer, 
        sdl2.SDL_PIXELFORMAT_ARGB8888, 
        sdl2.SDL_TEXTUREACCESS_STREAMING,
        glob.lcd_rect_tex.w,
        glob.lcd_rect_tex.h,
    )
    sdl2.SDL_SetTextureBlendMode(glob.lcd_texture_sprites_p0, sdl2.SDL_BLENDMODE_BLEND)
    
    # text
    sdlboy_text.init(glob.renderer)    
    sdlboy_text.load_font("console", file="res/font.png", char_size=(7, 9))
    #sdlboy_text.load_font("console", file="res/font_large.png", char_size=(14, 18))
           
    # sdlboy components
    sdlboy_input.init()
    sdlboy_console.init()
    
    # open console
    sdlboy_console.set_open(True)
    sdlboy_console.set_control(False)
            
    # trigger resize
    on_window_resize()
        
    # start main loop    
    last_speed_estimate_cpu_time = 0
    last_speed_estimate = 0
    sdlboy_time.start()
    glob.event = sdl2.SDL_Event()
    lost_time = 0
    
    while(not glob.exit_requested):
    
        frame_start_time = time.time()
        sdlboy_time.update()
        
        if(sdlboy_time.since_start - last_speed_estimate >= 1.0):            
            glob.speed_estimate = (z80.state.time_passed-last_speed_estimate_cpu_time)
            last_speed_estimate = sdlboy_time.since_start
            last_speed_estimate_cpu_time = z80.state.time_passed
            
        # poll events
        sdlboy_input.clear_on_keys()
        poll_events()         

        # update console
        if(sdlboy_console.is_open):
            sdlboy_console.update()
            
        if(not sdlboy_console.has_control):
            # tick until vblank
            if(glob.cycle_limiter):
                cycle_counter = 0
                while(cycle_counter < glob.cycle_limiter):
                    gameboy.tick()
                    cycle_counter += z80.state.cycles_delta
            else:                
                glob.vblank_occured = False
                while(not glob.vblank_occured):
                    gameboy.tick()
                    
        # render
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 0xFF)
        sdl2.SDL_RenderClear(glob.renderer)
        if(lcd.state.lcdc_b7):
            sdl2.SDL_UpdateTexture(
                glob.lcd_texture_background, 
                glob.lcd_rect_tex,
                lcd.pixels_background_front,
                glob.lcd_rect_tex.w*4,
            )
            sdl2.SDL_UpdateTexture(
                glob.lcd_texture_sprites_p1, 
                glob.lcd_rect_tex,
                lcd.pixels_sprites_p1_front,
                glob.lcd_rect_tex.w*4,
            )
            sdl2.SDL_UpdateTexture(
                glob.lcd_texture_sprites_p0, 
                glob.lcd_rect_tex,
                lcd.pixels_sprites_p0_front,
                glob.lcd_rect_tex.w*4,
            )
            sdl2.SDL_RenderCopy(
                glob.renderer, 
                glob.lcd_texture_background, 
                glob.lcd_rect_src, 
                glob.lcd_rect_dst,
            )         
            sdl2.SDL_RenderCopy(
                glob.renderer, 
                glob.lcd_texture_sprites_p1, 
                glob.lcd_rect_src, 
                glob.lcd_rect_dst
            )
            sdl2.SDL_RenderCopy(
                glob.renderer, 
                glob.lcd_texture_sprites_p0, 
                glob.lcd_rect_src, 
                glob.lcd_rect_dst
            )
        else:
            sdl2.SDL_SetRenderDrawColor(
                glob.renderer, 
                lcd.color_0.r,
                lcd.color_0.g,
                lcd.color_0.b,
                lcd.color_0.a,
            )
            sdl2.SDL_RenderFillRect(glob.renderer, glob.lcd_rect_dst)
            
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
        sleep_duration = 1.0/60.0 - frame_time_passed - lost_time
        if(sleep_duration > 0.0):
            sdl2.SDL_Delay(int(sleep_duration*1000.0))
            lost_time = 0
            pass
        else:
            lost_time = -sleep_duration
    
    # shutdown
    sdl2.SDL_DestroyWindow(glob.window)
    sdl2.SDL_Quit()   
    return 0
    
def poll_events():
    event = glob.event
    while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
        if(event.type == sdl2.SDL_KEYDOWN):
            handle_keydown_event(event)
        elif(event.type == sdl2.SDL_KEYUP):
            handle_keyup_event(event)
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

def handle_keydown_event(event):
    sdlboy_input.handle_key_down(event)
    # toggle console
    if(event.key.keysym.sym == 1073741882):
        sdlboy_console.set_open(not sdlboy_console.is_open)
    if(sdlboy_console.allow_input):
        key = event.key.keysym.sym
        if(key == 1073741906): # up
            joy.press_dir(joy.DIR_UP)
        elif(key == 1073741905): # down
            joy.press_dir(joy.DIR_DOWN)
        elif(key == 1073741904): # left
            joy.press_dir(joy.DIR_LEFT)
        elif(key == 1073741903): # right
            joy.press_dir(joy.DIR_RIGHT)
        elif(key == 115): # S
            joy.press_btn(joy.BTN_SELECT)
        elif(key == 100): # D
            joy.press_btn(joy.BTN_START)
        elif(key == 119): # W
            joy.press_btn(joy.BTN_A)
        elif(key == 101): # E
            joy.press_btn(joy.BTN_B)

def handle_keyup_event(event):
    sdlboy_input.handle_key_up(event)
    key = event.key.keysym.sym
    if(key == 1073741906): # up
        joy.release_dir(joy.DIR_UP)
    elif(key == 1073741905): # down
        joy.release_dir(joy.DIR_DOWN)
    elif(key == 1073741904): # left
        joy.release_dir(joy.DIR_LEFT)
    elif(key == 1073741903): # right
        joy.release_dir(joy.DIR_RIGHT)
    elif(key == 115): # S
        joy.release_btn(joy.BTN_SELECT)
    elif(key == 100): # D
        joy.release_btn(joy.BTN_START)
    elif(key == 119): # W
        joy.release_btn(joy.BTN_A)
    elif(key == 101): # E
        joy.release_btn(joy.BTN_B)
        
def on_window_resize():
    w = ctypes.c_int()
    h = ctypes.c_int()
    sdl2.SDL_GetWindowSize(glob.window, w, h)
    glob.window_rect.w = w.value
    glob.window_rect.h = h.value
    window_wf = float(glob.window_rect.w)
    window_hf = float(glob.window_rect.h)
    window_af = window_wf/window_hf
    screen_wf = float(160)
    screen_hf = float(144)
    screen_af = screen_wf/screen_hf
    
    if(window_af > screen_af):
        glob.lcd_rect_dst.h = glob.window_rect.h
        glob.lcd_rect_dst.w = int(window_hf*screen_af)
        glob.lcd_rect_dst.x = int(window_wf/2.0-window_hf*screen_af/2.0)
        glob.lcd_rect_dst.y = 0
    else:    
        glob.lcd_rect_dst.w = glob.window_rect.w
        glob.lcd_rect_dst.h = int(window_wf/screen_af)
        glob.lcd_rect_dst.x = 0
        glob.lcd_rect_dst.y = int(window_hf/2.0-window_wf/screen_af/2.0)
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
