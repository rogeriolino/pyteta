# -*- coding: UTF-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject

from time import sleep
from time import strftime

from chat import *
from message import *
from client import Client
from gui import GUI


# todas as janelas de pvt
pvts = {}


class GUI_Client(GUI):
   
    
    def __init__(self):
        GUI.__init__(self)
        # titulo das janelas
        self.title = 'PyTETA'
        self.window = None
        self.connected = False   
        # usuario
        self.client = Client()
        # todos clientes conectados
        self.clients = {} 
        
        
    def createTray(self):
        """Cria Icone na bandeja e menu popup (ao clicar-lo com o botao direito)"""
        # TrayIcon
        self.statusIcon = gtk.StatusIcon()      
 
        self.menu = gtk.Menu()
        
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        #self.menuItem.connect('activate', self.gtk_main_quit)
        self.menu.append(self.menuItem)
        
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.gtk_main_quit)
        self.menu.append(self.menuItem)
        
        self.imageicon = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.getImagesPath() + 'icon2.png')
        scaled_buf = pixbuf.scale_simple(23, 23, gtk.gdk.INTERP_BILINEAR)
        self.statusIcon.set_from_pixbuf(scaled_buf)
        
        self.statusIcon.set_tooltip(self.title)
        self.statusIcon.connect('activate', self.activate_icon_cb)
        self.statusIcon.connect('popup-menu', self.show_popup_menu, self.menu)
        self.statusIcon.set_visible(1)        
        
        
    def remove_popup(widget, event, data = None):
        """Remove o menu popup"""
        if data:
            data.set_blinking(1)
        return 0
        
        
    def activate_icon_cb(self, widget, data = None):
        """Ao clicar com o botao esquerdo"""
        self.window.set_focus(1)
    
    
    def show_popup_menu(self, widget, button, time, data = None):
        """Exibe o menu popup ao clicar no StatusIcon com o botao direito"""
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)
            
        
    def start(self):
        """Inicia o programa"""
        try:
            # StatusIcon
            self.createTray()
            self.xml = gtk.glade.XML(self.getGladePath() + 'chat.glade')
            self.xml.signal_autoconnect(self)
            # Window
            self.window = self.xml.get_widget('chat')
            self.window.set_title(self.title)
            self.window.maximize()
            # TextView
            self.set_text_areas()
            # Buttons
            self.set_buttons()
            # TreeViews
            self.set_tree_views()
            # janela de preferencias
            self.settings = Settings()
            # variavel para controlar o thread, mata-lo quando desconectar
            self.thread_id = 0            
        except IMException, e:
            self.disconnect()
            self.show_alert(e.get_message()) 

            
    def set_text_areas(self):
        """Resgata do glade os campos de texto da interface"""
        self.txt_chat = self.xml.get_widget('txt_chat')
        self.buffer = self.txt_chat.get_buffer()
        # mark
        self.mark = self.buffer.create_mark("end", self.buffer.get_end_iter(), False)
        # background
        self.pixmap, mask = gtk.gdk.pixbuf_new_from_file(self.getImagesPath() + 'pateta.png').render_pixmap_and_mask()
        self.txt_chat.get_window(gtk.TEXT_WINDOW_TEXT).set_back_pixmap(self.pixmap, False)
        self.txt_send = self.xml.get_widget('txt_send')
        self.txt_send.connect("activate", self.on_btn_send_clicked)
            
            
    def set_buttons(self):
        """Resgata do glade os botoes da interface"""
        self.btn_connect = self.xml.get_widget('btn_connect')
        self.btn_disconnect = self.xml.get_widget('btn_disconnect')
        self.btn_send = self.xml.get_widget('btn_send')
        self.btn_settings = self.xml.get_widget('btn_settings')
        self.toggle_connect_button(False)
        
        
    def set_tree_views(self):
        """Resgata do glade e define o TreeView da interface"""
        self.tv_clients = self.xml.get_widget('tv_clients')
        self.tv_clients.set_size_request(200, 0)
        self.tv_clients_model = gtk.ListStore(str)
        self.tv_clients.set_model(self.tv_clients_model)
        coluna = gtk.TreeViewColumn('Usuários Conectados', gtk.CellRendererText(), text=0)
        coluna.set_reorderable(1)        
        self.tv_clients.append_column(coluna)
        # click duplo abre pvt
        self.tv_clients.connect("row-activated", self.open_pvt)
        
        
    def check_messages(self, sock, *args):
        """Metodo para verficar mensagens vindas do servidor em tempos em tempos"""
        try:
            if self.connected:
                # recebe retorno do servidor
                full_data = self.client.response()
                # erro ao tentar conectar
                if not (full_data or self.has_confirm):
                    self.disconnect()
                    raise IMException('Erro ao tentar conectar.')
                elif not full_data and self.has_confirm:
                    self.disconnect()
                    raise IMException('Server Error: Conexão caiu.')
                # trata a mensagem
                while len(full_data):                
                    # pega no cabecalho o tamanho da mensagem da vez
                    size = Message.get_message_size(full_data)
                    # pega o conteudo da mensagem
                    response = Message.get_message(full_data)[:size]
                    # elimina a mensagem consumida
                    full_data = Message.get_message(full_data)[size:]                                          
                    # confirmacao de login
                    if not self.has_confirm:
                        if response[0] == 'I':
                            # decodifica mensagem
                            message = Event(Message.SERVER_CLIENT, 'I')
                            message.decode(response)
                            # atualiza dados
                            self.client.set_id(message.get_id())
                            self.client.set_nick_name(message.get_data())
                            # estado conectado
                            self.has_confirm = True
                        elif response[0] == '!':
                            # provavelmente nickname ja existe, entao desconecta
                            self.disconnect()
                            message = Event(Message.SERVER_CLIENT, '!')
                            message.decode(response)                            
                            raise IMException('Server Error: %s' % message.get_data())
                    # conexao confirmada
                    elif self.connected:                    
                        # lista de clientes conectados
                        if response[0] == 'L':
                            message = Event(Message.SERVER_CLIENT, 'L')
                            message.decode(response)
                            # adiciona novo cliente
                            self.set_client(message.get_id(), message.get_data())
                        # alguem entrou
                        elif response[0] == 'E':
                            message = Event(Message.SERVER_CLIENT, 'E')
                            message.decode(response)
                            # adiciona novo cliente
                            self.set_client(message.get_id(), message.get_data())
                            # imprime mensagem na tela
                            self.client_signon(message.get_data())
                        # alteracao de nickname
                        elif response[0] == 'I':
                            message = Event(Message.SERVER_CLIENT, 'I')
                            message.decode(response)
                            old = self.clients[message.get_id()]
                            self.set_client(message.get_id(), message.get_data())
                            # imprime mensagem na tela
                            self.client_changed(old, self.clients[message.get_id()])
                        # mensagem para todos
                        elif response[0] == 'M':
                            message = Public(Message.SERVER_CLIENT)
                            message.decode(response)
                            self.client_say(self.clients[message.get_id()], message.get_data())
                        # mensagem privada
                        elif response[0] == 'P':
                            message = Private(Message.SERVER_CLIENT)
                            message.decode(response)
                            # se o pvt nao esta aberto, cria a janela
                            if not pvts.has_key(message.get_id()):
                                pvts[message.get_id()] = PVT(self.client, message.get_id(), self.clients[message.get_id()])
                                self.append_line('(%s) Iniciada conversa privada com: %s' % (strftime('%H:%M:%S'), self.clients[message.get_id()]), 'orange')
                            # imprime mensagem na janela pvt
                            pvts[message.get_id()].client_say(self.clients[message.get_id()], message.get_data(), 'orange')
                            
                        # alguem saiu
                        elif response[0] == 'S':
                            message = Event(Message.SERVER_CLIENT, 'S')
                            message.decode(response)
                            # imprime mensagem na tela
                            self.client_signout(self.clients[message.get_id()], message.get_data())
                            # remove da lista
                            self.remove_client(message.get_id())
                        # mensagem de welcome
                        elif response[0] == 'W':
                            message = Event(Message.SERVER_CLIENT, 'W')
                            message.decode(response)
                            self.display_welcome(message.get_data())
                        # algum alerta do servidor
                        elif response[0] == '!':
                            message = Event(Message.SERVER_CLIENT, '!')
                            message.decode(response)
                            raise IMException(message.get_data())
            # metodo e executado enquanto retornar True
            return self.connected
        except IMException, e:
            self.append_line(e.get_message(), 'red')
            self.show_alert(e.get_message())
            return False
           
    
    def parse_message(self, msg):
        """"""
        cmd = msg.split()
        if len(cmd) > 1:
            if cmd[0] == '/quit':
                msg = ' '.join(cmd[1:])
                self.client.set_quit_msg(msg)                
                self.disconnect()
                return True
            if cmd[0] == '/nick':
                self.client.set_nick_name(cmd[1])
                self.client.send_nick_name()
                return True
            if cmd[0] == '/pvt' and cmd[1] in self.clients.values():
                return True
        return False
    
    def alert(self):
        self.start_alert()
        gobject.timeout_add(1500, self.stop_alert)
        
    
    def start_alert(self):
        """Alerta o usuario sobre envio de novas mensagens"""
        self.statusIcon.set_blinking(1)
        
        
    def stop_alert(self):
        """Para o alerta"""        
        self.statusIcon.set_blinking(0)
        
        
    def disconnect(self):
        """Desconecta do servidor"""
        try:
            if self.connected:
                self.connected = False                            
                self.clients.clear()
                self.set_treeview()
                gobject.source_remove(self.thread_id)                
                self.client.disconnect(self.client.get_quit_msg())                                                
                self.toggle_connect_button(False)
                # imprime mensagem no chat
                self.client_signout(self.client.get_nick_name(), self.client.get_quit_msg())
                # fecha os pvts abertos
                for k in pvts.keys():
                    pvts.pop(k).on_window_destroy(None)
        except IMException, e:
            self.show_alert(e.get_message())        
        
    def toggle_connect_button(self, connected):
        """
            Alterna os botoes 'Conectar' e 'Desconectar' em habilitado ou nao. Alterna
            tambem o botao 'Enviar' para que o usuario possa enviar as mensagens.
        """
        try:
            self.btn_connect.set_sensitive(not connected)
            self.btn_settings.set_sensitive(not connected)
            self.btn_disconnect.set_sensitive(connected)            
            self.btn_send.set_sensitive(connected)
        except IMException, e:
            self.show_alert(e.get_message())
        
        
    def on_btn_connect_clicked(self, widget):
        """
            Metodo chamado quando o botao 'Conecta' e pressionado,
            conectando entao no servidor do chat.
        """
        try:
            # caso a janela de preferencias esteja aberta, fecha
            if self.settings.window != None:
               self.settings.on_window_destroy(None)
            if not self.connected:
                # atualiza cliente
                self.client.set_client()
                # conecta o socket
                self.client.connect()
                self.connected = True
                self.has_confirm = False
                # envia o nickname para receber confirmacao de conexao
                self.client.send_nick_name()                
                # limpa o chat
                self.clear()
                # chama thread para checar novas mensages, e guarda o id da thread
                self.thread_id = gobject.io_add_watch(self.client.get_socket(), gobject.IO_IN, self.check_messages)
            self.toggle_connect_button(True)
        except IMException, e:
            self.disconnect()
            self.append_line(e.get_message(), 'red')
            self.show_alert(e.get_message())
            
            
    def on_btn_disconnect_clicked(self, widget):
        """
            Metodo chamado quando o botao 'Desconectar' e pressionado,
            desconectando do servidor do chat.
            
            obs: Exibe uma janela de confirmacao de saida.
        """
        if self.show_confirm('Deseja realmente desconectar?') == gtk.RESPONSE_YES:
            self.disconnect()
            
    
    def on_btn_settings_clicked(self, widget):
        """
            Metodo chamado quando o botao 'Preferencias' e pressionado,
            abrindo uma nova janela.
        """
        if self.settings.window == None:
            self.settings.show()
            
            
    def on_btn_send_clicked(self, widget):
        """
            Metodo chamado quando o botao 'Enviar' e pressionado,
            enviando a mensagem contida no campo para o servidor.
        """
        try:
            if self.connected:
                data = self.txt_send.get_text()
                self.txt_send.set_text('')
                if not self.parse_message(data):
                    self.client.send(data)
        except IMException, e:
            self.append_line(e.get_message(), 'red')
            self.show_alert(e.get_message())
                
        
    def open_pvt(self, widget, path, column):
        """Abre janela de conversa privada, e imprima aviso na tela"""
        iter = self.tv_clients_model.get_iter(path)
        nickname = self.tv_clients_model.get_value(iter, 0)
        # se nao for o proprio usuario
        if nickname != self.client.get_nick_name():
            self.append_line('(%s) Iniciada conversa privada com: %s' % (strftime('%H:%M:%S'), nickname), 'orange')
            for k, v in self.clients.items():
                if v == nickname:
                    pvts[k] = PVT(self.client, k, v)
                    return True
        return False
    
    
    def clear(self):
        """Limpa o chat"""
        self.buffer.set_text('')
      
            
    def append_line(self, msg, color):
        """Adiciona uma nova linha na janela de conversa"""
        tag = self.buffer.create_tag()
        tag.set_property("foreground", color)
        tag.set_property("font", "Courier")
        tag.set_property("size-points", 12)
        tag.set_property("weight", 600)
        self.buffer.insert_with_tags(self.buffer.get_end_iter(), '%s\n' % msg, tag)
        self.txt_chat.scroll_to_mark(self.mark, 0.05, True, 0.0, 1.0)
        self.alert()
    
    
    def client_signout(self, nickname, msg):
        """Adiciona uma nova linha na janela de conversa de saida de cliente"""        
        self.append_line('(%s) %s saiu: %s' % (strftime('%H:%M:%S'), nickname, msg), 'red')
       
    def client_signon(self, nickname):
        """Adiciona uma nova linha na janela de conversa de entrada de cliente"""
        self.append_line('(%s) Entrou: %s' % (strftime('%H:%M:%S'), nickname), 'green')
            
    def client_changed(self, old_nick, new_nick):
        """Adiciona uma nova linha na janela de conversa de mudanca de nickname"""
        self.append_line('(%s) %s  mudou o nickname para: %s' % (strftime('%H:%M:%S'), old_nick, new_nick), 'green')
        
    def client_say(self, nickname, msg):
        """Adiciona uma nova linha na janela de conversa de uma mensagem publica"""
        self.append_line('(%s) %s diz: ' % (strftime('%H:%M:%S'), nickname), 'blue')
        self.append_line('%s' % msg, 'black')
                
    def display_welcome(self, msg):
        """Adiciona na janela de conversa a mensagem de WELCOME do servidor"""
        self.append_line('%s' % msg, 'brown')
                
    def set_client(self, id, nick):
        """Altera/Adiciona um cliente na lista de clientes conectados"""
        self.clients[id] = nick
        self.set_treeview()
        
    def remove_client(self, id):
        """Remove um cliente da lista de clientes conectados"""
        try:
            self.clients.pop(id)
            self.set_treeview()
        except:
            pass        
        
        
    def set_treeview(self):
        """
            Remove todos os nicknames dos clientes na treeview e percorre a lista de
            clientes adicionando-os
        """
        self.tv_clients_model.clear()
        for k, v in self.clients.items():
            self.tv_clients_model.append([v])
        
        
    def gtk_main_quit(self, widget):
        self.client.disconnect()
        gtk.main_quit(0)
        print "Bye"
            
            
