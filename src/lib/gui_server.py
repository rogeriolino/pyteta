# -*- coding: UTF-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject

import thread

from chat import *
from message import *
from server import Server
from gui import GUI


class GUI_Server(GUI):

    
    def __init__(self):
        GUI.__init__(self)
        # titulo das janelas
        self.title = 'PyTETA'
        self.window = None
        self.connected = False
        self.server = Server()
        

    def start(self):
        """Exibe a janela do server"""
        try:           
            self.xml = gtk.glade.XML('%s/glade/server.glade' % self.getDir())
            self.xml.signal_autoconnect(self)
            self.window = self.xml.get_widget('server')            
            self.set_buttons()
            self.set_inputs()
        except IMException, e:
            self.show_alert(e.get_message())
            
    
    def set_buttons(self):
        self.btn_run = self.xml.get_widget('btn_run')
        self.btn_stop = self.xml.get_widget('btn_stop')
        self.toggle_connect_button(self.connected)
            
            
    def set_inputs(self):
        # atualiza dados
        self.server.set_server()
        self.txt_port = self.xml.get_widget('txt_port')        
        self.txt_max_conn = self.xml.get_widget('txt_max_conn')
        self.txt_port.set_text('%s' % self.server.get_server_port())
        self.txt_max_conn.set_text('%s' % self.server.get_max_conn())
        
            
    def toggle_connect_button(self, connected):
        """
            Alterna os botoes 'Conectar' e 'Desconectar' em habilitado ou nao. Alterna
            tambem o botao 'Enviar' para que o usuario possa enviar as mensagens.
        """
        try:
            self.btn_run.set_sensitive(not connected)
            self.btn_stop.set_sensitive(connected)
        except IMException, e:
            self.show_alert(e.get_message())
            
            
    def on_btn_run_clicked(self, widget):
        """"""
        try:
            self.server_run()
            self.connected = True
            self.toggle_connect_button(self.connected)
        except IMException, e:
            self.show_alert(e.get_message())
        
        
    def on_btn_stop_clicked(self, widget):
        """"""
        try:
            self.server.running = False
            self.connected = False
            self.toggle_connect_button(self.connected)
        except IMException, e:
            self.show_alert(e.get_message())
        
        
    def on_btn_save_clicked(self, widget):
        """"""
        try:
             # atualiza valores do cliente (tratando-os)
            self.server.set_server_port(self.txt_port.get_text())
            self.server.set_max_conn(self.txt_max_conn.get_text())        
            # atualiza arquivo de configuracao
            IOConf.INI['server_port'] = self.server.get_server_port()
            IOConf.INI['max_conn'] = self.server.get_max_conn()                
            IOConf.save_file()
            self.show_alert('Dados salvos com sucesso.')
        except IMException, e:
            self.show_alert(e.get_message())
        
        
    def server_run(self):
        """"""       
        gtk.gdk.threads_leave()
        thread.start_new_thread(self.server.run, ())        
        gtk.gdk.threads_init()
        
      
    def gtk_main_quit(self, widget):
        gtk.main_quit(0)
        print "Bye"
        
          