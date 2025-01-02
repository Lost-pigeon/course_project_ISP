import json
import os

from flask import Flask, render_template, session, current_app

from database.select import select_dict, select_list
from database.sql_provider import SQLProvider
from query.route import blueprint_query
from auth.route import blueprint_auth
from report.route import blueprint_report
from order.route import blueprint_order

app = Flask(__name__)

with open("../data/db_config.json") as f:
    app.config['db_config'] = json.load(f)
with open('../data/db_access.json') as f:
    app.config['db_access'] = json.load(f)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_key')

app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_report, url_prefix='/report')
app.register_blueprint(blueprint_order, url_prefix='/order')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@app.route("/")
def main_menu():
    user_group = session.get('user_group')
    print(user_group)
    if user_group == 'client' or user_group is None:
        if user_group == 'client':
            user_id = session.get('user_id')
            _sql = provider.get('name_client.sql', Contract_num=user_id)
            name_client = select_list(current_app.config['db_config'], _sql)
            first_name_client, last_name_client, balance = name_client[0][0]
            _sql = provider.get('list_connect_service.sql', user_id=user_id)
            items_con = select_dict(current_app.config['db_config'], _sql)
            message = f'Здравствуйте, {last_name_client} {first_name_client}!'

            return render_template("main_menu_client.html", message=message, balance=balance, items_con=items_con)

        else:
            message = "Вы не авторизованы"
        return render_template('main_menu_client.html', message=message)

    if user_group:
        message = f"Вы зашли как: {user_group}"

    else:
        message = "Вы не авторизованы"
    return render_template('main_menu.html', message=message)


@app.route('/exit')
def exit_func():
    session.clear()
    message = "Вы не авторизованны"
    return render_template('exit.html', message=message)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
