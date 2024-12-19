import statistics
import streamlit as st
import cv2
import pandas as pd
import numpy as np

from helpers import receipt_to_df

st.title("Spending Tracker")
message = "Upload your receipts. Ensure that the receipt contains the date and items, no subtotals"
receipts = st.file_uploader(message, ["heic", "jpg", "jpeg", "png"], accept_multiple_files=True)
if receipts is not None:
    for receipt in receipts:
        # Convert file upload into opencv readable format
        file_bytes = np.frombuffer(receipt.read(), np.uint8)
        receipt = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        
        df = receipt_to_df(receipt)  # extract relevant information from receipt
        df.to_csv('receipt_data.csv', mode='a', index=False, header=False)  # add to receipt_data.csv


# Data Processing
mm_sum = {}      # the total amount spent for each month
item_occur = {}  # item name and the number of times it was purchased

total_items = 0
healthy_count = 0
unhealthy_count = 0
unknown_count = 0
with open(file="receipt_data.csv", mode="r", encoding="UTF-8") as f:
    for line in f:
        date, item, price, classification = line.split(",")
        price = float(price)
        classification = classification.strip()

        # Counting the number of Healthy and Unhealthy items
        # Unknown items do not factor in
        if classification == "Healthy":
            healthy_count += 1
        elif classification == "Unhealthy":
            unhealthy_count += 1
        else:
            unknown_count += 1
        total_items += 1

        if item not in item_occur:
            item_occur[item] = 1
        else:
            item_occur[item] += 1

        mm, dd, yy = date.split("/")
        mm = int(mm)
        if mm not in mm_sum:
            mm_sum[mm] = price
        else:
            mm_sum[mm] += price

item_occur = sorted(item_occur.items(), key=lambda x:x[1])

mm_month = {
    1: "January ❄️",
    2: "February ❤️",
    3: "March 🍀",
    4: "April 🌷",
    5: "May 🌸",
    6: "June ☀️",
    7: "July 🎆",
    8: "August 🌻",
    9: "September 🍂",
    10: "October 🎃",
    11: "November 🦃",
    12: "December 🎄"
}


# At a Glance
max_spending_month = mm_month[max(mm_sum, key=mm_sum.get)]
st.write(f"Max Spending Month: {max_spending_month}")
st.write(f"Mean Monthly Spending: ${statistics.mean(mm_sum.values()):.2f}")

st.write(f"{int(100 * (healthy_count / (total_items - unknown_count)))}% of your purchases were healthy and {int(100 * (unhealthy_count / (total_items - unknown_count)))}% were unhealthy")
st.write("(Note: Numbers may not be 100% accurate and are only meant to give a rough idea)")

st.write("Top 3 Most Purchased Items:")
top_3_md = f"""
1. {item_occur[-1][0]} {"were" if item_occur[-1][0].endswith("S") else "was"} bought {item_occur[-1][1]} times
2. {item_occur[-2][0]} {"were" if item_occur[-2][0].endswith("S") else "was"} bought {item_occur[-2][1]} times
3. {item_occur[-3][0]} {"were" if item_occur[-3][0].endswith("S") else "was"} bought {item_occur[-3][1]} times
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
