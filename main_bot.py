#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters
from src import sqlite_handler as sh
from src import timedel_repr as tdr
import subprocess
import textwrap
import telegram
import datetime
import logging
import random
import json
import os

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

lamp_state = 0


RES_DIR = 'res'
spath = os.path.dirname(os.path.realpath(__file__))
db = sh.database(os.path.join(spath, RES_DIR, 'data.db'))

listening_for_record = False
listening_for_list = False

RELAY_PIN = 26
GPIO.setup(RELAY_PIN, GPIO.OUT)

PHRASES = ['Чем ты занят?', 'Опять видосы смотришь?', 'Про физику не забыл?']


def get_token():
    path = os.path.join(spath, 'res', 'token.json')
    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def stop(bot, update):
    GPIO.cleanup()
    p = subprocess.Popen([os.path.join(spath, './telegramd'), 'stop'],
                         stdout=subprocess.PIPE)


def restart(bot, update):
    update.message.reply_text('will be back soon...')
    p = subprocess.Popen([os.path.join(spath, './telegramd'), 'restart'],
                         stdout=subprocess.PIPE)


def alarm(bot, job):
    """Function to send the alarm message"""
    bot.sendMessage(job.context, text='Beep!')


def add_msg_record(chat_id, msg_text):
    now = datetime.datetime.utcnow()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day_time = now.strftime("%d%H%M%S")

    path = os.path.join(spath, RES_DIR, 'user_data', chat_id,
                        year, month, day_time)
    if os.path.exists(path):
        # TODO: make nicer
        assert(1 == 0)
    else:
        os.makedirs(path)

    msg_path = os.path.join(path, 'msg.txt')

    epoch = datetime.datetime.utcfromtimestamp(0)
    cur_secs = int((datetime.datetime.utcnow() - epoch).total_seconds())

    values = [chat_id, cur_secs, msg_path]
    db.insert('users', values)

    with open(msg_path, 'w') as f:
        f.write(msg_text)

    return path


def echo(bot, update):
    global listening_for_record

    chat_id = str(update.message.chat.id)
    msg_text = update.message.text.encode('utf-8')

    if listening_for_record:
        path = add_msg_record(chat_id, msg_text)
        listening_for_record = False
        update.message.reply_text('Записал ✅\nПуть к файлу: {}'.format(path))
    else:
        update.message.reply_text('echo: {}'.format(msg_text))


# def add_task_record():
#     now = datetime.datetime.utcnow()
#     year = now.strftime("%Y")
#     month = now.strftime("%m")
#     day_time = now.strftime("%d%H%M%S")
#
#     path = os.path.join(spath, RES_DIR, 'user_data', chat_id,
#                         year, month, day_time)
#     if os.path.exists(path):
#         # TODO: make nicer
#         assert(1 == 0)
#     else:
#         os.makedirs(path)
#
#     msg_path = os.path.join(path, 'msg.txt')
#
#     cur_secs = int(now.strftime("%s"))
#     values = [chat_id, cur_secs, msg_path]
#     db.insert('users', values)
#
#     with open(msg_path, 'w') as f:
#         f.write(msg_text)
#
#     return path


def add_act_record(bot, update, args):
    epoch = datetime.datetime.utcfromtimestamp(0)
    cur_secs = int((datetime.datetime.utcnow() - epoch).total_seconds())

    chat_id = str(update.message.chat.id)
    activity = (' '.join(args)).lower().encode('utf-8')

    values = [chat_id, cur_secs, activity]
    db.insert('acts', values)
    update.message.reply_text('Ok')


def get_time():
    epoch = datetime.datetime.utcfromtimestamp(0)
    cur_secs = int((datetime.datetime.utcnow() - epoch).total_seconds())
    return datetime.datetime.utcfromtimestamp(cur_secs).strftime('%y-%b-%d, \
                                                                  %a, %H:%M')


