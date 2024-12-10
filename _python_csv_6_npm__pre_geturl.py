import csv

with open('filtered_output_npm.csv', mode='r') as file:
    reader = csv.reader(file)
    header = next(reader)
    rows = list(reader)

rows.sort(key=lambda x: x[0], reverse=False)

with open('filtered_output_npm_sorted.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(rows)