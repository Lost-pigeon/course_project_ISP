from dataclasses import dataclass
from database.select import procedure, select_list
from access import group_required
import pymysql


@dataclass
class ProductInfoResponse:
    result: tuple
    error_message: str
    status: bool


# обработка ошибок SQL
def handle_sql_error(e, error_type):
    error_messages = {
        pymysql.err.IntegrityError: "IntegrityError: Отчет уже существует или нарушение уникальности.",
        pymysql.err.DataError: "DataError: Ошибка данных или формат неправильный.",
        TypeError: "type_error"
    }
    error_message = error_messages.get(type(e), str(e))
    print(f"{error_type}: {error_message}")
    return ProductInfoResponse((), error_message=error_message, status=False)


# выполнение SQL-запроса и обработка возможных ошибок
def execute_sql_query(db_config, sql_query):
    try:
        return procedure(db_config, sql_query)
    except (pymysql.err.IntegrityError, pymysql.err.DataError) as e:
        return handle_sql_error(e, "SQL Error")


# выполнение SQL-запроса для выборки данных и обработка ошибок
def execute_select_query(db_config, sql_query):
    try:
        result, schema = select_list(db_config, sql_query)
        return ProductInfoResponse(result, error_message='', status=True)
    except TypeError as e:
        return handle_sql_error(e, "Select Error")


@group_required
def model_route(db_config, user_input_data, sql_provider, report_id):
    print("report_id = ", report_id)

    report_queries = {
        1: 'procedure.sql',
        3: 'procedure_2.sql',
        2: 'report_output.sql',
        4: 'report_output_2.sql'
    }

    if report_id in report_queries:
        _sql = sql_provider.get(report_queries[report_id], reportYear=user_input_data.get('reportYear'),
                                reportMonth=user_input_data.get('reportMonth'))
        print("sql=", _sql)

        # для отчетов 1 и 3 выполняем процедуру
        if report_id in [1, 3]:
            error_message = execute_sql_query(db_config, _sql)
            return ProductInfoResponse((), error_message=error_message, status=True)

        # для отчетов 2 и 4 выполняем запросы SELECT
        else:
            return execute_select_query(db_config, _sql)

    else:
        raise ValueError('Неверный идентификатор запроса.')
