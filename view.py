from flask import render_template, request
from app import app, db, bot
from models import *

from telebot import types
from config import token, web_site

from datetime import datetime, timedelta
from dateutil.tz import tzutc
import pytz
from sqlalchemy import and_

from app import service
from config import spreadsheet_id
import time

import botan
from config import botan_key

### Front page ###
@app.route('/')
def index():
    ''' Connecting with bot '''
    bot.remove_webhook()
    bot.set_webhook(url='{}{}'.format(web_site, token))

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
    # bot.process_new_updates([types.Update.de_json(request.stream.read().decode('utf-8'))])
    bot.process_new_updates([types.Update.de_json(request.data.decode('utf-8'))])
    return 'ok', 200
### Telegram webhook ###

### /start command ###
@bot.message_handler(commands=['start'])
def start(message):
    user = Users.query.filter_by(chat_id=message.from_user.id).first()
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
    markup.row('Где покушать?', 'Кто на TTH?')
    markup.row('В какой я группе?', 'Мастер-классы')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Отправить опрос', 'Обновить')
        markup.row('Отправить стикеры')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Отправить опрос', 'Отправить сообщение')
    elif (user.status == 'Memeses'):
        markup.row('Отправить мем')
    elif (user.status == 'VIP'):
        markup.row('Отправить сообщение')

    bot.send_message(message.chat.id, \
                    '<b>{}, желаем хорошо провести время на TTH 😊</b>'.format( \
                                                                message.chat.first_name), \
                    parse_mode='HTML', \
                    reply_markup=markup)
### /start command ###

### /start_keyboard command ###
@bot.message_handler(commands=['start_keyboard'])
def start_keyboard(message):
    user = Users.query.filter_by(chat_id=message.from_user.id).first()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Расписание', 'Что сейчас?')
    markup.row('Регистрация', 'Я не расселен')
    markup.row('Где покушать?', 'Кто на TTH?')
    markup.row('В какой я группе?', 'Мастер-классы')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Отправить опрос', 'Обновить')
        markup.row('Отправить стикеры')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Отправить опрос', 'Отправить сообщение')
    elif (user.status == 'Memeses'):
        markup.row('Отправить мем')
    elif (user.status == 'VIP'):
        markup.row('Отправить сообщение')

    bot.send_message(message.chat.id, 'Клавиатура включена', reply_markup=markup)

    try:
        botan.track(botan_key, message.chat.id, None, 'start_keyboard')
    except Exception as e:
        pass
### /start_keyboard command ###

### /stop_keyboard command ###
@bot.message_handler(commands=['stop_keyboard'])
def stop_keyboard(message):
    remove_markup = types.ReplyKeyboardRemove()

    bot.send_message(message.chat.id, 'Клавиатура отключена', reply_markup=remove_markup)

    try:
        botan.track(botan_key, message.chat.id, None, 'stop_keyboard')
    except Exception as e:
        pass
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

    try:
        botan.track(botan_key, message.chat.id, None, 'git')
    except Exception as e:
        pass
### /git command ###

# Google: create array when app starting
start_range_ = 'A2:AD2'
start_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                            range=start_range_, \
                                            majorDimension='ROWS')
start_response = start_request.execute()
start_conf_info = start_response['values'][0]
conf_info_temp = [start_conf_info, time.time()]


start_small_group_range_ = 'C3:G1000'
start_small_group_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                            range=start_small_group_range_, \
                                                            majorDimension='ROWS')
start_small_group_response = start_small_group_request.execute()
if 'values' in start_small_group_response:
    start_small_group_val = start_small_group_response['values']
    small_group_temp = [start_small_group_val, time.time()]
# Google: create array when app starting

