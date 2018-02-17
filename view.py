from flask import render_template, request
from app import app, db, bot
from models import *

from telebot import types
from config import token

import hashlib

from datetime import datetime
from sqlalchemy import and_

from app import service
from config import spreadsheet_id

### Front page ###
@app.route('/')
def index():
    ''' Connecting with bot '''
    bot.remove_webhook()
    bot.set_webhook(url='https://your-web-site.com/{}'.format(token))

    return render_template('index.html')
### Front page ###

### 404 ###
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
### 404 ###



### TELEGRAM VIEWS ###

### Telegram webhook ###
@app.route('/{}'.format(token), methods=['POST'])
def webhook():
    bot.process_new_updates([types.Update.de_json(request.stream.read().decode('utf-8'))])
    return 'ok', 200
### Telegram webhook ###

### /start command ###
@bot.message_handler(commands=['start'])
def start(message):
    user = Users.query.filter_by(username=message.chat.username).first()
    if (user is None):
        user = Users(chat_id=message.chat.id, \
                    username=message.chat.username, \
                    first_name=message.chat.first_name, \
                    last_name=message.chat.last_name, \
                    status='User')
        db.session.add(user)
        db.session.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Расписание', 'Что сейчас?')
    markup.row('Регистрация', 'Я не расселен')
    markup.row('Где покушать?')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Опросы')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Опросы')
    elif (user.status == 'Memeses'):
        markup.row('Отправить мем')
    elif (user.status == 'VIP'):
        markup.row('Отправить мем', 'Отправить сообщение')

    bot.send_message(message.chat.id, \
                    'Здравствуйте, ' + message.chat.first_name + '!', \
                    reply_markup=markup)
### /start command ###

### /start_keyboard command ###
@bot.message_handler(commands=['start_keyboard'])
def start_keyboard(message):
    user = Users.query.filter_by(username=message.chat.username).first()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Расписание', 'Что сейчас?')
    markup.row('Регистрация', 'Я не расселен')
    markup.row('Где покушать?')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Опросы')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Опросы')
    elif (user.status == 'Memeses'):
        markup.row('Отправить мем')
    elif (user.status == 'VIP'):
        markup.row('Отправить мем', 'Отправить сообщение')

    bot.send_message(message.chat.id, 'Клавиатура включена', reply_markup=markup)
### /start_keyboard command ###

### /stop_keyboard command ###
@bot.message_handler(commands=['stop_keyboard'])
def stop_keyboard(message):
    remove_markup = types.ReplyKeyboardRemove()

    bot.send_message(message.chat.id, 'Клавиатура выключена', reply_markup=remove_markup)
### /stop_keyboard command ###

### /git command ###
@bot.message_handler(commands=['git'])
def git(message):
    buttons = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Перейти по ссылке', \
                                        url='https://github.com/KonstantinShvyryaev/tth-2018-bot')
    buttons.add(url_button)
    bot.send_message(message.chat.id, \
                    '<b>Хотите посмотреть код нашего бота?</b>', \
                    parse_mode='HTML', \
                    reply_markup=buttons)
### /git command ###

