# tth-2018-bot
## Для запуска бота вам *необходимо*:
* Создать бота в telegram при помощи [BotFather](https://telegram.me/BotFather)
* Создать приложение на платформе [Heroku](https://www.heroku.com/)
* Подключить базу данных и получить **URI** базы данных
* Создать сервисный аккаунт через **Google Developers Console** по [инструкции](https://habrahabr.ru/post/305378/), получить **json** файл и добавить его в **корень** проекта
* Создать **таблицу** в Google и включить в ней доступ по ссылке
* Теперь в файле проекта config.py **изменить** переменные:
    * SQLALCHEMY_DATABASE_URI = 'URI_вашей_базы_данных'
    * SECRET_KEY = 'любая_последовательность_символов_придуманная_вами'
    * SECURITY_PASSWORD_SALT = 'любая_последовательность_символов_придуманная_вами'
    * token = 'токен_вашего_бота'
    * web_site = 'https://название_вашего_приложения.herokuapp.com/'
    * CREDENTIALS_FILE = 'имя_вашего_сервисного_ключа.json'
    * preadsheet_id = 'ID_вашей_таблицы'
* После чего необходимо создать вируальное окружение и произвести **миграцию**:
    * pip install virtualenv
    * virtualenv venv
    * source venv/bin/activate (Linux)
    * pip install -r requirements.txt
    * python manage.py db init
    * python manage.py db migrate
    * python manage.py db upgrate
* Для корректной работы метода register_next_step_handler() **необходимо** прописать команду:
    * heroku config:set WEB_CONCURRENCY=1
    * [Подробности](https://devcenter.heroku.com/articles/python-gunicorn)

## Админка
### Для подключения админки вам *необходимо*:
* Войти в heroku bash (*команда:* heroku bash)
* Запустить интерпритатор python и выполнить следующие команды:
    * # from app import db
    * # from admin import user_datastore
    * # user_datastore.create_user(email='ваш емейл', password='ваш пароль')
    * # db.session.commit()
    * # from models import User
    * # user = User.query.first()
    * # user_datastore.create_role(name='admin', description='administrator')
    * # db.session.commit()
    * # from models import Role
    * # role = Role.query.first()
    * # user_datastore.add_role_to_user(user, role)
    * # db.session.commit()
    * # exit()
    * exit
* После чего 