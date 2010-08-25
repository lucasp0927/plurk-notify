import urllib, urllib2, cookielib
from datetime import datetime
import pynotify
import json, os, time, sys

api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
username_and_password = 'password.dat'

class Plurk:
    def __init__(self):
        self.currentpath=self.get_current_path()
        self.login_state = False
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

    def get_current_path(self):
        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+'/'
        return pathname

    def load_login_data(self):
        file_line = open(self.currentpath+username_and_password,"r").readlines()
        self.username = file_line[0].strip()
        self.password = file_line[1].strip()

    def login(self):
        print 'start login...'
        result=self.opener.open(self.get_api_url('/Users/login'),
                                self.encode({'username': self.username,
                                             'password': self.password,
                                             'api_key':  self.api_key,
                                             'no_data':  '1'}))


        if json.load(result)['success_text'] == 'ok':
            print 'login success'
            return True
        else:
            print 'login failed'
            return False

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
        if not(os.path.exists(self.currentpath+'avatar')):
            os.mkdir(self.currentpath+'avatar')
        fileurl = self.currentpath+'avatar/'+str(uid)+'-'+str(avatar_version)+'.gif'
        if not(os.path.isfile(fileurl)):
            urllib.urlretrieve(url, fileurl )
        return fileurl

    def get_avatar(self, uid, plurk_user):
        if plurk_user['has_profile_image'] == 1:
            if plurk_user['avatar'] == 0: #0 or None?
                return self.download_avatar('http://avatars.plurk.com/%s-medium.gif' % uid, uid, 'none')
            else:
                return self.download_avatar('http://avatars.plurk.com/%s-medium%s.gif' % (uid, plurk_user['avatar']), uid, plurk_user['avatar'])
        else:
            return self.download_avatar('http://www.plurk.com/static/default_medium.gif', 'default', 'medium')

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
        self.login_state = self.login()
        if self.login_state == True:
            self.get_unread_count()
            plurks = self.get_recent_plurks()
            self.parse_plurk_data(plurks)
            self.notify_plurks(plurks)
            self.set_offset()
        else:
            print 'login error'