### Text Handler ###
@bot.message_handler(content_types=['text'])
def text(message):
    # Расписание
    if (message.text == 'Расписание'):
        bot.send_message(message.chat.id, timetable(), parse_mode='HTML')
    # Расписание

    # Что сейчас?
    elif (message.text == 'Что сейчас?'):
        bot.send_message(message.chat.id, events_now(), parse_mode='HTML')
    # Что сейчас?

    # Регистрация
    elif (message.text == 'Регистрация'):
        buttons = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text='Зарегистрироваться', \
                                                url='https://docs.google.com/forms/d/1M7oxELpr4mlPjbOATYi-d7o29bs8T5fcfISEu2woxy4/viewform?ts=5a7ad9e7&edit_requested=true#responses')
        buttons.add(url_button)

        user = Users.query.filter_by(username=message.chat.username).first()
        if not user.is_confirmed:
            confirm_reg = types.InlineKeyboardButton(text='Подтвердить регистрацию', \
                                            callback_data='confirm_reg')
            buttons.add(confirm_reg)

            bot.send_message(message.chat.id, \
                            registration(), \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        else:
            bot.send_message(message.chat.id, \
                    '<b>Вы подтвердили регистрацию. Желаем отлично провести время на TTH!</b>', \
                    parse_mode='HTML', \
                    reply_markup=buttons)
    # Регистрация
    
    # Я не расселен
    elif (message.text == 'Я не расселен'):
        buttons = types.InlineKeyboardMarkup()
        res_send = types.InlineKeyboardButton(text='Отправить', \
                                            callback_data='res_send')
        res_break = types.InlineKeyboardButton(text='Отмена', \
                                            callback_data='res_break')
        buttons.add(res_send, res_break)

        bot.send_message(message.chat.id, \
                        '''<b>Мы можем отправить сообщение ответственному \
за расселение и он вам ответит )</b>''', \
                        parse_mode='HTML', \
                        reply_markup=buttons)
    # Я не расселен

    # Где покушать?
    if (message.text == 'Где покушать?'):
        buttons = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text='Перейти по ссылке', \
                                                url='https://yandex.ru/maps/-/CBeRiStO~D')
        buttons.add(url_button)
        bot.send_message(message.chat.id, \
                        '<b>Мы подобрали для вас места, где можно перекусить )</b>', \
                        parse_mode='HTML', \
                        reply_markup=buttons)
    # Где покушать?

    # Изменить статус пользователя
    elif (message.text == 'Изменить статус пользователя'):
        user = Users.query.filter_by(username=message.chat.username).first()
        if(user.status == 'Admin'):
            msg = bot.send_message(message.chat.id, \
                            '<b>Сформируйте запрос в формате:</b> <i>username new_status</i>', \
                            parse_mode='HTML')
            bot.register_next_step_handler(msg, change_status_for_user)
    # Изменить статус пользователя

    # Отправить мем
    elif (message.text == 'Отправить мем'):
        def mem_pocessing(message):
            try:
                buttons = types.InlineKeyboardMarkup()
                mem_post = types.InlineKeyboardButton(text='Отправить', \
                                                    callback_data='mem_post')
                mem_post_anonymously = types.InlineKeyboardButton(text='Отправить анонимно', \
                                                    callback_data='mem_post_anonymously')
                mem_break = types.InlineKeyboardButton(text='Отмена', \
                                                    callback_data='mem_break')
                buttons.add(mem_post)
                buttons.add(mem_post_anonymously)
                buttons.add(mem_break)

                bot.send_message(message.chat.id, \
                                    '<b>Вот что получилось )</b>', \
                                     parse_mode="HTML")

                max_quality = len(message.photo) - 1
                bot.send_message(message.chat.id, \
                                '<i>Memes by</i> @{}'.format(message.chat.username), \
                                parse_mode="HTML")
                bot.send_photo(message.chat.id, \
                                message.photo[max_quality].file_id, \
                                message.caption, \
                                reply_markup=buttons)
            except Exception as e:
                bot.send_message(message, 'oooops')

        user = Users.query.filter_by(username=message.chat.username).first()
        if(user.status == 'Admin' or user.status == 'VIP' or user.status == 'Memeses'):
            msg = bot.send_message(message.chat.id, '<b>Загрузите мем )</b>', parse_mode='HTML')
            bot.register_next_step_handler(msg, mem_pocessing)
    # Отправить мем

    # Отправить сообщение
    elif (message.text == 'Отправить сообщение'):
        def message_pocessing(message):
            try:
                buttons = types.InlineKeyboardMarkup()
                message_post = types.InlineKeyboardButton(text='Отправить', \
                                                    callback_data='message_post')
                message_post_anonymously = types.InlineKeyboardButton(text='Отправить анонимно', \
                                                    callback_data='message_post_anonymously')
                message_break = types.InlineKeyboardButton(text='Отмена', \
                                                    callback_data='message_break')
                buttons.add(message_post)
                buttons.add(message_post_anonymously)
                buttons.add(message_break)

                bot.send_message(message.chat.id, \
                                    '<b>Вот что получилось )</b>', \
                                     parse_mode='HTML')
                bot.send_message(message.chat.id, \
                                '<i>Message by</i> @{}'.format(message.chat.username), \
                                parse_mode='HTML')
                bot.send_message(message.chat.id, \
                                '{}'.format(message.text), \
                                parse_mode='HTML', \
                                reply_markup=buttons)
            except Exception as e:
                bot.send_message(message, 'oooops')

        user = Users.query.filter_by(username=message.chat.username).first()
        if(user.status == 'Admin' or user.status == 'VIP'):
            msg = bot.send_message(message.chat.id, \
                                '<b>Введите сообщение:</b>', \
                                parse_mode='HTML')
            bot.register_next_step_handler(msg, message_pocessing)
    # Отправить сообщение

    # Опросы
    elif (message.text == 'Опросы'):
        user = Users.query.filter_by(username=message.chat.username).first()
        if(user.status == 'Admin' or user.status == 'Questions'):
            buttons = types.InlineKeyboardMarkup()
            inter_join = types.InlineKeyboardButton(text='Предложить вступить', \
                                                    callback_data='inter_join')
            inter_report = types.InlineKeyboardButton(text='Сообщить о новых вопросах', \
                                                    callback_data='inter_report')
            inter_break = types.InlineKeyboardButton(text='Отмена', \
                                                    callback_data='inter_break')
            buttons.add(inter_join)
            buttons.add(inter_report)
            buttons.add(inter_break)

            bot.send_message(message.chat.id, \
                            '<b>Канал </b><i>"TTH Опросы"</i><b>.Что будем делать?</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
    # Опросы
### Text Handler ###

### Callback query handler ###
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:

        # res_send button
        if call.data == 'res_send':
            recipient_username = 'konstantinShvyryaev'
            recipient = Users.query.filter_by(username=recipient_username).first()
            recipient_id = recipient.chat_id

            sender_username = call.message.chat.username

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Мы отправили сообщение ответственному \
за расселение, вам сейчас ответят )</b>', \
                                parse_mode='HTML')

            bot.send_message(recipient_id, \
                        '@{} <b>нуждается в расселении!</b>'.format(sender_username), \
                        parse_mode="HTML")
        # res_send button

        # res_break button
        elif call.data == 'res_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Желаем отлично провести время на TTH )</b>', \
                                parse_mode='HTML')
        # res_break button

        #confirm_reg button
        elif call.data == 'confirm_reg':
            def confirm_pocessing(message):
                username = message.chat.username

                target = username
                if (username[0] == '@'):
                    target = username[1:]
                target = target.lower()

                hash_object = hashlib.md5(target.encode('UTF-8'))

                if message.text == hash_object.hexdigest():
                    range_ = 'A2:A1000'
                    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                                range=range_, \
                                                                majorDimension='COLUMNS')
                    response = request.execute()

                    usernames = response['values'][0]
                    for i in range(len(usernames)):
                        username = usernames[i]
                        if (username[0] == '@'):
                            username = username[1:]
                        username = username.lower()

                        if (username == message.chat.username.lower()):
                            body = {
                                'valueInputOption': 'USER_ENTERED',
                                'data': [
                                    {
                                        'range': 'md5!C{}'.format(i + 2),
                                        'majorDimension': 'COLUMNS',
                                        'values': [['Confirmed']]
                                    },
                                ]}
                            service.spreadsheets().values().batchUpdate( \
                                                            spreadsheetId = spreadsheet_id, \
                                                            body = body).execute()
                            break
                        
                    user = Users.query.filter_by(username=message.chat.username).first()
                    user.is_confirmed = True
                    db.session.commit()

                    bot.send_message(message.chat.id, \
                            '<b>Поздравляем! Вы подтвердили регистрацию!</b>', \
                            parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, \
                            '<b>Неверный код! Спросите ваш код на столе регистрации!</b>', \
                            parse_mode='HTML')

            msg = bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>Введите код, который вам дали на столе регистрации:</b>', \
                            parse_mode='HTML')

            bot.register_next_step_handler(msg, confirm_pocessing)
        #confirm_reg button

        # mem_post button
        elif call.data == 'mem_post':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 
                                '<b>Мем отправлен )</b>', 
                                parse_mode='HTML')

            users = Users.query.all()
            max_quality = len(call.message.photo) - 1
            for user in users:
                bot.send_message(user.chat_id, \
                                '<i>Memes by</i> @{}'.format(call.message.chat.username), \
                                parse_mode='HTML')
                bot.send_photo(user.chat_id, \
                            call.message.photo[max_quality].file_id, \
                            call.message.caption)
        # mem_post button

        # mem_post_anonymously button
        elif call.data == 'mem_post_anonymously':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 
                                '<b>Мем отправлен )</b>', 
                                parse_mode='HTML')

            users = Users.query.all()
            max_quality = len(call.message.photo) - 1
            for user in users:
                if (user.status == 'Admin') or (user.status == 'VIP'):
                    bot.send_message(user.chat_id, \
                                '<i>Anonymously by</i> @{}'.format(call.message.chat.username), \
                                parse_mode='HTML')
                bot.send_photo(user.chat_id, \
                            call.message.photo[max_quality].file_id, \
                            call.message.caption)
        # mem_post_anonymously button

        # mem_break button
        elif call.data == 'mem_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, '<b>В другой раз )</b>', parse_mode='HTML')
        # mem_break button

        # message_post button
        elif call.data == 'message_post':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Сообщение отправлено )</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                bot.send_message(user.chat_id, \
                        '<i>Message by</i> @{}\n\n{}'.format(call.message.chat.username, \
                                                            call.message.text), \
                        parse_mode='HTML')
        # message_post button

        # message_post_anonymously button
        elif call.data == 'message_post_anonymously':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Сообщение отправлено )</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                if (user.status == 'Admin') or (user.status == 'VIP'):
                    bot.send_message(user.chat_id, \
                        '<i>Anonymously by</i> @{}\n\n{}'.format(call.message.chat.username, \
                                                                call.message.text), \
                        parse_mode='HTML')
                else:
                    bot.send_message(user.chat_id, \
                        '<b>Сообщение от TTH:</b>\n\n{}'.format(call.message.text), \
                        parse_mode='HTML')
        # message_post_anonymously button

        # message_break button
        elif call.data == 'message_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз )</b>", \
                                parse_mode='HTML')
        # message_break button

        # inter_join button
        elif call.data == 'inter_join':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Сообщение отправлено )</b>", \
                                parse_mode='HTML')

            buttons = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text='Вступить', \
                                            url='https://t.me/joinchat/AAAAAFLPXRh0y3s_NXRd_Q')
            buttons.add(url_button)
            users = Users.query.all()
            for user in users:
                bot.send_message(user.chat_id, \
                            '<b>Вступайте в наш канал! В нем будут различные опросы ))</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # inter_join button

        # inter_report button
        elif call.data == 'inter_report':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Сообщение отправлено )</b>', \
                                parse_mode='HTML')

            buttons = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text='Новые вопросы', \
                                            url='https://t.me/joinchat/AAAAAFLPXRh0y3s_NXRd_Q')
            buttons.add(url_button)
            users = Users.query.all()
            for user in users:
                bot.send_message(user.chat_id, \
                            '<b>Переходите скорее отвечать на новые вопросы ))</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # inter_report button

        # inter_break button
        elif call.data == 'inter_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>В другой раз )</b>', \
                                parse_mode='HTML')
        # inter_break button
