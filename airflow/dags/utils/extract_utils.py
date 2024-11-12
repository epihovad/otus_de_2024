from pathlib import Path
import os
import time
import csv
import json


# считываем json модель
def _model(model_name, package):

    model_path = str(Path(package['PATH']) / 'model' / (model_name + '.json'))

    with open(model_path, encoding='utf8') as f:
        model = json.load(f)

    return model


# model_list = {'order', 'order_geo_distr', 'order_fias_distr', 'order_line'}
def get_csv_vars_for_export(model, package):

    # путь к CSV (дампы)
    dump = str(Path(package['TMP_PATH']) / (model['name'] + '.csv'))

    # удаляем старые CSV файлы
    if os.path.isfile(dump):
        os.remove(dump)

    # создаём новые CSV файлы
    fl = open(dump, 'w', encoding='utf-8', newline='')

    # создаём writer
    writer = csv.writer(fl, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)

    # добавляем заголовки
    writer.writerow(model['source']['headers'])

    # счетчик кол-ва строк
    row_count = 0

    return dump, fl, writer, row_count


# подсчет кол-ва строк в csv
def get_csv_row_count(
    dump: str,
    delimiter: str = ',',
    quoting: int = csv.QUOTE_ALL,
    dialect: str = 'unix',
) -> int:
    with open(dump, 'r', encoding='utf-8') as fl:
        reader = csv.reader(fl, delimiter=delimiter, quoting=quoting, dialect=dialect)
        next(reader, None)  # Пропускаем заголовок
        row_count = sum(1 for _ in reader)
    return row_count


# универсальная выгрузка данных из mssql
def dwh_to_csv(
    model: dict,
    package: dict,
    logger,
    quoting: int = csv.QUOTE_MINIMAL,  # csv.QUOTE_ALL | csv.QUOTE_MINIMAL | csv.QUOTE_NONNUMERIC | csv.QUOTE_NONE
    chunk_size: int = 5000,
    processed_nulls: bool = False,
):

    sql_path = ''
    if 'query' in model['source'] and model['source']['query']:
        sql_path = os.path.join(package['SQL_PATH'], model['source']['table'] + '.sql')

    dwh = conn_greenplum.Greenplum(logger=logger)

    row_count = dwh.get_csv_from_db(
        model=model,
        dump_path=package['TMP_PATH'],
        sql_path=sql_path,
        quoting=quoting,
        chunk_size=chunk_size,
        processed_nulls=processed_nulls,
    )

    if not row_count:
        err = 'данные отсутствуют'
        logger.info(err)
        raise ValueError(err)


# универсальная выгрузка данных из mssql
def mssql_to_csv(
    cred: dict,
    model: dict,
    package: dict,
    logger,
    quoting: int = csv.QUOTE_MINIMAL,  # csv.QUOTE_ALL | csv.QUOTE_MINIMAL | csv.QUOTE_NONNUMERIC | csv.QUOTE_NONE
    chunk_size: int = 1000,
    processed_nulls: bool = False,
):

    sql_path = ''
    if 'query' in model['source'] and model['source']['query']:
        sql_path = os.path.join(package['SQL_PATH'], model['source']['table'] + '.sql')

    db = conn_mssql.MSSQL(
        host=cred['host'],
        port=cred['port'],
        user=cred['user'],
        password=cred['password'],
        database=cred['database'],
        logger=logger,
    )

    row_count = db.get_csv_from_db(
        model=model,
        dump_path=package['TMP_PATH'],
        sql_path=sql_path,
        quoting=quoting,
        chunk_size=chunk_size,
        processed_nulls=processed_nulls,
    )

    if not row_count:
        err = 'данные отсутствуют'
        logger.info(err)
        raise ValueError(err)


