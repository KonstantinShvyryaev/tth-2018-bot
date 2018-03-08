from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_security import SQLAlchemyUserDatastore, Security, current_user, utils

from wtforms.fields import PasswordField

from app import app, db
from models import *

### Admin ###
class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

class AdminView(AdminMixin, ModelView):
    pass

class HomeAdminView(AdminMixin, AdminIndexView):
    pass

#admin = Admin(app, 'TTH helper', url='/', index_view=HomeAdminView(name='Home'))
admin = Admin(app)
admin.add_view(ModelView(Events, db.session))
admin.add_view(ModelView(Users, db.session))

### Flask-Security ###
#user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)