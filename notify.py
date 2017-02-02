#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import json
import urllib2
import telepot
import time
from plurk_oauth import PlurkAPI
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('apitoken.txt')

plurk = PlurkAPI(parser.get('plurk','appkey'),parser.get('plurk','appsecret'))
plurk.authorize(parser.get('plurk','usertoken'),parser.get('plurk','usersecret'))

try:
	comet = plurk.callAPI('/APP/Realtime/getUserChannel')
except:
	time.sleep(3)
	comet = plurk.callAPI('/APP/Realtime/getUserChannel')
comet_channel = comet.get('comet_server') + "&amp;new_offset=%d"
jsonp_re = re.compile('CometChannel.scriptCallback\((.+)\);\s*');
new_offset = -1

def handle(msg):
	#pprint.pprint(msg)
	content_type, chat_type, chat_id = telepot.glance(msg)
	chat_id = msg['chat']['id']
	message_id = msg['message_id']
	try:
		username = msg['from']['first_name'] +' '+ msg['from']['last_name']
	except:
		username = msg['from']['first_name']
	user_id = msg['from']['id']
owner_id = int(parser.get('bottoken','id'))
bot_apitoken = parser.get('bottoken', 'token')
bot = telepot.Bot(bot_apitoken)
bot.message_loop(handle)
print '監聽中 ...'

while True:
	#plurk.callAPI('/APP/Alerts/addAllAsFriends')
	req = urllib2.urlopen(comet_channel % new_offset, timeout=80)
	rawdata = req.read()
	match = jsonp_re.match(rawdata)
	if match:
		rawdata = match.group(1)
	data = json.loads(rawdata)
	new_offset = data.get('new_offset', -1)
	msgs = data.get('data')
	if not msgs:
		continue
	for msg in msgs:
		if msg.get('type') == 'new_plurk':
			pid = msg.get('plurk_id')
			content = msg.get('content_raw')
			feeling = msg.get('qualifier')
			full_name = plurk.callAPI('/APP/Timeline/getPlurk',
								{'plurk_id': pid})
			name = str(full_name).split("u'full_name': u'")[1].split("',")[0].decode('unicode-escape')
			bot.sendMessage(owner_id,'新訊息！\n'+name.encode('utf-8')+' '+feeling.encode('utf-8')+'：\n'+str(content.encode('utf-8')))
"""
: = :
玩 = plays
愛 = loves
喜歡 = likes
分享 = shares
給 = gives
討厭 = hates
想要 = wants
期待 = wishes
需要 = needs
打算 = wills
希望 = hopes
問 = asks
已經 = hates
曾經 = wants
好奇 = wonders
覺得 = feels
想 = thinks
畫 = draws
正在 = is
說 = says
寫 = writes
偷偷說 = whispers


			if content.find("hello") != -1:
				plurk.callAPI('/APP/Responses/responseAdd',
							  {'plurk_id': pid,
							   'content': 'world',
							   'qualifier': ':' })
			"""
