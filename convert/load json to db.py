import json
import mysql.connector

# JSON data (can also be loaded from a file)
json_data = None
with open(r"C:\Users\Lenovo1\Desktop\New folder\AJAX_Dashboard\data\PLC_Address_registory.json") as f:
    json_data = json.load(f)

# MySQL connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'User1',
    'password': 'User1.',  
    'database': 'Ajax'
}


# Connect to MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Insert data
insert_query = """
    INSERT INTO data_registers (reg_name, reg_type, address, inverse)
    VALUES (%s, %s, %s, %s)
"""

for reg_name, details in json_data.items():
    reg_type = details.get("register_type", "")
    address = details.get("address", 0)
    inverse = details.get("inverse")
    if inverse == "null":
        inverse = False  # Treat null as False
    cursor.execute(insert_query, (reg_name, reg_type, address, int(inverse)))

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully.")
