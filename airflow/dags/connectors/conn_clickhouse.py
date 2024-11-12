import os
import sys

# путь к корню проекта
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))))

from clickhouse_driver import Client as CH_client


class ClickHouse:

    # метод инициализации класса
    def __init__(
        self,
        host=None,  # имя сервера БД
        port_tcp=None,  # порт TCP
        port_http=None,  # порт HTTP
        user=None,  # учетка
        password=None,  # пароль
        database=None,  # имя БД
    ):
        self.host = host
        self.port_tcp = port_tcp
        self.port_http = port_http
        self.user = user
        self.password = password
        self.database = database
        self.conn = self._connect()

    # обработка ошибки при срабатывание исключения типа Exception
    def parse_exception(self, err):

        error = ''

        try:
            error = str(err.args[0])
        except Exception:
            pass

        return error

    # коннектимся к БД
    def _connect(self):

        conn = None

        try:
            conn = CH_client(
                host=self.host,
                port=self.port_tcp,
                user=self.user,
                password=self.password,
                database=self.database,
            )
        except Exception as e:
            err = 'Ошибка подключения к ClickHouse: {}'.format(self.parse_exception(e))
            raise ValueError(err)

        return conn

    # закрываем соединений
    def close(self):
        self.conn.disconnect()