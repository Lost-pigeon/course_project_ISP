import os
from flask import render_template, Blueprint, current_app, request, flash, url_for, redirect
from database.sql_provider import SQLProvider
from report.model_route import model_route
from access import group_required

blueprint_report = Blueprint('report_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

REPORT_PAGES = {
    1: ('report_form.html', 'Отчет об услугах за заданный год и месяц'),
    2: ('report_form.html', 'Посмотреть отчет об услугах за заданный год и месяц'),
    3: ('report_form.html', 'Отчет об изменениях баланса клиентов'),
    4: ('report_form.html', 'Посмотреть отчет об изменениях баланса клиентов')
}

REPORT_NAMES = {
    1: 'Отчет о услугах за год и месяц',
    2: lambda year, month: f'Результаты отчета об услугах за {year} год и {month} месяц',
    3: 'Отчет об изменениях баланса клиентов',
    4: lambda year, month: f'Результаты об изменениях баланса клиентов за {year} год и {month} месяц'
}


# функция для проверки корректности ввода данных
def is_valid_input(user_data):
    return user_data.get('reportYear') and user_data.get('reportMonth') and \
        user_data['reportYear'].isdigit() and user_data['reportMonth'].isdigit()


# функция для получения названия отчета
def get_report_name(report_id, user_data=None):
    report_name = REPORT_NAMES.get(report_id)

    if callable(report_name):  # проверяем, является ли значение функцией
        return report_name(user_data['reportYear'], user_data['reportMonth'])

    return report_name  # если это строка, просто возвращаем ее


@blueprint_report.route('/')
@group_required
def report_menu():
    return render_template('report_menu.html')


@blueprint_report.route('/report_menu_create')
@group_required
def report_menu_create():
    reports = [
        {'id': 1, 'name': 'Отчет об услугах за заданный год и месяц'},
        {'id': 3, 'name': 'Отчет об изменениях баланса клиентов'},
    ]
    return render_template('report_menu_work.html', reports=reports)


@blueprint_report.route('/report_menu_viewing')
@group_required
def report_menu_viewing():
    reports = [
        {'id': 2, 'name': 'Посмотреть отчет об услугах за заданный год и месяц'},
        {'id': 4, 'name': 'Посмотреть отчет об изменениях баланса клиентов'},
    ]
    return render_template('report_menu_work.html', reports=reports)


@blueprint_report.route('/<int:report_id>', methods=['GET'])
@group_required
def report_handler(report_id):
    page, report_name = REPORT_PAGES.get(report_id, (None, None))
    if page:
        return render_template(page, report_name=report_name)
    return render_template('error_page.html', error_title='Ошибка', message_error='Неверный идентификатор запроса.')


@blueprint_report.route('/<int:report_id>', methods=['POST'])
@group_required
def query_result_handler(report_id):
    user_data = request.form

    if not is_valid_input(user_data):
        flash("Некорректный ввод. Введите числовое значение.", category='error')
        return redirect(url_for('report_bp.report_menu'))

    res_info = model_route(current_app.config['db_config'], user_data, provider, report_id)

    report_name = get_report_name(report_id, user_data)

    if report_id in [1, 3]:
        if not res_info.error_message:
            return render_template('report_success.html')
        flash(res_info.error_message, category='error')
        return redirect(url_for('report_bp.report_menu'))

    if report_id in [2, 4]:
        if res_info.status and res_info.result:
            template = 'dynamic_report.html' if report_id == 2 else 'dynamic_report_2.html'
            return render_template(template, prod_title=report_name, products=res_info.result, report_name=report_name)
        flash("Проверьте введенные данные", category='error')
        return redirect(url_for('report_bp.report_menu'))

    return render_template('error_page.html', error_title='Ошибка', message_error='Неверный идентификатор запроса.')
