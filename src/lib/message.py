# -*- coding: UTF-8 -*-

from struct import pack
from struct import unpack

from chat import IMException

class Message:
    """
        Classe Message
    """
    
    SIGNALS = ('!', 'A', 'E', 'I', 'L', 'M', 'P', 'S', 'W')    
    CLIENT_SERVER = 0
    SERVER_CLIENT = 1
    
    def __init__(self, type):
        self.set_type(type)
        
    def encode(self):
        raise IMException('Metodo Message.encode() não implementado')
    
    def decode(self, type, message):        
        raise IMException('Metodo Message.decode() não implementado')
    
    def set_type(self, type):
        """Define o sinal da mensagem"""
        if type != self.CLIENT_SERVER and type != self.SERVER_CLIENT:
            raise IMException('Erro ao definir tipo da mensagem.')
        self.type = type
            
    def get_type(self):
        """Retorna o valor de sinal da mensagem"""
        return self.type
        
    def set_signal(self, signal):
        """Define o sinal da mensagem"""
        if signal in self.SIGNALS:
            self.signal = signal
            
    def get_signal(self):
        """Retorna o valor de sinal da mensagem"""
        return self.signal
    
    def set_data(self, data):
        """Define o conteudo da mensagem, o dado"""
        self.data = data
        
    def get_data(self):
        """Retorna o conteudo da mensagem, o dado"""
        return self.data
    
    def set_id(self, id):
        """Define o id de controle de origem/destino da mensagem"""
        self.id = id
        
    def get_id(self):
        """Retorna o id de controle de origem/destino da mensagem"""
        return self.id
        
    def pack(self, data):
	""""""
   	return pack('<h', data)
    	
    def unpack(self, data):        
	""""""
	return unpack('<h', data)[0]
    
    def get_message_size(message):
        """Retorna o tamanho da mensagem contido no cabecalho"""        
        return unpack('<h', message[0:2])[0]
    
    def get_message(message):
        """Remove o cabecalho com o tamanho da mensagem e retorna o resto"""
        return message[2:] 
    
    get_message_size = staticmethod(get_message_size)
    get_message = staticmethod(get_message)
    
    
class Public(Message):
    """Mensagem Publica enviada entre o servidor e o cliente"""
    
    def __init__(self, type):
        Message.__init__(self, type)
        if self.get_type() == self.CLIENT_SERVER:
            self.set_signal('A')
        else:
            self.set_signal('M')
        
    def encode(self):
        # se for mensagem do cliente para o servidor
        if self.get_type() == self.CLIENT_SERVER:
            message = '%s%s' % (self.get_signal(), self.get_data()) # signal == 'A'
            return '%s%s' % (self.pack(len(message)), message)
        # se for mensagem do servidor para o cliente
        elif self.get_type() == self.SERVER_CLIENT:
            message = '%s%s%s' % (self.get_signal(), self.pack(self.get_id()), self.get_data()) # signal == 'M'
            return '%s%s' % (self.pack(len(message)), message)
        raise IMException('Erro ao decodificar mensagem de Evento, formato incorreto.')
    
    def decode(self, message):
        if message.strip() == '':
            raise IMException('Erro ao decodificar a mensagem, formato incorreto')
        # se for mensagem do cliente para o servidor
        if self.get_type() == self.CLIENT_SERVER:
            self.set_data(message[1:])
        # se for mensagem do servidor para o cliente
        elif self.get_type() == self.SERVER_CLIENT:
            self.set_id(self.unpack(message[1:3]))
            self.set_data(message[3:])
        

class Private(Message):
    """Mensagem Privada enviada entre o servidor e o cliente"""
    
    def __init__(self, type, id = None):
        Message.__init__(self, type)
        self.set_signal('P')
        self.set_id(id)
        
    def encode(self):
        if self.get_id() == None:
            raise IMException('Erro ao codificar mensagem Privada, formado incorreto.')
        message = '%s%s%s' % (self.get_signal(), self.pack(self.get_id()), self.get_data())
        return '%s%s' % (self.pack(len(message)), message)
    
    def decode(self, message):
        if message.strip() == '':
            raise IMException('Erro ao decodificar a mensagem, formato incorreto')
        self.set_id(self.unpack(message[1:3]))
        self.set_data(message[3:])
        
        
class Event(Message):
    """Mensagem de Evento enviada entre o servidor e o cliente"""
    
    def __init__(self, type, signal, id = None): 
        Message.__init__(self, type)
        self.set_signal(signal)
        self.set_id(id)
        
    def encode(self):
        if self.get_type() == self.CLIENT_SERVER:
            message = '%s%s' % (self.get_signal(), self.get_data())
            return '%s%s' % (self.pack(len(message)), message)
        elif self.get_type() == self.SERVER_CLIENT:
            if self.get_signal() in ('!', 'W'):
                message = '%s%s' % (self.get_signal(), self.get_data())
                return '%s%s' % (self.pack(len(message)), message)
            elif self.get_id() != None:
                message = '%s%s%s' % (self.get_signal(), self.pack(self.get_id()), self.get_data())
                return '%s%s' % (self.pack(len(message)), message)
        raise IMException('Erro ao codificar mensagem de Evento, formato incorreto.')
        
    def decode(self, message):
        if message.strip() == '':
            raise IMException('Erro ao decodificar a mensagem, formato incorreto')
        if self.get_type() == self.CLIENT_SERVER:
            self.set_data(message[1:])
        elif self.get_type() == self.SERVER_CLIENT:
            if self.get_signal() in ('!', 'W'):
                self.set_data(message[1:])
            else:
                self.set_id(self.unpack(message[1:3]))
                self.set_data(message[3:])
        
    
        
