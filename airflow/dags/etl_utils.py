import glob
import logging
import os

import pandas as pd
import requests
from airflow.hooks.postgres_hook import PostgresHook

log = logging.getLogger(__name__)


def clean_directory(data_path: str) -> None:
    """
    removes all items in a directory
    """

    log.info(f"removing items from {data_path}")

    files = glob.glob(os.path.join(data_path, "*"))
    for f in files:
        os.remove(f)

    log.info(f"successfully removed items from {data_path}")


def download_data(download_url: str, parquet_file_destination: str) -> None:
    """
    downloads parquet file to a directory
    """

    log.info(f"downloading from {download_url}")

    response = requests.get(download_url)
    with open(parquet_file_destination, "wb") as f:
        f.write(response.content)

    log.info(
        f"successfully downloaded and saved parquet file to {parquet_file_destination}"
    )


def convert_to_csv(parquet_file_path: str, csv_file_destination: str) -> None:
    """
    convert parquet file to CSV and saves it in a directory
    """

    df = pd.read_parquet(parquet_file_path)
    df.to_csv(csv_file_destination, index=False)

    log.info(
        f"successfully converted parquet file and saved csv file to {csv_file_destination}"
    )


def send_csv_to_db(postgres_conn_id: str, csv_file_path: str) -> None:
    """
    create required tables and store CSV file data in DB table
    """

    hook = PostgresHook(postgres_conn_id)

    with open("dags/sql/create_db_table.sql", "r") as sql_file:
        create_table_sql_commands = sql_file.read()
    hook.run(create_table_sql_commands, autocommit=True)

    log.info("successfully created required tables to load data.")

    with open("dags/sql/copy_csv_to_table.sql", "r") as sql_file:
        copy_csv_to_table_command = sql_file.read()
    hook.copy_expert(copy_csv_to_table_command, csv_file_path)

    log.info("successfully imported data to table.")
