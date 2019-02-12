from flask import Blueprint, render_template

from flaskr.db import get_db

blue_print = Blueprint('blog', __name__)


@blue_print.route('/')
def index():
    db = get_db()
    posts = db.execute('SELECT p.id, title, body, created, author_id, username'
                       'FROM post p JOIN user u ON p.author_id = u.id'
                       'ORDER BY created DESC').fetchall()
    return render_template('blog/index.html', posts=posts)