### Text Handler ###
@bot.message_handler(content_types=['text'])
def text(message):
    # Расписание
    if (message.text == 'Расписание'):
        bot.send_message(message.chat.id, timetable(), parse_mode='HTML')

        try:
            botan.track(botan_key, message.chat.id, None, 'Расписание')
        except Exception as e:
            pass
    # Расписание

    # Что сейчас?
    elif (message.text == 'Что сейчас?'):
        bot.send_message(message.chat.id, events_now(), parse_mode='HTML')

        try:
            botan.track(botan_key, message.chat.id, None, 'Что сейчас?')
        except Exception as e:
            pass
    # Что сейчас?

    # Регистрация
    elif (message.text == 'Регистрация'):
        buttons = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text='Зарегистрироваться', \
                                                url='https://goo.gl/ae2xLR')
        buttons.add(url_button)

        bot.send_message(message.chat.id, \
                '<b>Для регистрации вам необходимо перейти по ссылке 👇</b>', \
                parse_mode='HTML', \
                reply_markup=buttons)

        try:
            botan.track(botan_key, message.chat.id, None, 'Регистрация')
        except Exception as e:
            pass
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
за расселение и он вам ответит 😉</b>''', \
                        parse_mode='HTML', \
                        reply_markup=buttons)

        try:
            botan.track(botan_key, message.chat.id, None, 'Я не расселен')
        except Exception as e:
            pass
    # Я не расселен

    # Где покушать?
    elif (message.text == 'Где покушать?'):
        buttons = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text='Перейти по ссылке', \
                                                url='https://goo.gl/FsBvF2')
        buttons.add(url_button)
        bot.send_message(message.chat.id, \
                        '<b>Мы подобрали для вас места, где можно перекусить 😉</b>', \
                        parse_mode='HTML', \
                        reply_markup=buttons)

        try:
            botan.track(botan_key, message.chat.id, None, 'Где покушать?')
        except Exception as e:
            pass
    # Где покушать?

    # Кто на TTH?
    elif (message.text == 'Кто на TTH?'):
        global conf_info_temp
        cur_time = time.time()
        diff = cur_time - conf_info_temp[1]

        if diff > 60:
            conf_info_temp[1] = time.time()

            range_ = 'A2:AD2'
            request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                        range=range_, \
                                                        majorDimension='ROWS')
            response = request.execute()
            conf_info = response['values'][0]
            conf_info_temp[0] = conf_info

        bot.send_message(message.chat.id, \
                        '<b>💡 На конференции 💡</b>\n🚗 Приехали: {}\n\
⚽ Младше 14 лет: {}\n🎮 От 14 до 18 лет: {}\n🍀 Старше 18 лет: {}\n\
👱 Парней: {}\n👩 Девушек: {}'.format(conf_info_temp[0][1], \
                                conf_info_temp[0][25], \
                                conf_info_temp[0][26], \
                                conf_info_temp[0][27], \
                                conf_info_temp[0][28], \
                                conf_info_temp[0][29]), \
                        parse_mode='HTML')

        try:
            botan.track(botan_key, message.chat.id, None, 'Кто на TTH?')
        except Exception as e:
            pass
    # Кто на TTH?

    # В какой я группе?
    elif (message.text == 'В какой я группе?'):
        try:
            botan.track(botan_key, message.chat.id, None, 'В какой я группе?')
        except Exception as e:
            pass

        global small_group_temp

        try:
            small_group_temp
        except NameError:
            bot.send_message(message.chat.id, \
                            '<b>Мы еще не распределили малые группы 🤔</b>', \
                            parse_mode='HTML')
            return

        cur_time = time.time()
        diff = cur_time - small_group_temp[1]

        # grp_processing
        def grp_processing(message):
            full_name = message.text.split()
            size = len(full_name)
            if size != 3:
                if (size == 1):
                    bot.send_message(message.chat.id, \
                            '<b>Ошибка! Вы ввели {} слово 🙄</b>'.format(size), \
                            parse_mode='HTML')
                elif ((size == 2) or (size == 4)):
                    bot.send_message(message.chat.id, \
                            '<b>Ошибка! Вы ввели {} слова 🙄</b>'.format(size), \
                            parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, \
                            '<b>Ошибка! Вы ввели {} слов 🙄</b>'.format(size), \
                            parse_mode='HTML')
                return

            if full_name[0] == 'Мемесов' \
                and full_name[1] == 'Угандий' \
                    and full_name[2] == 'Наклсович':
                bot.send_message(message.chat.id, \
                            '<b>Я знал, что хоть один человек сделает это 😂\n\
И в подарок ты получаешь 🎉 ничего 🎉</b>', \
                            parse_mode='HTML')
                return

            is_distributed = False
            for i in small_group_temp[0]:
                if i[0] != '':
                    if (i[2] == full_name[0] and i[3] == full_name[1] and i[4] == full_name[2]):
                        if i[0] == '2':
                            bot.send_message(message.chat.id, \
                                '<b>Вы во {} группе 😊</b>'.format(i[0]), \
                                parse_mode='HTML')
                        else:
                            bot.send_message(message.chat.id, \
                                '<b>Вы в {} группе 😊</b>'.format(i[0]), \
                                parse_mode='HTML')

                        try:
                            grp_map = open('static/img/map.jpg', 'rb')
                            bot.send_photo(message.chat.id, grp_map)
                            grp_map.close()
                        except Exception as e:
                            pass

                        buttons = types.InlineKeyboardMarkup()
                        grp_save = types.InlineKeyboardButton(text='Сохранить', \
                                                            callback_data='grp_save')
                        grp_break = types.InlineKeyboardButton(text='Отмена', \
                                                            callback_data='grp_break')
                        buttons.add(grp_save, grp_break)

                        bot.send_message(message.chat.id, \
                                '<b>{} {} {}\nХотите ли вы сохранить ваши ФИО? 🙃 \
Вам больше не придется их вводить 😉</b>'.format(full_name[0], \
                                                    full_name[1], \
                                                        full_name[2]), \
                                parse_mode='HTML', \
                                reply_markup=buttons)
                        return
                    
                    is_distributed = True

            if is_distributed:
                bot.send_message(message.chat.id, \
                                '<b>Мы еще не распределили вас в малую группу, \
либо вы неверно ввели ваши ФИО 🤔</b>\n<i>Либо мы неверно ввели ваши ФИО</i> 😉', \
                                parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, \
                                '<b>Мы еще не распределили малые группы 🤔</b>', \
                                parse_mode='HTML')
        # grp_processing

        if diff > 120:
            small_group_temp[1] = time.time()

            range_ = 'C3:G1000'
            request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                        range=range_, \
                                                        majorDimension='ROWS')
            response = request.execute()
            if 'values' in response:
                small_group_val = response['values']
                small_group_temp[0] = small_group_val

        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if user.grp_last_name is not None:
            return grp_db_processing(message, \
                                    user.grp_last_name, \
                                    user.grp_first_name, \
                                    user.grp_second_name)

        msg = bot.send_message(message.chat.id, \
                            '<b>Введите фамилию, имя, отчество через пробел 😌</b>\n\
<i>(Пример: Мемесов Угандий Наклсович)</i>', \
                            parse_mode='HTML')
        bot.register_next_step_handler(msg, grp_processing)
    # В какой я группе?

    # Мастер-классы
    if (message.text == 'Мастер-классы'):
        buttons = types.InlineKeyboardMarkup()
        ws_friday = types.InlineKeyboardButton(text='Пятница', \
                                            callback_data='ws_friday')
        ws_saturday = types.InlineKeyboardButton(text='Суббота', \
                                            callback_data='ws_saturday')
        buttons.add(ws_friday)
        buttons.add(ws_saturday)

        bot.send_message(message.chat.id, \
                        '<b>✏️ Мастер-классы</b>', \
                        parse_mode='HTML', \
                        reply_markup=buttons)

        try:
            botan.track(botan_key, message.chat.id, None, 'Мастер-классы')
        except Exception as e:
            pass
    # Мастер-классы

    # Обновить
    elif (message.text == 'Обновить'):
        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin'):
            buttons = types.InlineKeyboardMarkup()
            upd_success = types.InlineKeyboardButton(text='Обновить', \
                                                    callback_data='upd_success')
            update_break = types.InlineKeyboardButton(text='Отмена', \
                                                    callback_data='update_break')
            buttons.add(upd_success, update_break)

            bot.send_message(message.chat.id, \
                            '<b>Вы хотите обновить клавиатуры всех пользователей?</b>', \
                            parse_mode="HTML", \
                            reply_markup=buttons)
    # Обновить

    # Отправить стикеры
    elif (message.text == 'Отправить стикеры'):
        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin'):
            buttons = types.InlineKeyboardMarkup()
            stc_post = types.InlineKeyboardButton(text='Отправить', \
                                                    callback_data='stc_post')
            stc_break = types.InlineKeyboardButton(text='Отмена', \
                                                    callback_data='stc_break')
            buttons.add(stc_post, stc_break)

            bot.send_message(message.chat.id, \
                            '<b>Вы хотите отправить стикеры всем пользователям?</b>', \
                            parse_mode="HTML", \
                            reply_markup=buttons)
    # Отправить стикеры

    # Изменить статус пользователя
    elif (message.text == 'Изменить статус пользователя'):
        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin'):
            msg = bot.send_message(message.chat.id, \
                            '<b>Сформируйте запрос в формате:</b> <i>username new_status</i>', \
                            parse_mode='HTML')
            bot.register_next_step_handler(msg, change_status_for_user)
    # Изменить статус пользователя

    # Отправить мем
    elif (message.text == 'Отправить мем'):
        # mem_processing
        def mem_processing(message):
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
                                    '<b>Вот что получилось 😊</b>', \
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
                bot.send_message(message.chat.id, 'oooops')
        # mem_processing

        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin' or user.status == 'Memeses'):
            msg = bot.send_message(message.chat.id, '<b>Загрузите мем 😌</b>', parse_mode='HTML')
            bot.register_next_step_handler(msg, mem_processing)
    # Отправить мем

    # Отправить сообщение
    elif (message.text == 'Отправить сообщение'):
        # message_processing
        def message_processing(message):
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
                                    '<b>Вот что получилось 😊</b>', \
                                     parse_mode='HTML')
                bot.send_message(message.chat.id, \
                                '<i>Message by</i> @{}'.format(message.chat.username), \
                                parse_mode='HTML')
                bot.send_message(message.chat.id, \
                                '{}'.format(message.text), \
                                reply_markup=buttons)
            except Exception as e:
                bot.send_message(message.chat.id, 'oooops')
        # message_processing

        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin' or user.status == 'VIP' or user.status == 'Questions'):
            msg = bot.send_message(message.chat.id, \
                                '<b>Введите сообщение 😌</b>', \
                                parse_mode='HTML')
            bot.register_next_step_handler(msg, message_processing)
    # Отправить сообщение

    # Отправить опрос
    elif (message.text == 'Отправить опрос'):
        # inter_pocessing
        def inter_processing(message):
            try:
                text_splt = message.text.split()
                url = text_splt[0]

                buttons = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text='Пройти опрос', \
                                                        url=url)
                inter_post = types.InlineKeyboardButton(text='Отправить', \
                                                        callback_data='inter_post')
                inter_break = types.InlineKeyboardButton(text='Отмена', \
                                                        callback_data='inter_break')       
                buttons.add(url_button)
                buttons.add(inter_post, inter_break)

                bot.send_message(message.chat.id, \
                        '<b>Вот что получилось(ссылки в текстовом поле не будет) 😊</b>', \
                        parse_mode='HTML')
                bot.send_message(message.chat.id, \
                                '{}\n<b>Мы подготовили для вас опрос 😊\n\
Скорее переходите отвечать 👇</b>'.format(url), \
                                parse_mode='HTML', \
                                reply_markup=buttons)
            except Exception as e:
                bot.send_message(message.chat.id, 'oooops')
        # inter_pocessing

        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin' or user.status == 'Questions'):
            msg = bot.send_message(message.chat.id, \
                        '<b>Введите ссылку на опрос 😌</b>', \
                        parse_mode='HTML')
            bot.register_next_step_handler(msg, inter_processing)
    # Отправить опрос
### Text Handler ###

### Callback query handler ###
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:

        # res_send button
        if call.data == 'res_send':
            recipient_username = 'VitaVet'
            recipient = Users.query.filter_by(username=recipient_username).first()
            recipient_id = recipient.chat_id

            sender_username = call.message.chat.username
            if sender_username is None:
                bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Придумайте себе username! \
Мы не сможем связаться с вами без этого 😢</b>', \
                                parse_mode='HTML')
                return

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Мы отправили сообщение ответственному \
за расселение, вам сейчас ответят 😊</b>', \
                                parse_mode='HTML')

            bot.send_message(recipient_id, \
                        '@{} <b>нуждается в расселении!</b>'.format(sender_username), \
                        parse_mode="HTML")
        # res_send button

        # res_break button
        elif call.data == 'res_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Желаем отлично провести время на TTH 😊</b>', \
                                parse_mode='HTML')
        # res_break button

        # grp_save button
        elif call.data == 'grp_save':
            text_splt = call.message.text.split()

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>Готово 😊</b>', \
                                parse_mode='HTML')

            user = Users.query.filter_by(chat_id=call.message.chat.id).first()
            user.grp_last_name = text_splt[0]
            user.grp_first_name = text_splt[1]
            user.grp_second_name = text_splt[2]
            db.session.commit()
        # grp_save button

        # grp_break button
        elif call.data == 'grp_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>В другой раз 😉</b>', \
                                parse_mode='HTML')
        # grp_break button

        # mem_post button
        elif call.data == 'mem_post':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 
                            '<b>Мем отправлен 😊</b>', 
                            parse_mode='HTML')

            users = Users.query.all()
            max_quality = len(call.message.photo) - 1
            for user in users:
                try:
                    bot.send_message(user.chat_id, \
                                    '<i>Memes by</i> @{}'.format(call.message.chat.username), \
                                    parse_mode='HTML')
                    bot.send_photo(user.chat_id, \
                                call.message.photo[max_quality].file_id, \
                                call.message.caption)
                except Exception as e:
                    continue
        # mem_post button

        # mem_post_anonymously button
        elif call.data == 'mem_post_anonymously':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 
                            '<b>Мем отправлен 😊</b>', 
                            parse_mode='HTML')

            users = Users.query.all()
            max_quality = len(call.message.photo) - 1
            for user in users:
                try:
                    if (user.status == 'Admin') or (user.status == 'VIP'):
                        bot.send_message(user.chat_id, \
                                '<i>Anonymously by</i> @{}'.format(call.message.chat.username), \
                                parse_mode='HTML')
                    bot.send_photo(user.chat_id, \
                                call.message.photo[max_quality].file_id, \
                                call.message.caption)
                except Exception as e:
                    continue
        # mem_post_anonymously button

        # mem_break button
        elif call.data == 'mem_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 
                                '<b>В другой раз 😉</b>', 
                                parse_mode='HTML')
        # mem_break button

        # message_post button
        elif call.data == 'message_post':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Сообщение отправлено 😊</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                try:
                    bot.send_message(user.chat_id, \
                                '<i>Message by</i> @{}'.format(call.message.chat.username), \
                                parse_mode='HTML')
                    bot.send_message(user.chat_id, \
                                    '{}'.format(call.message.text), \
                                    parse_mode='HTML')
                except Exception as e:
                    continue
        # message_post button

        # message_post_anonymously button
        elif call.data == 'message_post_anonymously':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Сообщение отправлено 😊</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                try:
                    if (user.status == 'Admin') or (user.status == 'VIP'):
                        bot.send_message(user.chat_id, \
                                '<i>Anonymously by</i> @{}'.format(call.message.chat.username), \
                                parse_mode='HTML')
                    bot.send_message(user.chat_id, \
                                    '{}'.format(call.message.text), \
                                    parse_mode='HTML')
                except Exception as e:
                    continue
        # message_post_anonymously button

        # message_break button
        elif call.data == 'message_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 2)
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз 😉</b>", \
                                parse_mode='HTML')
        # message_break button

        # inter_post button
        elif call.data == 'inter_post':
            text_splt = call.message.text.split()
            url = text_splt[0]

            buttons = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text='Пройти опрос', \
                                                    url=url)
            buttons.add(url_button)

            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Опрос отправлен 😊</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                try:
                    bot.send_message(user.chat_id, \
                            '<b>Мы подготовили для вас опрос 😊\n\
Скорее переходите отвечать 👇</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
                except Exception as e:
                    continue
        # inter_post button

        # inter_break button
        elif call.data == 'inter_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз 😉</b>", \
                                parse_mode='HTML')
        # inter_break button


        # upd_success button
        elif call.data == 'upd_success':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Готово 😊</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                try:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row('Расписание', 'Что сейчас?')
                    markup.row('Регистрация', 'Я не расселен')
                    markup.row('Где покушать?', 'Кто на TTH?')
                    markup.row('В какой я группе?', 'Мастер-классы')
                    if (user.status == 'User'):
                        pass
                    elif (user.status == 'Admin'):
                        markup.row('Отправить мем', 'Отправить сообщение')
                        markup.row('Отправить опрос', 'Обновить')
                        markup.row('Отправить стикеры')
                        markup.row('Изменить статус пользователя')
                    elif (user.status == 'Questions'):
                        markup.row('Отправить опрос', 'Отправить сообщение')
                    elif (user.status == 'Memeses'):
                        markup.row('Отправить мем')
                    elif (user.status == 'VIP'):
                        markup.row('Отправить сообщение')

                    bot.send_message(user.chat_id, \
                                    '<b>💢 Обновление 💢</b>', \
                                    parse_mode='HTML', \
                                    reply_markup=markup)
                except Exception as e:
                    continue
        # upd_success button

        # update_break button
        elif call.data == 'update_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз 😉</b>", \
                                parse_mode='HTML')
        # update_break button

        # stc_post button
        elif call.data == 'upd_success':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>Готово 😊</b>", \
                                parse_mode='HTML')

            users = Users.query.all()
            for user in users:
                try:
                    buttons = types.InlineKeyboardMarkup()
                    url_button = types.InlineKeyboardButton(text='Стикеры', \
                                        url='https://t.me/addstickers/tth_2018')
                    buttons.add(url_button)

                    bot.send_message(user.chat_id, \
                            '<b>Мы сделали для вас стикеры 👇</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
                except Exception as e:
                    continue
        # stc_post button

        # stc_break button
        elif call.data == 'stc_break':
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз 😉</b>", \
                                parse_mode='HTML')
        # stc_break button

        # ws_friday button
        elif call.data == 'ws_friday':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_michael = types.InlineKeyboardButton(text='Кофе брейк с Михаилом Нокарашвили', \
                                                callback_data='ws_fr_michael')
            ws_fr_maxim = types.InlineKeyboardButton(text='Сила и продуктивность \
домашних групп', \
                                                callback_data='ws_fr_maxim')
            ws_fr_roman = types.InlineKeyboardButton(text='Как не состариться в ожидании перемен?', \
                                                callback_data='ws_fr_roman')
            ws_fr_eugene = types.InlineKeyboardButton(text='Подростковое \
служение – конвейер пробуждения', \
                                                callback_data='ws_fr_eugene')
            ws_fr_igor = types.InlineKeyboardButton(text='Ораторское искусство и раскрепощение', \
                                                callback_data='ws_fr_igor')
            ws_fr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_comeback')
            buttons.add(ws_fr_michael)
            buttons.add(ws_fr_maxim)
            buttons.add(ws_fr_roman)
            buttons.add(ws_fr_eugene)
            buttons.add(ws_fr_igor)
            buttons.add(ws_fr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>✏️ Мастер-классы => Пятница</b>', \
                                parse_mode='HTML', \
                                reply_markup=buttons)
        # ws_friday button

        # ws_fr_michael button
        elif call.data == 'ws_fr_michael':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_descr_comeback')
            buttons.add(ws_fr_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Пятница => "Кофе-брейк с \
Михаил Нокарашвили"</b>\n\n\
Место: <i>Кафе</i>\n\n\
Это отличное время, которое вы можете провести вместе с Михаилом Нокарашвили 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_michael button

        # ws_fr_maxim button
        elif call.data == 'ws_fr_maxim':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_descr_comeback')
            buttons.add(ws_fr_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Пятница => "Сила и продуктивность \
домашних групп или как сделать, чтобы моя домашняя группа росла?"</b>\n\n\
Место: <i>Большой зал (центр)</i>\n\n\
Максим Тычков расскажет о том, в чем является \
успех домашней группы и поделится идями о том, как же умножать свою домашнюю группу 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_maxim button

        # ws_fr_roman button
        elif call.data == 'ws_fr_roman':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_descr_comeback')
            buttons.add(ws_fr_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Пятница => "Как не состариться \
в ожидании перемен?"</b>\n\n\
Место: <i>Большой зал (перед сценой)</i>\n\n\
Когда жизнь преподносит выбор, как понять вызов ли это от Бога, \
или ловушка от дьявола? На что опираться, принимая судьбоносные решения? Если ты \
задавался этими или похожими вопросами и пока не получил ответа, приглашаем тебя \
на мастер-класс с Романом 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_roman button

        # ws_fr_eugene button
        elif call.data == 'ws_fr_eugene':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_descr_comeback')
            buttons.add(ws_fr_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Пятница => "Подростковое служение – \
конвейер пробуждения"</b>\n\n\
Место: <i>Большой зал (задние ряды)</i>\n\n\
Евгений Брощенко расскажет вам о важности подросткового служения и о том, что \
нужно делать сегодня, чтобы завтра был результат! 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_eugene button

        # ws_fr_igor button
        elif call.data == 'ws_fr_igor':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_descr_comeback')
            buttons.add(ws_fr_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Пятница => "Ораторское искусство \
и раскрепощение"</b>\n\n\
Место: <i>Виноградная комната</i>\n\n\
О том, как готовится к выступлению и как не боятся выступать перед публикой, \
вам расскажет Игорь Попов на мастер-классе «Ораторское искусство и раскрепощение» 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_igor button

        # ws_fr_comeback button
        elif call.data == 'ws_fr_comeback':
            buttons = types.InlineKeyboardMarkup()
            ws_friday = types.InlineKeyboardButton(text='Пятница', \
                                                callback_data='ws_friday')
            ws_saturday = types.InlineKeyboardButton(text='Суббота', \
                                                callback_data='ws_saturday')
            buttons.add(ws_friday)
            buttons.add(ws_saturday)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_fr_comeback button

        # ws_fr_descr_comeback button
        elif call.data == 'ws_fr_descr_comeback':
            buttons = types.InlineKeyboardMarkup()
            ws_fr_michael = types.InlineKeyboardButton(text='Кофе брейк с Михаилом Нокарашвили', \
                                                callback_data='ws_fr_michael')
            ws_fr_maxim = types.InlineKeyboardButton(text='Сила и продуктивность \
домашних групп', \
                                                callback_data='ws_fr_maxim')
            ws_fr_roman = types.InlineKeyboardButton(text='Как не состариться в ожидании перемен?', \
                                                callback_data='ws_fr_roman')
            ws_fr_eugene = types.InlineKeyboardButton(text='Подростковое \
служение – конвейер пробуждения', \
                                                callback_data='ws_fr_eugene')
            ws_fr_igor = types.InlineKeyboardButton(text='Ораторское искусство и раскрепощение', \
                                                callback_data='ws_fr_igor')
            ws_fr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_fr_comeback')
            buttons.add(ws_fr_michael)
            buttons.add(ws_fr_maxim)
            buttons.add(ws_fr_roman)
            buttons.add(ws_fr_eugene)
            buttons.add(ws_fr_igor)
            buttons.add(ws_fr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>✏️ Мастер-классы => Пятница</b>', \
                                parse_mode='HTML', \
                                reply_markup=buttons)
        # ws_fr_descr_comeback button

        # ws_saturday button
        elif call.data == 'ws_saturday':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_аlexey = types.InlineKeyboardButton(text='Финансовая грамотность', \
                                                callback_data='ws_sat_аlexey')
            ws_sat_oksana = types.InlineKeyboardButton(text='Как начать пророчествовать?', \
                                                callback_data='ws_sat_oksana')
            ws_sat_yaroslav = types.InlineKeyboardButton(text='Предпринимательство в \
молодом возрасте', \
                                                callback_data='ws_sat_yaroslav')
            ws_sat_julia = types.InlineKeyboardButton(text='Между нами девочками', \
                                                callback_data='ws_sat_julia')
            ws_sat_denis = types.InlineKeyboardButton(text='Как же мне жениться', \
                                                callback_data='ws_sat_denis')
            ws_sat_igor = types.InlineKeyboardButton(text='Ораторское искусство \
и раскрепощение', \
                                                callback_data='ws_sat_igor')
            ws_sat_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_comeback')
            buttons.add(ws_sat_аlexey)
            buttons.add(ws_sat_oksana)
            buttons.add(ws_sat_yaroslav)
            buttons.add(ws_sat_julia)
            buttons.add(ws_sat_denis)
            buttons.add(ws_sat_igor)
            buttons.add(ws_sat_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text='<b>✏️ Мастер-классы => Суббота</b>', \
                                parse_mode='HTML', \
                                reply_markup=buttons)
        # ws_saturday button

        # ws_sat_аlexey button
        elif call.data == 'ws_sat_аlexey':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Финансовая \
грамотность"</b>\n\n\
Место: <i>Кафе</i>\n\n\
Баталов Алексей расскажет о том, как эффективно распоряжаться теми деньгами, которые уже у \
тебя есть, чтобы они умножались и отвечали на твои потребности 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_аlexey button

        # ws_sat_oksana button
        elif call.data == 'ws_sat_oksana':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Как начать \
пророчествовать?"</b>\n\n\
Место: <i>Большой зал (перед сценой)</i>\n\n\
Как стать проводников Божьего слова, начать слышать Его и делиться этим с другими? Ответы \
на эти и другие вопросы вы узнаете на мастер - классе Оксаны Тарановой \
"Как начать пророчествовать?" 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_oksana button

        # ws_sat_yaroslav button
        elif call.data == 'ws_sat_yaroslav':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Предпринимательство в \
молодом возрасте"</b>\n\n\
Место: <i>Большой зал (центр)</i>\n\n\
Ярослав Муромцев расскажет почему же не страшно начинать свое дело в 17 и почему \
стоит это делать. Также вы сможете задать ему свои вопросы 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_yaroslav button

        # ws_sat_julia button
        elif call.data == 'ws_sat_julia':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Между нами девочками"</b>\n\n\
Место: <i>Гостевая комната</i>\n\n\
У каждой девушки есть секретики, которые поймем только мы-девушки. Нам так необходима \
помощь и советы в некоторых вопросах и моментах, которые сложно пройти. \
В том числе и вопрос отношений с сильным представителями планеты. Команд жен и невест \
будет искренне делиться своими ошибками, переживаниями и Божьими ответами в их жизни 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_julia button

        # ws_sat_denis button
        elif call.data == 'ws_sat_denis':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Как же мне жениться \
или мужской разговор"</b>\n\n\
Место: <i>Большой зал (задние ряды)</i>\n\n\
Опытный семейный консультант и человек, помогший построить качественные отношения многих \
пар с юмором расскажет о том, как сделать один их самых важных выборов в жизни: брак, \
ответит на актуальные вопросы, даст духовно-практичный взгляд 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_denis button

        # ws_sat_igor button
        elif call.data == 'ws_sat_igor':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_descr_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_descr_comeback')
            buttons.add(ws_sat_descr_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота => "Ораторское искусство \
и раскрепощение"</b>\n\n\
Место: <i>Виноградная комната</i>\n\n\
О том, как готовится к выступлению и как не боятся выступать перед публикой, \
вам расскажет Игорь Попов на мастер-классе «Ораторское искусство и раскрепощение» 😉', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_igor button

        # ws_sat_comeback button
        elif call.data == 'ws_sat_comeback':
            buttons = types.InlineKeyboardMarkup()
            ws_friday = types.InlineKeyboardButton(text='Пятница', \
                                                callback_data='ws_friday')
            ws_saturday = types.InlineKeyboardButton(text='Суббота', \
                                                callback_data='ws_saturday')
            buttons.add(ws_friday)
            buttons.add(ws_saturday)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_comeback button

        # ws_sat_descr_comeback button
        elif call.data == 'ws_sat_descr_comeback':
            buttons = types.InlineKeyboardMarkup()
            ws_sat_аlexey = types.InlineKeyboardButton(text='Финансовая грамотность', \
                                                callback_data='ws_sat_аlexey')
            ws_sat_oksana = types.InlineKeyboardButton(text='Как начать пророчествовать?', \
                                                callback_data='ws_sat_oksana')
            ws_sat_yaroslav = types.InlineKeyboardButton(text='Предпринимательство в \
молодом возрасте', \
                                                callback_data='ws_sat_yaroslav')
            ws_sat_julia = types.InlineKeyboardButton(text='Между нами девочкам', \
                                                callback_data='ws_sat_julia')
            ws_sat_denis = types.InlineKeyboardButton(text='Как же мне жениться', \
                                                callback_data='ws_sat_denis')
            ws_sat_igor = types.InlineKeyboardButton(text='Ораторское искусство \
и раскрепощение', \
                                                callback_data='ws_sat_igor')
            ws_sat_comeback = types.InlineKeyboardButton(text='👈 Назад', \
                                                callback_data='ws_sat_comeback')
            buttons.add(ws_sat_аlexey)
            buttons.add(ws_sat_oksana)
            buttons.add(ws_sat_yaroslav)
            buttons.add(ws_sat_julia)
            buttons.add(ws_sat_denis)
            buttons.add(ws_sat_igor)
            buttons.add(ws_sat_comeback)

            bot.edit_message_text(chat_id=call.message.chat.id, \
                            message_id=call.message.message_id, \
                            text='<b>✏️ Мастер-классы => Суббота</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # ws_sat_descr_comeback button

### Callback query handler ###



# Create the timetable line
def timetable():
    return '''\r
