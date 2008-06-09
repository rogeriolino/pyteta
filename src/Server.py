# -*- coding: UTF-8 -*-

from lib.server import Server

if __name__ == '__main__':
    try:
        server = Server()
        server.run()
    except:
        import traceback
        traceback.print_exc()