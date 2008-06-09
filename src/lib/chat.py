# -*- coding: UTF-8 -*-

import os
import sys
import socket

from struct import pack
from struct import unpack

class Chat:
    """
        Classe mae, contem atributos comum para Client e Server
    """

    def __init__(self):
        self.set_data_size(4096)
        self.socket = None
        
    def get_socket(self):
        return self.socket
        
    def set_data_size(self, size):
        self.data_size = size
        
    def get_data_size(self):
        return self.data_size
    
    def set_server_port(self, port):
        errors = ['Por favor, informa um número para porta.', 'Número da porta é inválido.', 'A porta informada é reservada, favor informar outra.']
        e = self.is_valid_port(port)
        if e != -1:
            raise IMException(e)
            raise IMException(erros[e])
        self.server_port = int(port)
        
    def get_server_port(self):
        return self.server_port
    
    def set_server_host(self, host):
        if not self.is_valid_ip(host):
            raise IMException('Endereço de ip inválido.')
        self.server_host = host
        
    def get_server_host(self):
        return self.server_host
            
    def close(self):
        """Fecha a conexao do socket"""
        if self.get_socket() != None:
            self.socket.close()
            
    def is_valid_ip(self, ip):
        """Verifica se e um endereco de ip valido"""
        try:        
            if len(ip.split('.')) != 4:
                print 'tamanho invalido'
                return False
            else:
                c = [int(i) for i in ip.split('.') ]
                if c[0] < 1 or c[0] >  254:
                    print c[0]
                    return False
                if c[3] < 1 or c[3] >  254:
                    print 'quarto'
                    return False
                for i in c[1:2]:
                    if i < 0 or i >  254:
                        print 'meio'
                        return False            
            return True
        except ValueError:
            return False

    def is_valid_port(self, port):
        """Retorna -1 se a porta for valida, senao retorna o numero do erro"""
        try:
            port = int(port)
            if port < 0 or port > 65535:
                return 1
            if port <= 1023:
                return 2
            return -1
        except ValueError:
            return 0
        
        
        

class IOConf:
    """
        Classe responsável por ler e escrever o arquivo de configuração
    """
    
    # dicionario que contem as informacoes do ini
    INI = {
        'server_host' : '',
        'server_port' : '',
        'max_conn' : '',
        'nick_name' : '',
        'quit_msg' : '',
    }
    # caminho do arquivo de configuracao
    FILE = '%s/conf/pyteta.ini' % sys.path[0]
    
    def exists():
        """Retorna se o arquivo de configuracao existe ou nao"""
        return os.path.exists(IOConf.FILE)

    def open_file():
        """Retorna uma lista contendo as linhas do arquivo de configuracao"""
        try:
            if IOConf.exists():
                return file(IOConf.FILE, 'r').readlines()
            else:
                raise IMException("Arquivo de configuração não encontrado.")
        except IOError, e:
            raise IMException(e)
            
    def save_file():
        """Salva o arquivo de configuracao a partir do dicionario da classe"""
        try:
            if IOConf.exists():
                ini = '[pyteta]\n'
                ini += '\n'.join(['%s=%s' % (k, IOConf.INI[k]) for k in IOConf.INI.keys() ])
                file(IOConf.FILE, 'w').write(ini)
            else:
                raise IMException("Arquivo de configuração não encontrado.")
        except IOError, e:
            raise IMException(e)
        
    def read():
        """Le o arquivo de configuracao e retorna o dicionario"""
        lines = IOConf.open_file()
        for l in lines:
            pos = l.find('=')
            if l[:pos] in IOConf.INI.keys():
                value = l[pos+1:]
                value = value.replace('\n', '')
                value = value.replace('\r', '')
                IOConf.INI[l[:pos]] = value.strip()
        return IOConf.INI
     
    # tornando os metodos static
    exists = staticmethod(exists)
    open_file = staticmethod(open_file)
    save_file = staticmethod(save_file)
    read = staticmethod(read)
     
        
class IMException(Exception):
    """
        Classe para controlar as mensagens de erro do programa
    """
    
    def __init__(self, msg):
        self.message = msg
        
    def get_message(self):
        return self.message
        
        
