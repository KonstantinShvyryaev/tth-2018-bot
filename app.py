from flask import Flask
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy

from config import Configuration, token, CREDENTIALS_FILE

import telebot

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from googleapiclient import discovery

### Google API ###
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, \
                    ['https://www.googleapis.com/auth/spreadsheets', \
                            'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())

service = discovery.build('sheets', 'v4', http = httpAuth)
driveService = discovery.build('drive', 'v3', http = httpAuth)

### BOT ###
bot = telebot.TeleBot(token)
#bot = telebot.AsyncTeleBot(token)
# https://github.com/eternnoir/pyTelegramBotAPI#asynchronous-delivery-of-messages #
# https://devcenter.heroku.com/articles/python-gunicorn #

### App ###
app = Flask(__name__)
app.config.from_object(Configuration)

### SSL ###
sslify = SSLify(app)

### DB ###
db = SQLAlchemy(app)

### Migrate ###
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

### Admin ###
from admin import *