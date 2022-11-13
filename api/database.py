import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
BASE = declarative_base()


db_string = f"postgresql://{DB_USER}:{DB_PASS}@app_db:5432/{DB_NAME}"
db = create_engine(db_string)
Session = sessionmaker(db)
session = Session()


class VoucherSegmentation(BASE):
    __tablename__ = "voucher_segmentation"

    id = Column(Integer, primary_key=True)
    segment_name = Column(String)
    segment_type = Column(String)
    voucher_amount = Column(Integer)
