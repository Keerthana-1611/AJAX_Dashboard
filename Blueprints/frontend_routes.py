from flask import Blueprint, request, jsonify
from db_handler import create_db_connection
from main import is_pendrive_connected
import os
import json
from datetime import datetime
import sys

if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running as script or unpacked
    BASE_PATH = os.getcwd()

frontend = Blueprint('frontend', __name__)

@frontend.route('/',methods=['GET'])
def home():
    return " Home Page"

# Gives the status of the licene key
@frontend.route('/licence_key_connected',methods=['GET'])
def licence_key_connected():
    result = is_pendrive_connected('ABC00253')
    if result:
        return {'success':True,'message': "Licence is connected"}
    else:
        return {'success':False,'message': "Licence is not connected"}

# Validate Username and Password from front end
@frontend.route('/validate_user', methods=['POST'])
def validate_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False ,"valid": False, "message": "Missing 'username' or 'password' field"}), 400

    username = data['username']
    password = data['password']

    conn = create_db_connection()
    if conn is None:
        return jsonify({"success": False ,"valid": False, "message": "Database connection failed"}), 500

    cursor = conn.cursor()
    query = "SELECT Password FROM Users WHERE Username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        # Username not found
        return jsonify({"success": False ,"valid": False, "message": "Invalid username or password"}), 401
    # Check password hash
    if result[0] == password:
        return jsonify({"success": True ,"valid": True})
    else:
        return jsonify({"success": False ,"valid": False, "message": "Invalid username or password"}), 401

# Signup Users
@frontend.route('/signup_user', methods=['POST'])
def signup_user():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "success": False,
            "message": "Missing 'username' or 'password' field"
        }), 400

    username = data['username']
    password = data['password']

    conn = create_db_connection()
    if conn is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT ID FROM Users WHERE Username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 409

    # Insert new user
    try:
        cursor.execute("INSERT INTO Users (Username, Password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return jsonify({
            "success": True,
            "message": "User signed up successfully"
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    finally:
        cursor.close()
        conn.close()

# Delete Users
@frontend.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.get_json()

    if not data or 'username' not in data:
        return jsonify({
            "success": False,
            "message": "Missing 'username' field"
        }), 400

    username = data['username']
    if username.lower() not in ["oem","admin"]:
        conn = create_db_connection()
        if conn is None:
            return jsonify({
                "success": False,
                "message": "Database connection failed"
            }), 500

        cursor = conn.cursor()

        try:
            # Check if user exists
            cursor.execute("SELECT ID FROM Users WHERE Username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404

            # Delete the user
            cursor.execute("DELETE FROM Users WHERE Username = %s", (username,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "User deleted successfully"
            }), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({
                    "success": False,
                    "message": "User Can't be deleted"
                }), 404

# Updates the New password in db
@frontend.route('/update_password', methods=['POST'])
def update_password():
    data = request.get_json()
    if not data or 'username' not in data or 'new_password' not in data:
        return jsonify({"error": "Missing 'username' or 'new_password' field"}), 400

    username = data['username']
    new_password = data['new_password']

    conn = create_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    update_query = "UPDATE Users SET Password = %s WHERE Username = %s"
    cursor.execute(update_query, (new_password, username))
    conn.commit()

    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"success": False, "message": "Username not found"})
    else:
        return jsonify({"success": True, "message": "Password updated successfully"})

# Get IDS Parameters
@frontend.route('/get_ids_parameters', methods=['GET'])
def get_ids_parameters():
    file_path = os.path.join(BASE_PATH,"data","IDS_Paramters.json")
    # Check if file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500

