import streamlit as st
import cv2
import pandas as pd
import numpy as np

from helpers import receipt_to_df


st.title("Spending Tracker")
message = "Upload your receipts. Ensure that the receipt contains the date and items, no subtotals"
receipts = st.file_uploader(message, ["png", "jpg"], accept_multiple_files=True)
if receipts is not None:
    for receipt in receipts:
        file_bytes = np.frombuffer(receipt.read(), np.uint8)
        receipt = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        df = receipt_to_df(receipt)
        df.to_csv('receipt_data.csv', mode='a', index=False, header=False)

mm_month = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

mm_sum = {}
with open("receipt_data.csv", "r") as f:
    for line in f:
        date, name, price = line.split(",")
        price = float(price)

        mm, dd, yy = date.split("/")
        mm = int(mm)
        if mm not in mm_sum:
            mm_sum[mm] = price
        else:
            mm_sum[mm] += price

month_totals = pd.DataFrame({
    "Month": mm_sum.keys(),
    "Spending": [mm_sum[mm] for mm in sorted(mm_sum.keys())]
})

month_totals = month_totals.set_index("Month")
# Bar chart with months as x-axis labels
st.bar_chart(
    data=month_totals,
    x_label = "Month",
    y_label = "Spending ($)",
    color="#118C4F"
)

