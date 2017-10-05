#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess
import telegram
import logging
import json

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

lamp_state = 0
RELAY_PIN = 26
GPIO.setup(RELAY_PIN, GPIO.OUT)


def get_token():
    with open('token.json') as jsn:
        data = json.load(jsn)
    return data['token']


def echo(bot, update):
    msg = 'echo: {}'.format(update.message.text)
    update.message.reply_text(msg)
    logger.info(msg)


def temp(bot, update):
    p = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    update.message.reply_text(output)
    logger.info(output)


def lamp_switch(bot, update):
    global lamp_state

    lamp_state = 1 - lamp_state
    GPIO.output(RELAY_PIN, lamp_state)
    if lamp_state == 1:
        update.message.reply_text('Lamp is on')
        logger.info("Lamp is on")
    else:
        update.message.reply_text('Lamp is off')
        logger.info("Lamp is off")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(get_token())
    bot = telegram.Bot(token=get_token())
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("temp", temp))
    dp.add_handler(CommandHandler("switch", lamp_switch))
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logger.info("Hi!")
    main()