# Update IDS parameters
@frontend.route('/update_ids_parameters', methods=['POST'])
def update_ids_parameters():
    data = request.get_json()
    updates = data.get('updates')

    if not isinstance(updates, dict):
        return jsonify({"error": "'updates' must be a dictionary"}), 400

    file_path = os.path.join(BASE_PATH, "data", "IDS_Paramters.json")

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, 'r') as f:
            original_data = json.load(f)

        for key, value in updates.items():
            if key not in original_data:
                return jsonify({"error": f"Key '{key}' not found in original file"}), 400

            expected_type = type(original_data[key])

            # Allow int if original is float
            if expected_type == float and isinstance(value, int):
                value = float(value)
            elif not isinstance(value, expected_type):
                return jsonify({
                    "error": f"Type mismatch for key '{key}'. Expected {expected_type.__name__}"
                }), 400

            original_data[key] = value

        with open(file_path, 'w') as f:
            json.dump(original_data, f, indent=4)

        return jsonify({"success": True, "message": "IDS Parameters updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Operator Parameters
@frontend.route('/get_operator_parameters', methods=['GET'])
def get_operator_parameters():
    file_path = os.path.join(BASE_PATH,"data","Operator_Parameter.json")
    # Check if file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM operator_parameters")
        rows = cursor.fetchall()
        conn.close()
        json_data["table_values"] = rows
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500

# Update Operator parameters
@frontend.route('/update_operator_parameters', methods=['POST'])
def update_operator_parameters():
    data = request.get_json()
    updates = data.get('updates')

    if not isinstance(updates, dict):
        return jsonify({"error": "'updates' must be a dictionary"}), 400

    file_path = os.path.join(BASE_PATH, "data", "Operator_Parameter.json")

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Load the original JSON
        with open(file_path, 'r') as f:
            original_data = json.load(f)

        # Update file parameters, skipping "table_values"
        for key, value in updates.items():
            if key == "table_values":
                continue  # Skip this key — only for DB update

            if key not in original_data:
                return jsonify({"error": f"Key '{key}' not found in original file"}), 400

            expected_type = type(original_data[key])
            if expected_type == float and isinstance(value, int):
                value = float(value)
            elif not isinstance(value, expected_type):
                return jsonify({
                    "error": f"Type mismatch for key '{key}'. Expected {expected_type.__name__}"
                }), 400

            original_data[key] = value

        # Write updated JSON back to file
        with open(file_path, 'w') as f:
            json.dump(original_data, f, indent=4)

        # Now update the database table if "table_values" is present
        table_values = updates.get("table_values")
        if table_values:
            if not isinstance(table_values, list):
                return jsonify({"error": "'table_values' must be a list"}), 400

            conn = create_db_connection()
            if conn is None:
                return jsonify({"error": "Database connection failed"}), 500

            cursor = conn.cursor()
            update_query = """
                UPDATE Operator_Parameters
                SET Defination = %s,
                    Flight_Weight = %s,
                    Moisture = %s,
                    Recalculate = %s,
                    Tolerance = %s
                WHERE ID = %s
            """

            for row in table_values:
                required_keys = {"Defination", "Flight_Weight", "Moisture", "Recalculate", "Tolerance", "ID"}
                if not required_keys.issubset(row.keys()):
                    return jsonify({"error": f"Missing keys in row: {row}"}), 400

                cursor.execute(update_query, (
                    row["Defination"],
                    float(row["Flight_Weight"]),
                    float(row["Moisture"]),
                    int(row["Recalculate"]),
                    float(row["Tolerance"]),
                    int(row["ID"])
                ))

            conn.commit()
            cursor.close()
            conn.close()

        return jsonify({"success": True, "message": "Operator Parameters updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Plant Details
@frontend.route('/get_plant_details', methods=['GET'])
def get_plant_details():
    file_path = os.path.join(BASE_PATH,"data","Plant_Details.json")
    # Check if file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500
    
# Update Plant Details    
@frontend.route('/update_plant_details', methods=['POST'])
def update_plant_details():
    data = request.get_json()
    updates = data.get('updates')

    if not isinstance(updates, dict):
        return jsonify({"error": "'updates' must be a dictionary"}), 400

    file_path = os.path.join(BASE_PATH, "data", "Plant_Details.json")

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, 'r') as f:
            original_data = json.load(f)

        for key, value in updates.items():
            if key not in original_data:
                return jsonify({"error": f"Key '{key}' not found in original file"}), 400

            expected_type = type(original_data[key])

            # Allow int if original is float
            if expected_type == float and isinstance(value, int):
                value = float(value)
            elif not isinstance(value, expected_type):
                return jsonify({
                    "error": f"Type mismatch for key '{key}'. Expected {expected_type.__name__}"
                }), 400

            original_data[key] = value

        with open(file_path, 'w') as f:
            json.dump(original_data, f, indent=4)

        return jsonify({"success": True, "message": "Operator Parameter updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Get Plant Parameters
@frontend.route('/get_plant_parameters', methods=['GET'])
def get_plant_parameters():
    file_path = os.path.join(BASE_PATH,"data","Plant_Parameters.json")
    # Check if file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500

# Update Plant Parameters    
@frontend.route('/update_plant_parameters', methods=['POST'])
def update_plant_parameters():
    data = request.get_json()
    updates = data.get('updates')

    if not isinstance(updates, dict):
        return jsonify({"error": "'updates' must be a dictionary"}), 400

    file_path = os.path.join(BASE_PATH, "data", "Plant_Parameters.json")

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, 'r') as f:
            original_data = json.load(f)

        for key, value in updates.items():
            if key not in original_data:
                return jsonify({"error": f"Key '{key}' not found in original file"}), 400

            expected_type = type(original_data[key])

            # Allow int if original is float
            if expected_type == float and isinstance(value, int):
                value = float(value)
            elif not isinstance(value, expected_type):
                return jsonify({
                    "error": f"Type mismatch for key '{key}'. Expected {expected_type.__name__}"
                }), 400

            original_data[key] = value

        with open(file_path, 'w') as f:
            json.dump(original_data, f, indent=4)

        return jsonify({"success": True, "message": "Plant Parameter updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Gives the list of sales orders
@frontend.route('/get_sales_orders', methods=['GET'])
def get_sales_orders():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                so.SalesOrderID,
                so.Mix_Name,
                so.Client_ID,
                cd.Client_Name,
                cd.Site,
                cd.Address,
                so.`DateTime`,
                so.Ordered_Qty,
                so.Load_Qty,
                so.Produced_Qty,
                so.MixingTime,
                md.ID AS MixDesignID,
                md.MixdesignName,
                md.Grade,
                md.MixingTime AS DesignMixingTime,
                md.`20MM`,
                md.`10MM`,
                md.R_Sand,
                md.C_Sand,
                md.MT,
                md.CMT1,
                md.CMT2,
                md.WTR1,
                md.ADM1,
                md.ADM2
            FROM sales_order so
            LEFT JOIN client_details cd ON so.Client_ID = cd.Client_ID
            LEFT JOIN mix_design md ON so.Mix_Name = md.MixdesignName
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        result = []

        for row in rows:
            row_dict = dict(zip(column_names, row))

            # Format order DateTime
            date_time = row_dict.get('DateTime')
            row_dict['Date_Time'] = (
                date_time.strftime('%Y-%m-%d %H:%M:%S') if date_time else None
            )
            del row_dict['DateTime']

            result.append(row_dict)

        return jsonify({"success": True, "sales_orders": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

#Allows you to update the existing sales order but not the Sale order ID
@frontend.route('/update_sales_order', methods=['POST'])
def update_sales_order():
    try:
        all_data = request.get_json()
        data = all_data.get("updates")

        if not data:
            return jsonify({"success": False, "error": "'updates' is required in the payload"}), 400

        sales_order_id = data.get('SalesOrderID')
        if not sales_order_id:
            return jsonify({"success": False, "error": "SalesOrderID is required"}), 400

        mix_name = data.get('Mix_Name')
        if not mix_name:
            return jsonify({"success": False, "error": "Mix_Name is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Step 1: Validate Mix_Name exists
        cursor.execute("SELECT ID FROM mix_design WHERE MixdesignName = %s", (mix_name,))
        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": f"Mix_Name '{mix_name}' does not exist in mix_design"
            }), 400

        # Step 2: Get Client_ID from Client_Name (if provided)
        client_id = None
        if 'Client_Name' in data:
            client_name = data['Client_Name']
            cursor.execute("SELECT Client_ID FROM client_details WHERE Client_Name = %s", (client_name,))
            client_row = cursor.fetchone()
            if not client_row:
                return jsonify({
                    "success": False,
                    "error": f"Client_Name '{client_name}' does not exist in client_details"
                }), 400
            client_id = client_row[0]

        # Step 3: Prepare update fields
        valid_fields = [
            'Mix_Name', 'Ordered_Qty', 'Load_Qty',
            'Produced_Qty', 'MixingTime'
        ]

        updates = []
        values = []

        for field in valid_fields:
            if field in data:
                updates.append(f"`{field}` = %s")
                values.append(data[field])

        if client_id is not None:
            updates.append("`Client_ID` = %s")
            values.append(client_id)

        if 'Date_Time' in data:
            updates.append("`DateTime` = %s")
            values.append(data['Date_Time'])

        if not updates:
            return jsonify({"success": False, "error": "No valid fields provided to update"}), 400

        # Finalize query
        values.append(sales_order_id)
        update_query = f"""
            UPDATE sales_order SET {', '.join(updates)}
            WHERE SalesOrderID = %s
        """

        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Sales order updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Allows you to create new sales order
@frontend.route('/create_sales_order', methods=['POST'])
def create_sales_order():
    try:
        data = request.get_json()

        required_fields = [
            'Mix_Name', 'Client_Name',
            'Ordered_Qty', 'Load_Qty', 'Produced_Qty', 'MixingTime'
        ]

        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = create_db_connection()
        cursor = conn.cursor()

        # Step 1: Get Client_ID from Client_Name
        cursor.execute("SELECT Client_ID FROM client_details WHERE Client_Name = %s", (data['Client_Name'],))
        client_row = cursor.fetchone()
        if not client_row:
            return jsonify({
                "success": False,
                "error": f"Client_Name '{data['Client_Name']}' does not exist in client_details"
            }), 400
        client_id = client_row[0]

        # Step 2: Validate Mix_Name in mix_design
        cursor.execute("SELECT ID FROM mix_design WHERE MixdesignName = %s", (data['Mix_Name'],))
        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": f"Mix_Name '{data['Mix_Name']}' does not exist in mix_design"
            }), 400

        # Step 3: Insert into sales_order
        insert_sales_query = """
            INSERT INTO sales_order (
                Mix_Name, Client_ID, `DateTime`,
                Ordered_Qty, Load_Qty, Produced_Qty, MixingTime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        sales_values = (
            data['Mix_Name'],
            client_id,
            current_time,
            data['Ordered_Qty'],
            data['Load_Qty'],
            data['Produced_Qty'],
            data['MixingTime']
        )

        cursor.execute(insert_sales_query, sales_values)
        sales_order_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Sales order created successfully",
            "SalesOrderID": sales_order_id
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get Sales order details of single Order based on the Sale Order Id
@frontend.route('/get_sales_order_details', methods=['POST'])
def get_sales_order_details():
    try:
        data = request.get_json()
        saled_order_id = data.get('SalesOrderID')

        if not saled_order_id:
            return jsonify({
                "success": False,
                "error": "SalesOrderID is required",
                "sales_order": None
            }), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # --- Get Sales Order ---
        cursor.execute("SELECT * FROM Sales_Order WHERE SalesOrderID = %s", (saled_order_id,))
        sales_order_row = cursor.fetchone()

        if not sales_order_row:
            return jsonify({
                "success": False,
                "error": "Sales order not found",
                "sales_order": None
            }), 404

        sales_columns = [desc[0] for desc in cursor.description]
        sales_order = dict(zip(sales_columns, sales_order_row))

        if 'DateTime' in sales_order:
            dt = sales_order['DateTime']
            if dt and not isinstance(dt, str):
                sales_order['Date_Time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                sales_order['Date_Time'] = dt
            del sales_order['DateTime']

        return jsonify({
            "success": True,
            "sales_order": sales_order
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "sales_order": None
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Get all distinct Clients from the sales order table
@frontend.route('/clients', methods=['GET'])
def get_all_client_names():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Client_Name FROM client_details")
        results = cursor.fetchall()

        client_names = [row[0] for row in results]

        return jsonify({"success": True, "clients": client_names})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get All Mix Designs
@frontend.route('/get_all_mix_design', methods=['GET'])
def get_all_mix_design():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mix_design")
        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        result = [dict(zip(column_names, row)) for row in rows]

        return jsonify({"success": True, "mix_designs": result})
    except Exception as e:
        return jsonify({"success": False, "mix_designs": [], "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Create New Mix Designs
@frontend.route('/create_mix_design', methods=['POST'])
def create_mix_design():
    try:
        data = request.get_json()

        fields = [
            'MixdesignName', 'Grade', 'MixingTime', '20MM', '10MM',
            'R_Sand', 'C_Sand', 'MT', 'CMT1', 'CMT2',
            'WTR1', 'ADM1', 'ADM2'
        ]

        if not all(field in data for field in fields):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        insert_query = f"""
            INSERT INTO mix_design ({', '.join(fields)})
            VALUES ({', '.join(['%s'] * len(fields))})
        """
        values = tuple(data[field] for field in fields)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Mix design created", "MixDesignID": cursor.lastrowid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Updating Existing Mix Design based on the MixDesignID
@frontend.route('/update_mix_design', methods=['POST'])
def update_mix_design():
    try:
        data = request.get_json()
        mix_id = data.get('MixDesignID')

        if not mix_id:
            return jsonify({"success": False, "error": "MixDesign ID (ID) is required"}), 400

        fields = [
            'MixdesignName', 'Grade', 'MixingTime', '20MM', '10MM',
            'R_Sand', 'C_Sand', 'MT', 'CMT1', 'CMT2',
            'WTR1', 'ADM1', 'ADM2'
        ]

        updates = []
        values = []

        for field in fields:
            if field in data:
                updates.append(f"`{field}` = %s")
                values.append(data[field])

        if not updates:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE mix_design SET {', '.join(updates)}
            WHERE ID = %s
        """
        values.append(mix_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Mix design updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

'''
#Allow you to delete the mix designs
@frontend.route('/delete_mix_design', methods=['POST'])
def delete_mix_design():
    try:
        data = request.get_json()
        mix_design_id = data.get('Mix_Design_ID')

        if not mix_design_id:
            return jsonify({"success": False, "error": "Mix Design ID is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Check if the Mix Design exists
        cursor.execute("SELECT * FROM Mix_Design WHERE ID = %s", (mix_design_id,))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"success": False, "error": "Mix Design not found"}), 404

        # Delete the Mix Design
        cursor.execute("DELETE FROM Mix_Design WHERE ID = %s", (mix_design_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Mix Design deleted successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
'''

#Allow you to delete multiple Mix Designs
@frontend.route('/delete_mix_design', methods=['POST'])
def delete_mix_design():
    try:
        data = request.get_json()
        mix_design_ids = data.get('Mix_Design_ID')  # expecting a list of IDs

        if not mix_design_ids or not isinstance(mix_design_ids, list):
            return jsonify({"success": False, "error": "Mix_Design_IDs must be a non-empty list"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Check which of the IDs exist
        format_strings = ','.join(['%s'] * len(mix_design_ids))
        cursor.execute(f"SELECT ID FROM Mix_Design WHERE ID IN ({format_strings})", tuple(mix_design_ids))
        existing_ids = [row[0] for row in cursor.fetchall()]

        if not existing_ids:
            return jsonify({"success": False, "error": "None of the provided Mix Design IDs were found"}), 404

        # Delete the existing ones
        format_strings = ','.join(['%s'] * len(existing_ids))
        cursor.execute(f"DELETE FROM Mix_Design WHERE ID IN ({format_strings})", tuple(existing_ids))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {len(existing_ids)} Mix Design(s)",
            "deleted_ids": existing_ids
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

'''
# Allows you to delete the sales order and associated batches
@frontend.route('/delete_sales_order', methods=['POST'])
def delete_sales_order():
    try:
        data = request.get_json()
        saled_order_id = data.get('SalesOrderID')

        if not saled_order_id:
            return jsonify({"success": False, "error": "SalesOrderID is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Check if the Sales Order exists
        cursor.execute("SELECT * FROM Sales_Order WHERE SalesOrderID = %s", (saled_order_id,))
        existing_order = cursor.fetchone()
        if not existing_order:
            return jsonify({"success": False, "error": "Sales order not found"}), 404

        # Delete associated Batches first
        cursor.execute("DELETE FROM Batches WHERE SalesOrderID = %s", (saled_order_id,))

        # Delete the Sales Order
        cursor.execute("DELETE FROM Sales_Order WHERE SalesOrderID = %s", (saled_order_id,))

        conn.commit()

        return jsonify({"success": True, "message": "Sales order and associated batches deleted successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
'''

# Allows you to delete multiple sales order and associated batches
@frontend.route('/delete_sales_order', methods=['POST'])
def delete_sales_order():
    try:
        data = request.get_json()
        sales_order_ids = data.get('SalesOrderID')  # Expecting a list of IDs

        if not sales_order_ids or not isinstance(sales_order_ids, list):
            return jsonify({"success": False, "error": "SalesOrderID must be a non-empty list"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Step 1: Check existing sales orders
        format_strings = ','.join(['%s'] * len(sales_order_ids))
        cursor.execute(f"SELECT SalesOrderID FROM sales_order WHERE SalesOrderID IN ({format_strings})", tuple(sales_order_ids))
        existing_ids = [row[0] for row in cursor.fetchall()]

        if not existing_ids:
            return jsonify({"success": False, "error": "None of the provided Sales Order IDs were found"}), 404

        # Step 2: Get all associated Batch_IDs
        cursor.execute(f"SELECT Batch_ID FROM batches WHERE SalesOrderID IN ({format_strings})", tuple(existing_ids))
        batch_ids = [row[0] for row in cursor.fetchall()]

        # Step 3: Delete from transport_log first (if there are any related batches)
        if batch_ids:
            batch_format = ','.join(['%s'] * len(batch_ids))
            cursor.execute(f"DELETE FROM transport_log WHERE Batch_ID IN ({batch_format})", tuple(batch_ids))

        # Step 4: Delete from batches
        if existing_ids:
            cursor.execute(f"DELETE FROM batches WHERE SalesOrderID IN ({format_strings})", tuple(existing_ids))

        # Step 5: Delete from sales_order
        cursor.execute(f"DELETE FROM sales_order WHERE SalesOrderID IN ({format_strings})", tuple(existing_ids))

        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {len(existing_ids)} sales order(s), their batches and related transport logs.",
            "deleted_ids": existing_ids
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

#Gets list of Truc numbers from the sales order list
@frontend.route('/get_truck_numbers', methods=['GET'])
def get_truck_numbers():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        query = "SELECT DISTINCT Truck_Number FROM Sales_Order WHERE Truck_Number IS NOT NULL"
        cursor.execute(query)
        results = cursor.fetchall()

        truck_numbers = [row[0] for row in results]

        return jsonify({
            "success": True,
            "truck_numbers": truck_numbers
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "truck_numbers": []
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Gets the list of users in the users tables
@frontend.route('/get_usernames', methods=['GET'])
def get_usernames():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Username FROM Users")
        rows = cursor.fetchall()

        usernames = [row[0] for row in rows]

        return jsonify({
            "success": True,
            "usernames": usernames
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "usernames": []
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Get the product settings from database and  the json file
@frontend.route('/get_product_settings_details', methods=['GET'])
def get_product_settings_details():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all product container settings
        cursor.execute("SELECT * FROM product_container_settings")
        container_settings = cursor.fetchall()

        # Fetch all product settings
        cursor.execute("SELECT * FROM product_settings")
        product_settings = cursor.fetchall()

        # Start building the response dictionary
        response_data = {
            "success": True,
            "product_container_settings": container_settings,
            "product_settings": product_settings
        }

        # Read and merge JSON file content
        file_path = os.path.join(BASE_PATH, "data", "Product_Settings.json")
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    response_data.update(json_data)  # Merge contents into response_data
            except Exception as file_error:
                # Optionally log the error or add a debug message
                response_data["json_read_error"] = f"Could not parse JSON: {str(file_error)}"
        else:
            response_data["json_read_error"] = "File not found"

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "product_container_settings": [],
            "product_settings": []
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Update product settings into the database and the json file
@frontend.route('/update_product_settings', methods=['POST'])
def update_product_settings():
    data = request.get_json()
    updates = data.get('updates')

    if not isinstance(updates, dict):
        return jsonify({"success": False,"error": "'updates' must be a dictionary"}), 400

    file_path = os.path.join(BASE_PATH, "data", "Product_Settings.json")

    if not os.path.isfile(file_path):
        return jsonify({"success": False,"error": "File not found"}), 404

    try:
        # Load current JSON file
        with open(file_path, 'r') as f:
            original_data = json.load(f)

        # Keys to exclude from JSON file (these are stored in DB)
        skip_keys = {"product_settings", "product_container_settings"}

        # Update values in JSON, excluding database-bound keys
        for key, value in updates.items():
            if key in skip_keys:
                continue

            if key not in original_data:
                return jsonify({"error": f"Key '{key}' not found in original file"}), 400

            expected_type = type(original_data[key])
            if expected_type == float and isinstance(value, int):
                value = float(value)
            elif not isinstance(value, expected_type):
                return jsonify({
                    "success": False,
                    "error": f"Type mismatch for key '{key}'. Expected {expected_type.__name__}"
                }), 400

            original_data[key] = value

        # Save updated values back to JSON file
        with open(file_path, 'w') as f:
            json.dump(original_data, f, indent=4)

        # Handle DB updates
        conn = create_db_connection()
        if conn is None:
            return jsonify({"success": False,"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Update product_settings table
        product_settings = updates.get("product_settings")
        if product_settings:
            if not isinstance(product_settings, list):
                return jsonify({"success": False,"error": "'product_settings' must be a list"}), 400

            for item in product_settings:
                required_keys = {"ID", "Scales", "Dead_Weight", "Fill_time", "Discharge_time", "Loading_Sequence", "Jog_Close_Time"}
                if not required_keys.issubset(item.keys()):
                    return jsonify({"success": False,"error": f"Missing keys in product_settings item: {item}"}), 400

                cursor.execute("""
                    UPDATE product_settings SET
                        Scales = %s,
                        Dead_Weight = %s,
                        Fill_time = %s,
                        Discharge_time = %s,
                        Loading_Sequence = %s,
                        Jog_Close_Time = %s
                    WHERE ID = %s
                """, (
                    item["Scales"],
                    float(item["Dead_Weight"]),
                    float(item["Fill_time"]),
                    float(item["Discharge_time"]),
                    float(item["Loading_Sequence"]),
                    float(item["Jog_Close_Time"]),
                    int(item["ID"])
                ))

        # Update product_container_settings table
        product_container_settings = updates.get("product_container_settings")
        if product_container_settings:
            if not isinstance(product_container_settings, list):
                return jsonify({"success": False,"error": "'product_container_settings' must be a list"}), 400

            for item in product_container_settings:
                required_keys = {"ID", "Product_Code", "Defination", "Large_Jog_Weight", "Large_Jog_Time", "Small_Jog_Time", "Weighting_Mode"}
                if not required_keys.issubset(item.keys()):
                    return jsonify({"success": False,"error": f"Missing keys in product_container_settings item: {item}"}), 400

                cursor.execute("""
                    UPDATE product_container_settings SET
                        Product_Code = %s,
                        Defination = %s,
                        Large_Jog_Weight = %s,
                        Large_Jog_Time = %s,
                        Small_Jog_Time = %s,
                        Weighting_Mode = %s
                    WHERE ID = %s
                """, (
                    item["Product_Code"],
                    item["Defination"],
                    float(item["Large_Jog_Weight"]),
                    float(item["Large_Jog_Time"]),
                    float(item["Small_Jog_Time"]),
                    float(item["Weighting_Mode"]),
                    int(item["ID"])
                ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Product settings updated successfully"})

    except Exception as e:
        return jsonify({"success": False,"error": str(e)}), 500

# Gets the alarm history based on the give date range
@frontend.route('/get_alarm_history', methods=['POST'])
def get_alarm_history():
    try:
        data = request.get_json()
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        conn = create_db_connection()
        cursor = conn.cursor()

        if start_time and end_time:
            # Validate datetime format
            try:
                start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify({"success": False, "error": "Datetime format must be 'YYYY-MM-DD HH:MM:SS'"}), 400

            cursor.execute("""
                SELECT * FROM alarm_history 
                WHERE Timestamp BETWEEN %s AND %s
                ORDER BY Timestamp DESC
            """, (start_time, end_time))
        else:
            cursor.execute("SELECT * FROM alarm_history ORDER BY Timestamp DESC")

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        alarm_data = []
        for row in rows:
            record = dict(zip(columns, row))
            timestamp = record.get("Timestamp")
            if timestamp and not isinstance(timestamp, str):
                record["Timestamp"] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            alarm_data.append(record)

        return jsonify({"success": True, "alarm_history": alarm_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Give the total quantity is produced
@frontend.route('/get_total_production', methods=['GET'])
def get_total_production():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(Quantity) as TotalProduction FROM batches")
        result = cursor.fetchone()

        total_production = result[0] if result[0] is not None else 0.0

        return jsonify({
            "success": True,
            "total_production": total_production
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@frontend.route('/get_batch_report_by_filters', methods=['POST'])
def get_batch_report_by_filters():
    try:
        data = request.get_json()

        client = data.get('Client', '').strip()
        truck_number = data.get('Truck_Number', '').strip()
        mix_name = data.get('Mix_Name', '').strip()
        start_time = data.get('Start_Time', '')
        end_time = data.get('End_Time', '')

        conn = create_db_connection()
        cursor = conn.cursor()

        filters = []
        values = []

        if client.lower() != 'all' and client != '':
            filters.append("cd.Client_Name = %s")
            values.append(client)

        if truck_number.lower() != 'all' and truck_number != '':
            filters.append("vd.Vehicle_Number = %s")
            values.append(truck_number)

        if mix_name.lower() != 'all' and mix_name != '':
            filters.append("so.Mix_Name = %s")
            values.append(mix_name)

        if start_time and end_time:
            filters.append("b.DateTime BETWEEN %s AND %s")
            values.append(start_time)
            values.append(end_time)

        query = """
            SELECT 
                b.*,
                so.Mix_Name,
                cd.Client_Name,
                vd.Vehicle_Number,
                tl.Transport_DateTime
            FROM batches b
            JOIN sales_order so ON b.SalesOrderID = so.SalesOrderID
            LEFT JOIN client_details cd ON so.Client_ID = cd.Client_ID
            LEFT JOIN transport_log tl ON b.Batch_ID = tl.Batch_ID
            LEFT JOIN vehicle_details vd ON tl.Truck_ID = vd.Vehicle_ID
        """

        if filters:
            query += " WHERE " + " AND ".join(filters)

        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            batch = dict(zip(columns, row))
            if 'DateTime' in batch and batch['DateTime']:
                dt = batch['DateTime']
                batch['Date_Time'] = (
                    dt if isinstance(dt, str) else dt.strftime('%Y-%m-%d %H:%M:%S')
                )
                del batch['DateTime']
            results.append(batch)

        return jsonify({
            "success": True,
            "filters_applied": {
                "Client": client if client else "all",
                "Truck_Number": truck_number if truck_number else "all",
                "Mix_Name": mix_name if mix_name else "all",
                "Start_Time": start_time,
                "End_Time": end_time
            },
            "batches": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Delete Clients Based on the client if given
@frontend.route('/delete_client', methods=['POST'])
def delete_client():
    try:
        data = request.get_json()
        client_ids = data.get('Client_ID')

        if not client_ids or not isinstance(client_ids, list):
            return jsonify({"success": False, "error": "Client_ID must be a non-empty list"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        format_strings = ','.join(['%s'] * len(client_ids))

        # Get Vehicle_IDs linked to clients
        cursor.execute(f"SELECT Vehicle_ID FROM vehicle_details WHERE Client_ID IN ({format_strings})", tuple(client_ids))
        vehicle_ids = [row[0] for row in cursor.fetchall()]

        # Get SalesOrderIDs linked to clients
        cursor.execute(f"SELECT SalesOrderID FROM sales_order WHERE Client_ID IN ({format_strings})", tuple(client_ids))
        sales_order_ids = [row[0] for row in cursor.fetchall()]

        # Get Batch_IDs linked to sales orders
        if sales_order_ids:
            batch_format = ','.join(['%s'] * len(sales_order_ids))
            cursor.execute(f"SELECT Batch_ID FROM batches WHERE SalesOrderID IN ({batch_format})", tuple(sales_order_ids))
            batch_ids = [row[0] for row in cursor.fetchall()]
        else:
            batch_ids = []

        # Step 1: Delete from transport_log
        if batch_ids:
            batch_format = ','.join(['%s'] * len(batch_ids))
            cursor.execute(f"DELETE FROM transport_log WHERE Batch_ID IN ({batch_format})", tuple(batch_ids))

        if vehicle_ids:
            vehicle_format = ','.join(['%s'] * len(vehicle_ids))
            cursor.execute(f"DELETE FROM transport_log WHERE Truck_ID IN ({vehicle_format})", tuple(vehicle_ids))

        if sales_order_ids:
            so_format = ','.join(['%s'] * len(sales_order_ids))
            cursor.execute(f"DELETE FROM transport_log WHERE SalesOrderID IN ({so_format})", tuple(sales_order_ids))

        # Step 2: Delete batches
        if sales_order_ids:
            cursor.execute(f"DELETE FROM batches WHERE SalesOrderID IN ({so_format})", tuple(sales_order_ids))

        # Step 3: Delete sales orders
        if sales_order_ids:
            cursor.execute(f"DELETE FROM sales_order WHERE SalesOrderID IN ({so_format})", tuple(sales_order_ids))

        # Step 4: Delete vehicles
        if vehicle_ids:
            cursor.execute(f"DELETE FROM vehicle_details WHERE Vehicle_ID IN ({vehicle_format})", tuple(vehicle_ids))

        # Step 5: Delete clients
        cursor.execute(f"DELETE FROM client_details WHERE Client_ID IN ({format_strings})", tuple(client_ids))

        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Clients and all associated records deleted successfully",
            "deleted_client_ids": client_ids
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


# Gives all the client Details
@frontend.route('/add_client', methods=['POST'])
def add_client():
    try:
        data = request.get_json()

        client_name = data.get('Client_Name')
        site = data.get('Site')
        address = data.get('Address')

        if not client_name or not site or not address:
            return jsonify({
                "success": False,
                "error": "Client_Name, Site, and Address are required"
            }), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Check if Client_Name already exists (case-insensitive)
        cursor.execute("SELECT Client_ID FROM client_details WHERE LOWER(Client_Name) = LOWER(%s)", (client_name,))
        existing = cursor.fetchone()

        if existing:
            return jsonify({
                "success": False,
                "error": f"Client_Name '{client_name}' already exists"
            }), 409

        insert_query = """
            INSERT INTO client_details (Client_Name, Site, Address)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (client_name, site, address))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Client added successfully",
            "Client_ID": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Update Client Details
@frontend.route('/update_client_details', methods=['POST'])
def update_client_details():
    try:
        all_values = request.get_json()
        data = all_values.get('updates')
        client_id = data.get('Client_ID')

        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        
        if not client_id:
            return jsonify({"success": False, "error": "Client_ID is required"}), 400

        fields = ['Client_Name', 'Site', 'Address']

        updates = []
        values = []

        for field in fields:
            if field in data:
                updates.append(f"`{field}` = %s")
                values.append(data[field])

        if not updates:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        # Check for duplicate Client_Name (excluding this Client_ID)
        if 'client_name' in data:
            conn = create_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Client_ID FROM client_details
                WHERE LOWER(Client_Name) = LOWER(%s) AND Client_ID != %s
            """, (data['client_name'], client_id))
            duplicate = cursor.fetchone()
            if duplicate:
                return jsonify({
                    "success": False,
                    "error": f"Client_Name '{data['client_name']}' already exists for another client"
                }), 409
            cursor.close()
            conn.close()

        update_query = f"""
            UPDATE client_details SET {', '.join(updates)}
            WHERE Client_ID = %s
        """
        values.append(client_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Client details updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get details of all the clients
@frontend.route('/get_all_clients', methods=['GET'])
def get_all_clients():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM client_details")
        clients = cursor.fetchall()

        return jsonify({"success": True, "clients": clients})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get client Details by id
@frontend.route('/get_client_by_id', methods=['POST'])
def get_client_by_id():
    try:
        data = request.get_json()
        client_id = data.get('Client_ID')

        if not client_id:
            return jsonify({"success": False, "error": "Client_ID is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM client_details WHERE Client_ID = %s", (client_id,))
        client = cursor.fetchone()

        if not client:
            return jsonify({"success": False, "error": f"No client found with ID {client_id}"}), 404

        return jsonify({"success": True, "client": client})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Add new vehicle
@frontend.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()

        client_id = data.get('Client_ID')
        vehicle_type = data.get('Vehicle_Type')
        vehicle_quantity = data.get('Vehicle_Quantity')
        vehicle_number = data.get('Vehicle_Number')

        if not client_id or not vehicle_type or not vehicle_quantity or not vehicle_number:
            return jsonify({"success": False, "error": "All fields (Client_ID, Vehicle_Type, Vehicle_Quantity, Vehicle_Number) are required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO vehicle_details (Client_ID, Vehicle_Type, Vehicle_Quantity, Vehicle_Number)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (client_id, vehicle_type, vehicle_quantity, vehicle_number))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Vehicle added successfully",
            "vehicle_id": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update Vehicle details
@frontend.route('/update_vehicle', methods=['POST'])
def update_vehicle():
    try:
        updates = request.get_json()
        data = updates.get('updates')
        vehicle_id = data.get('Vehicle_ID')
        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        if not vehicle_id:
            return jsonify({"success": False, "error": "Vehicle_ID is required"}), 400

        fields = ['Vehicle_Type', 'Vehicle_Quantity', 'Vehicle_Number']
        updates = []
        values = []

        for field in fields:
            if field in data:
                updates.append(f"`{field}` = %s")
                values.append(data[field])

        if not updates:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE vehicle_details SET {', '.join(updates)}
            WHERE Vehicle_ID = %s
        """
        values.append(vehicle_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Vehicle details updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Detele vehicle details
@frontend.route('/delete_vehicle', methods=['POST'])
def delete_vehicle():
    try:
        data = request.get_json()
        vehicle_ids = data.get('Vehicle_ID')

        if not vehicle_ids or not isinstance(vehicle_ids, list):
            return jsonify({"success": False, "error": "Vehicle_ID (list) is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        # Convert list to comma-separated placeholders
        placeholders = ','.join(['%s'] * len(vehicle_ids))

        # Delete associated records from transport_log
        cursor.execute(f"DELETE FROM transport_log WHERE Truck_ID IN ({placeholders})", tuple(vehicle_ids))

        # Delete from vehicle_details
        cursor.execute(f"DELETE FROM vehicle_details WHERE Vehicle_ID IN ({placeholders})", tuple(vehicle_ids))

        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {cursor.rowcount} vehicle(s) and associated transport log records"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get vehicle detils by using ID
@frontend.route('/get_vehicle_by_id', methods=['POST'])
def get_vehicle_by_id():
    try:
        data = request.get_json()
        vehicle_id = data.get('Vehicle_ID')

        if not vehicle_id:
            return jsonify({"success": False, "error": "Vehicle_ID is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vehicle_details WHERE Vehicle_ID = %s", (vehicle_id,))
        vehicle = cursor.fetchone()

        if not vehicle:
            return jsonify({"success": False, "error": f"No vehicle found with ID {vehicle_id}"}), 404

        return jsonify({"success": True, "vehicle": vehicle})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get all vehicles details
@frontend.route('/get_all_vehicles', methods=['GET'])
def get_all_vehicles():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vehicle_details")
        vehicles = cursor.fetchall()

        return jsonify({"success": True, "vehicles": vehicles})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get list of vehicles by the client ID
@frontend.route('/get_vehicles_by_client', methods=['POST'])
def get_vehicles_by_client():
    try:
        data = request.get_json()
        client_id = data.get('Client_ID')

        if not client_id:
            return jsonify({"success": False, "error": "Client_ID is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vehicle_details WHERE Client_ID = %s", (client_id,))
        vehicles = cursor.fetchall()

        return jsonify({"success": True, "vehicles": vehicles})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# To Get all the transport Logs
@frontend.route('/get_all_transport_logs', methods=['GET'])
def get_all_transport_logs():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                tl.Transport_ID,
                tl.Transport_DateTime,
                tl.Delivered_Qty,
                tl.Batch_Series_ID,
                tl.Batch_ID,
                tl.Truck_ID,
                vd.Vehicle_Number,
                vd.Vehicle_Type,
                vd.Vehicle_Quantity,
                so.SalesOrderID,
                so.Mix_Name,
                cd.Client_Name,
                cd.Site,
                cd.Address,
                b.Batch_Number,
                b.DateTime
            FROM transport_log tl
            LEFT JOIN vehicle_details vd ON tl.Truck_ID = vd.Vehicle_ID
            LEFT JOIN batches b ON tl.Batch_ID = b.Batch_ID
            LEFT JOIN sales_order so ON tl.SalesOrderID = so.SalesOrderID
            LEFT JOIN client_details cd ON so.Client_ID = cd.Client_ID
            ORDER BY tl.Transport_DateTime DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        transport_logs = []
        for row in rows:
            log = dict(zip(columns, row))
            # Format datetime fields
            for key in ['Transport_DateTime', 'DateTime']:
                if key in log and log[key]:
                    dt = log[key]
                    log[key] = dt if isinstance(dt, str) else dt.strftime('%Y-%m-%d %H:%M:%S')
            transport_logs.append(log)

        return jsonify({
            "success": True,
            "transport_logs": transport_logs
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get All distinct Alarm names for the alarm history
@frontend.route('/get_distinct_alarm_names', methods=['GET'])
def get_distinct_alarm_names():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT Alarm_Type FROM alarm_history ORDER BY Alarm_Type")
        rows = cursor.fetchall()
        alarm_types = [row[0] for row in rows]

        return jsonify({
            "success": True,
            "alarm_types": alarm_types
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get Alarm history by filters
@frontend.route('/get_alarm_history_by_filter', methods=['POST'])
def get_alarm_history_by_filter():
    try:
        data = request.get_json()

        start_time = data.get('Start_Time', '').strip().lower()
        end_time = data.get('End_Time', '').strip().lower()
        alarm_type = data.get('Alarm_Type', '').strip()

        conn = create_db_connection()
        cursor = conn.cursor()

        filters = []
        values = []

        # Filter by alarm type if not "all"
        if alarm_type and alarm_type.lower() != 'all':
            filters.append("Alarm_Type = %s")
            values.append(alarm_type)

        # Filter by time range if both start and end time are given
        if (start_time not in ['all', '']) and (end_time not in ['all', '']):
            filters.append("Event_datetime BETWEEN %s AND %s")
            values.append(start_time)
            values.append(end_time)

        # Final SQL query
        query = "SELECT * FROM alarm_history"
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY Event_datetime DESC"

        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        results = [dict(zip(columns, row)) for row in rows]
        for r in results:
            if isinstance(r.get("Event_datetime"), (datetime,)):
                r["Event_datetime"] = r["Event_datetime"].strftime('%Y-%m-%d %H:%M:%S')
            for ts_field in ["Acknowledge_datetime", "Accept_datetime", "Normalise_datetime"]:
                if isinstance(r.get(ts_field), (datetime,)):
                    r[ts_field] = r[ts_field].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "success": True,
            "filters_applied": {
                "Alarm_Type": alarm_type or "all",
                "Start_Time": start_time or "all",
                "End_Time": end_time or "all"
            },
            "alarms": results
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get all alarm history
@frontend.route('/get_all_alarm_history', methods=['GET'])
def get_all_alarm_history():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alarm_history ORDER BY Event_datetime DESC")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            record = dict(zip(columns, row))

            # Format all datetime fields
            datetime_fields = [
                "Event_datetime",
                "Acknowledge_datetime",
                "Accept_datetime",
                "Normalise_datetime"
            ]
            for field in datetime_fields:
                if isinstance(record.get(field), (datetime,)):
                    record[field] = record[field].strftime('%Y-%m-%d %H:%M:%S')

            results.append(record)

        return jsonify({
            "success": True,
            "total": len(results),
            "alarms": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Add Material
@frontend.route('/add_material', methods=['POST'])
def add_material():
    try:
        data = request.get_json()

        material_code = data.get('Material_Code')
        material_name = data.get('Material_Name')
        short_name = data.get('Short_Name')
        description = data.get('Description')
        specific_gravity = data.get('Specific_Gravity')
        action = data.get('Action')
        category_code = data.get('Category_Code')

        # Input validation
        if not all([material_code, material_name, short_name, description, specific_gravity, action, category_code]):
            return jsonify({
                "success": False,
                "error": "All fields (Material_Code, Material_Name, Short_Name, Description, Specific_Gravity, Action, Category_Code) are required"
            }), 400

        # Connect to DB
        conn = create_db_connection()
        cursor = conn.cursor()

        # Insert into qc_control table
        insert_query = """
            INSERT INTO qc_control (
                Material_Code,
                Material_Name,
                Short_Name,
                Description,
                Specific_Gravity,
                Action,
                Category_Code
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            material_code,
            material_name,
            short_name,
            description,
            specific_gravity,
            action,
            category_code
        ))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Material added successfully",
            "material_id": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update Material
@frontend.route('/update_material', methods=['POST'])
def update_material():
    try:
        updates = request.get_json()
        data = updates.get('updates')
        material_id = data.get('ID')

        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        if not material_id:
            return jsonify({"success": False, "error": "Material ID is required"}), 400

        fields = [
            'Material_Code',
            'Material_Name',
            'Short_Name',
            'Description',
            'Specific_Gravity',
            'Action',
            'Category_Code'
        ]
        update_clauses = []
        values = []

        for field in fields:
            if field in data:
                update_clauses.append(f"`{field}` = %s")
                values.append(data[field])

        if not update_clauses:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE qc_control SET {', '.join(update_clauses)}
            WHERE ID = %s
        """
        values.append(material_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Material updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Delete Material
@frontend.route('/delete_material', methods=['POST'])
def delete_material():
    try:
        data = request.get_json()
        material_ids = data.get('Material_ID')

        # Validate input
        if not material_ids or not isinstance(material_ids, list) or not all(isinstance(mid, int) for mid in material_ids):
            return jsonify({"success": False, "error": "Material_ID must be a list of integers"}), 400

        # DB Connection
        conn = create_db_connection()
        cursor = conn.cursor()

        # SQL delete query with dynamic placeholders
        placeholders = ','.join(['%s'] * len(material_ids))
        delete_query = f"DELETE FROM qc_control WHERE ID IN ({placeholders})"

        cursor.execute(delete_query, tuple(material_ids))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {cursor.rowcount} material record(s) from qc_control"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get all Material
@frontend.route('/get_all_materials', methods=['GET'])
def get_all_materials():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM qc_control")
        materials = cursor.fetchall()

        return jsonify({"success": True, "materials": materials})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Add Configuration BOM Section 1
@frontend.route('/add_configuration_bom_sec1', methods=['POST'])
def configuration_bom_sec1():
    try:
        data = request.get_json()

        short_code = data.get('Short_Code')
        scale_type = data.get('Scale_Type')
        max_value = data.get('Max_Value')
        bin_number = data.get('Bin_Number')
        batch_number = data.get('Batch_Number')
        material_code = data.get('Material_Code')
        action = data.get('Action')

        # Input validation
        if not all([short_code, scale_type, max_value, bin_number, batch_number, material_code, action]):
            return jsonify({
                "success": False,
                "error": "All fields (Short_Code, Scale_Type, Max_Value, Bin_Number, Batch_Number, Material_Code, Action) are required"
            }), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO config_bom_sec1 (
                Short_Code, 
                Scale_Type, 
                Max_Value, 
                Bin_Number, 
                Batch_Number, 
                Material_Code, 
                Action
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            short_code,
            scale_type,
            max_value,
            bin_number,
            batch_number,
            material_code,
            action
        ))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "ConfigurationBom Section1 added successfully",
            "config_id1": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update Configuration BOM Section 1
@frontend.route('/update_configuration_bom_sec1', methods=['POST'])
def update_configuration_bom_sec1():
    try:
        updates = request.get_json()
        data = updates.get('updates')
        product_id = data.get('Product_ID') 

        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        if not product_id:
            return jsonify({"success": False, "error": "Product_ID is required"}), 400

        fields = [
            'Short_Code', 'Scale_Type', 'Max_Value',
            'Bin_Number', 'Batch_Number', 'Material_Code', 'Action'
        ]
        update_clauses = []
        values = []

        for field in fields:
            if field in data:
                update_clauses.append(f"`{field}` = %s")
                values.append(data[field])

        if not update_clauses:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE config_bom_sec1 SET {', '.join(update_clauses)}
            WHERE Product_ID = %s
        """
        values.append(product_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Configuration BOM Section 1 updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Delete Configuration BOM Section 1
@frontend.route('/delete_configuration_bom_sec1', methods=['POST'])
def delete_configuration_bom_sec1():
    try:
        data = request.get_json()
        product_ids = data.get('Product_ID')

        if not product_ids or not isinstance(product_ids, list):
            return jsonify({"success": False, "error": "Product_ID (list) is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        placeholders = ','.join(['%s'] * len(product_ids))
        cursor.execute(f"DELETE FROM config_bom_sec1 WHERE Product_ID IN ({placeholders})", tuple(product_ids))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {cursor.rowcount} configuration record(s)"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get all Configuration BOM Section 1
@frontend.route('/get_configuration_bom_sec1', methods=['GET'])
def get_configuration_bom_sec1():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM config_bom_sec1")
        records = cursor.fetchall()

        return jsonify({"success": True, "config_bom_sec1": records})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Add Configuration BOM Section 2
@frontend.route('/add_configuration_bom_sec2', methods=['POST'])
def configuration_bom_sec2():
    try:
        data = request.get_json()

        material_code = data.get('Material_Code')
        offset_value = data.get('Offset_Value')
        tolerance = data.get('Tolerance')
        max_absorption = data.get('Max_Absorption')
        max_surface = data.get('Max_Surface')
        coarse_feed_associate = data.get('Coarse_Feed_Associate')

        # Input validation
        required_fields = [material_code, offset_value, tolerance, max_absorption, max_surface, coarse_feed_associate]
        if any(field is None for field in required_fields):
            return jsonify({
                "success": False,
                "error": "All fields (Material_Code, Offset_Value, Tolerance, Max_Absorption, Max_Surface, Coarse_Feed_Associate) are required"
            }), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO config_bom_sec2 (
                Material_Code, 
                Offset_Value, 
                Tolerance, 
                Max_Absorption, 
                Max_Surface, 
                Coarse_Feed_Associate
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            material_code,
            offset_value,
            tolerance,
            max_absorption,
            max_surface,
            coarse_feed_associate
        ))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Configuration BOM Section 2 added successfully",
            "config_id2": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update Configuration BOM Section 2
@frontend.route('/update_configuration_bom_sec2', methods=['POST'])
def update_configuration_bom_sec2():
    try:
        updates = request.get_json()
        data = updates.get('updates')
        record_id = data.get('ID')  # Must match table's primary key

        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        if not record_id:
            return jsonify({"success": False, "error": "ID is required"}), 400

        fields = [
            'Material_Code', 'Offset_Value', 'Tolerance', 'Max_Absorption',
            'Max_Surface', 'Coarse_Feed_Associate'
        ]
        update_clauses = []
        values = []

        for field in fields:
            if field in data:
                update_clauses.append(f"`{field}` = %s")
                values.append(data[field])

        if not update_clauses:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE config_bom_sec2 SET {', '.join(update_clauses)}
            WHERE ID = %s
        """
        values.append(record_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Configuration BOM Section 2 updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Delete Configuration BOM Section 2
@frontend.route('/delete_configuration_bom_sec2', methods=['POST'])
def delete_configuration_bom_sec2():
    try:
        data = request.get_json()
        record_ids = data.get('ID')

        if not record_ids or not isinstance(record_ids, list):
            return jsonify({"success": False, "error": "IDs (list) is required"}), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        placeholders = ','.join(['%s'] * len(record_ids))
        cursor.execute(f"DELETE FROM config_bom_sec2 WHERE ID IN ({placeholders})", tuple(record_ids))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Deleted {cursor.rowcount} configuration record(s)"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get All Configuration BOM Section 2
@frontend.route('/get_configuration_bom_sec2', methods=['GET'])
def get_configuration_bom_sec2():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM config_bom_sec2")
        data = cursor.fetchall()

        return jsonify({"success": True, "config_bom_sec2": data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Add QC_Calibration
@frontend.route('/add_qc_calibration', methods=['POST'])
def add_qc_calibration():
    try:
        data = request.get_json()

        scale_name = data.get('Scale_Name')
        min_value = data.get('Min_Value')
        max_value = data.get('Max_Value')
        span_weight = data.get('Span_Weight')
        actual_value = data.get('Actual_Value')

        # Input validation
        required_fields = [scale_name, min_value, max_value, span_weight, actual_value]
        if any(field is None for field in required_fields):
            return jsonify({
                "success": False,
                "error": "All fields (Scale_Name, Min_Value, Max_Value, Span_Weight, Actual_Value) are required"
            }), 400

        conn = create_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO qc_calibration (
               Scale_Name, 
               Min_Value, 
               Max_Value, 
               Span_Weight, 
               Actual_Value
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
           scale_name, 
           min_value, 
           max_value, 
           span_weight, 
           actual_value
        ))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Calibration added successfully",
            "calibration": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update QC Calibration
@frontend.route('/update_qc_calibration', methods=['POST'])
def update_qc_calibration():
    try:
        updates = request.get_json()
        data = updates.get('updates')
        calibration_id = data.get('ID')

        if not data:
            return jsonify({"success": False, "error": "updates is required"}), 400
        if not calibration_id:
            return jsonify({"success": False, "error": "ID is required"}), 400

        fields = ['Scale_Name', 'Min_Value', 'Max_Value', 'Span_Weight', 'Actual_Value']
        update_clauses = []
        values = []

        for field in fields:
            if field in data:
                update_clauses.append(f"`{field}` = %s")
                values.append(data[field])

        if not update_clauses:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE qc_calibration SET {', '.join(update_clauses)}
            WHERE ID = %s
        """
        values.append(calibration_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "update": "QC Calibration updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get All QC Calibration
@frontend.route('/get_qc_calibration', methods=['GET'])
def get_qc_calibration():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM qc_calibration")
        records = cursor.fetchall()

        return jsonify({"success": True, "qc_calibration_data": records})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Update QC permission setting
@frontend.route('/update_qc_permission_settings', methods=['POST'])
def qc_update_permission_settings():
    try:
        data = request.get_json()
        setting_id = data.get('ID')

        if not setting_id:
            return jsonify({"success": False, "error": "ID is required"}), 400

        # Fields that can be updated
        fields = ['Channel_Description', 'Coarse_Feed', 'Bin_Correction', 'Offline_Swapp', 'Batch_Correction', 'Terminate']
        update_clauses = []
        values = []

        for field in fields:
            if field in data:
                update_clauses.append(f"`{field}` = %s")
                values.append(data[field])

        if not update_clauses:
            return jsonify({"success": False, "error": "No fields to update"}), 400

        update_query = f"""
            UPDATE qc_permission_settings SET {', '.join(update_clauses)}
            WHERE ID = %s
        """
        values.append(setting_id)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": "Permission settings updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Get all qc permission settings
@frontend.route('/qc_get_permission_settings', methods=['GET'])
def qc_get_permission_settings():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM qc_permission_settings")
        settings = cursor.fetchall()

        return jsonify({"success": True, "qc_permission_settings": settings})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
