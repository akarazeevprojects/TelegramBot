from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess
import telegram
import json
import RPi.GPIO as GPIO
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

gpio_mapping = {
    'Fan': 12,
    'Right lamp': 16,
    'Left lamp': 20
}

# {gpio: state}.
relays = {
    12: 0,
    16: 0,
    20: 0
}


def get_token():
    with open('token.json') as jsn:
        data = json.load(jsn)
    return data['token']


def echo(bot, update):
    msg = 'echo: {}'.format(update.message.text)
    update.message.reply_text(msg)


def temp(bot, update):
    p = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    update.message.reply_text(output)


def switch_relay(relay):
    global relays

    relays[relay] = 1 - relays[relay]
    GPIO.output(relay, relays[relay])
    return relays[relay]


def switcher(bot, update, title):
    state = switch_relay(gpio_mapping[title])

    if state == 1:
        update.message.reply_text('{} is on'.format(title))
    else:
        update.message.reply_text('{} is off'.format(title))


def switch_left_lamp(bot, update):
    switcher(bot, update, 'Left lamp')


def switch_right_lamp(bot, update):
    switcher(bot, update, 'Right lamp')


def switch_fan(bot, update):
    switcher(bot, update, 'Fan')


def main():
    # Setup GPIO.OUT.
    for key in relays:
        GPIO.setup(key, GPIO.OUT)

    token = get_token()
    req = telegram.utils.request.Request(proxy_url='socks5h://127.0.0.1:9050',
                                         read_timeout=30, connect_timeout=20,
                                         con_pool_size=10)
    bot = telegram.Bot(token=token, request=req)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("temp", temp))
    dp.add_handler(CommandHandler("switch_left_lamp", switch_left_lamp))
    dp.add_handler(CommandHandler("switch_right_lamp", switch_right_lamp))
    dp.add_handler(CommandHandler("switch_fan", switch_fan))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Hi!")
    main()
