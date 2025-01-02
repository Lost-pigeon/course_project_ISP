# функции связанные с выполнением запроса в базу данных

from database.DBcm import DBContextManager
from pymysql.err import OperationalError

def select_list(db_config: dict, _sql: str):
    result = ()
    schema = []
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError("Cursor not created")
        try:
            cursor.execute(_sql)
            # Если запрос возвращает данные, сохраняем их
            result = cursor.fetchall() if cursor.description else []
            schema = [item[0] for item in cursor.description] if cursor.description else []
        except OperationalError as error:
            print("Error:", error)
            return result, schema
        else:
            print("Cursor no errors")

    return result, schema


def select_dict(db_config: dict, _sql: str):
    result, schema = select_list(db_config, _sql)
    result_dict = []
    for item in result:
        result_dict.append(dict(zip(schema, item)))
    # print(result_dict)
    return result_dict

def procedure(db_config: dict, _sql: str):
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError("Cursor not created")
        try:
            cursor.execute(_sql)
        except OperationalError as error:
            # Извлечение сообщения об ошибке
            error_message = str(error)
            # Убираем скобки и цифры кода ошибки
            clean_message = error_message.split(', ')[-1].strip("()'")
            print("Error:", clean_message)
            return clean_message
        else:
            print("Cursor no errors")

    return ''