import csv
from helpers import classify


with open('./receipt_data.csv', mode='r', newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)  # Read all rows into a list

# Open the same CSV file in write mode to overwrite it with updated content
with open('./receipt_data.csv', mode='w', newline='') as f:
    writer = csv.writer(f)

    # Iterate over each row and append the new word
    for row in rows:
        name = row[1]
        classification = classify(name)
        row.append(classification)
        writer.writerow(row)   # Write the modified row back to the file
