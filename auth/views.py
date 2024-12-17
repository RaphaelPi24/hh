from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user
from peewee import IntegrityError
from pydantic import ValidationError

from auth.validation import Register, Login, bcrypt
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
bp.secret_key = 'secret'


@bp.route('/login', methods=['GET'])
def login_get():
    return render_template('views/login.html')


@bp.route('/login', methods=['POST'])
def login_post():
    form = request.form.to_dict(flat=True)
    try:
        user_data = Login.model_validate(form)
    except ValidationError as e:
        flash(f'ошибка! {e}')
        return redirect(url_for('auth.login_get'))

    login_user(User.get(User.name == user_data.name))
    flash('Вы вошли в систему')
    return render_template('views/base_content.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_get'))


@bp.route('/register', methods=['GET'])
def register_get():
    return render_template('views/register.html')


@bp.route('/register', methods=['POST'])
def register_post():
    form = request.form.to_dict(flat=True)

    try:
        user_data = Register.model_validate(form)
    except ValidationError as e:
        flash(f'ошибка {e}')
        return redirect(url_for('auth.register_get'))

    hasched_password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    try:
        User.create(
            name=user_data.name,
            email=user_data.email,
            password=hasched_password
        )
    except IntegrityError as e:
        flash(f'ошибка {e}')
        return redirect(url_for('auth.register_get'))

    login_user(User.get(User.name == user_data.name))
    return redirect(url_for('get_base'))

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('views/profile.html')