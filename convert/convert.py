import csv
import json

# Input CSV file path
csv_file = r"C:\Users\VINO\Desktop\Ajax-Backend-main\convert\MODBUS Address AJAX REGISTERS - Sheet3.csv"

# Output JSON file path
json_file = r'C:\Users\VINO\Desktop\Ajax-Backend-main\data\PLC_Address_registory.json'

output_data = {}

with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 5:
            continue  # skip malformed rows
        name = row[0].strip()
        register_type = row[1].strip()
        address = int(row[2].strip())
        value_type = row[3].strip()
        inverse = row[4].strip().lower()

        # Convert 'FALSE'/'TRUE' string to boolean
        if inverse == 'false':
            inverse_val = False
        elif inverse == 'true':
            inverse_val = True
        else:
            inverse_val = "null"  # treat unexpected as null

        # Assign dictionary
        output_data[name] = {
            "register_type": register_type,
            "address": address,
            "value_type": value_type,
            "inverse": inverse_val
        }

# Write to JSON
with open(json_file, 'w') as f:
    json.dump(output_data, f, indent=4)

print("Conversion complete. JSON saved to", json_file)
