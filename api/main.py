import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from get_voucher import get_voucher_value

TODAY_DATE = datetime.strptime(os.getenv("TODAY"), "%Y-%m-%d")


app = FastAPI()


class Customer(BaseModel):
    customer_id: int
    country_code: str
    last_order_ts: datetime
    first_order_ts: datetime
    total_orders: int
    segment_name: str


class Voucher(BaseModel):
    voucher_amount: int


@app.post("/segmentation-voucher/", response_model=Voucher)
async def create_item(customer: Customer):
    """
    endpoint to get voucher amount for a customer
    """

    segment_name = customer.segment_name
    total_orders = customer.total_orders
    date_diff_days = (TODAY_DATE - customer.last_order_ts).days

    voucher_amount = get_voucher_value(segment_name, total_orders, date_diff_days)

    # if input values are not in specified range, return 400 error code!
    if not voucher_amount:
        raise HTTPException(status_code=400, detail="invalid input")

    return Voucher(voucher_amount=voucher_amount)
