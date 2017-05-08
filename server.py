#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, logging
from flask import Flask, request
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from emoji import emojize
from models import User, Group, List, Item, Payment, db

sys.path.append(os.path.join(os.path.abspath('.'), 'venv/lib/site-packages'))
logging.basicConfig(level=logging.DEBUG,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

TOKEN='#'
SITE_URL='#'

global bot, updater
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)
updater = Updater(TOKEN)

def start(bot, update):
    update.message.reply_text(u'Hola!, Soy SlaveBot {}'.format(
        emojize(':grinning_face:', use_aliases=True)))

def create(bot, update):
    _from = update.message.from_user
    chat = update.message.chat

    if 'group' in chat['type']:
        group = Group.where('telegram_chat_id', chat['id']).first()
        if group is None:
            group = Group.create(telegram_chat_id=chat['id'],
                                 title=chat['title'])

        bot.send_message(chat_id=chat['id'],
            text='Hola grupo {}'.format(chat['title']))

        list_active = group.lists().opened().first()

        if list_active is None:
            user = User.where('telegram_chat_id', _from['id']).first()

            if user is None:
                user = User.create(name=_from['first_name'],
                                   username=_from['username'],
                                   telegram_chat_id=_from['id'])
                update.message.reply_text('Hola esclavo {}, mucho gusto.'.format(user.name))
            else:
                update.message.reply_text('Hola esclavo {}'.format(user.name))

            group.lists().save(List(user_id=user.id))
            bot.send_message(chat_id=chat['id'], text='Lista creada')
        else:
            bot.send_message(chat_id=chat['id'], text='Ya hay una lista abierta')

        send_items(bot, chat['id'])
    else:
        bot.send_message(chat_id=chat['id'],
            text='Lo siento, el Bot solo esta disponible para grupos')

def add(bot, update):
    query = update.callback_query
    data = query.data.split()
    chat = query.message.chat
    _from = query.from_user

    item = Item.find(data[1])
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_active = group.lists().opened().first()

    if list_active is not None:
        user = User.where('telegram_chat_id', _from['id']).first()

        if user is None:
            user = User.create(name=_from['first_name'],
                               username=_from['username'],
                               telegram_chat_id=_from['id'])

        list_active.items().attach(item, {'user_id': user.id})
        message = '{} fue agregado a la lista.'.format(item.name)
    else:
        message = 'No hay una lista abierta'

    query.message.reply_text(message)

def items(bot, update):
    chat = update.message.chat
    send_items(bot, chat['id'])

def send_items(bot, chat_id):
    items = Item.defaults().get()

    keyboard = []
    for i in xrange(0, len(items), 2):
        left = items.get(i)
        right = items.get(i+1)
        keyboard.append([
            InlineKeyboardButton('{} - {}'.format(left.name, left.price_format),
                callback_data='item {}'.format(left.id)),
            InlineKeyboardButton('{} - {}'.format(right.name, right.price_format),
                callback_data='item {}'.format(right.id))
        ])

    bot.send_message(chat_id=chat_id, text='Escoge un producto',
                     reply_markup=InlineKeyboardMarkup(keyboard))

def check_slave(list_active, _from):
    return list_active.slave.telegram_chat_id == _from.id

def close(bot, update):
    chat = update.message.chat
    _from = update.message.from_user
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_active = group.lists().opened().first()

    if list_active is not None:
        if check_slave(list_active, _from):
            list_active.close()
            message = 'Lista cerrada'
        else:
            message = 'Solo el esclavo puede eliminar la lista'
    else:
        message = 'No habia lista abierta'

    bot.send_message(chat_id=chat['id'], text=message)

def _open(bot, update):
    chat = update.message.chat
    _from = update.message.from_user
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_active = group.lists().closed().first()
    is_slave = False

    if list_active is not None:
        is_slave = check_slave(list_active, _from)
        if is_slave:
            list_active.open()
            message = 'Lista de nuevo abierta'
        else:
            message = 'Solo el esclavo puede reabrir la lista'
    else:
        message = 'No habia ninguna lista cerrada'

    bot.send_message(chat_id=chat['id'], text=message)

    if is_slave:
        send_items(bot, chat['id'])

