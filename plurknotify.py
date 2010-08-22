#! /usr/bin/env python
#--- Setup ----------------------------------------------
import urllib, urllib2, cookielib
import time
import pynotify
from datetime import datetime
import simplejson

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
api_key = 'vB8TYzK9lyDFfHvCjSf0RlF9KBYAUTaL'
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
password = ''
encode = urllib.urlencode

username = 'lucasp0927'
#read password
passfile="password.dat"
infile = open(passfile,"r")
password = infile.readline().rstrip()
pynotify.init("plurk")

offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
print 'offset =',
print offset
while(True):
    time.sleep(10)                            
    
    opener.open('https://www.plurk.com/API/Users/login',
                     encode({'username': username,
                             'password': password,
                             'api_key': api_key}))
    fp2 = opener.open(get_api_url('/Polling/getPlurks'),
                     encode({'api_key': api_key,
                             'offset': offset,
                             'limit' : 5}))
    offset = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    print 'offset =',
    print offset
    plurk = simplejson.load(fp2)
    print plurk
    print len(plurk['plurks'])
    for p in plurk['plurks']:
        n = pynotify.Notification ("New plurk from ",str(p['content']))
        n.show()
    print 'finish a cycle'
