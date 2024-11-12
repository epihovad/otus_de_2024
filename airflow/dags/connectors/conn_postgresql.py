import os
import sys

# путь к корню проекта
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))))

import psycopg2


class PostgreSQL:

    # метод инициализации класса
    def __init__(
        self,
        host=None,  # имя сервера БД
        port=None,
        user=None,  # учетка
        password=None,  # пароль
        database=None,  # имя БД
    ):
        self.host = host
        self.port = port
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
            None

        return error

    # коннектимся к БД
    def _connect(self):

        conn = None

        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            conn.autocommit = True
        except Exception as e:
            err = 'Ошибка подключения к БД:\n{}'.format(self.parse_exception(e))
            raise ValueError(err)

        return conn

    # закрываем соединений
    def close(self):
        self.conn.close()
