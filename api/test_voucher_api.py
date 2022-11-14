import pytest
from starlette.testclient import TestClient

from database import db, voucher_segmentation_table
from main import app

client = TestClient(app)

VALID_CUSTOMER_OBJECT = {
    "customer_id": 123,
    "country_code": "Peru",
    "total_orders": 3,
    "last_order_ts": "2018-05-03 00:00:00",
    "first_order_ts": "2017-05-03 00:00:00",
    "segment_name": "frequent_segment",
}


@pytest.fixture(autouse=False)
def clean_up():
    with db.connect() as conn:
        delete_statement = voucher_segmentation_table.delete()
        conn.execute(delete_statement)


@pytest.fixture
def populate_voucher_values():
    with db.connect() as conn:
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="frequent_segment", segment_type="0-4", voucher_amount=1200
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="frequent_segment", segment_type="5-13", voucher_amount=1500
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="frequent_segment", segment_type="14-37", voucher_amount=1800
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="recency_segment", segment_type="30-60", voucher_amount=1900
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="recency_segment", segment_type="61-90", voucher_amount=1700
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="recency_segment", segment_type="91-120", voucher_amount=1500
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="recency_segment", segment_type="121-180", voucher_amount=1300
        )
        conn.execute(insert_statement)
        insert_statement = voucher_segmentation_table.insert().values(
            segment_name="recency_segment", segment_type="180+", voucher_amount=1000
        )
        conn.execute(insert_statement)


def test_get_voucher_before_pipeline(clean_up):
    response = client.post("/segmentation-voucher/", json=VALID_CUSTOMER_OBJECT)
    assert response.status_code == 400
    assert response.json() == {"detail": "invalid input"}


def test_get_voucher_successful(populate_voucher_values):
    response = client.post("/segmentation-voucher/", json=VALID_CUSTOMER_OBJECT)
    assert response.status_code == 200
    assert response.json() == {"voucher_amount": 1200}
