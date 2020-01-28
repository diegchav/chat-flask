from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .forms import LoginForm, RegisterForm
from .models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('chat.index'))
        else:
            flash('Invalid username or password', 'danger')

    if g.user:
        return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password != confirm_password:
            flash('Passwords don\'t match', 'danger')
        else:
            existing_user = User.query.filter_by(username=username).first()
            # Don't let the user know that this username already exists to prevent user enumeration
            if existing_user is None:
                new_user = User(username=username, password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()

            flash('Account successfully created', 'success')

            return redirect(url_for('auth.login'))

    if g.user:
        return redirect(url_for('chat.index'))

    return render_template('auth/register.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))