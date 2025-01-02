import os

import requests
from flask import Blueprint, session, redirect, url_for, request, render_template, flash, current_app
from auth.model_route import model_route
from typing import List

from database.sql_provider import SQLProvider

blueprint_auth = Blueprint('auth_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_auth.route('/', methods=['GET'])
def auth_index():
    return render_template('login.html')


@blueprint_auth.route('/login', methods=['POST'])
def auth_login():
    is_external_user = 'is_external_user' in request.form
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if is_external_user:
        api_url = "http://127.0.0.1:5004/api/auth"
        payload = {'username': username, 'password': password}
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            user_data = response.json()
            print(user_data)
            session['user_id'] = user_data['id']
            session['user_group'] = user_data['role']
            return redirect(url_for('main_menu'))
        else:
            flash('Неправильный логин или пароль')
            return render_template('login.html', error_message="Неверный логин или пароль.")
    else:
        user_data: List[str] = [username, password]
        user = model_route(current_app.config['db_config'], user_data, provider)
        print(user.status)
        if user.status and user.result != ():
            session['user_id'] = user.result[0][0]
            session['user_group'] = user.result[0][1]
            print('Успешная аутентификация')
            return redirect(url_for('main_menu'))
        else:
            flash('Неправильный логин или пароль')
            return redirect(url_for('auth_hp.auth_index'))
