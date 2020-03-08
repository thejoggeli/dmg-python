import sdlboy_window
import util_config as config
import sys

if __name__ == "__main__":
    config.load()    
    ret = sdlboy_window.main()
    config.save()
    sys.exit(ret)

