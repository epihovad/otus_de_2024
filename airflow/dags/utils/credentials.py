from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# путь к корню проекта
sys.path.append(str(Path(__file__).parents[2]))

# загружаем переменные окружения из файла .env в текущей директории
load_dotenv()

# ################################ WMS (PostgreSQL)
ENV_WMS = {
    'host': os.getenv('ENV_WMS_HOST'),
    'port': os.getenv('ENV_WMS_PORT'),
    'user': os.getenv('ENV_WMS_USER'),
    'password': os.getenv('ENV_WMS_PASSWORD'),
    'database': os.getenv('ENV_WMS_DATABASE'),
}

# ################################ BI (ClickHouse)
ENV_BI = {
    'host': os.getenv('ENV_BI_HOST'),
    'port_tcp': os.getenv('ENV_BI_PORT_TCP'),
    'port_http': os.getenv('ENV_BI_PORT_HTTP'),
    'user': os.getenv('ENV_BI_USER'),
    'password': os.getenv('ENV_BI_PASSWORD'),
    'database': os.getenv('ENV_BI_DATABASE'),
}
