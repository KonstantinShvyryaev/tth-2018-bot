from flask import render_template, request
from app import app, db, bot
from models import *

from telebot import types
from config import token, web_site

from datetime import datetime
from sqlalchemy import and_

from app import service
from config import spreadsheet_id
import time

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
    bot.process_new_updates([types.Update.de_json(request.stream.read().decode('utf-8'))])
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
    markup.row('В какой я группе?')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Отправить опрос')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Отправить опрос')
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
    markup.row('В какой я группе?')
    if (user.status == 'User'):
        pass
    elif (user.status == 'Admin'):
        markup.row('Отправить мем', 'Отправить сообщение')
        markup.row('Отправить опрос')
        markup.row('Изменить статус пользователя')
    elif (user.status == 'Questions'):
        markup.row('Отправить опрос')
    elif (user.status == 'Memeses'):
        markup.row('Отправить мем')
    elif (user.status == 'VIP'):
        markup.row('Отправить сообщение')

    bot.send_message(message.chat.id, 'Клавиатура включена', reply_markup=markup)
### /start_keyboard command ###

### /stop_keyboard command ###
@bot.message_handler(commands=['stop_keyboard'])
def stop_keyboard(message):
    remove_markup = types.ReplyKeyboardRemove()

    bot.send_message(message.chat.id, 'Клавиатура отключена', reply_markup=remove_markup)
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
    # Расписание

    # Что сейчас?
    elif (message.text == 'Что сейчас?'):
        bot.send_message(message.chat.id, events_now(), parse_mode='HTML')
    # Что сейчас?

    # Регистрация
    elif (message.text == 'Регистрация'):
        buttons = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text='Зарегистрироваться', \
                                                url='https://goo.gl/ae2xLR')
        buttons.add(url_button)

        bot.send_message(message.chat.id, \
                '<b>Для регистрации вам необходимо перейти поссылке 👇</b>', \
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
за расселение и он вам ответит 😉</b>''', \
                        parse_mode='HTML', \
                        reply_markup=buttons)
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
    # Где покушать?

    # Кто на TTH?
    elif (message.text == 'Кто на TTH?'):
        global conf_info_temp
        cur_time = time.time()
        diff = cur_time - conf_info_temp[1]

        if diff > 10:
            conf_info_temp[1] = time.time()

            range_ = 'A2:AD2'
            request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                        range=range_, \
                                                        majorDimension='ROWS')
            response = request.execute()
            conf_info = response['values'][0]
            conf_info_temp[0] = conf_info

        users = Users.query.all()
        bot.send_message(message.chat.id, \
                        '<b>💡 На конференции 💡</b>\n🚗 Приехали: {}\n\
🖐️ Младше 14 лет: {}\n🤞 От 14 до 18 лет: {}\n👌 Старше 18 лет: {}\n\
👱 Парней: {}\n👩 Девушек: {}'.format(conf_info_temp[0][1], \
                                conf_info_temp[0][25], \
                                conf_info_temp[0][26], \
                                conf_info_temp[0][27], \
                                conf_info_temp[0][28], \
                                conf_info_temp[0][29]), \
                        parse_mode='HTML')
    # Кто на TTH?

    # В какой я группе?
    elif (message.text == 'В какой я группе?'):
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

            is_distributed = False
            for i in small_group_temp[0]:
                if i[0] != '':
                    if (i[2] == full_name[0] and i[3] == full_name[1] and i[4] == full_name[2]):
                        bot.send_message(message.chat.id, \
                                '<b>Вы в {} группе 😊</b>'.format(i[0]), \
                                parse_mode='HTML')
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

        if diff > 100:
            small_group_temp[1] = time.time()

            range_ = 'C3:G1000'
            request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, \
                                                        range=range_, \
                                                        majorDimension='ROWS')
            response = request.execute()
            if 'values' in response:
                small_group_val = response['values']
                small_group_temp[0] = small_group_val

        msg = bot.send_message(message.chat.id, \
                            '<b>Введите фамилию, имя, отчество через пробел 😌</b>\n\
<i>(Пример: Мемесов Угандий Наклсович)</i>', \
                            parse_mode='HTML')
        bot.register_next_step_handler(msg, grp_processing)
    # В какой я группе?

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
                                parse_mode='HTML', \
                                reply_markup=buttons)
            except Exception as e:
                bot.send_message(message.chat.id, 'oooops')
        # message_processing

        user = Users.query.filter_by(chat_id=message.from_user.id).first()
        if(user.status == 'Admin' or user.status == 'VIP'):
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
                test_splt = message.text.split()
                url = test_splt[0]

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
                            '<b>Мем отправлен 😊</b>', 
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
                                text="<b>Сообщение отправлено 😊</b>", \
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
                bot.send_message(user.chat_id, \
                            '<b>Мы подготовили для вас опрос 😊\n\
Скорее переходите отвечать 👇</b>', \
                            parse_mode='HTML', \
                            reply_markup=buttons)
        # inter_post button

        # inter_break button
        elif call.data == 'inter_break':
            bot.delete_message(call.message.chat.id, call.message.message_id - 1)
            bot.edit_message_text(chat_id=call.message.chat.id, \
                                message_id=call.message.message_id, \
                                text="<b>В другой раз 😉</b>", \
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

# Create the line of events which now
def events_now():
    now = datetime.now()
    events = Events.query.filter(and_(Events.dateStart <= now, Events.dateFinish >= now))

    line = '<b>Сейчас:</b>\n'

    for i in events:
        if (i.name == 'ЗАВТРАК'):
            line += '    <b>{}</b>  -  ☕ {} <i>({})</i>\n' \
                .format(getTime(i.dateStart), i.name, i.speaker)
        elif (i.name == 'МОЛИТВА'):
            line += '    <b>{}</b>  -  🙏 {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'СОБРАНИЕ' or i.name == 'СОБРАНИЕ (Подростки)'):
            if i.description is None:
                line += '    <b>{}</b>  -  🔥 {}  ( <b>Проповедник:</b> <i>{}</i> )\n' \
                            .format(getTime(i.dateStart), \
                                    i.name, \
                                    i.speaker)
            else:
                line += '    <b>{}</b>  -  🔥 {}  ( <b>Проповедник:</b> <i>{}</i> \
<b>; тема:</b> <i>"{}"</i> )\n'.format(getTime(i.dateStart), \
                                        i.name, \
                                        i.speaker, \
                                        i.description)
        elif (i.name == 'МАСТЕР КЛАСС'):
            line += '    <b>{}</b>  -  ✏️ {}  ( <b>Спикер:</b> <i>{}</i> \
<b>; тема:</b> <i>"{}"</i> <b>; локация:</b> <i>{}</i> )\n' \
                .format(getTime(i.dateStart), \
                        i.name, i.speaker, i.description, i.location)
        elif (i.name == 'МАЛЫЕ ГРУППЫ'):
            line += '    <b>{}</b>  -  ☁️ {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'ОТКРЫТИЕ'):
            line += '    <b>{}</b>  -  💣 {}\n'.format(getTime(i.dateStart), i.name)
        elif (i.name == 'ВЕЧЕР ХВАЛЫ'):
            line += '    <b>{}</b>  -  🔥 {}\n'.format(getTime(i.dateStart), i.name)

    if (line == '<b>Сейчас:</b>\n'):
        line += '    Свободное время 😉\n'

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