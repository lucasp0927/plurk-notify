#! /usr/bin/env python
#--- Setup ----------------------------------------------
import pygtk
import webbrowser
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


class PlurkNotify:
    def __init__(self):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.api_key = api_key
        self.get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
        self.encode = urllib.urlencode
        self.offset = None
        self.unReadCount = 0
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

    def get_unread_plurks(self):
        unreadplurks = self.opener.open(self.get_api_url('/Timeline/getUnreadPlurks'),
                                  self.encode({'api_key': self.api_key,
                                               'offset':  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
                                               }))
        return json.load(unreadplurks)

    def mark_all_as_read(self):
        plurks = self.get_unread_plurks()
        for plurk_id in plurks['plurks']:
            print 'not yet'

    def get_unread_count(self):
        unread = self.opener.open(self.get_api_url('/Polling/getUnreadCount'),
                                  self.encode({'api_key': self.api_key}))
        self.unReadCount = json.load(unread)['all']

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
            if plurk_user['avatar'] == 0: #0 or None?
                return self.download_avatar('http://avatars.plurk.com/%s-small.gif' % uid, uid, 'none')
            else:
                return self.download_avatar('http://avatars.plurk.com/%s-small%s.gif' % (uid, plurk_user['avatar']), uid, plurk_user['avatar'])
        else:
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
        self.get_unread_count()
        plurks = self.get_recent_plurks()
        self.parse_plurk_data(plurks)
        self.notify_plurks(plurks)
        self.set_offset()
#        time.sleep(120)

if __name__ == "__main__":
    tray = PlurkTray()
#    tray.notify()

