# -*- coding: UTF-8 -*-

from chat import *
from message import *

class Client(Chat):
    """
        The Client class
    """
    
    def __init__(self):
        Chat.__init__(self)
        self.id = 0
        self.port = 0
        self.ip_address = ''
        self.nick_name = ''
        self.quit_msg = ''
        self.set_client()
        
    def set_client(self):
        """Resgata as informacoes de conexao do arquivo de configuracao"""
        ini = IOConf.read()
        self.set_nick_name(ini['nick_name'])
        self.set_quit_msg(ini['quit_msg'])
        self.set_server_port(ini['server_port'])
        self.set_server_host(ini['server_host'])        
        
    def get_id(self):
        """Return the Client id"""
        return self.id
    
    def set_id(self, id):
        """Set the Client id"""
        self.id = id
        
    def get_port(self):
        """Return the Client port"""
        return self.port
    
    def set_port(self, port):
        """Set the Client port"""
        try:
	        self.port = int(port)
	except ValueError:
		raise IMException('A porta do servidor deve ser um inteiro')
    
    def get_nick_name(self):
        """Return the Client nick name"""
        return self.nick_name
    
    def set_nick_name(self, nick):
        """Set the Client nick name"""
        self.nick_name = nick
    
    def get_ip_address(self):
        """Retorna o endereco ip do cliente"""
        return self.ip_address
    
    def set_ip_address(self, ip):
        """Define o endereco ip do cliente"""
        self.ip_address = ip
        
    def get_quit_msg(self):
        """"""
        return self.quit_msg
    
    def set_quit_msg(self, msg):
        """"""
        self.quit_msg = msg
    
    def send(self, data):
        """Envia uma mensagem publica para o servidor"""
        message = Public(Message.CLIENT_SERVER)
        message.set_data(data)
        self.socket.sendall(message.encode())
    
    def send_to(self, id, data):
        """Envia uma mensagem privada para o id especificado"""
        message = Private(Message.CLIENT_SERVER, id)
        message.set_data(data)
        self.socket.sendall(message.encode())
        
    def send_nick_name(self):
        """Envia ao servidor uma mensagem sobre mudança de nickname ou de entrada no chat"""
        message = Event(Message.CLIENT_SERVER, 'I')
        message.set_data(self.get_nick_name())
        self.socket.sendall(message.encode())
        
    def send_close_msg(self, data):
        """Envia ao servidor uma mensagem de saida"""
        message = Event(Message.CLIENT_SERVER, 'S')
        message.set_data(data)
        self.socket.sendall(message.encode())
        
    def connect(self):
        """Conecta ao servidor do chat"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            
            self.socket.connect((self.get_server_host(), self.get_server_port()))
        except socket.error, e:
            raise IMException('Socket Error: %s' % e[1])
        except Exception, e:
            raise IMException('Error: %s' % e)
        
    def disconnect(self, msg = ''):
        """Desconecta do servidor"""
        if msg:
            self.send_close_msg(msg)
        self.close()
        self.socket = None
        
    def response(self):
        """Retorna uma string contendo a mensagem do servidor"""
        return self.socket.recv(self.get_data_size())
            