class Settings(GUI_Client):
    """
    	Classe de interface responsavel por ler e salvar o arquivo de configuracao
    """

    def __init__(self):
        GUI_Client.__init__(self)
        self.window = None
        
    def show(self):
    	"""Exibe a janela de configuracao"""
    	try:
            self.xml = gtk.glade.XML(self.getGladePath() + 'settings.glade')
            self.xml.signal_autoconnect(self)
            self.window = self.xml.get_widget('settings')
            self.set_inputs()
        except IMException, e:
            self.show_alert(e.get_message())
        
    def set_inputs(self):
    	"""Resgata os valores do arquivo de configuracao e adiciona aos inputs"""
        # atualiza dados
        self.client.set_client()
        # pega campos
        self.nickname = self.xml.get_widget('txt_nick_name')
        self.msg_quit = self.xml.get_widget('txt_msg_quit')
        self.server_host = self.xml.get_widget('txt_server_host')
        self.server_port = self.xml.get_widget('txt_server_port')
        # seta valores
        self.nickname.set_text(self.client.get_nick_name())
        self.msg_quit.set_text(self.client.get_quit_msg())
        self.server_host.set_text(self.client.get_server_host())
        self.server_port.set_text('%s' % self.client.get_server_port())
        
    def on_btn_save_clicked(self, widget):
        """Le os inputs e salva os valores do arquivo de configuracao"""
        try:
            # atualiza valores do cliente (tratando-os)
            self.client.set_nick_name(self.nickname.get_text())
            self.client.set_quit_msg(self.msg_quit.get_text())
            self.client.set_server_host(self.server_host.get_text())
            self.client.set_server_port(self.server_port.get_text())
            # atualiza arquivo de configuracao
            IOConf.INI['server_host'] = self.client.get_server_host()
            IOConf.INI['server_port'] = self.client.get_server_port()
            IOConf.INI['nick_name'] = self.client.get_nick_name()
            IOConf.INI['quit_msg'] = self.client.get_quit_msg()
            IOConf.save_file()
            # fecha janela
            self.on_window_destroy(widget)
        except IMException, e:
            self.show_alert(e.get_message())

