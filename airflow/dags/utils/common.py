"""
Файл c общими/полезными настройками и переменными, подключаемый из пользовательского кода.
"""

from pathlib import Path
import os

PROJECT = {}
PROJECT['ROOT_PATH'] = str(Path(__file__).parents[1])
PROJECT['TMP_PATH'] = str(Path(__file__).parents[1] / 'tmp')

# Создание каталога для размещения временных файлов
os.makedirs(PROJECT['TMP_PATH'], exist_ok=True)
# os.chmod(PROJECT['TMP_PATH'], 0o755)


def get_package(caller_file):

    package = {}
    package['NAME'] = str(Path(caller_file).parent.stem)
    package['PATH'] = str(Path(caller_file).parent)
    package['TMP_PATH'] = str(Path(PROJECT['TMP_PATH']) / package['NAME'])
    package['SQL_PATH'] = str(Path(caller_file) / 'sql')

    # создаём директорию, если её нет
    os.makedirs(package['TMP_PATH'], exist_ok=True)
    # os.chmod(package['TMP_PATH'], 0o755)

    return package
