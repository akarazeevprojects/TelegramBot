#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to send timed Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters
import datetime
import logging
import json
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PHRASES = ['Чем ты занят?', 'Опять видосы смотришь?', 'Про физику не забыл?']


def get_token():
    path = 'token.json'
    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(bot, job):
    """Function to send the alarm message"""
    bot.sendMessage(job.context, text='Beep!')


def echo(bot, update):
    chat_id = str(update.message.chat.id)
    now = datetime.datetime.utcnow()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day_time = now.strftime("%d%H%M%S")

    path = os.path.join(chat_id, year, month, day_time)
    if os.path.exists(path):
        # TODO: make nicer
        assert(1 == 0)
    else:
        os.makedirs(path)

    with open(os.path.join(path, 'msg.txt'), 'w') as f:
        f.write(update.message.text.encode('utf-8'))

    update.message.reply_text('Your message is stored at {}.\nAnything else?'.format(path))

# def say_smt(bot, job):


# def lets_chat(bot, update, args, job_queue, chat_data):



def set(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = Job(alarm, due, repeat=False, context=chat_id)
        chat_data['job'] = job
        job_queue.put(job)

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(get_token())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