class PVT(GUI_Client):
    
    def __init__(self, client, dest_id, dest_nick):
        GUI_Client.__init__(self)
        self.xml = gtk.glade.XML(self.getGladePath() + 'pvt.glade')
        self.xml.signal_autoconnect(self)
        self.window = self.xml.get_widget('pvt')
        # id do cliente destino
        self.dest_id = dest_id
        # nick do cliente destino
        self.dest_nick = dest_nick
        # usuario
        self.client = client
        # define os text views
        self.set_text_views()
        
        
    def set_text_views(self):
        self.send = self.xml.get_widget('txt_send')
        self.sbuffer = self.send.get_buffer()
        self.receive = self.xml.get_widget('txt_receive')
        self.rbuffer = self.receive.get_buffer()
        # mark
        self.mark = self.rbuffer.create_mark("end", self.rbuffer.get_end_iter(), False)        
        self.receive = self.xml.get_widget('txt_receive')        
        self.btn = self.xml.get_widget('btn_send')
        
    
    def on_btn_send_clicked(self, widget):
        msg = self.sbuffer.get_text(self.sbuffer.get_start_iter(), self.sbuffer.get_end_iter())
        if not msg:
            return
        self.clear_send()
        self.client_say(self.client.get_nick_name(), msg, 'brown')
        self.client.send_to(self.dest_id, msg)
    
        
    def clear_send(self):
        self.sbuffer.set_text('')
       
        
    def append_line(self, msg, color):
        """Adiciona uma nova linha na janela de conversa"""       
        tag = self.rbuffer.create_tag()
        tag.set_property("foreground", color)
        tag.set_property("font", "Courier")
        tag.set_property("size-points", 12)
        tag.set_property("weight", 600)        
        self.rbuffer.insert_with_tags(self.rbuffer.get_end_iter(), '%s\n' % msg, tag)
        self.receive.scroll_to_mark(self.mark, 0.05, True, 0.0, 1.0)
    
    
    def client_say(self, nickname, msg, color):
        """Adiciona uma nova linha na janela de conversa de saida de cliente"""
        self.append_line('(%s) %s diz:' % (strftime('%H:%M:%S'), nickname), color)
        self.append_line('%s' % msg, 'black')


    def on_pvt_destroy(self, widget):
        if pvts.has_key(self.dest_id):
            pvts.pop(self.dest_id)
        self.on_window_destroy(widget)
    
    

