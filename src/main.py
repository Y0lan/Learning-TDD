import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify

# configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'password'
USERNAME = 'admin'
PASSWORD = 'admin'

# initialisation
main = Flask(__name__)
main.config.from_object(__name__)


# creation de la bdd
def init_db():
    with main.app_context():
        db = get_db()
        with main.open_resource('sql/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# connection à la bdd
def connect_db():
    db = sqlite3.connect(main.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


# ouvre la connection
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# clos la connexion de la bdd
@main.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@main.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    init_db()
    main.run()
