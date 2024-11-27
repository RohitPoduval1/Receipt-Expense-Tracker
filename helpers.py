import re
import cv2
import pytesseract
import pandas as pd


# Convert the given image to grayscale
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Given an OpenCV compatible image, return a pandas dataframe with the date, item name, price
def receipt_to_df(receipt):
    _, receipt_bw = cv2.threshold(grayscale(receipt), 127, 255, cv2.THRESH_BINARY)
    ocr_result = pytesseract.image_to_string(receipt_bw)
    receipt_text = ocr_result.replace("NF ", "").replace("NE ", "")

    # regex to match (serial number, item name, price) from each line
    info_regex = r"(?P<serial>\d{4,})\s?(?P<name>.*[a-zA-Z].*)\s(?P<price>\$?\d+\.\d{2})"
    matches = re.findall(info_regex, receipt_text, re.MULTILINE)

    # Populate lists
    item_names = []
    prices = []
    for match in matches:
        # Some receipts do not have a serial number but all have name and price
        if len(match) == 2:
            name, price = match
        if len(match) == 3:
            serial, name, price = match
        item_names.append(name)
        prices.append(price)

    # Clean up prices from str to float
    for i, price in enumerate(prices):
        prices[i] = float(price.replace("$", ""))

    for i, item in enumerate(item_names):
        item_names[i] = item
        item_names[i] = "".join(c for c in item if c.isalnum() or c == " ")

    # Extract date from receipt
    date_regex = r"(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/([0-9]{4})"
    month, day, year = re.findall(date_regex, ocr_result)[0] if len(re.findall(date_regex, ocr_result)) > 0 else ["", "", ""]
    date = f"{month}/{day}/{year}" if month != "" and day != "" and year != "" else ""

    data = {
        "date": date,
        "item_name": item_names,
        "price": prices,
    }

    return pd.DataFrame(data)
