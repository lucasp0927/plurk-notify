#! /usr/bin/env python
#--- Setup ----------------------------------------------
import pygtk, gtk, glib
pygtk.require('2.0')
import pynotify
import webbrowser
import urllib, urllib2, cookielib
from datetime import datetime
import json, os, time
from plurk import Plurk

api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
username_and_password = 'password.dat'

class PlurkTray:

    def __init__(self):
        self.first = 0
        self.notify_on = True
        self.p = Plurk()
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_file(os.path.abspath(os.path.curdir)+"/plurk_mono48.png")
        self.statusIcon.set_visible(True)
#        self.statusIcon.connect('activate', self.open_browser)
        self.make_menu()
        self.make_lmenu()
        #self.statusIcon.set_visible(1)
        self.notify()
        gtk.main()
    
    def make_menu(self):
        self.menu = gtk.Menu()
#        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem = gtk.MenuItem(label='Unread Plurk: '+str(self.p.unReadCount),use_underline=False)
        self.menu.append(self.menuItem)
        self.menu.add(gtk.SeparatorMenuItem())
        self.menuItem = gtk.MenuItem(label=self.notify_state(),use_underline=True)
        self.menuItem.connect('activate', self.execute_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menu.show_all()
#        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.connect('popup-menu', self.on_popup_menu)

    def make_lmenu(self):
        self.lmenu = gtk.Menu()
#        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem = gtk.MenuItem(label='Open Plurk in browser',use_underline=False)
        self.menuItem.connect('activate', self.open_browser)
        self.lmenu.append(self.menuItem)
        self.lmenu.show_all()
#        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.connect('activate', self.on_lmenu)

#    def run_cb(self, data = None):
#        self.notify()

    def execute_cb(self, widget, event, data = None):
        self.notify_on = not self.notify_on
        self.make_menu()

    def quit_cb(self, widget, data = None):
        gtk.main_quit()

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)

    def on_lmenu(self, *args):
        self.lmenu.popup(None, None, gtk.status_icon_position_menu, 1 , gtk.get_current_event_time(), self.statusIcon)

    def notify(self):
        if self.first == 0:
            self.first = 1
            self.p.set_offset()
            if self.notify_on == True:
                self.p.run()
        else:
            if self.notify_on == True:
                self.p.run()

        self.make_menu()
        self.statusIcon.set_tooltip("unread plurk: "+str(self.p.unReadCount))

        glib.timeout_add_seconds(120, self.notify)
        self.p.set_offset()

    def notify_state(self):
        if self.notify_on == True:
            return "Plurk Notify is on"
        else:
            return "Plurk Notify is off"
        
    def open_browser(self,event):
        webbrowser.open("http://www.plurk.com")

if __name__ == "__main__":
    tray = PlurkTray()
#    tray.notify()

