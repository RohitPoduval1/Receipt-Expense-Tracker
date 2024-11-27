import streamlit as st
import cv2
import pandas as pd
import numpy as np
import statistics
from collections import Counter

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

# Data Processing
mm_sum = {}
name_occur = {}
with open("receipt_data.csv", "r") as f:
    for line in f:
        date, name, price = line.split(",")
        price = float(price)

        if name not in name_occur:
            name_occur[name] = 1
        else:
            name_occur[name] += 1

        mm, dd, yy = date.split("/")
        mm = int(mm)
        if mm not in mm_sum:
            mm_sum[mm] = price
        else:
            mm_sum[mm] += price

name_occur = sorted(name_occur.items(), key=lambda x:x[1])

mm_month = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


# At a Glance
max_month = mm_month[max(mm_sum, key=mm_sum.get)]
st.write(f"Max Spending Month: {max_month}")
st.write(f"Mean Monthly Spending: ${statistics.mean(mm_sum.values())}")
st.write("Top 3 Most Purchased Items:")
top_3_md = f"""
1. {name_occur[-1][0]} {"were" if name_occur[-1][0].endswith("S") else "was"} bought {name_occur[-1][1]} times
2. {name_occur[-2][0]} {"were" if name_occur[-2][0].endswith("S") else "was"} bought {name_occur[-2][1]} times
3. {name_occur[-3][0]} {"were" if name_occur[-3][0].endswith("S") else "was"} bought {name_occur[-3][1]} times
"""
st.markdown(top_3_md)

# Graphing the Data
month_totals = pd.DataFrame({
    "Month": mm_sum.keys(),
    "Spending": mm_sum.values()
})
month_totals = month_totals.set_index("Month")
st.bar_chart(
    data=month_totals,
    x_label = "Month",
    y_label = "Spending ($)"
)
