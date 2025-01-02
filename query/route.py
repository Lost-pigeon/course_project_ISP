import os
from flask import render_template, Blueprint, current_app, request, flash, redirect, url_for
from database.sql_provider import SQLProvider
from query.model_route import model_route
from access import group_required

blueprint_query = Blueprint('query_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_query.route('/')
@group_required
def query_menu():
    queries = [
        {'id': 1, 'name': 'Запрос об изменении баланса заданного клиента'},
        {'id': 2, 'name': 'Запрос об изменении цен заданной услуги'}
    ]
    return render_template('query_menu.html', queries=queries)


@blueprint_query.route('/<int:query_id>', methods=['GET'])
@group_required
def query_handler(query_id):
    query_pages = {
        1: 'input_changing_balance.html',
        2: 'input_changing_price_services.html'
    }

    # Проверка существования страницы для запроса
    page = query_pages.get(query_id)
    if page:
        return render_template(page)
    return render_template('error_page.html', error_title='Ошибка', message_error='Неверный идентификатор запроса.')


@blueprint_query.route('/<int:query_id>', methods=['POST'])
def query_result_handler(query_id):
    try:
        user_data = request.form

        # Проверка корректности введенных данных
        if not user_data.get('prod_category') or not user_data['prod_category'].isdigit():
            raise ValueError("Некорректный ввод. Введите числовое значение.")

        # Выполнение модели маршрута для получения данных
        res_info = model_route(current_app.config['db_config'], user_data, provider, query_id)

        # Проверка успешности результата
        if res_info.status and res_info.result:
            templates = {
                1: {'title': 'Запрос об изменении баланса {} клиента', 'template': 'dynamic_1.html'},
                2: {'title': 'Запрос об изменении цен {} услуги', 'template': 'dynamic_2.html'}
            }
            template_info = templates.get(query_id)
            if template_info:
                formatted_title = template_info['title'].format(user_data['prod_category'])
                return render_template(template_info['template'], prod_title=formatted_title, products=res_info.result)

        # Сообщение о некорректных параметрах
        flash('Необработанный контент. Проверьте введенные параметры.', category='error')
        return redirect(url_for('query_bp.query_menu'))

    except ValueError:
        flash('Ошибка в данных. Пожалуйста, проверьте ввод.', category='error')
        return redirect(url_for('query_bp.query_menu'))
    except Exception as e:
        flash('Внутренняя ошибка сервера. Попробуйте снова позже.', category='error')
        return redirect(url_for('query_bp.query_menu'))
