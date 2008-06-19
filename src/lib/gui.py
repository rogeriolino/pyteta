# -*- coding: UTF-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject

import os
import sys


class GUI:
    """
        Classe mae
    """    
    
    def __init__(self):
        self.sep = os.path.sep
    
    def getDir(self):
        va = sys.argv[0]
        if va[0] == self.sep:
            return os.path.dirname(va)
        else:
            return os.path.dirname(os.getcwd() + self.sep + va)
        
    
    def getGladePath(self):
        return self.getDir() + self.sep + 'glade' + self.sep
    
    def getImagesPath(self):
        return self.getDir() + self.sep + 'imgs' + self.sep
            
    
    def on_window_destroy(self, widget):
        """"""
        if self.window != None:
            self.window.destroy()
            self.window = None
        
        
    def show_dialog(self, type, buttons, msg):
        """Exibe uma janela do tipo Dialog"""
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, type, buttons, msg)        
        dialog.set_title(self.title)
        #dialog.set_icon_from_file(self.icon)
        dialog.width, dialog.height = dialog.get_size()
        dialog.move(gtk.gdk.screen_width()/2-dialog.width/2, gtk.gdk.screen_height()/2-dialog.height/2)
        op = dialog.run()
        dialog.destroy()
        return op
            
            
    def show_alert(self, msg):
        """Exibe janela do tipo Alert"""
        return self.show_dialog(gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
            
            
    def show_confirm(self, msg):
        """Exibe janela do tipo confirmacao (Cancel, OK) e retorna o valor escolhido"""
        return self.show_dialog(gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
            
            
    
        
        