#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from emoji import emojize
from user import User
from group import Group
import logging

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
        group = Group.find(chat['id'])
        if group is None:
            Group.create(chat)
            update.message.reply_text('Hola grupo {}'.format(chat['title']))

        user = User.find(_from['id'])
        if user is None:
            User.create(_from)
            update.message.reply_text(u'Hola {}, mucho gusto {}'.format(
                chat.first_name,
                emojize(':grinning_face:', use_aliases=True)))
        else:
            update.message.reply_text('Hola de nuevo {}'.format(user['name']))

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('create', create))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook(port=5000)
updater.idle()
