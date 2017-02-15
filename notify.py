#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import json
import urllib2
import telepot
import time
import pprint
from plurk_oauth import PlurkAPI
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('apitoken.txt')
plurk = PlurkAPI(parser.get('plurk','appkey'),parser.get('plurk','appsecret'))
plurk.authorize(parser.get('plurk','usertoken'),parser.get('plurk','usersecret'))
try:
	comet = plurk.callAPI('/APP/Realtime/getUserChannel')
except:
	while True:
		comet = plurk.callAPI('/APP/Realtime/getUserChannel')
		if 'channel_name' in comet:
			break
comet_channel = comet.get('comet_server') + "&amp;new_offset=%d"
jsonp_re = re.compile('CometChannel.scriptCallback\((.+)\);\s*');
new_offset = -50

def handle(msg):
	#debug用
	#pprint.pprint(msg)
	content_type, chat_type, chat_id = telepot.glance(msg)
	chat_id = msg['chat']['id']
	message_id = msg['message_id']
	try:
		username = msg['from']['first_name'] +' '+ msg['from']['last_name']
	except:
		username = msg['from']['first_name']
	user_id = msg['from']['id']
owner_id = int(parser.get('telegram','id'))
bot_apitoken = parser.get('telegram', 'token')
bot = telepot.Bot(bot_apitoken)
plurk_url = 'https://www.plurk.com/'
#bot.message_loop(handle)
print '監聽中 ...'

down = urllib2.urlopen('url').read()
f = open('notify_id.txt','w')

for x in down.split('\n'):
	try:
		plurk_user_site = urllib2.urlopen(plurk_url+x).read()
		find_plurk_id = plurk_user_site.split('"user_id": ')[1].split(',')[0]
		f = open('notify_id.txt','a')
		f.write(find_plurk_id+'\n')
		f.close()
	except:
		bot.sendMessage(owner_id,x+'使用者id找不到欸QQ')
while True:
	if time.strftime('%M') == '00':
		down = urllib2.urlopen('url').read()
		f = open('notify_id.txt','w')
		for x in down.split('\n'):
			try:
				plurk_user_site = urllib2.urlopen(plurk_url+x).read()
				find_plurk_id = plurk_user_site.split('"user_id": ')[1].split(',')[0]
				f = open('notify_id.txt','a')
				f.write(find_plurk_id+'\n')
				f.close()
			except:
				bot.sendMessage(owner_id,x+'使用者id找不到欸QQ')
	#plurk.callAPI('/APP/Alerts/addAllAsFriends')
	#if handle.msg()['text'] == '!':
	#	print '!'
	#handle(chat_id)
	try:
		req = urllib2.urlopen(comet_channel % new_offset, timeout=80)
	except:
		while True:
			req = urllib2.urlopen(comet_channel % new_offset, timeout=80)
			if '<addinfourl at' in req:
				break
	try:
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
				f = open('notify_id.txt','r').read()
				if str(msg.get('owner_id')) in f:
					pid = msg.get('plurk_id')
					content = msg.get('content_raw')
					feeling = msg.get('qualifier')
					plurk_userid = msg.get('user_id')
					plurk_name = plurk.callAPI('/APP/Timeline/getPlurk',{'plurk_id': pid})['plurk_users'][str(plurk_userid)]['display_name']
					emotion = {
						':' : ':',
						'plays' : '玩',
						'loves' : '愛',
						'likes' : '喜歡',
						'shares' : '分享',
						'gives' : '給',
						'hates' : '討厭',
						'wants' : '想要',
						'wishes' : '期待',
						'needs' : '需要',
						'will' : '打算',
						'hopes' : '希望',
						'asks' : '問',
						'hates' : '已經',
						'wants' : '曾經',
						'wonders' : '好奇',
						'feels' : '覺得',
						'thinks' : '想',
						'draws' : '畫',
						'is' : '正在',
						'says' : '說',
						'writes' : '寫',
						'whispers' : '偷偷說',
						'freestyle' : ':'
					}

					bot.sendMessage(owner_id,'新訊息！\n'+plurk_name.encode('utf-8')+' '+emotion[feeling]+'\n'+str(content.encode('utf-8')))
					print 'new!'
	except Exception as e:
		with open('raise.txt','w') as f:
			f.write(str(e))
		bot.sendMessage(205721848,'噴錯了\n'+str(e))
"""
			if content.find("hello") != -1:
				plurk.callAPI('/APP/Responses/responseAdd',
							  {'plurk_id': pid,
							   'content': 'world',
							   'qualifier': ':' })
			"""
