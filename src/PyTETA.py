# -*- coding: UTF-8 -*-


if __name__ == '__main__':

    from lib.gui_client import *

    try:    
        chat = GUI_Client()    
        chat.start()
        gtk.main()
        
    except IMException, e:
        print e.get_message()
