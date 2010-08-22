#! /usr/bin/env python
#--- Setup ----------------------------------------------
import urllib, urllib2, cookielib
import time
import pynotify
from datetime import datetime
import json
import os

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
fileurl = "file://" + os.path.abspath(os.path.curdir)+"/temp.png"
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
        if 'display_name' in plurks['plurk_users'][uid]:
            friends[uid] = {}
            friends[uid]['name'] = plurks['plurk_users'][uid]['display_name']
            if plurks['plurk_users'][uid]['has_profile_image'] == 1 and plurks['plurk_users'][uid]['avatar'] == None:
                friends[uid]['url'] = 'http://avatars.plurk.com/'+str(uid)+'-small.gif'
            elif plurks['plurk_users'][uid]['has_profile_image'] == 1 and plurks['plurk_users'][uid]['avatar'] != None:
                friends[uid]['url'] = 'http://avatars.plurk.com/'+str(uid)+'-small'+str(plurks['plurk_users'][uid]['avatar'])+'.gif'
            else:
                friends[uid]['url'] = 'http://www.plurk.com/static/default_small.gif'
        else:
            friends[uid] = {}
            friends[uid]['name'] = plurks['plurk_users'][uid]['nick_name']
            if plurks['plurk_users'][uid]['has_profile_image'] == 1 and plurks['plurk_users'][uid]['avatar'] == None:
                friends[uid]['url'] = 'http://avatars.plurk.com/'+str(uid)+'-small.gif'
            elif plurks['plurk_users'][uid]['has_profile_image'] == 1 and plurks['plurk_users'][uid]['avatar'] != None:
                friends[uid]['url'] = 'http://avatars.plurk.com/'+str(uid)+'-small'+str(plurks['plurk_users'][uid]['avatar'])+'.gif'
            else:
                friends[uid]['url'] = 'http://www.plurk.com/static/default_small.gif'
    print friends

    for p in plurks['plurks']:
#        urllib.urlretrieve(friends[str(p['owner_id'])]['url'], fileurl)
        if 'qualifier_translated' in p:
            n = pynotify.Notification (friends[str(p['owner_id'])]['name'] + ' ' + p['qualifier_translated'],str(p['content']),fileurl)
        else:
            n = pynotify.Notification (friends[str(p['owner_id'])]['name'] + ' ' + p['qualifier'],str(p['content']),fileurl)
        n.show()
    print 'finish a cycle'
    time.sleep(60)

