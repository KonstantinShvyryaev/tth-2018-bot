### Configurations ###
class Configuration(object):
    ### Flask-SQLAlchemy ###
    #DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'your_uri'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Flask-Admin ###
    SECRET_KEY = 'your_secret_key'

    ### Flask-Security ###
    SECURITY_PASSWORD_SALT = 'your_salt'
    SECURITY_PASSWORD_HASH = 'sha512_crypt'

# Telegram API #
token = 'your_token'

# Google API #
CREDENTIALS_FILE = 'your_credentials_file'
spreadsheet_id = 'your_spreadsheet_id'