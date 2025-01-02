import datetime

import os
from flask import render_template, Blueprint, current_app, request, session, url_for
from werkzeug.utils import redirect

from access import group_required
from database.DBcm import DBContextManager
from database.select import select_dict
from database.sql_provider import SQLProvider

blueprint_order = Blueprint('order_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET', 'POST'])
@group_required
def order_index():
    if request.method == 'GET':
        user_id = session.get('user_id')
        _sql = provider.get('list_unconnected_service.sql', user_id=user_id)
        print("_sql = ", _sql)
        items = select_dict(current_app.config['db_config'], _sql)
        basket_items = session.get('basket', {})
        print("items = ", items)
        _sql = provider.get('list_connect_service.sql', user_id=user_id)
        items_con = select_dict(current_app.config['db_config'], _sql)
        return render_template("basket_list.html", items=items, basket=basket_items, items_con=items_con)
    else:
        action = request.form.get('action')
        id_service = request.form.get('id_service')
        if action == 'Подключить':
            status_service = 1
            add_to_basket(id_service, status_service)
            return redirect(url_for("order_bp.order_index"))
        elif action == 'Отключить':
            status_service = 0
            add_to_basket(id_service, status_service)
            return redirect(url_for("order_bp.order_index"))
        elif action == 'Удалить':
            remove_from_basket(id_service)
    return redirect(url_for('order_bp.order_index'))


def add_to_basket(id_service, status_service):
    current_basket = session.get('basket', {})
    print('current_basket=', current_basket)
    print("id_service = ", id_service)
    if id_service in current_basket:
        return redirect(url_for('order_bp.order_index'))
    else:
        _sql = provider.get('added_item.sql', id_service=id_service)
        print("_sql = ", _sql)
        item = select_dict(current_app.config['db_config'], _sql)[0]
        print("item = ", item)
        current_basket[id_service] = {
            'Name_service': item['Name_service'],
            'Price_service': item['Price_service'],
            'status_service': status_service}
        session['basket'] = current_basket
        print(session.get('basket', {}))
        session.permanent = True


def remove_from_basket(id_service):
    current_basket = session.get('basket', {})
    if id_service in current_basket:
        del current_basket[id_service]
        session['basket'] = current_basket
        session.permanent = True


@blueprint_order.route('/clear_basket')
@group_required
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
        return redirect(url_for('order_bp.order_index'))
    else:
        return redirect(url_for('order_bp.order_index'))


@blueprint_order.route('/save_basket')
@group_required
def save_basket():
    if  'basket' in session:
        user_id = session.get('user_id')
        if not user_id:
            return "User not authenticated", 401

        current_basket = session.get('basket', {})
        print(current_basket)

        order_date = datetime.datetime.now().strftime('%Y-%m-%d')

        _sql_insert_basket = provider.get('saving_receipt.sql', user_id=user_id, order_date=order_date)

        try:
            with DBContextManager(current_app.config['db_config']) as cursor:
                print("_sql_insert_basket = ", _sql_insert_basket)
                cursor.execute(_sql_insert_basket)

                id_basket = cursor.lastrowid
                if not id_basket:
                    raise ValueError("Basket ID not found")
                print("id_basket = ", id_basket)

                for id_service, details in current_basket.items():
                    _sql_insert_item = provider.get(
                        'saving_list.sql',
                        basket_id=id_basket,
                        service_id=id_service,
                        status_service=details['status_service']
                    )
                    print(_sql_insert_item)
                    cursor.execute(_sql_insert_item)

            session.pop('basket', None)
            return render_template('save_basket_message.html', order_id=id_basket)

        except Exception as e:
            print("Transaction failed: ", str(e))
            return "An error occurred while saving the basket.", 500
    else:
        return redirect(url_for('order_bp.order_index'))