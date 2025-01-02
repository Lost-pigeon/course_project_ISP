from functools import wraps
from flask import session, request, redirect, url_for, current_app, flash


def login_required(func):
    @wraps(func)
    def wrapper(*argc, **kwargs):
        if 'user_group' in session:
            return func(*argc, **kwargs)
        else:
            return redirect(url_for('main_menu'))

    return wrapper


def group_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_group' not in session:
            flash('У вас нет доступа к данному разделу', category='error')
            return redirect(request.referrer or url_for('query_bp.query_menu'))

        user_role = session.get('user_group')
        user_request = request.endpoint
        user_bp = user_request.split('.')[0]
        access = current_app.config['db_access']

        # Проверка доступа пользователя к указанному блоку
        if user_role in access and user_bp in access[user_role]:
            resource_id_key = f"{user_bp.split('_')[0]}_id"  # Автоматически определяем ключ ('query_id', 'report_id', и т.д.)
            if resource_id_key in kwargs:
                resource_id = kwargs[resource_id_key]
                allowed_resources = access[user_role][user_bp]
                if allowed_resources != ["*"] and resource_id not in allowed_resources:
                    flash('У вас нет доступа к данному разделу', category='error')
                    return redirect(request.referrer or url_for(f'{user_bp}.{user_bp.split("_")[0]}_menu'))
            return func(*args, **kwargs)

        # Обработка случаев, когда доступ отсутствует
        flash('У вас нет доступа к данному разделу', category='error')
        return redirect(request.referrer or url_for(f'{user_bp}.{user_bp.split("_")[0]}_menu'))

    return wrapper
