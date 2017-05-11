#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, logging
from flask import Flask, request
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from emoji import emojize
from models import User, Group, List, Item, db

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

def _help(bot, update):
    chat = update.message.chat

    message = "Lista de comandos\n"
    message += "=================\n"
    message += "/start - Saludo\n"
    message += "/create - Crear Lista de pedidos\n"
    message += "/items - Listar items disponibles en el grupo\n"
    message += "/close - Cerrar Lista de pedidos\n"
    message += "/open - Reabrir Lista de pedidos\n"
    message += "/list - Mostrar detalle de lista de pedido actual\n"
    message += "/paylist - Mostrar nombre y monto de lista de pedido actual"

    bot.send_message(chat_id=chat['id'], text=message)

def create(bot, update):
    _from = update.message.from_user
    chat = update.message.chat

    if 'group' in chat['type']:
        group = Group.find(chat['id'])

        if group is None:
            group = Group.create(id=chat['id'],
                                 title=chat['title'])

        bot.send_message(chat_id=chat['id'],
            text='Hola grupo {}'.format(chat['title']))

        list_active = group.lists().opened().first()

        if list_active is None:
            user = User.find(_from['id'])

            if user is None:
                user = User.create(id=_from['id'],
                                   name=_from['first_name'],
                                   username=_from['username'])
                update.message.reply_text('Hola esclavo {}, mucho gusto.'.format(user.name))
            else:
                update.message.reply_text('Hola esclavo {}'.format(user.name))

            _list = List()
            _list.user_id = _from['id']
            _list.group_id = chat['id']
            _list.save()

            message = 'Lista creada'
        else:
            message = 'Ya hay una lista abierta'

        bot.send_message(chat_id=chat['id'], text=message)

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
    group = Group.find(chat['id'])
    list_active = group.lists().opened().first()

    if list_active is not None:
        user = User.find(_from['id'])

        if user is None:
            user = User.create(id=_from['id'],
                               name=_from['first_name'],
                               username=_from['username'])

        list_active.items().attach(item, {
            'user_id': user.id, 'price': item.price})
        message = '{} ha agregado {} a la lista.'.format(user.name, item.name)
    else:
        message = 'No hay una lista abierta'

    query.message.reply_text(message)

def items(bot, update):
    chat = update.message.chat
    send_items(bot, chat['id'])

def send_items(bot, chat_id):
    items = Item.where('group_id', chat_id).get()

    keyboard = []
    for i in xrange(0, len(items), 2):
        left = items.get(i)
        right = items.get(i+1)

        buttons = []
        buttons.append(InlineKeyboardButton(
            '{} - {}'.format(left.name, left.price_format),
            callback_data='item {}'.format(left.id))
        )
        if right is not None:
            buttons.append(InlineKeyboardButton(
                '{} - {}'.format(right.name, right.price_format),
                callback_data='item {}'.format(right.id))
            )

        keyboard.append(buttons)

    bot.send_message(chat_id=chat_id, text='Escoge un producto',
                     reply_markup=InlineKeyboardMarkup(keyboard))

def check_slave(list_active, _from):
    return list_active.slave.id == _from.id

def close(bot, update):
    chat = update.message.chat
    _from = update.message.from_user
    group = Group.find(chat['id'])
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
    group = Group.find(chat['id'])
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

def get_user_amounts(_list):
    return db.table('list_x_item')\
             .select(db.raw('sum(list_x_item.price) as total, users.name, users.id as user_id'))\
             .join('users', 'list_x_item.user_id', '=', 'users.id')\
             .where('list_id', _list.id)\
             .group_by('list_x_item.user_id')\
             .get()

def _list(bot, update):
    chat = update.message.chat
    group = Group.find(chat['id'])
    list_active = group.lists().opened().first()

    if list_active is not None:
        user_amounts = get_user_amounts(list_active)

        if len(user_amounts) > 0:
            message = ""
            all_items = list_active.items

            for user_amount in user_amounts:
                message += "{} S/{}\n".format(
                    user_amount.name, str(user_amount.total))

                user_items = all_items.filter(
                    lambda item: item.pivot.user_id == user_amount.user_id)
                for item in user_items:
                    message += "> {} {}\n".format(item.name, item.price_format)
        else:
            message = "No hay elementos en la lista"
    else:
        message = 'No hay lista abierta'

    bot.send_message(chat_id=chat['id'], text=message)

def paylist_message(user_amounts):
    if len(user_amounts) > 0:
        message = "Lista de Pagos\n"
        for user_amount in user_amounts:
            message += "{} S/{}\n".format(
                    user_amount.name, str(user_amount.total))
    else:
        message = 'Lista vacia'

    return message

def paylist(bot, update):
    chat = update.message.chat
    group = Group.find(chat['id'])
    list_active = group.lists().opened().first()

    if list_active is not None:
        message = ''
        user_amounts = get_user_amounts(list_active)
        message = paylist_message(user_amounts)
    else:
        list_active = group.lists().closed().first()

        if list_active is not None:
            user_amounts = get_user_amounts(list_active)
            message = paylist_message(user_amounts)
        else:
            message = 'Aun no hay listas en el grupo'

    bot.send_message(chat_id=chat['id'], text=message)

def add_item(bot, update):
    chat = update.message.chat
    text = update.message.text[10:]
    group = Group.find(chat['id'])
    args = text.split(',')

    if len(args) == 2:
        name = args[0].strip()
        price = args[1].strip()

        if group.items.count() < 8:
            group.items().save(Item(name=name, price=price))

            message = u'{} ha sido agregado a los items del grupo'.format(name)
        else:
            message = u'No se puede agregar más items'
    else:
        message = u'Son necesarios el nombre y el precio separados por comas'

    bot.send_message(chat_id=chat['id'], text=message)

def del_item(bot, update):
    chat = update.message.chat
    text = update.message.text[10:]
    group = Group.find(chat['id'])

    item = group.items().where('name', text).first()

    if item is not None:
        item.delete()
        message = '{} ha sido eliminado de los items'.format(text)
    else:
        message = 'Ingrese el nombre tal cual esta en la lista'

    bot.send_message(chat_id=chat['id'], text=message)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', _help))
updater.dispatcher.add_handler(CommandHandler('create', create))
updater.dispatcher.add_handler(CommandHandler('items', items))
updater.dispatcher.add_handler(CommandHandler('close', close))
updater.dispatcher.add_handler(CommandHandler('open', _open))
updater.dispatcher.add_handler(CommandHandler('list', _list))
updater.dispatcher.add_handler(CommandHandler('paylist', paylist))
updater.dispatcher.add_handler(CallbackQueryHandler(add, pattern='item [0-9]+'))
updater.dispatcher.add_handler(CommandHandler('add_item', add_item))
updater.dispatcher.add_handler(CommandHandler('del_item', del_item))

@app.route('/telegram_hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        updater.dispatcher.process_update(update)
    return 'ok'


@app.route('/sw', methods=['GET', 'POST'])
def set_webhook():
    return "webhook setup ok" if bot.setWebhook(SITE_URL + '/telegram_hook') else "webhook setup failed"

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    app.run(debug=True)
