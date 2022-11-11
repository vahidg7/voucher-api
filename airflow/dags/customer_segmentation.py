import datetime
import os

from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from etl_utils import (
    clean_directory,
    convert_to_csv,
    download_data,
    send_csv_to_db,
)

from airflow import DAG

DOWNLOAD_URL = "https://github.com/vahidg7/voucher-api/raw/master/data.parquet.gzip"
DAG_ID = "customer_segmentation"
POSTGRES_CONN_ID = "app_db"

DATA_PATH = "/opt/airflow/data"
DATA_FILE_NAME = "voucher"
PARQUET_FILE_PATH = os.path.join(DATA_PATH, f"{DATA_FILE_NAME}.parquet.gzip")
CSV_FILE_PATH = os.path.join(DATA_PATH, f"{DATA_FILE_NAME}.csv")


with DAG(
    dag_id=DAG_ID,
    start_date=datetime.datetime(2022, 11, 11),
    schedule="@once",
    max_active_runs=1,
    catchup=False,
) as dag:

    clean_task = PythonOperator(
        task_id="clean_task",
        dag=dag,
        python_callable=clean_directory,
        op_args=[DATA_PATH],
    )

    extract_task = PythonOperator(
        task_id="extract_task",
        dag=dag,
        python_callable=download_data,
        op_args=[DOWNLOAD_URL, PARQUET_FILE_PATH],
    )

    transform_task = PythonOperator(
        task_id="transform_task",
        dag=dag,
        python_callable=convert_to_csv,
        op_args=[PARQUET_FILE_PATH, CSV_FILE_PATH],
    )

    load_task = PythonOperator(
        task_id="load_task",
        dag=dag,
        python_callable=send_csv_to_db,
        op_args=[POSTGRES_CONN_ID, CSV_FILE_PATH],
    )

    calculate_segmentation = PostgresOperator(
        task_id="calculate_segmentation",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="sql/segmentation.sql",
    )

    extract_task >> transform_task >> load_task >> calculate_segmentation