def _list(bot, update):
    chat = update.message.chat
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_active = group.lists().opened().first()

    if list_active is not None:
        user_amounts = db.table('list_x_item')\
            .select(db.raw('sum(items.price) as total, users.name, users.id as user_id'))\
            .join('items', 'list_x_item.item_id', '=', 'items.id')\
            .join('users', 'list_x_item.user_id', '=', 'users.id')\
            .where('list_id', list_active.id)\
            .group_by('list_x_item.user_id')\
            .get()

        if len(user_amounts) > 0:
            message = ""
            all_items = list_active.items

            for user_amount in user_amounts:
                message += "{} S/{}\n".format(
                    user_amount.name, str(user_amount.total/100))

                user_items = all_items.filter(
                    lambda item: item.pivot.user_id == user_amount.user_id)
                for item in user_items:
                    message += "> {} {}\n".format(item.name, item.price_format)
        else:
            message = "No hay elementos en la lista"
    else:
        message = 'No hay lista abierta'

    bot.send_message(chat_id=chat['id'], text=message)

def paylist(bot, update):
    chat = update.message.chat
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_active = group.lists().opened().first()

    if list_active is not None:
        message = ''
        user_amounts = db.table('list_x_item')\
            .select(db.raw('sum(items.price) as total, users.name, users.id as user_id'))\
            .join('items', 'list_x_item.item_id', '=', 'items.id')\
            .join('users', 'list_x_item.user_id', '=', 'users.id')\
            .where('list_id', list_active.id)\
            .group_by('list_x_item.user_id')\
            .get()

        keyboard = []
        for user_amount in user_amounts:
            payment = Payment.where('list_id', list_active.id)\
                             .where('user_id', user_amount.user_id)\
                             .first()

            # To - Do
            # Print grin emoji when exists
            # And angry when not exists

            keyboard.append([
                InlineKeyboardButton(u'{} - S/{}'.format(
                    user_amount.name, str(user_amount.total/100)),
                    callback_data='pay {} {}'.format(
                        user_amount.user_id, list_active.id)
                )
            ])

        bot.send_message(chat_id=chat['id'], text='Lista de pagos',
                     reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        message = 'No hay lista abierta'
        bot.send_message(chat_id=chat['id'], text=message)

def pay(bot, update):
    query = update.callback_query
    data = query.data.split()
    print(data)
    chat = query.message.chat
    _from = query.from_user
    group = Group.where('telegram_chat_id', chat['id']).first()
    list_closed = group.lists().closed().first()
    user_id = data[1]
    list_id = data[2]

    if list_closed is not None:
        if check_slave(list_closed, _from):
            payment = Payment.where('list_id', list_id)\
                             .where('user_id', user_id)\
                             .first()
            user = User.find(user_id)

            if payment is None:
                Payment.create(user_id=user_id, list_id=list_id)
                message = '{} ha pagado.'.format(user.name)
            else:
                message = '{} ya pago anteriormente.'.format(user.name)
        else:
            message = 'Solo el esclavo puede decir si alguien pago su deuda'
    else:
        message = 'La lista debe estar cerrada para realizar los pagos'

    bot.send_message(chat_id=chat['id'], text=message)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('create', create))
updater.dispatcher.add_handler(CommandHandler('items', items))
updater.dispatcher.add_handler(CommandHandler('close', close))
updater.dispatcher.add_handler(CommandHandler('open', _open))
updater.dispatcher.add_handler(CommandHandler('list', _list))
updater.dispatcher.add_handler(CommandHandler('paylist', paylist))
updater.dispatcher.add_handler(CallbackQueryHandler(add, pattern='item [0-9]+'))
updater.dispatcher.add_handler(CallbackQueryHandler(pay, pattern='pay [0-9]+ [0-9]+'))

@app.route('/HOOK', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        updater.dispatcher.process_update(update)
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(SITE_URL + '/HOOK')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    app.run(debug=True)
