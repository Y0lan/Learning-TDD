import os
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'password'
USERNAME = 'admin'
PASSWORD = 'admin'
DATABASE_PATH = os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False

# initialisation
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

import models


@app.route('/')
def index():
    articles = db.session.query(models.Flaskr)
    return render_template('index.html', articles=articles)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('logged out')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_articles():
    if not session.get('logged_in'):
        abort(401)
    article = models.Flaskr(request.form['titre'], request.form['contenu'])
    db.session.add(article)
    db.session.commit()
    flash('Succès!')
    return redirect(url_for('index'))


@app.route('/delete/<id>', methods=['GET'])
def delete_entry(id):
    """Delete post from database"""
    result = {'status': 0, 'message': 'Erreur'}
    try:
        db.session.query(models.Flaskr).filter_by(id=id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Article Supprime"}
        flash('Article supprime')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)


if __name__ == '__main__':
    app.run()
