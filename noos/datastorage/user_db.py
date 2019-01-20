import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

import click
from flask import current_app, g
from flask.cli import with_appcontext


from uuid import uuid4
def uuid():
    return uuid4().hex




SCHEMA = """
DROP TABLE IF EXISTS user;

CREATE TABLE user (
  uuid TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  pseudo TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  active INTEGER NOT NULL,
  creation_time DATETIME
);
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['USER_DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        # g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_user_db():
    db = get_db()
    db.executescript(SCHEMA)


@click.command('init-sql')
@with_appcontext
def init_db_command():
    init_user_db()
    click.echo('Initialized the database.')


@click.command('init-users')
@with_appcontext
def init_users():
    click.echo("adding 'noos' user")
    init_user_db()
    uid = Users.add_user("ynnk@noos", 'nnk', 'secure', active=True)
    uid = Users.add_user("2@noos", 'k', 'secure', active=False)
    uid = Users.add_user("who@noos", 'noos', 'secure', active=True)
    Users.activate("2@noos")
    assert (uid is not None)


@click.command('db-stats')
@with_appcontext
def db_stats():
    click.echo("db has %s users" % Users.get_user_count() )

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * from user LIMIT 10;")
    rows = cursor.fetchall()
    cursor.close()

    for r in rows:
        print(r)

    print(Users.get_by_email('ynnk@noos'))




class User(object):

    def __init__(self, uuid, email, username, password=None, active=False, creation_time=None):

        self.uuid = uuid
        self.email = email
        self.username = username
        self.password = password
        self.active = active
        self.creation_time = creation_time

        self._verified = False

    @staticmethod
    def create(email, pseudo, password):
        return Users.add_user(uuid, email, pseudo, password, False)

    def change_password(self, password):
        hash_password = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(change_user_password_SQL, (hash_password, self.email))
        r = cursor.rowcount
        db.commit()
        cursor.close()

        self.password = hash_password
        self._verified = True
        return r == 1

    def verify_password(self, password, hashed=True):
        if hashed:
            self._verified = self.password is not None and self.password == password
        else:
            self._verified = check_password_hash(self.password, password)
        return self._verified

    def get_id(self):
        return self.uuid

    def is_authenticated(self):
        return self._verified

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def as_dict(self):
        return {'username': self.username,
                'email': self.email,
                'active': self.active,
                'uuid' : self.uuid
                }


add_user_SQL = "INSERT INTO user(uuid, email, pseudo, password, active, creation_time ) VALUES (?,?,?,?,?, date('now'))"
get_user_by_uuid_SQL = "SELECT uuid, email, pseudo, password, active, creation_time FROM user WHERE uuid=?"
get_user_by_email_SQL = "SELECT uuid, email, pseudo, password, active, creation_time FROM user WHERE email=?"
get_user_by_username_SQL = "SELECT uuid, email, pseudo, password, active, creation_time FROM user WHERE pseudo=?"
activate_user_SQL = "UPDATE user SET active=1 WHERE email=?"
change_user_password_SQL = "UPDATE user set password=? WHERE email=?"
count_users_SQL = "SELECT COUNT(email) FROM user"


class Users(object):

    @staticmethod
    def get_user_count():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(count_users_SQL)
        count = cursor.fetchone()[0]
        return count

    @staticmethod
    def add_user(email, username, password, active=False):
        current_app.logger.info("adding user : %s %s" %(email, username))
        pwd = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(add_user_SQL, [uuid(), email, username, pwd, active])
        last_id = cursor.lastrowid
        db.commit()
        cursor.close()
        current_app.logger.info('user added %s %s'%(username, last_id))
        return last_id

    @staticmethod
    def get_one_by(method, arg):

        sql = None
        if method == 'email':
            sql = get_user_by_email_SQL
        elif method == 'username':
            sql = get_user_by_username_SQL
        elif method == 'uuid':
            sql = get_user_by_uuid_SQL

        if None not in (method, sql, arg):
            db = get_db()
            cursor = db.cursor()
            cursor.execute(sql, [arg])
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return User(*row)

        return None

    @staticmethod
    def get_by_email(email):
        return Users.get_one_by('email', email)

    @staticmethod
    def get_by_username(username):
        user = Users.get_one_by('username', username)
        return user

    @staticmethod
    def get_by_uuid(uuid):
        return Users.get_one_by('uuid', uuid)

    @staticmethod
    def has_email(email):
        try:
            if email is not None:
                u = Users.get_by_email(email)
                return True
        except:
            return False

    @staticmethod
    def has_pseudo(username):
        try:
            if username is not None:
                u = Users.get_by_username(username)
                return u is not None
        except:
            return False

    @staticmethod
    def authenticate(email, password, hashed=False):
        """ get user by username, verify password if any given
            return User if username psswd match
        """
        user = Users.get_by_email(email)

        if user and user.is_active():
            user.verify_password(password, hashed=hashed)
            current_app.logger.info("authenticate: %s %s %s" % (email, user.username, user.is_authenticated()))
            return user

        return None

    @staticmethod
    def activate(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(activate_user_SQL, (email,))
        r = cursor.rowcount
        db.commit()
        cursor.close()
        print("activate:", email, r)
        return True

    @staticmethod
    def change_password(email, password):
        u = Users.get_by_email(email)
        return u.change_password(password)