<b>Четверг:</b>
    <b>15:00</b>  -  📌 РЕГИСТРАЦИЯ
    <b>18:00</b>  -  💣 ОТКРЫТИЕ

<b>Пятница:</b>
    <b>09:00</b>  -  🙏 МОЛИТВА
    <b>10:00</b>  -  🎤 БОЛЬШОЕ ТОК-ШОУ
    <b>12:30</b>  -  ✏️ МАСТЕР-КЛАССЫ
    <b>13:30</b>  -  🎈 ОБЕД + РАЗВЛЕЧЕНИЯ
    <b>14:30</b>  -  💡 СОБРАНИЕ
    <b>16:30</b>  -  ☁️ МАЛЫЕ ГРУППЫ
    <b>18:00</b>  -  💡 СОБРАНИЕ

<b>Суббота:</b>
    <b>09:00</b>  -  🙏 МОЛИТВА
    <b>10:00</b>  -  💡 СОБРАНИЕ
    <b>12:30</b>  -  ✏️ МАСТЕР-КЛАССЫ
    <b>13:30</b>  -  🎈 ОБЕД + РАЗВЛЕЧЕНИЯ
    <b>14:30</b>  -  💡 СОБРАНИЕ
    <b>16:30</b>  -  ☁️ МАЛЫЕ ГРУППЫ
    <b>18:00</b>  -  🔥 ВЕЧЕР ХВАЛЫ

