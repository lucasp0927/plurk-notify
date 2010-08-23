#! /usr/bin/env python
#--- Setup ----------------------------------------------
import urllib, urllib2, cookielib
import pynotify
from datetime import datetime
import json, os, time

api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
username_and_password = 'password.dat'


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
                         encode({'username': self.username,
                                 'password': self.password,
                                 'api_key':  self.api_key,
                                 'no_data':  '1'}))

    def get_recent_plurks(self):
        plurks = self.opener.open(self.get_api_url('/Polling/getPlurks'),
                           encode({'api_key': self.api_key,
                                   'offset':  self.offset,
                                   'limit' :  20})))
        return json.load(plurks)

    def set_offset(self):
        self.offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def get_avater(self, uid, plurk_user):
        if plurk_user['has_profile_image'] == 1:
            if plurk_user['avatar'] == None:
                return 'http://avatars.plurk.com/%d-small.gif' % uid
            else:
                return 'http://avatars.plurk.com/%d-small%s.gif' % plurk_user['avatar']
        else:
            return 'http://www.plurk.com/static/default_small.gif'

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
            self.friend_pic[uid] = self.get_avater(uid, plurk_data['plurk_users'][uid])

    def notify_header(self, plurk):
        return "%s %s" % (self.friend_name[str(plurk['owner_id'])],
                          self.get_qualifier(plurk))

    def notify_plurks(self, plurk_data):
        for p in plurk_data['plurks']:
            pynotify.Notification(notify_header(p),
                                  str(p['content']),
                                  self.friend_pic[str(p['owner_id'])]).show()

    def run(self):
        self.login()
        plurks = self.get_recent_plurks()
        self.parse_plurk_data(plurks)
        self.notify_plurks(plurks)
        self.set_offset()
        time.sleep(60)

if __name__ == "__main__":
    p = PlurkNotify()
    p.run()