# универсальная выгрузка данных из mssql
def clickhouse_to_csv(cred: dict, model: dict, package: dict, logger, chunk_size: int = 5000):

    sql_path = ''
    if 'query' in model['source'] and model['source']['query']:
        sql_path = os.path.join(package['SQL_PATH'], model['source']['table'] + '.sql')

    ch = conn_clickhouse.ClickHouse(
        host=cred['host'],
        port=cred['port'],
        user=cred['user'],
        password=cred['password'],
        database=cred['database'],
        logger=logger,
    )
    row_count = ch.get_csv_from_db(model, package['TMP_PATH'], sql_path, chunk_size=chunk_size)
    if not row_count:
        err = 'данные отсутствуют'
        logger.info(err)
        raise ValueError(err)


# TODO позже переделать под протокол file:// - нужно копировать csv на сервер БД
# копрование локального CSV на файловую систему DWH
def copy_csv_to_dwh_fs(model: dict, package: dict, logger):

    # путь к csv в локальной системе
    if 'path' in model['source']:  # если модель не имеет в секции source server/database/schema
        source_path = os.path.join(package['TMP_PATH'], model['source']['path'])
    else:  # если модель заточена под забор данных из БД
        source_path = os.path.join(package['TMP_PATH'], model['source']['table'] + '.csv')

    return source_path  # target_path


# создание таблицы в DWH в raw слое
# настройки задаются в секции settings в target блоке модели
def create_raw_table(dwh, model: dict, logger):

    # имя таблицы
    _table = model['target']['schema'] + '.' + model['target']['table']

    # поля таблицы
    field_list = []
    # добавим техническое поле inserted_at
    field_list.append('"_inserted_ts" timestamptz not null default timezone(\'Europe/Moscow\'::text, now())')
    # добавляем оставшиеся поля
    for field in model['target']['settings']['filed']:
        _item = '"' + field['name'] + '" ' + field['type']
        if 'nullable' in field and field['nullable'] is False:
            _item = _item + ' not null'
        field_list.append(_item)
    _field = '\n  ' + (',\n  '.join(field_list)) + '\n'

    # настройки таблицы
    if 'with' in model['target']['settings']:
        _with = model['target']['settings']['with']
    else:
        _with = 'appendonly=true, blocksize=32768, compresstype=zstd, compresslevel=10, orientation=column'
    _with = f'\nwith ({_with})'

    # ключ дистрибуции (по-умолчанию - первое поле в таблице)
    if 'distributed_by' in model['target']['settings']:
        _distributed_by = model['target']['settings']['distributed_by']
    else:
        _distributed_by = model['target']['settings']['filed'][0]['name']
    _distributed_by = f'\ndistributed by ("{_distributed_by}")'

    # формируем запрос
    query = f'create table if not exists {_table} ({_field}){_with}{_distributed_by}'

    # выполняем запрос
    dwh.execute(query)


# загрузка данных из CSV в DWH
def load_csv_to_dwh(model: dict, dump_csv: str, logger, chunk_size: int = 10000):

    # dwh = conn_mssql.MSSQL(server='LTRUS1DWH02.MAYTEA.COM', database='DWH', logger=logger)
    # dwh.put_csv_to_dwh_bulk(model, dump_csv, chunk_size=chunk_size)

    dwh = conn_greenplum.Greenplum(logger=logger)

    # если секции settings существует
    if 'settings' in model['target']:
        # создадим таблицу в DWH в raw слое
        create_raw_table(dwh, model, logger)

    # заливаем данные в целевую таблицу
    dwh.csv_to_dwh(model, dump_csv, chunk_size=chunk_size)


def load_csv_to_clickhouse(
    cred: dict,
    model: dict,
    dump_csv: str,
    create_table: bool = True,
    truncate: bool = True,  # применять ли TRUNCATE
    partition_column: str = '',  # условие для выборки по партиции
    partition_list: list = None,  # название партиции
    logger=None,
):

    ch = conn_clickhouse.ClickHouse(
        host=cred['host'],
        port=cred['port'],
        user=cred['user'],
        password=cred['password'],
        database=cred['database'],
        logger=Logger() if logger is None else logger,
    )
    ch.put_csv_to_ch_cli(
        model=model,
        dump_csv=dump_csv,
        create_table=create_table,
        truncate=truncate,
        partition_column=partition_column,
        partition_list=partition_list,
    )
    ch.close()
