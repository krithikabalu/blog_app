import functools

from flask import Blueprint, request, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from flaskr.db import get_db

blue_print = Blueprint('auth', __name__, url_prefix='/auth')


@blue_print.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        db = get_db()
        error = None

        if not user_name:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif db.execute('SELECT id FROM user WHERE username = ?', (user_name,)).fetchone() is not None:
            error = "User {} is already registered ". format(user_name)

        if error is None:
            db.execute('INSERT into user(username, password) VALUES (?, ?)', (user_name, generate_password_hash(password)))
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')


@blue_print.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user_name = request.form["user_name"]
        password = request.form["password"]
        db = get_db()
        error = None

        user = db.execute("SELECT * from user WHERE username = ?", (user_name,)).fetchone()

        if user is None:
            error = "Incorrect username"
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@blue_print.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * from user where id = ?', (user_id,)).fetchone()


@blue_print.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
