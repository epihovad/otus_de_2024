import re
import sqlparse


# чистка запроса
def clear_query(query):

    # чистим от однострочных комментов
    query = sqlparse.format(query, strip_comments=True).strip()
    # убираем переносы строк
    query = query.replace('\n', ' ')
    # убираем повторяющиеся пробелы
    query = re.sub(' +', ' ', query)

    return query
