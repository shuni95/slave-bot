#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from emoji import emojize
import pymysql.cursors
import logging
# Connect to the database
connection = pymysql.connect(host='localhost',
                              user='root',
                              password='root',
                              db='slave',
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

TOKEN='#'
SITE_URL='#'

def start(bot, update):
    update.message.reply_text('Hola!, Soy SlaveBot ' + emojize(':grinning_face:', use_aliases=True))

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.bot.setWebhook(SITE_URL)
updater.start_webhook(port=5000)
updater.idle()
