from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='wms_to_bi_daily',
    default_args=default_args,
    start_date=datetime(2024, 11, 1),
    schedule_interval='10 21 * * *',  # каждый день в 00:10 (UTC+3)
    catchup=False,
    tags=['wms', 'daily'],
) as dag:

    from packages.wms_to_bi_daily import main as pkg

    regions = PythonOperator(task_id='regions', python_callable=pkg.regions)
    warehouses = PythonOperator(task_id='warehouses', python_callable=pkg.warehouses)
    products = PythonOperator(task_id='products', python_callable=pkg.products)

regions >> warehouses >> products