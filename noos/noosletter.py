#-*- coding:utf-8 -*-
from .datastorage.user_db import Users

from flask import current_app, g
from flask.cli import with_appcontext



@click.command('send-mail')
@with_appcontext
def send_to_all_active(text):

    try:
        users = Users.iter_users()
        for user in users:
            email = user[1]
            print(email)

    except Exception as err:
        print (err)
