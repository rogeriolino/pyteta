# -*- coding: UTF-8 -*-

"""

    PyTETA Server
    
    Interface grafica para utilizar o sistema de chat, modo servidor, baseado no protocolo
    P.A.T.E.T.A. (Protocolo Aberto de Transferência Especialmente para Trabalhos Acadêmicos)
    
    @author: Rogério Alencar Lino Filho
    @version: 1.0.2

"""


if __name__ == '__main__':
    
    from lib.gui_server import *
    
    try:        
        
        server = GUI_Server()
        server.start()

        gtk.gdk.threads_init()
        gtk.main()
        gtk.gdk.threads_leave()
        
    except:
        import traceback
        traceback.print_exc()
        