def show_activities(bot, update):
    cursor = db.select_all('acts')

    text = []
    dict_to_print = {}
    epoch = datetime.datetime.utcfromtimestamp(0)

    for i in cursor:
        # to determine the midnight of the date
        date_stamp = int((datetime.datetime.utcfromtimestamp(i[1]).
                          replace(hour=0, minute=0, second=0, microsecond=0) -
                          epoch).total_seconds())

        activity = i[2]
        activity = '. '.join([s.strip().capitalize()
                             for s in activity.split('.')])

        # old
        # date_str = datetime.datetime.utcfromtimestamp(i[1]).
        # strftime('%y-%b-%d, %a, %H:%M') + ' - ' + activity

        date_str = "{} - {}".format(tdr.timedel_repr(datetime.datetime.
                                    utcnow() - datetime.datetime.
                                    utcfromtimestamp(i[1])),
                                    activity.encode('utf-8'))

        if date_stamp in dict_to_print:
            dict_to_print[date_stamp].append(date_str)
        else:
            dict_to_print[date_stamp] = [date_str]

    for i in sorted(list(dict_to_print.keys())):
        for j in dict_to_print[i]:
            text.append(j)
        text.append('                    -----|=======>')

    text = text[:-1]
    text.append('                    ~~~~~~~~~~~~')
    text.append(get_time() + ' - ' + 'now')
    text = '\n'.join(text)
    update.message.reply_text(text)


def todo(bot, update, args):
    global listening_for_list
    msg_text = (' '.join(args)).encode('utf-8')
    listening_for_list = True
    update.message.reply_text('"{}"'.format(msg_text) +
                              '\nВ какой список добавить? 🤔')


def show_db(bot, update):
    cursor = db.select_all('users')
    text = '\n'.join(map(str, cursor))
    update.message.reply_text(text)


def ask(bot, update):
    update.message.reply_text(PHRASES[random.randint(0, len(PHRASES)-1)])


def sigrecord(bot, update):
    global listening_for_record
    listening_for_record = True
    update.message.reply_text('Хорошо, я слушаю 👂🏼')


def temp(bot, update):
    p = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    update.message.reply_text(output)


def get_ip(bot, update):
    public_ip = subprocess.check_output(['curl', '-s', 'ipinfo.io/ip'])
    update.message.reply_text(public_ip)


def lamp_switch(bot, update):
    global lamp_state

    lamp_state = 1 - lamp_state
    GPIO.output(RELAY_PIN, lamp_state)
    print('Im here')
    if lamp_state == 1:
        update.message.reply_text('Лампа включена')
    else:
        update.message.reply_text('Лампа выключена')


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


def show_commands(bot, update):
    cmds = """\
    Command List:
    ------------
    start - to show start-info
    restart - to restart the Bot
    stop - GPIO.cleanup()
    help - to show help
    ask - to request for question from Finn
    r - to record your next message
    scmd - to show Command List
    show - select * from data.db;
    temp - to show temperature of raspberry
    ip - show public ip of router
    switch - to switch on/off my lamp
    set/unset <n> - set alarm for <n> seconds\
    """
    update.message.reply_text(textwrap.dedent(cmds))


def main():
    updater = Updater(get_token())

    bot = telegram.Bot(token=get_token())
    bot.sendMessage(chat_id=107183599, text='Я вернулся 🙂')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", show_commands))
    dp.add_handler(CommandHandler("scmd", show_commands))
    dp.add_handler(CommandHandler("help", show_commands))
    dp.add_handler(CommandHandler("restart", restart))
    dp.add_handler(CommandHandler("stop", stop))

    dp.add_handler(CommandHandler("todo", todo, pass_args=True))

    dp.add_handler(CommandHandler("add", add_act_record, pass_args=True))
    dp.add_handler(CommandHandler("s_acts", show_activities))

    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(CommandHandler("r", sigrecord))
    dp.add_handler(CommandHandler("show", show_db))
    dp.add_handler(CommandHandler("temp", temp))
    dp.add_handler(CommandHandler("ip", get_ip))

    dp.add_handler(CommandHandler("switch", lamp_switch))

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