<b>Воскресение:</b>
    <b>09:00</b>  -  ☁️ МОЛИТВА
    <b>10:00</b>  -  💡 СОБРАНИЕ
    <b>14:00</b>  -  💡 СОБРАНИЕ
    <b>17:00</b>  -  ☁️ МОЛИТВА
    <b>18:00</b>  -  💡 СОБРАНИЕ
'''
# Create the timetable line

# Create the line of events which now and further
def events_now():
    utc_now = datetime.now(tzutc())
    utc_next = utc_now + timedelta(minutes=120)

    events_now = Events.query.filter(and_(Events.dateStart <= utc_now, \
                                            Events.dateFinish >= utc_now)).all()

    line = '<b>СЕЙЧАС:</b>\n\n'
    if len(events_now) > 0:
        for event in events_now:
            line = generate_line(event, line)

    if (line == '<b>СЕЙЧАС:</b>\n\n'):
        line += '    Свободное время 😉\n\n'

    events_next = Events.query.filter(and_(Events.dateStart > utc_now, \
                                            Events.dateStart < utc_next)).all()
    
    line_add = '<b>ДАЛЕЕ:</b>\n\n'
    if len(events_next) > 0:
        minimal_date = events_next[0].dateStart
        for event in events_next:
            if (event.dateStart < minimal_date):
                minimal_date = event.dateStart

        for event in events_next:
            if (event.dateStart == minimal_date):
                line_add = generate_line(event, line_add)

    if (line_add != '<b>ДАЛЕЕ:</b>\n\n'):
        line += line_add

    return line
# Create the line of events which now and further

# Generate line
def generate_line(event, line):
    tz_samara = pytz.timezone('Europe/Samara')

    if (event.name == 'РЕГИСТРАЦИЯ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  📌 {}\n\n'.format(getTime(dt), event.name)
    elif (event.name == 'МОЛИТВА'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  🙏 {}\n\n'.format(getTime(dt), event.name)
    elif (event.name == 'МАЛЫЕ ГРУППЫ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  ☁️ {}\n\n'.format(getTime(dt), event.name)
    elif (event.name == 'ВЕЧЕР ХВАЛЫ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  🔥 {}\n\n'.format(getTime(dt), event.name)
    elif (event.name == 'ОБЕД + РАЗВЛЕЧЕНИЯ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  🎈 {}\n\n'.format(getTime(dt), event.name)
    elif (event.name == 'ОТКРЫТИЕ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  💣 {}\n        проповедник: <i>"{}"</i>\n\n' \
                                                .format(getTime(dt), \
                                                        event.name, \
                                                            event.speaker)
    elif (event.name == 'СОБРАНИЕ'):
        dt = event.dateStart.astimezone(tz_samara)
        if (event.speaker is None):
            line += '    <b>{}</b>  -  💡 {}\n\n'.format(getTime(dt), \
                                                        event.name)
        else:
            line += '    <b>{}</b>  -  💡 {}\n        проповедник: <i>"{}"</i>\n\n' \
                                                    .format(getTime(dt), \
                                                            event.name, \
                                                                event.speaker)
    elif (event.name == 'БОЛЬШОЕ ТОК-ШОУ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  🎤 {}\n        тема: <i>"{}"</i>\n\n' \
                                                .format(getTime(dt), \
                                                        event.name, \
                                                            event.description)
    elif (event.name == 'МАСТЕР-КЛАСС'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  ✏️ {}\n        спикер: <i>"{}"</i>\n\
        тема: <i>"{}"</i>\n        локация: <i>"{}"</i>\n\n' \
                                                .format(getTime(dt), \
                                                        event.name, \
                                                            event.speaker, \
                                                                event.description, \
                                                                    event.location)
    elif (event.name == 'ТОК-ШОУ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  🔔 {}\n        спикер: <i>"{}"</i>\n\
        тема: <i>"{}"</i>\n        локация: <i>"{}"</i>\n\n' \
                                                .format(getTime(dt), \
                                                        event.name, \
                                                            event.speaker, \
                                                                event.description, \
                                                                    event.location)
    elif (event.name == 'ПРЕСС-КОНФЕРЕНЦИЯ'):
        dt = event.dateStart.astimezone(tz_samara)
        line += '    <b>{}</b>  -  📢 {}\n        спикер: <i>"{}"</i>\n\
        локация: <i>"{}"</i>\n\n' \
                                                .format(getTime(dt), \
                                                        event.name, \
                                                            event.speaker, \
                                                                event.location)
    return line
# Generate line

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
# Generate line hour:minute

# grp_db_processing
def grp_db_processing(message, last_name, first_name, second_name):
    is_distributed = False
    for i in small_group_temp[0]:
        if i[0] != '':
            if (i[2] == last_name and i[3] == first_name and i[4] == second_name):
                if i[0] == '2':
                    bot.send_message(message.chat.id, \
                        '<b>Вы во {} группе 😊</b>'.format(i[0]), \
                        parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, \
                        '<b>Вы в {} группе 😊</b>'.format(i[0]), \
                        parse_mode='HTML')
                try:
                    grp_map = open('static/img/map.jpg', 'rb')
                    bot.send_photo(message.chat.id, grp_map)
                    grp_map.close()
                except Exception as e:
                    pass

                return
            
            is_distributed = True

    if is_distributed:
        bot.send_message(message.chat.id, \
                        '<b>Мы еще не распределили вас в малую группу, \
либо вы неверно ввели ваши ФИО 🤔</b>\n<i>Либо мы неверно ввели ваши ФИО</i> 😉', \
                        parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, \
                        '<b>Мы еще не распределили малые группы 🤔</b>', \
                        parse_mode='HTML')
# grp_db_processing

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
# Function for changing status for user