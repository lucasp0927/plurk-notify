#! /usr/bin/env python
#--- Setup ----------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk, glib
import urllib, urllib2, cookielib
import pynotify
from datetime import datetime
import json, os, time

api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
username_and_password = 'password.dat'

class PlurkTray:

    def __init__(self):
        self.first = 0
        self.notify_on = True
        self.p = PlurkNotify()
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_stock(gtk.STOCK_ABOUT)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip("Plurk Notify")
        self.make_menu()
        self.statusIcon.set_visible(1)
        self.run_cb()
        gtk.main()
    
    def make_menu(self):
        self.menu = gtk.Menu()
#        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        self.menuItem = gtk.MenuItem(label=self.notify_state(),use_underline=True)
        self.menuItem.connect('activate', self.execute_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.menuItem.connect('activate', self.quit_cb, self.statusIcon)
        self.menu.append(self.menuItem)
        self.statusIcon.connect('popup-menu', self.popup_menu_cb, self.menu)
        
    def notify_state(self):
        if self.notify_on == True:
            return "Plurk Notify is on"
        else:
            return "Plurk Notify is off"

    def run_cb(self, data = None):
        self.notify()

    def execute_cb(self, widget, event, data = None):
        self.notify_on = not self.notify_on
        self.make_menu()

    def quit_cb(self, widget, data = None):
        gtk.main_quit()

    def popup_menu_cb(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                #right click
                data.popup(None, None, gtk.status_icon_position_menu,
                           3, time, self.statusIcon)
                # left click
#                data.popup(None, None, gtk.status_icon_position_menu,
#                           1, gtk.get_current_event_time(), self.statusIcon)
                
    def notify(self):
        print 'start notifying'
        if self.first == 1:
            if notify_on == True:
                self.p.run()
        else:
            self.first = 1
        glib.timeout_add_seconds(120, self.notify)
        self.p.set_offset()
#        while True:
#            p.run()

class PlurkNotify:
    def __init__(self):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.api_key = api_key
        self.get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
        self.encode = urllib.urlencode
        self.offset = None
        self.friend_name = {}
        self.friend_pic = {}
        pynotify.init("plurk")
        self.load_login_data()

    def load_login_data(self):
        file_line = open(username_and_password,"r").readlines()
        self.username = file_line[0].strip()
        self.password = file_line[1].strip()

    def login(self):
        self.opener.open(self.get_api_url('/Users/login'),
                         self.encode({'username': self.username,
                                      'password': self.password,
                                      'api_key':  self.api_key,
                                      'no_data':  '1'}))

    def get_recent_plurks(self):
        plurks = self.opener.open(self.get_api_url('/Polling/getPlurks'),
                                  self.encode({'api_key': self.api_key,
                                               'offset':  self.offset,
                                               'limit' :  20}))
        return json.load(plurks)

    def set_offset(self):
        self.offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def download_avatar(self,url,uid, avatar_version):
        if not(os.path.exists(os.path.abspath(os.path.curdir)+'/avatar')):
            os.mkdir(os.path.abspath(os.path.curdir)+'/avatar')
        fileurl = os.path.abspath(os.path.curdir)+'/avatar/'+str(uid)+'-'+str(avatar_version)+'.gif'
        if not(os.path.isfile(fileurl)):
            urllib.urlretrieve(url, fileurl )
        return fileurl

    def get_avatar(self, uid, plurk_user):
        if plurk_user['has_profile_image'] == 1:
            if plurk_user['avatar'] == None:
                #                return 'http://avatars.plurk.com/%s-small.gif' % uid
                return self.download_avatar('http://avatars.plurk.com/%s-small.gif' % uid, uid, 'none')
            else:
                #                return 'http://avatars.plurk.com/%s-small%s.gif' % (uid, plurk_user['avatar'])
                return self.download_avatar('http://avatars.plurk.com/%s-small%s.gif' % (uid, plurk_user['avatar']), uid, plurk_user['avatar'])
        else:
            #            return 'http://www.plurk.com/static/default_small.gif'
            return self.download_avatar('http://www.plurk.com/static/default_small.gif', 'default', 'small')

    def get_name(self, plurk_user):
        if 'display_name' in plurk_user:
            return plurk_user['display_name']
        else:
            return plurk_user['nick_name']

    def get_qualifier(self, plurk):
        if 'qualifier_translated' in plurk:
            return plurk['qualifier_translated']
        else:
            return plurk['qualifier']

    def parse_plurk_data(self, plurk_data):
        for uid in plurk_data['plurk_users']:
            self.friend_name[uid] = self.get_name(plurk_data['plurk_users'][uid])
            self.friend_pic[uid] = self.get_avatar(uid, plurk_data['plurk_users'][uid])

    def notify_header(self, plurk):
        return "%s %s" % (self.friend_name[str(plurk['owner_id'])],
                          self.get_qualifier(plurk))

    def notify_plurks(self, plurk_data):
        for p in plurk_data['plurks']:
            pynotify.Notification(self.notify_header(p),
                                  str(p['content']),
                                  self.friend_pic[str(p['owner_id'])]).show()

    def run(self):
        self.login()
        plurks = self.get_recent_plurks()
        self.parse_plurk_data(plurks)
        self.notify_plurks(plurks)
        self.set_offset()
#        time.sleep(120)

if __name__ == "__main__":
    tray = PlurkTray()
#    tray.notify()

