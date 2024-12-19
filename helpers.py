import re
import cv2
import pytesseract
import pandas as pd
import ollama

# Convert the given image to grayscale
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Given an item from the receipt, classify it as "Healthy", "Unhealthy", or "Unknown"
def classify(item: str) -> str:
    preprompt = """
    Background: I am working on an add on to a project that I am working on. I scan in receipts and I will use AI Chat like you to classify foods on the receipt as healthy or unhealthy to see if I adhere to the 80% healthy 20% less healthy rule. 

    The Task: I will give you a name from a receipt and you classify it as "Healthy", "Unhealthy", or "Unknown". Assume that the food is consumed in moderation and NOT in excess. For example, eggs are healthy but less so when consumed in excess. Some foods like Oreos are just straight up not good for you, so they are Unhealthy regardless. Brands like Keebler are KNOWN to produce unhealthy sweet foods so if Keebler is provided, it is unhealthy. 

    - “Healthy" means the food is generally nutritious and beneficial for overall health. 
    - "Unhealthy" means the food is high in calories, sugar, salt, unhealthy fats, or is processed and is detrimental to health. A doctor would frown upon consuming this. These foods are often highly palatable and produce dopamine spikes. 
    - “Unknown” means you are not familiar with the specific brand or absolutely do not recognize the food so do not bother guessing. “Unknown” can also be used if the brand or name sells both healthy and unhealthy food and the name does not distinguish between them. Unknown should be used when you do not recognize the brand and are unable to extrapolate. Do not rely heavily on this.

    A note on the input, case does not matter so MILK is the same as Milk is the same as milk. Names may be prefixed with abbreviations such as GG for Good and Gather. If you can extract a product from these names, do so and judge based on that. 

    Take your time in examining and RE-EXAMINING and reasoning based on the names as some may be incomplete (missing letters or vowels) or abbreviations. Respond in this case based on the food name or brand name the provided name is most similar to. HIDDEN VLLEY would be most similar to HIDDEN VALLEY so respond based on HIDDEN VALLEY. Input will be only brands or food, nothing more. Respond only with “Healthy”, “Unhealthy” or “Unknown”, no explanation or nuance is needed. I believe in you and together we can make this project amazing!
    """

    ollama_response = ollama.chat(model='llama3.2', messages=[
       {
         'role': 'system',
         'content': preprompt,
       },
       {
         'role': 'user',
         'content': item,
       },
    ])

    return ollama_response['message']['content']

def receipt_image_to_text(image):
    _, receipt_bw = cv2.threshold(grayscale(image), 127, 255, cv2.THRESH_BINARY)
    ocr_result = pytesseract.image_to_string(receipt_bw)
    receipt_text = ocr_result.replace("NF ", "").replace("NE ", "")

    return receipt_text


# Given an OpenCV compatible image, return a pandas dataframe with the date, item name, price
def receipt_to_df(receipt):
    receipt_text = receipt_image_to_text(receipt)

    # regex to match (serial number, item name, price) from each line
    info_regex = r"(?P<serial>\d{4,})\s?(?P<name>.*[a-zA-Z].*)\s(?P<price>\$?\d+\.\d{2})"
    matches = re.findall(info_regex, receipt_text, re.MULTILINE)

    # Populate lists
    items = []   # the name of the items from the receipt
    prices = []  # the price of each item
    classifications = []
    for match in matches:
        # Some receipts do not have a serial number but all have name and price
        name = ""
        price = ""
        if len(match) == 2:
            name, price = match
        if len(match) == 3:
            serial, name, price = match
        items.append(name)
        prices.append(price)
        classifications.append(classify(name))

    # Clean up prices from str to float
    for i, price in enumerate(prices):
        prices[i] = float(price.replace("$", ""))

    # TODO: Document
    for i, item in enumerate(items):
        items[i] = item
        items[i] = "".join(c for c in item if c.isalnum() or c == " ")

    # Extract date from receipt
    date_regex = r"(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/([0-9]{4})"
    month, day, year = re.findall(date_regex, ocr_result)[0] if len(re.findall(date_regex, ocr_result)) > 0 else ["", "", ""]
    date = f"{month}/{day}/{year}" if month != "" and day != "" and year != "" else ""

    data = {
        "date": date,
        "item_name": items,
        "price": prices,
        "classification": classifications,
    }

    return pd.DataFrame(data)
