#! /usr/bin/env python
#--- Setup ----------------------------------------------
import urllib, urllib2, cookielib
import time
import pynotify
from datetime import datetime
import json

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode

file_line = open("password.dat","r").readlines()
username = file_line[0].strip()
password = file_line[1].strip()

pynotify.init("plurk")

offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
print username
print password
print 'offset =',
print offset
while(True):

    login_data_json = opener.open('https://www.plurk.com/API/Users/login',
                           encode({'username': username,
                                   'password': password,
                                   'api_key': api_key}))
    #print json.load(login_data)
    login_data = json.load(login_data_json)
    friends = {}
    for uid in login_data['plurks_users']:
        friends[uid] = login_data['plurks_users'][uid]['nick_name']
    print friends
    #print time.strftime(ISOTIMEFORMAT,time.gmtime(time.time()))
    fp2 = opener.open(get_api_url('/Polling/getPlurks'),
                     encode({'api_key': api_key,
                             'offset': offset,
                             'limit' : 5}))
    offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    print 'offset =',
    print offset
    plurk = json.load(fp2)
    print plurk
    print len(plurk['plurks'])
    for p in plurk['plurks']:
        n = pynotify.Notification (friends[p['user_id']] + ' ' + p['qualifier_translated'],str(p['content']))
        n.show()
    print 'finish a cycle'
    time.sleep(180)

