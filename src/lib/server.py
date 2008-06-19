# -*- coding: UTF-8 -*-

import time
import thread

from chat import *
from message import *
from client import Client


class Server(Chat):
    """
        The Server class
    """
    
    
    def __init__(self):
        Chat.__init__(self)
        self.ini = 1
        self.clients = {}
        self.connections = {}
        self.set_server()
        self.running = False
    
    def run(self):
        """Executa o servico"""
        try:
            # imprime mensagem de welcome
            print self.welcome()
            # cria o socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            self.socket.setblocking(False)
            # bind o socket a partir da porta configurada
            self.socket.bind(('0.0.0.0', self.get_server_port()))
            # backlog
            self.socket.listen(5)
            # rodando
            self.running = True
            while self.running:
                # aceita nova conexao
                try:
                    conn, addr = self.socket.accept()                
                    thread.start_new_thread(self.listen, (conn, addr))
                except:
                    time.sleep(0.1)
            # fecha as conexoes
            self.disconnect()
        except socket.error, e:
            print 'Erro: %s' % e.get_message()
            self.disconnect()
        except IMException, e:
            print 'Erro: %s' % e.get_message()
            self.disconnect()
        except:
            import traceback
            traceback.print_exc()

        
    def listen(self, conn, addr):
        """Metodo para ficar escutando a conexao informada por parametro"""
        try:
            client = None
            ip = addr[0]
            port = addr[1]
            while self.running:
                try:
                    full_data = conn.recv(self.get_data_size())
                except:
                    time.sleep(0.1)
                    continue
                # cliente desconectou
                if not full_data and client != None:
                    print 'Saiu  : %s, \tID: %s, \tIP: %s, \tPort: %s' % (client.get_nick_name(), client.get_id(), client.get_ip_address(), client.get_port())
                    # envia mensagem para todos informando saida do cliente                  
                    message = Event(Message.SERVER_CLIENT, 'S')
                    message.set_id(client.get_id())
                    message.set_data('')
                    self.send_to_all(message.encode())
                    # remove cliente e conexao (desconecta)
                    self.remove(client.get_id())
                    return
                # mudanca de nickname
                else:
                    # trata a mensagem
                    while len(full_data):
                        # pega no cabecalho o tamanho da mensagem da vez
                        size = Message.get_message_size(full_data)
                        # pega o conteudo da mensagem
                        data = Message.get_message(full_data)[:size]
                        # elimina a mensagem consumida
                        full_data = Message.get_message(full_data)[size:]
                        # entrou (client == None) ou mudou nickname (client != None)
                        if data[0] == 'I':
                            # decodifica a mensagem
                            receive = Event(Message.CLIENT_SERVER, 'I')
                            receive.decode(data)
                            # cliente ainda nao existe, mas o servidor esta cheio
                            if client == None and len(self.clients) > self.get_max_conn():
                                # envia mensagem alertando
                                message = Event(Message.SERVER_CLIENT, '!')
                                message.set_data('O Servidor está cheio.')
                                conn.send(message.encode())
                                # e remove a conexao
                                self.remove(client.get_id())
                                return
                            # verifica se e a primeira vez, usuario ainda nao existe
                            elif client == None:
                                client = Client()
                                client.set_id(self.ini)
                                client.set_port(port)
                                client.set_ip_address(ip)
                                # trata nickname, espacos e tamanho
                                nick = receive.get_data()
                                if nick.strip() == '':
                                    nick = 'user_%s' % client.get_id()
                                else:
                                    nick = receive.get_data().split()[0]
                                    nick = nick[:self.MAX_NICK_LEN]
                                client.set_nick_name(nick)
                                # verifica se ja existe o nickname e adiciona caso nao exista
                                if self.add_client(self.ini, client):
                                    self.add_connection(self.ini, conn)
                                    # incrementa o ini para o proximo cliente
                                    self.inc_ini()
                                    # envia confirmacao de conexao ao cliente
                                    message = Event(Message.SERVER_CLIENT, 'I')
                                    message.set_id(client.get_id())
                                    message.set_data(client.get_nick_name())
                                    conn.send(message.encode())
                                    # envia mensagem de Evento para o Cliente
                                    message = Event(Message.SERVER_CLIENT, 'W')
                                    message.set_data(self.welcome())                                                                
                                    conn.send(message.encode())
                                    # envia para o novo usuario a lista de clientes conectados
                                    self.send_connecteds(conn)
                                    # envia mensagem para todos (exceto este) que usuário entrou
                                    message = Event(Message.SERVER_CLIENT, 'E')
                                    message.set_id(client.get_id())
                                    message.set_data(client.get_nick_name())
                                    self.send_to_all(message.encode(), client.get_id())
                                    # imprime mensagem para log/debug
                                    print 'Entrou: %s, \tID: %s, \tIP: %s, \tPort: %s' % (client.get_nick_name(), client.get_id(), client.get_ip_address(), client.get_port())
                                # nickname ja existe envia mensagem alertando                                
                                else:
                                    # envia mensagem alertando
                                    message = Event(Message.SERVER_CLIENT, '!')
                                    message.set_data('Nickname já está em uso, favor escolher outro.')
                                    conn.send(message.encode())
                                    # e remove a conexao
                                    self.remove(client.get_id())
                                    return
                            # mudanca de nickname
                            else:
                                # se novo nick nao esta em uso                                
                                if not self.exists(receive.get_data()):
                                    # guarda nick velho so para exibir mudanca
                                    old = client.get_nick_name()
                                    # altera nickname
                                    client.set_nick_name(receive.get_data())
                                    # envia mensagem que usuário entrou para todos
                                    message = Event(Message.SERVER_CLIENT, 'I')
                                    message.set_id(client.get_id())
                                    message.set_data(client.get_nick_name())
                                    self.send_to_all(message.encode())
                                    print '%s mudou nick para %s' % (old, client.get_nick_name())                        
                        # mensagem para todos
                        elif data[0] == 'A':
                            # decodifica a mensagem para enviar a todos
                            receive = Public(Message.CLIENT_SERVER)
                            receive.set_id(client.get_id())
                            receive.decode(data)
                            # envia mensagem para todos
                            message = Public(Message.SERVER_CLIENT)
                            message.set_id(client.get_id())
                            message.set_data(receive.get_data())
                            self.send_to_all(message.encode())
                            # imprime mensagem para log/debug
                            print '%s say: %s' % (client.get_nick_name(), message.get_data())
                        # mensagem privada
                        elif data[0] == 'P':
                            # decodifica a mensagem para enviar ao destinatario
                            receive = Private(Message.CLIENT_SERVER)
                            receive.decode(data)
                            # verifica se o client ainda esta conectado
                            if self.clients.has_key(receive.get_id()):
                                # envia ao destinatario
                                message = Private(Message.SERVER_CLIENT)
                                message.set_id(client.get_id())
                                message.set_data(receive.get_data())
                                self.send_to(receive.get_id(), message.encode())
                                # imprime mensagem para log/debug
                                print '%s say to %s: %s' % (client.get_nick_name(), self.clients[receive.get_id()].get_nick_name(), receive.get_data())
                        # cliente enviou mensagem de saida
                        elif data[0] == 'S':
                            # decodifica a mensagem para enviar a todos
                            receive = Event(Message.CLIENT_SERVER, 'S')
                            receive.decode(data)
                            # envia mensagem para todos                           
                            message = Event(Message.SERVER_CLIENT, 'S')
                            message.set_id(client.get_id())
                            message.set_data(receive.get_data())
                            self.send_to_all(message.encode())
                            # imprime mensagem para log/debug
                            print 'Saiu  : %s, \tID: %s, \tMensagem: %s' % (client.get_nick_name(), client.get_id(), receive.get_data())
                            # remove cliente e conexao (desconecta)
                            self.remove(client.get_id())
                            return
        
        except socket.error, e:
            print 'Erro: %s' % e.get_message()
            
        except IMException, e:
            self.remove(client.get_id())
            print 'Erro: %s' % e.get_message()
        
        except:         
            import traceback
            traceback.print_exc()


    def inc_ini(self):
        """Incrementa o valor de ini de acordo com a regra do servidor"""
        if len(self.clients) < self.MAX_CONN:
            if self.ini < self.MAX_CONN:
                self.ini += 1
            else:
                free = [ i for i in range(1, len(self.clients)+1) if not i in self.clients.keys() ]
                self.ini = free[0]
            return True
        return False           
            

    def set_server(self):
        """Resgata as informacoes de conexao do arquivo de configuracao"""
        ini = IOConf.read()
        self.set_server_port(ini['server_port'])       
        self.MAX_CONN = ini['max_conn']
        self.MAX_NICK_LEN = 20
        
    
    def send_connecteds(self, conn):
        """Envia para a conexao especificada todos os usuarios conectados"""
        message = Event(Message.SERVER_CLIENT, 'L')
        for k in self.clients.keys():
            message.set_id(self.clients[k].get_id())
            message.set_data(self.clients[k].get_nick_name())
            conn.sendall(message.encode())
    
    
    def send_to(self, id, signal):
        """Send the signal for especify client"""
        try:
            self.connections[id].sendall(signal)
        except:
            import traceback
            traceback.print_exc()
            
            
    def send_to_all(self, message, skip = None):
        """Envia uma mensage para todos os clientes"""
        for k in self.connections.keys():
            if skip != k:
                self.connections[k].send(message)
            
            
    def exists(self, nick):
        """Verifica se já existe o nick no servidor"""
        if nick in [ self.clients[k].get_nick_name() for k in self.clients.keys() ]:
            return True
        return False
        
        
    def add_client(self, id, client):
        """Adiciona um novo cliente na lista de clientes conectados"""
        if self.exists(client.get_nick_name()):
            return False
        self.clients[id] = client
        return True
    
    
    def add_connection(self, id, conn):
        """Adiciona uma nova conexao na lista de conexoes"""
        self.connections[id] = conn
        return True
    
    
    def disconnect(self):
        """Disconecta todas as conexoes"""
        for cli in self.clients.values():
            self.remove(cli.get_id())
        self.socket.close()        
        print 'Disconnected'
   
    
    def remove(self, id):
        """Remove o cliente e sua conexao do id informado"""
        self.remove_client(id)
        self.remove_connection(id)
    
    
    def remove_client(self, id):
        """Remove o cliente da lista de clientes conectados"""
        try:            
            self.clients.pop(id)
        except:
            pass
        
        
    def remove_connection(self, id):
        """Remove a conexao da lista de conexoes"""
        try:
            conn = self.connections.pop(id)
            conn.close()
        except:
            pass


    def welcome(self):
        """Retorna a mensagem de Welcome do servidor"""
        w = []
        w.append(" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
        w.append(" ++      _____________________________________________________________      ++ ")
        w.append(" ++    /                                                               \    ++ ")
        w.append(" ++   |              ***    Welcome to PyTETA Server    ***             |   ++ ")
        w.append(" ++   |                                                                 |   ++ ")
        w.append(" ++   |                                               version 1.0.2     |   ++ ")
        w.append(" ++   |                                                                 |   ++ ")
        w.append(" ++   |  Author:  Rogério Alencar Lino Filho                            |   ++ ")
        w.append(" ++   |  Website: http://rogeriolino.wordpress.com/                     |   ++ ")
        w.append(" ++   |                                                                 |   ++ ")
        w.append(" ++   |                                                                 |   ++ ")
        w.append(" ++   |                      NO FLOOD, PLEASE !!!                       |   ++ ")
        w.append(" ++   |                                                                /    ++ ")
        w.append(" ++    \_______________________________________________________    ___/     ++ ")
        w.append(" ++                                                             \ |         ++ ")
        w.append(" ++                                                              \|         ++ ")
        w.append(" ++                                                               `         ++ ")
        w.append(" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
        return '\n'.join(w)
          
        
        

