from dataclasses import dataclass
from database.select import select_dict

@dataclass
class ProductInfoResponse:
    result: tuple
    error_message: str
    status: bool

def model(db_config, user_data, sql_provider):
    error_message = ''
    _sql = ''
    if 'username' in user_data:
        _sql = sql_provider.get('auth2.sql', login = user_data['username'], password = user_data['password'])
        print(_sql)

    result = select_dict(db_config, _sql)
    print(result)
    if result:
        return ProductInfoResponse(result, error_message=error_message, status=True)
    return ProductInfoResponse(result, error_message=error_message, status=False)
