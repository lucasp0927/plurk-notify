#! /usr/bin/env python
#--- Setup ----------------------------------------------
import pygtk, gtk, glib
pygtk.require('2.0')
import webbrowser
import os, sys, json
from plurk import Plurk
import urllib2

class PlurkTray:

    def __init__(self):
        self.first = 0
        self.notify_on = True
        self.p = Plurk()
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_visible(True)
        self.set_icon('normal')
        self.make_menu()
        self.make_lmenu()
        #self.statusIcon.set_visible(1)
        self.notify()
        gtk.main()

    def set_icon (self, status):
        if status == 'normal':
            if self.p.unReadCount == 0:
                self.statusIcon.set_from_file(os.path.abspath(os.path.dirname(sys.argv[0]))+"/plurk_mono48.png")
            else:
                self.statusIcon.set_from_file(os.path.abspath(os.path.dirname(sys.argv[0]))+"/plurk_red48.png")
        elif status == 'connect_error':
            self.statusIcon.set_from_file(os.path.abspath(os.path.dirname(sys.argv[0]))+"/plurk_error48.png")

    def make_menu(self):
        self.menu = gtk.Menu()
        self.menuItem = gtk.MenuItem(label=self.notify_state(),use_underline=True)
        self.menuItem.connect('activate', self.toggle, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menu.show_all()
#        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.connect('popup-menu', self.on_popup_menu)
        self.statusIcon.set_tooltip("unread plurk: "+str(self.p.unReadCount))

    def make_lmenu(self):
        self.lmenu = gtk.Menu()

#        self.lmenu.add(gtk.SeparatorMenuItem())
        self.menuItem = gtk.MenuItem(label='Unread Plurk: '+str(self.p.unReadCount),use_underline=False)
        self.lmenu.append(self.menuItem)
        self.lmenu.add(gtk.SeparatorMenuItem())

        for pl in self.p.unReadPlurks['plurks']:
            self.menuItem = gtk.MenuItem(label=self.p.notify_header(pl,True)+str(pl['content']),use_underline=False)
            self.menuItem.set_submenu(self.create_response_menu(pl['plurk_id']))
            #self.menuItem = gtk.MenuItem(str(pl['content']),use_underline=False)
            self.lmenu.append(self.menuItem)
            self.lmenu.add(gtk.SeparatorMenuItem())

        self.menuItem = gtk.MenuItem(label='Open Plurk in browser',use_underline=False)
        self.menuItem.connect('activate', self.open_browser)
        self.lmenu.append(self.menuItem)
        self.lmenu.show_all()
#        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        self.statusIcon.connect('activate', self.on_lmenu)

#    def run_cb(self, data = None):
#        self.notify()

    def create_response_menu(self, plurkID):
        #    if depth < 1:
        #	return None
        menu = gtk.Menu()
        group= None
        for r in self.p.responses[plurkID]['responses']:
            menuitem = gtk.MenuItem(label=r['content_raw'])
            menu.append(menuitem)
        menuitem.show()
        return menu


    def toggle(self, widget, event, data = None):
        self.notify_on = not self.notify_on
        self.make_menu()

    def quit_cb(self, widget, data = None):
        gtk.main_quit()

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)

    def on_lmenu(self, *args):
        self.lmenu.popup(None, None, gtk.status_icon_position_menu, 1 , gtk.get_current_event_time(), self.statusIcon)

    def notify(self):
        try:
            if self.first == 0:
                print 'fisst time'
                self.first = 1
                self.p.set_offset()
                if self.notify_on == True:
                    self.p.run()
            else:
                if self.notify_on == True:
                    self.p.run()
            self.make_menu()
            self.make_lmenu()
            self.set_icon('normal')
            glib.timeout_add_seconds(60, self.notify)
            self.p.set_offset()

        except urllib2.URLError:
            print 'connection error'
            self.statusIcon.set_tooltip("connection error!")
            self.set_icon('connect_error')
            glib.timeout_add_seconds(10, self.notify)
#            self.p.buildopener()
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