### Callback query handler ###



# Create the timetable line
def timetable():
    return '''\r
<b>Четверг:</b>
    <b>18:30</b>  -  ОТКРЫТИЕ

<b>Пятница:</b>
    <b>08:30</b>  -  ЗАВТРАК
    <b>09:10</b>  -  МОЛИТВА
    <b>10:00</b>  -  СОБРАНИЕ
    <b>12:00</b>  -  МАСТЕР КЛАССЫ
    <b>14:30</b>  -  СОБРАНИЕ
    <b>16:00</b>  -  МАЛЫЕ ГРУППЫ
    <b>18:30</b>  -  СОБРАНИЕ

<b>Суббота:</b>
    <b>08:30</b>  -  ЗАВТРАК
    <b>09:10</b>  -  МОЛИТВА
    <b>10:00</b>  -  СОБРАНИЕ
    <b>12:00</b>  -  МАСТЕР КЛАССЫ
    <b>14:30</b>  -  СОБРАНИЕ
    <b>16:00</b>  -  МАЛЫЕ ГРУППЫ
    <b>19:00</b>  -  ВЕЧЕР ХВАЛЫ

<b>Воскресение:</b>
    <b>09:00</b>  -  МОЛИТВА
    <b>10:00</b>  -  СОБРАНИЕ
    <b>14:00</b>  -  СОБРАНИЕ (Подростки)
    <b>17:00</b>  -  МОЛИТВА
    <b>18:00</b>  -  СОБРАНИЕ
'''

