

if __name__ == '__main__':
    
    from lib.server import Server
    
    try:
        server = Server()
        server.run()
    except:
        import traceback
        traceback.print_exc()