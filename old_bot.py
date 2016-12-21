#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
import json
from time import sleep
import subprocess
from sys import platform as platform_

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def GetToken():
	path='token.json'
	with open(path) as f:
		data = json.load(f)
	return data['token']

updater = Updater(token=GetToken())

####################################
####################################

def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm bot, please talk to me!")

def kek(bot, update):
	tmp = ' '
	for i in range(5):
		tmp += 'kek\n'
	bot.sendMessage(chat_id=update.message.chat_id, text=tmp)

def echo(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text='echo: ' + update.message.text)

def unknow(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text='gtfo, plz')

def stop(bot, update):
	global updater
	print('= updater.stop() =')
	updater.stop()

def gettabs(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text='uploading...')
	bot.sendDocument(chat_id=update.message.chat_id, document=open('/Users/AntonWetret/Documents/!Ukulele, Guitar and Flute/Around the Fire.pdf','rb'))

def getip(bot, update):
	if platform_ == 'darwin':
		command = ['dig','+short','myip.opendns.com','@resolver1.opendns.com']
		p = subprocess.Popen(command, stdout=subprocess.PIPE)
		text = p.stdout.read()
		text = text.decode('utf-8')
		text = text.rstrip()
		bot.sendMessage(chat_id=update.message.chat_id, text='Public: ' + text)
	else:
		bot.sendMessage(chat_id=update.message.chat_id, text='I dunno')

def caps(bot, update, args):
	text_caps = ' '.join(args).upper()
	bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)

####################################
####################################

def main():
	dp = updater.dispatcher

	dp.addHandler(CommandHandler('start', start))
	dp.addHandler(CommandHandler('stop', stop))
	dp.addHandler(CommandHandler('kek', kek))
	dp.addHandler(CommandHandler('gettabs', gettabs))
	dp.addHandler(CommandHandler('getip', getip))
	dp.addHandler(CommandHandler('caps', caps, pass_args=True))

	dp.addHandler(RegexHandler(r'/.*', unknow))

	dp.addHandler(MessageHandler([Filters.text], echo))

	updater.start_polling()

	bot = telegram.Bot(token=GetToken())
	print(bot.getMe())
	updates = bot.getUpdates()
	print([u.message.text for u in updates])
	chat_id = bot.getUpdates()[-1].message.chat_id
	print(chat_id)

	bot.sendMessage(chat_id=chat_id, text=updates[-1].message.text)
	bot.sendMessage(chat_id=chat_id, text="*bold* _italic_ [link](http://google.com).", parse_mode=telegram.ParseMode.MARKDOWN)
	bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)
	bot.sendPhoto(chat_id=chat_id, photo='https://storage.mds.yandex.net/get-sport/10493/f03a90be063e60babadb018cafe033ad.png')
	bot.sendPhoto(chat_id=chat_id, photo=open('../image_png/cards/01_a.jpg', 'rb'))
	bot.sendVoice(chat_id=chat_id, voice=open('/Users/AntonWetret/Music/The Elder Scrolls Skyrim OST/Complete Score/mus_levelup_03.mp3', 'rb'))

	# custom_keyboard = [[ telegram.KeyboardButton(telegram.Emoji.THUMBS_UP_SIGN),\
	# 	telegram.KeyboardButton(telegram.Emoji.THUMBS_DOWN_SIGN) ]]
	# reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	# bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)
	# sleep(2)
	# reply_markup = telegram.ReplyKeyboardHide()
	# bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)

	# file_id = updates[-1].message.voice.file_id
	# newFile = bot.getFile(file_id)
	# newFile.download('voice.mp3')


if __name__ == '__main__':
	main()
