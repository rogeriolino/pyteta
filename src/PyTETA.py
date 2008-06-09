# -*- coding: UTF-8 -*-

"""

    PyTETA Client
    
    Interface grafica para utilizar o sistema de chat, modo cliente, baseado no protocolo
    P.A.T.E.T.A. (Protocolo Aberto de Transferência Especialmente para Trabalhos Acadêmicos)
    
    @author: Rogério Alencar Lino Filho
    @version: 0.0.1

"""


if __name__ == '__main__':

    from lib.gui_client import *

    try:    
        chat = GUI_Client()    
        chat.start()
        gtk.main()
        
    except IMException, e:
        print e.get_message()
