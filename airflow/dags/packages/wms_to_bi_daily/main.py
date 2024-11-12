from pathlib import Path
import os
import sys

# путь к директории dags
project_path = Path(__file__).parents[2]
sys.path.append(str(project_path))

import requests

from utils.credentials import ENV_WMS, ENV_BI
import utils.extract_utils as extract
from utils.common import get_package
import utils.utils as utils
from connectors import conn_postgresql
from connectors import conn_clickhouse

PACKAGE = get_package(__file__)


# универсальный экспорт данных
def _extract(model):

    # переменные для экспорта
    dump, fl, writer, row_count = extract.get_csv_vars_for_export(model, PACKAGE)

    # полное имя таблицы на источнике
    table = ('{}.{}.{}').format(
        model['source']['database'],
        model['source']['schema'],
        model['source']['table'],
    )

    # формируем запрос
    query = ('select {} from {}').format(
        ', '.join(model['source']['headers']),
        table,
    )

    # очищаем запрос
    query = utils.clear_query(query)

    # подключаемся к БД WMS
    wms = conn_postgresql.PostgreSQL(
        host=ENV_WMS['host'],
        port=ENV_WMS['port'],
        user=ENV_WMS['user'],
        password=ENV_WMS['password'],
        database=ENV_WMS['database'],
    )

    # запускаем запрос
    cursor = wms.conn.cursor()

    try:
        # Выполнение запроса
        cursor.execute(query)
        # Построчное чтение данных и запись в CSV
        for row in cursor:
            writer.writerow(row)
            row_count += 1
    except Exception as e:
        err = 'Ошибка выполнения запроса к БД: {}'.format(wms.parse_exception(e))
        raise ValueError(err)
    finally:
        cursor.close()

    fl.close()

    if not row_count:
        err = 'данные отсутствуют'
        raise ValueError(err)
    
    info = 'статистика загрузки:'
    info += '\n - загружено строк в «{}.csv»: {};'.format(model['name'], row_count)
    print(info)


# универсальная загрузка данных
def _load(model):

    dump = str(Path(PACKAGE['TMP_PATH']) / (model['name'] + '.csv'))

    # полное имя таблицы на приёмнике
    table = model['target']['database'] + '.' + model['target']['table']

    # проверка наличия CSV
    if not os.path.exists(dump):
        err = 'файл «{}» не найден'.format(os.path.basename(dump))
        raise ValueError(err)

    # количество строк в CSV
    cnt_source = extract.get_csv_row_count(dump)
    if not cnt_source:
        err = f'данные в «{dump}» отсутствуют'
        raise ValueError(err)
    
    # подключаемся к БД ClickHouse
    bi = conn_clickhouse.ClickHouse(
        host=ENV_BI['host'],
        port_tcp=ENV_BI['port_tcp'],
        port_http=ENV_BI['port_http'],
        user=ENV_BI['user'],
        password=ENV_BI['password'],
        database=ENV_BI['database'],
    )

    try:
        # очистка таблицы
        bi.conn.execute(f'truncate table {table}')

        # грузим данные через HTTP
        url = 'http://{}:{}'.format(ENV_BI['host'], ENV_BI['port_http'])
        with open(dump, 'rb') as f:
            response = requests.post(
                url,
                params={'query': f'insert into {table} format csv'},
                data=f,
                headers={'Content-Type': 'text/csv'}
            )
        
        # проверяем статус запроса
        if response.status_code != 200:
            err = 'ошибка загрузки данных в ClickHouse'
            raise ValueError(err)
        
        # проверяем кол-во записей после INSERT
        cnt_target = bi.conn.execute(f'select count(1) from {table}')
        cnt_target = int(cnt_target[0][0])
        if cnt_target == 0:
            err = 'не удалось загрузить данные в ClickHouse'
            raise ValueError(err)

    except Exception as e:
        err = 'ошибка загрузки данных в ClickHouse: {}'.format(bi.parse_exception(e))
        raise ValueError(err)
    finally:
        bi.close()

    info = 'статистика загрузки:'
    info += '\n - загружено строк в ClickHouse: {};'.format(cnt_target)
    print(info)


# Регионы
def regions():
    model = extract._model('regions', PACKAGE)
    _extract(model)
    _load(model)


# Склады
def warehouses():
    model = extract._model('warehouses', PACKAGE)
    _extract(model)
    _load(model)


# Товары
def products():
    model = extract._model('products', PACKAGE)
    _extract(model)
    _load(model)


if __name__ == '__main__':
    regions()
    pass