import os

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASS}@app_db:5432/{DB_NAME}"


db = create_engine(DB_CONNECTION_STRING)
meta = MetaData(db)

voucher_segmentation_table = Table(
    "voucher_segmentation",
    meta,
    Column("id", Integer),
    Column("segment_name", String),
    Column("segment_type", String),
    Column("voucher_amount", Integer),
)

if not voucher_segmentation_table.exists():
    voucher_segmentation_table.create()
