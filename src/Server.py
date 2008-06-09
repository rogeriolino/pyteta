# -*- coding: UTF-8 -*-

"""

    PyTETA Server
    
    Interface grafica para utilizar o sistema de chat, modo servidor, baseado no protocolo
    P.A.T.E.T.A. (Protocolo Aberto de Transferência Especialmente para Trabalhos Acadêmicos)
    
    @author: Rogério Alencar Lino Filho
    @version: 0.0.1

"""

from lib.server import Server

if __name__ == '__main__':
    try:
        server = Server()
        server.run()
    except:
        import traceback
        traceback.print_exc()