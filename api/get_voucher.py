from typing import Optional

from database import db, voucher_segmentation_table


def get_voucher_value(
    segment_name: str, total_orders: int, date_diff_days: int
) -> Optional[int]:
    """
    get voucher amount based on input segment_name and features
    voucher values are fetched from pre-calculated values in database
    """

    if segment_name == "frequent_segment":
        if 0 <= total_orders <= 4:
            segment_type = "0-4"
        elif 5 <= total_orders <= 13:
            segment_type = "5-13"
        elif 14 <= total_orders <= 37:
            segment_type = "14-37"
        else:
            return None

    elif segment_name == "recency_segment":
        if 30 <= date_diff_days <= 60:
            segment_type = "30-60"
        elif 61 <= date_diff_days <= 90:
            segment_type = "61-90"
        elif 91 <= date_diff_days <= 120:
            segment_type = "91-120"
        elif 121 <= date_diff_days <= 180:
            segment_type = "121-180"
        elif 181 <= date_diff_days:
            segment_type = "180+"
        else:
            return None

    else:
        return None

    with db.connect() as conn:
        select_statement = (
            voucher_segmentation_table.select()
            .where(
                voucher_segmentation_table.c.segment_name == segment_name,
                voucher_segmentation_table.c.segment_type == segment_type,
            )
            .limit(1)
        )
        result_set = conn.execute(select_statement)
    voucher_amount = [item.voucher_amount for item in result_set]

    return voucher_amount[0] if len(voucher_amount) > 0 else None
