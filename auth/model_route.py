from dataclasses import dataclass
from database.select import select_list


@dataclass
class ProductInfoResponse:
    result: tuple
    error_message: str
    status: bool


def model_route(db_config, user_input_data, sql_provider_):
    error_message = ''
    _sql = sql_provider_.get('auth.sql', login=user_input_data[0], password=user_input_data[1])
    print("sql=", _sql)
    try:
        result, schema = select_list(db_config, _sql)
        return ProductInfoResponse(result, error_message=error_message, status=True)
    except TypeError:
        error_message = 'type_error'
        return ProductInfoResponse((), error_message=error_message, status=False)
