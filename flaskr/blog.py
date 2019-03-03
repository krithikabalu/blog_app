from http import HTTPStatus

from flask import Blueprint, render_template, request, flash, g, url_for
from flask_restplus import abort
from werkzeug.utils import redirect

from flaskr.auth import login_required
from flaskr.db import get_db

blue_print = Blueprint('blog', __name__)


@blue_print.route('/')
def index():
    db = get_db()
    posts = db.execute('SELECT p.id, title, body, created, author_id, username '
                       'FROM post p JOIN user u ON p.author_id = u.id '
                       'ORDER BY created DESC').fetchall()
    return render_template('blog/index.html', posts=posts)


@blue_print.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post(title, body, author_id) VALUES (?,?,?)', (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute('SELECT p.id, title, body, created, author_id, username FROM'
                            'post p JOIN user u on p.author_id = u.id'
                            'WHERE p.id = ?',(id,)).fetchone()
    if post is None:
        abort(HTTPStatus.NOT_FOUND, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user["id"]:
        abort(HTTPStatus.FORBIDDEN)

    return post


@blue_print.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@blue_print.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))