#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from emoji import emojize
#from eloquent import DatabaseManager, Model
import logging
from models import User, Group

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
        group = Group.first_or_create(telegram_chat_id=chat['id'])
        update.message.reply_text('Hola grupo {}'.format(chat['title']))

        user = User.where('telegram_chat_id', _from['id']).first()
        if user is None:
            user = User.create(name=_from['first_name'], username=_from['username'],
                telegram_chat_id=_from['id'])
            update.message.reply_text('Hola {}, mucho gusto.'.format(user.name))
        else:
            update.message.reply_text('Hola {}'.format(user.name))

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('create', create))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook(port=5000)
updater.idle()
