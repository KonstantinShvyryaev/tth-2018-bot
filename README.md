# tth-2018-bot
[Ссылка на проект](https://telegram.me/tth_2018_bot)
## 1. Создание бота
* Перейдите по ссылке [BotFather](https://telegram.me/BotFather)
* Вызовите команду **/newbot** и следуйте инструкциям
* В файле **config.py** измените значение переменной **token** на ваше значение
* Вызовите команду **/setcommands** и создайте три команды
    > /start_keyboard - Включить клавиатуру
    > /stop_keyboard - Выключить клавиатуру
    > /git - Для разработчиков
## 2. Деплой
* Зарегистрируйтесь на платформе [Heroku](https://www.heroku.com/)
* Скачайте [CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) для вашей системы
* Введите логин и пароль в **CLI**
    > heroku login
* Создайте приложение
    > git init

    > git commit -m "first commit"

    > heroku create name_of_your_app --region eu
* Задеплойте приложение
    > git push heroku master
* Для корректной работы метода register_next_step_handler() **необходимо** прописать команду
    > heroku config:set WEB_CONCURRENCY=1
## 3. Подключение базы данных
* Зайдите в раздел **Data** и создайте **postgresql** базу данных / подключите к своему приложению
* В разделе your_db -> Settings -> View Credentials... вы найдете **URI**
* Скопируйте **URI** и добавьте его в переменную **SQLALCHEMY_DATABASE_URI**, которая находится в файле **confug.py**
## 4. Миграция базы данных
* Создайте **виртуальное окружение** в корне проекта и установите нужные пакеты
    > virtualenv venv 

    > source venv/bin/activate (for Linux)

    > pip install -r requirements.txt
* Произведите **миграцию**
    > python manage.py db init

    > python manage.py db migrate

    > python manage.py db upgrade
## 5. Админка
* Раскомментируйте строчку **47** в файле **app.py**
* Измените значение переменной **SECRET_KEY** в файле **config.py** на любую последовательность символов
## 6. Security
* Раскомментируйте строки **26**, **33**, **33** в файле **admin.py** и закомментируйте **27** строку
* Создайте пользователя для админки
    > heroku run bash

    > python

    > from app import db

    > from admin import user_datastore

    > user_datastore.create_user(email='ваш емейл', password='ваш пароль')

    > db.session.commit()

    > from models import User

    > user = User.query.first()

    > user_datastore.create_role(name='admin', description='administrator')

    > db.session.commit()

    > from models import Role

    > role = Role.query.first()

    > user_datastore.add_role_to_user(user, role)

    > db.session.commit()

    > exit()

    > exit
* Измените значение переменной **SECURITY_PASSWORD_SALT** в файле **config.py** на любую последовательность символов
## 7. Google sheets
* Создайте сервисный аккаунт через **Google Developers Console** по [инструкции](https://habrahabr.ru/post/305378/), получите **json** файл и добавьте его в **корень** проекта
* Создайте **таблицу** в Google и добавить сервисному аккаунту доступ на чтение
* Измените значение переменной **CREDENTIALS_FILE** в файле **config.py** на название вашего json файла
* Измените значение переменной **spreadsheet_id** в файле **config.py** на значение **id** вашей таблицы
* Просмотрите в файле **view.py** строчки 127:145(Начальная инициализация), 201:304(Команды, в которых используется обращение к таблице); вам придется менять значения в этих методах, так как они настроены под нашу таблицу
* Воспользуйтесь справочником по [Google Sheets API](https://developers.google.com/sheets/api/reference/rest/)