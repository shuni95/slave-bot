#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize
from models import User, Group, List, Item

logging.basicConfig(level=logging.DEBUG,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

TOKEN='#'
SITE_URL='#'

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
    user = User.where('telegram_chat_id', _from['id']).first()

    list_active = group.lists().opened().first()

    if list_active is not None:
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

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('create', create))
updater.dispatcher.add_handler(CommandHandler('items', items))
updater.dispatcher.add_handler(CommandHandler('close', close))
updater.dispatcher.add_handler(CommandHandler('open', _open))
updater.dispatcher.add_handler(CallbackQueryHandler(add, pattern='item [0-9]'))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook(port=5000)
updater.idle()
