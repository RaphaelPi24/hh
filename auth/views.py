from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user

from auth.forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')
bp.secret_key = 'secret'


@bp.route('/login', methods=['GET'])
def login_get():
    return render_template('views/login.html')


@bp.route('/login', methods=['POST'])
def login_post():
    form = LoginForm(request.form)
    form.validate()
    if form.errors:
        flash(form.errors)
        return redirect(url_for('auth.login_get'))

    login_user(form.user)
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
    form = RegistrationForm(request.form)
    form.validate_and_write_in_bd()
    if form.errors:
        flash(form.errors)
        return redirect(url_for('auth.register_get'))
    login_user(form.user)
    return redirect(url_for('get_base'))


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('views/profile.html')