# Create the registration line
def registration():
    return '''\r
<b>На конференции вам необходимо получить код на столе регистрации, \
после чего нажать кнопку </b><i>"Подтвердить регистрацию"</i> <b>и ввести код )</b>
'''

# Create the line of events which now
def events_now():
    now = datetime.now()
    events = Events.query.filter(and_(Events.dateStart <= now, Events.dateFinish >= now))

    line = '<b>Сейчас:</b>\n'

    for i in events:
        if (i.name == 'ЗАВТРАК'):
            line += '    <b>{}</b>  -  {} <i>({})</i>\n' \
                .format(getTime(i.dateStart), i.name, i.speaker)
        elif (i.name == 'МОЛИТВА'):
            line += '    <b>{}</b>  -  {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'СОБРАНИЕ' or i.name == 'СОБРАНИЕ (Подростки)'):
            line += '    <b>{}</b>  -  {} <i>(Проповедник: {}; тема: "{}")</i>\n' \
                .format(getTime(i.dateStart), \
                        i.name, i.speaker, i.description)
        elif (i.name == 'МАСТЕР КЛАСС'):
            line += '    <b>{}</b>  -  {} <i>(Спикер: {}; тема: "{}")</i>\n' \
                .format(getTime(i.dateStart), \
                        i.name, i.speaker, i.description)
        elif (i.name == 'МАЛЫЕ ГРУППЫ'):
            line += '    <b>{}</b>  -  {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'ОТКРЫТИЕ'):
            line += '    <b>{}</b>  -  {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'ВЕЧЕР ХВАЛЫ'):
            line += '    <b>{}</b>  -  {}\n'.format(getTime(i.dateStart), i.name)

    if (line == '<b>Сейчас:</b>\n'):
        line += '    Свободное время )\n'

    return line

# Generate line hour:minute
def getTime(dt):
    temp = dt.timetuple()
    hour = temp[3]
    minute = temp[4]

    if hour < 10:
        hour = '0' + str(hour)
    if minute < 10:
        minute = '0' + str(minute)

    return '{}:{}'.format(hour, minute)

# Function for changing status for user
def change_status_for_user(message):
    try:
        request = message.text.split()
        user = Users.query.filter_by(username=request[0]).first()

        if (user is None):
            bot.send_message(message.chat.id, \
                '<b>Ошибка! Пользователя</b> {} <b>нет в базе данных (</b>' \
                    .format(request[0]), parse_mode='HTML')
        else:
            user.status = request[1]
            db.session.commit()

            bot.send_message(message.chat.id, \
                '<b>Cтатус пользователя</b> {} <b>сменен на</b> {}' \
                    .format(request[0], request[1]), parse_mode='HTML')
    except Exception as e:
        bot.send_message(message, 'oooops')