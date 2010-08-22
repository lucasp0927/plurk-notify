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
                                   'api_key': api_key,
                                   'no_data': '1'}))
    #print json.load(login_data)
    #login_data = json.load(login_data_json)

    #print time.strftime(ISOTIMEFORMAT,time.gmtime(time.time()))
    recent_plurks = opener.open(get_api_url('/Polling/getPlurks'),
                         encode({'api_key': api_key,
                                 'offset': offset,
                                 'limit' : 20}))

    offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    print 'offset =',
    print offset

    plurks = json.load(recent_plurks)
    print plurks
    print len(plurks['plurks'])

    friends = {}
    for uid in plurks['plurk_users']:
        friends[uid] = plurks['plurk_users'][uid]['nick_name']
    print friends

    for p in plurks['plurks']:
        n = pynotify.Notification (str(friends[p['owner_id']]) + ' ' + str(p['qualifier_translated']),str(p['content']))
        n.show()
    print 'finish a cycle'
    time.sleep(180)

