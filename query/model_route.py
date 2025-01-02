from dataclasses import dataclass
from database.select import select_list
from access import group_required


@dataclass
class ProductInfoResponse:
    result: tuple
    error_message: str
    status: bool


@group_required
def model_route(db_config, user_input_data, sql_provider, query_id):
    error_message = ''

    try:
        if query_id == 1:
            _sql = sql_provider.get('changing_balance.sql', prod_category=user_input_data['prod_category'])
        elif query_id == 2:
            _sql = sql_provider.get('changing_price_service.sql', prod_category=user_input_data['prod_category'])
        else:
            raise ValueError('Неверный идентификатор запроса.')

        print("SQL запрос:", _sql)

        # Выполнение запроса к базе данных
        result, schema = select_list(db_config, _sql)
        return ProductInfoResponse(result=result, error_message=error_message, status=True)

    except ValueError as e:
        return ProductInfoResponse((), error_message=str(e), status=False)
    except TypeError:
        return ProductInfoResponse((), error_message='type_error', status=False)
    except Exception as e:
        return ProductInfoResponse((), error_message='unknown_error: ' + str(e), status=False)