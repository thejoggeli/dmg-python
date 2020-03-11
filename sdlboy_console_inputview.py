import sdl2
import sdlboy_text
import sdlboy_window
import sdlboy_console
import sdlboy_console_component
import sdlboy_time
import util_dlog as dlog
import util_config as config

class Inputview(sdlboy_console_component.ConsoleComponent):
    text = None
    text_blocked = None
    font = None
    cursor_timer = 0
    cursor_rect = None
    prev_messages = []
    prev_messages_ptr = -1
    prev_messages_max = 32
    cursor_position = 4
    line_height = 0
    line_offset = 0
    def on_init(self):
        self.font = sdlboy_text.get_font("console")   
        self.text = sdlboy_text.Text(
            font=self.font,
            value=">>> ",
            buffer_size=256
        )
        self.text_blocked = sdlboy_text.Text(
            font=self.font,
            value="PLAY MODE ENABLED (F3)",
            buffer_size=256
        )
        self.line_height = self.font.char_height+4
        self.line_offset = 1
        self.text.update()
        self.cursor_rect = sdl2.SDL_Rect(0, 0, 0, 0) 
        # load saved history
        saved_history = config.get("sdlboy_console_history", False)
        if(saved_history):
            self.prev_messages = saved_history
            self.prev_messages_ptr = len(self.prev_messages)-1    
    def on_update(self):
        self.set_render_required()
    def on_render(self):  
        if(sdlboy_console.allow_input):
            self.text_blocked.set_position(0, self.line_offset)
            self.text_blocked.update()
            self.text_blocked.render()
        else:
            self.text.set_position(0, self.line_offset)
            self.text.update()
            self.text.render()
            self.cursor_timer += sdlboy_time.delta_time
            if(self.cursor_timer >= 1.5):
                self.cursor_timer = 0.0
            if(self.cursor_timer <= 0.75):
                self.cursor_rect.x = self.cursor_position*self.font.char_width
                self.cursor_rect.y = self.font.char_height + self.line_offset - 1
                self.cursor_rect.w = self.font.char_width
                self.cursor_rect.h = 4
                sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255, 255, 255)
                sdl2.SDL_RenderFillRect(self.renderer, self.cursor_rect)
    def on_resize(self):
        pass
    def on_enter(self):
        user_input = self.text.value[4:].strip()
        if(user_input != ""):
            sdlboy_console.textview.print_line(self.text.value.strip())
        if(len(self.text.value.strip()) > 4):
            try:
                self.prev_messages.remove(self.text.value.strip())
            except:
                pass
            self.prev_messages.append(self.text.value.strip())
            self.prev_messages_ptr = len(self.prev_messages)-1
            if(len(self.prev_messages) > self.prev_messages_max):
                start = len(self.prev_messages)-self.prev_messages_max
                end   = len(self.prev_messages)
                self.prev_messages = self.prev_messages[start:end]
                self.prev_messages_ptr = self.prev_messages_max-1              
            config.set("sdlboy_console_history", self.prev_messages)
            config.save()
        self.text.value = ">>> "
        self.text.update()
        self.cursor_position = 4
        self.cursor_timer = 0.25        
        try:
            sdlboy_console.input_handler.handle_input(user_input)
        except Exception as e:
            dlog.print_msg("SYS", str(e))
            sdlboy_console.textview.print_line(str(e))
        dlog.enable.errors();    
    def write_chars(self, chars):
        self.text.value = self.text.value[:self.cursor_position] \
                        + chars \
                        + self.text.value[self.cursor_position:]
        self.text.update()
        self.cursor_position += len(chars)
        self.cursor_timer = 0.25           
    def write_delete(self, ctrl):
        if(self.cursor_position >= len(self.text.value)):
            return
        subtext = self.text.value[self.cursor_position:].strip()
        left = self.cursor_position
        if(ctrl):
            index = len(subtext)
            try: 
                index = subtext.index(" ")+1
            except ValueError:
                pass
            self.text.value = self.text.value[0:left] + subtext[index:]
        else:
            self.text.value = self.text.value[0:self.cursor_position] \
                            + self.text.value[self.cursor_position+1:]
        self.text.update()       
        self.cursor_timer = 0.25            
    def write_backspace(self, ctrl):
        if(self.cursor_position <= 4):
            return
        subtext = self.text.value[0:self.cursor_position].strip()
        right = self.cursor_position
        if(ctrl):
            index = 4
            try: 
                index = subtext.rindex(" ", 4)
            except ValueError:
                pass
            self.text.value = self.text.value[0:index] + self.text.value[right:]
            self.cursor_position = index
        else:
            self.text.value = self.text.value[0:self.cursor_position-1] \
                            + self.text.value[self.cursor_position:]                              
            self.cursor_position -= 1
        self.text.update()        
        self.cursor_timer = 0.25           
    def move_cursor(self, delta, ctrl):
        if(delta == 1):
            if(ctrl):
                while(True):                
                    self.cursor_position += 1
                    if(self.cursor_position >= len(self.text.value)):
                        self.cursor_position = len(self.text.value)
                        break
                    if(self.text.value[self.cursor_position-1] == " "):
                        break
            else:
                self.cursor_position += 1
                if(self.cursor_position >= len(self.text.value)):
                    self.cursor_position = len(self.text.value)        
        elif(delta == -1):
            if(ctrl):
                while(True):                
                    self.cursor_position -= 1
                    if(self.cursor_position <= 4):
                        self.cursor_position = 4
                        break
                    if(self.text.value[self.cursor_position-1] == " "):
                        break
            else:
                self.cursor_position -= 1
                if(self.cursor_position <= 4):
                    self.cursor_position = 4
        self.cursor_timer = 0.25            
    def move_history_up(self):
        if(self.prev_messages_ptr >= 0):
            self.text.value = self.prev_messages[self.prev_messages_ptr]
            self.prev_messages_ptr -= 1
        self.cursor_position = len(self.text.value)
        self.cursor_timer = 0.25           
    def move_history_down(self):
        self.prev_messages_ptr += 1
        if(self.prev_messages_ptr > len(self.prev_messages)-1):
            self.prev_messages_ptr = len(self.prev_messages)-1
        actual_ptr = self.prev_messages_ptr+1
        if(actual_ptr < len(self.prev_messages)): 
            self.text.value = self.prev_messages[actual_ptr]
        else:  
            self.text.value = ">>> "
        self.cursor_position = len(self.text.value)
        self.cursor_timer = 0.25           
    def clear(self):
        self.text.value = ">>> "
        self.cursor_position = 4
    
   