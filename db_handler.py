import mysql.connector
from datetime import datetime

# ---------- Global Connection Info ----------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'User1',
    'password': 'User1.',  
    'database': 'Ajax'
}

# ---------- Create MySQL Server Connection (without DB) ----------
def create_server_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print("[✔] Server connection established.")
        return connection
    except mysql.connector.Error as err:
        print(f"[✖] Error: {err}")
        return None

# ---------- Create Database if Not Exists ----------
def create_database():
    connection = create_server_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS Ajax")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
    finally:
        cursor.close()
        connection.close()

# ---------- Connect to Ajax DB ----------
def create_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"DB Connection error: {err}")
        return None

# Function to insert users
def insert_default_users():
    users = [("Admin", "Admin"), ("Operator", "Operator"), ("OEM", "OEM")]
    
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        for username, password in users:
            cursor.execute(
                "INSERT INTO Users (Username, Password) VALUES (%s, %s)",
                (username, password)
            )

        conn.commit()
        print("Users inserted successfully.")
    
    except mysql.connector.Error as err:
        print("Error:", err)
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Insert default operator parameters
def insert_default_operator_parameters():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()
        Defination_lists = ["MT","CMT1","CMT2","CMT3","WTR1","ADM1","ADM2"]

        for defination in Defination_lists:
            insert_query = """
                INSERT INTO operator_parameters 
                (Defination, Moisture, Tolerance, Flight_Weight, Recalculate) 
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (defination, 0.0, 0.0, 0.0, 0)
            cursor.execute(insert_query, values)

        conn.commit()

        print(f"Inserted default operator parameter with ID: {cursor.lastrowid}")
        return cursor.lastrowid

    except Exception as e:
        print(f"Error inserting default operator parameter: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Insert deafult container settings
def insert_default_container_settings():
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        # --- Default entries for product_container_settings ---
        product_container_defaults = [
            {
                "Product_Code": "CMT1",
                "Defination": "CMT1",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
            {
                "Product_Code": "CMT2",
                "Defination": "CMT2",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
            {
                "Product_Code": "CMT3",
                "Defination": "CMT3",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
            {
                "Product_Code": "WTR1",
                "Defination": "WTR1",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
            {
                "Product_Code": "ADT1",
                "Defination": "ADT1",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
            {
                "Product_Code": "ADT2",
                "Defination": "ADT2",
                "Large_Jog_Weight": 5.0,
                "Large_Jog_Time": 1.0,
                "Small_Jog_Weight": 0.5,
                "Small_Jog_Time": 0.5,
                "Weighting_Mode": 1
            },
        ]

        insert_container_sql = """
            INSERT INTO product_container_settings 
            (Product_Code, Defination, Large_Jog_Weight, Large_Jog_Time, Small_Jog_Weight ,Small_Jog_Time, Weighting_Mode)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for item in product_container_defaults:
            cursor.execute(insert_container_sql, (
                item['Product_Code'],
                item['Defination'],
                item['Large_Jog_Weight'],
                item['Large_Jog_Time'],
                item['Small_Jog_Weight'],
                item['Small_Jog_Time'],
                item['Weighting_Mode']
            ))

            conn.commit()
        print("Default product container and product settings inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Insert default product settings
def insert_default_product_settings():

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # --- Default entries for product_settings ---
        product_settings_defaults = [
            {
                "Scales": "Cement",
                "Dead_Weight": 10.0,
                "Fill_time": 5.0,
                "Discharge_time": 10.0,
                "Loading_Sequence": 1.0,
                "Jog_Close_Time": 2.0
            },
            {
                "Scales": "Water",
                "Dead_Weight": 0.5,
                "Fill_time": 5.0,
                "Discharge_time": 10.0,
                "Loading_Sequence": 2.0,
                "Jog_Close_Time": 2.0
            },
            {
                "Scales": "Admixture",
                "Dead_Weight": 10.0,
                "Fill_time": 5.0,
                "Discharge_time": 10.0,
                "Loading_Sequence": 4.0,
                "Jog_Close_Time": 2.0
            },
        ]

        insert_product_sql = """
            INSERT INTO product_settings 
            (Scales, Dead_Weight, Fill_time, Discharge_time, Loading_Sequence, Jog_Close_Time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for item in product_settings_defaults:
            cursor.execute(insert_product_sql, (
                item['Scales'],
                item['Dead_Weight'],
                item['Fill_time'],
                item['Discharge_time'],
                item['Loading_Sequence'],
                item['Jog_Close_Time']
            ))

        conn.commit()
        print("Default product container and product settings inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- Main Setup Function ----------
def setup_database_and_tables():
    create_database()
    create_tables()
    
# ---------- Create All Tables ----------
def create_tables():
    TABLES = {
        'ClientDetails':"""
            CREATE TABLE IF NOT EXISTS `client_details` (
                `Client_ID` INT AUTO_INCREMENT PRIMARY KEY,
                `Client_Code` VARCHAR(100),
                `Client_Name` VARCHAR(100),
                `Address` VARCHAR(100),
            );        
        """,
        
        'VehicleDetails':"""
            CREATE TABLE IF NOT EXISTS `vehicle_details` (
                `Vehicle_ID` INT AUTO_INCREMENT PRIMARY KEY,
                `Client_ID` INT,
                `Vehicle_Code` VARCHAR(100),
                `Vehicle_Type` VARCHAR(100),
                `Vehicle_Quantity` VARCHAR(100),
                `Vehicle_Number` VARCHAR(100),
                FOREIGN KEY (Client_ID) REFERENCES client_details(Client_ID)
            );
        """,

        'Site Details': """
            CREATE TABLE IF NOT EXISTS site_details (
                `Site_ID` INT AUTO_INCREMENT PRIMARY KEY,
                `Client_ID` INT,
                `Site_Name` VARCHAR(100) NOT NULL,
                `Site_Code` VARCHAR(100) NOT NULL,
                `Site_Address` VARCHAR(255) NOT NULL
            );
        """,

         'Sales_Order': """
            CREATE TABLE IF NOT EXISTS Sales_Order (
                SalesOrderID INT AUTO_INCREMENT PRIMARY KEY,
                Mix_Name VARCHAR(100),
                Client_ID INT,
                `DateTime` DATETIME,
                Ordered_Qty FLOAT,
                Load_Qty FLOAT,
                Produced_Qty FLOAT,
                MixingTime FLOAT,
                FOREIGN KEY (Client_ID) REFERENCES client_details(Client_ID)
            );
        """,

        'Sales_Order_Bom': """
            CREATE TABLE IF NOT EXISTS `sales_order_bom` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `mix_name` VARCHAR(225) NOT NULL,
                `quantity` FLOAT NOT NULL,
                `progress` FLOAT NOT NULL,
                `site_name` VARCHAR(225) NOT NULL,
                `site_address` VARCHAR(225) NOT NULL,
                `vehicle` VARCHAR(225) NOT NULL,
                `action` TINYINT NOT NULL,
                PRIMARY KEY (`id`)
            );
        """,

        'Product_Settings': """
            CREATE TABLE IF NOT EXISTS Product_Settings (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Scales VARCHAR(255),
                Dead_Weight FLOAT,
                Fill_time FLOAT,
                Discharge_time FLOAT,
                Loading_Sequence FLOAT,
                Jog_Close_Time FLOAT
            )
        """,
        'Product_Container_Settings': """
            CREATE TABLE IF NOT EXISTS Product_Container_Settings (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Product_Code VARCHAR(255),
                Defination VARCHAR(255),
                Large_Jog_Weight FLOAT,
                Large_Jog_Time FLOAT,
                Small_Jog_Weight FLOAT,
                Small_Jog_Time FLOAT,
                Weighting_Mode FLOAT
            )
        """,
        'Operator_Parameters': """
            CREATE TABLE IF NOT EXISTS Operator_Parameters (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Defination VARCHAR(255),
                Moisture FLOAT,
                Tolerance FLOAT,
                Flight_Weight FLOAT,
                Recalculate BOOLEAN
            )
        """,
        'Users': """
            CREATE TABLE IF NOT EXISTS Users (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Username VARCHAR(255),
                Password VARCHAR(255)
            )
        """,
        'Mix_Design': """
            CREATE TABLE IF NOT EXISTS Mix_Design (
                `id` INT NOT NULL AUTO_INCREMENT,
                `code` VARCHAR(225) NOT NULL,
                `name` VARCHAR(225) NOT NULL,
                `description` VARCHAR(225) NOT NULL,
                `grade` VARCHAR(225) NOT NULL,
                `action` TINYINT NOT NULL,
                PRIMARY KEY (`id`)
            )
        """,

        'Mix_Design_Bom':"""
            CREATE TABLE IF NOT EXISTS mix_design_bom (
                `id` INT NOT NULL AUTO_INCREMENT,
                `mix_id` INT NOT NULL,
                `Product_ID` INT NOT NULL,
                `Batch_Number` INT NOT NULL,
                `Bin_Number` INT NOT NULL,
                `Material_Code` VARCHAR(225) NOT NULL,
                `Max_Value` INT NOT NULL,
                `Scale_Type` VARCHAR(225) NOT NULL,
                `Short_Code` VARCHAR(225) NOT NULL,
                `uom` INT NOT NULL,
                `tolerance` VARCHAR(50) NOT NULL,
                PRIMARY KEY (`id`),
                CONSTRAINT `fk_bom_product` FOREIGN KEY (`Product_ID`)
                    REFERENCES `config_bom_sec1`(`Product_ID`)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """,
       
        'Batches': """
           CREATE TABLE IF NOT EXISTS Batches (
            Batch_ID INT AUTO_INCREMENT PRIMARY KEY,
            SalesOrderID INT,
            Batch_Series_ID INT,
            Batch_Number INT,
            `DateTime` DATETIME,
            `20MM` FLOAT,
            `10MM` FLOAT,
            R_Sand FLOAT,
            C_Sand FLOAT,
            MT FLOAT,
            CMT1 FLOAT,
            CMT2 FLOAT,
            WTR1 FLOAT,
            ADM1 FLOAT,
            ADM2 FLOAT,
            Quantity FLOAT,
            FOREIGN KEY (SalesOrderID) REFERENCES Sales_Order(SalesOrderID)
        );
        """,
        'TransportLogs': """
           CREATE TABLE IF NOT EXISTS Transport_log (
                Transport_ID INT AUTO_INCREMENT PRIMARY KEY,
                SalesOrderID INT,
                Batch_ID INT,
                Batch_Series_ID INT,
                Truck_Number VARCHAR(50),
                Driver_Name VARCHAR(100),
                Transport_DateTime DATETIME,
                Delivered_Qty FLOAT,
                FOREIGN KEY (SalesOrderID) REFERENCES Sales_Order(SalesOrderID),
                FOREIGN KEY (Batch_ID) REFERENCES Batches(Batch_ID)
            );
        """,
        'AlramHistory': """
            CREATE TABLE IF NOT EXISTS `alarm_history` (
                `ID` int NOT NULL AUTO_INCREMENT,
                `Alarm_Type` varchar(255) NOT NULL,
                `Message` text,
                `Event_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
                `User` varchar(50) DEFAULT NULL,
                `Acknowledge_datetime` datetime DEFAULT NULL,
                `Accept_datetime` datetime DEFAULT NULL,
                `Normalise_datetime` varchar(45) DEFAULT NULL,
                PRIMARY KEY (`ID`)
                );
        """,
            
        'QC_Control': """
            CREATE TABLE IF NOT EXISTS `qc_control` (
                `ID` INT NOT NULL AUTO_INCREMENT,
                `Material_Code` VARCHAR(225) NOT NULL,
                `Material_Name` VARCHAR(225) NOT NULL,
                `Short_Name` VARCHAR(225) NOT NULL,
                `Description` VARCHAR(45) NOT NULL,
                `Specific_Gravity` FLOAT NOT NULL,
                `Action` VARCHAR(45) NOT NULL,
                `Category_Code` VARCHAR(225) NOT NULL,
                PRIMARY KEY (`ID`)
            );
        """,

        'Config_BOM_Sec1': """
            CREATE TABLE IF NOT EXISTS `config_bom_sec1` (
                `Product_ID` INT NOT NULL AUTO_INCREMENT,
                `Short_Code` VARCHAR(225) NOT NULL,
                `Scale_Type` VARCHAR(225) NOT NULL,
                `Max_Value` FLOAT NOT NULL,
                `Bin_Number` INT NOT NULL,
                `Batch_Number` INT NOT NULL,
                `Material_Code` VARCHAR(225) NOT NULL,
                `Action` VARCHAR(45) NOT NULL,
                PRIMARY KEY (`Product_ID`)    
            );
        """,

        'Config_BOM_Sec2': """
            CREATE TABLE IF NOT EXISTS `config_bom_sec2` (
                `ID` INT NOT NULL AUTO_INCREMENT,
                `Material_Code` VARCHAR(225) NOT NULL,
                `Offset_Value` INT NOT NULL,
                `Tolerance` INT NOT NULL,
                `Max_Absorption` FLOAT NOT NULL,
                `Max_Surface` FLOAT NOT NULL,
                `Coarse_Feed_Associate` VARCHAR(225) NOT NULL,
                PRIMARY KEY (`ID`)
            );
        """,

        'Calibration': """
            CREATE TABLE IF NOT EXISTS `qc_calibration` (
                `ID` INT NOT NULL AUTO_INCREMENT,
                `Scale_Name` VARCHAR(225) NOT NULL,
                `Min_Value` FLOAT NOT NULL,
                `Max_Value` FLOAT NOT NULL,
                `Span_Weight` FLOAT NOT NULL,
                `Actual_Value` FLOAT NOT NULL,
                PRIMARY KEY (`ID`));
        """,

        'Permission_Settings': """
            CREATE TABLE IF NOT EXISTS `qc_permission_settings` (
                `ID` INT NOT NULL AUTO_INCREMENT,
                `Channel_Description` VARCHAR(225) NOT NULL,
                `Coarse_Feed` TINYINT NOT NULL,
                `Bin_Correction` TINYINT NOT NULL,
                `Offline_Swapp` TINYINT NOT NULL,
                `Batch_Correction` TINYINT NOT NULL,
                `Terminate` TINYINT NOT NULL,
                PRIMARY KEY (`ID`));
        """

    }

    conn = create_db_connection()
    cursor = conn.cursor()

    for name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
            print(f"[✔] Table '{name}' checked/created.")
        except mysql.connector.Error as err:
            print(f"[✖] Failed creating table {name}: {err}")

    # Check if Users table has any rows
    try:
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        if count == 0:
            insert_default_users()
        
        cursor.execute("SELECT COUNT(*) FROM operator_parameters")
        count = cursor.fetchone()[0]
        if count == 0:
            insert_default_operator_parameters()

        cursor.execute("SELECT COUNT(*) FROM product_settings")
        count = cursor.fetchone()[0]
        if count == 0:
                insert_default_product_settings()

        cursor.execute("SELECT COUNT(*) FROM product_container_settings")
        count = cursor.fetchone()[0]
        if count == 0:
            insert_default_container_settings()

    except mysql.connector.Error as err:
        print("[!] Could not verify Users table:", err)

    cursor.close()
    conn.close()

# Saving the alarm history to the table
def insert_alarm_record(alarm_type, message, source):
    try:
        conn = create_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO alarm_history (Alarm_Type, Message, Source, Timestamp)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            alarm_type,
            message,
            source,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        print("Alarm record inserted successfully.")
    except Exception as e:
        print(f"Error inserting alarm: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



# ---------------- ALARM HANDLING FUNCTIONS EVENTS ----------------


def insert_alarm(message, user='Unknown'):
    now = datetime.now()
    query = """
        INSERT INTO alarm_history (Alarm_Type, Message, Event_datetime, User)
        VALUES (%s, %s, %s, %s)
    """
    values = (message, message, now, user)

    conn = create_db_connection()  # Your DB connection helper
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()

    alarm_id = cursor.lastrowid  # Get auto-incremented ID
    cursor.close()
    conn.close()

    return {
        "alarm_id": alarm_id,
        "message": message,
        "event_datetime": now.strftime('%Y-%m-%d %H:%M:%S')
    }

def update_alarm_datetime(alarm_id, field):
    """
    Update the specified datetime field if not already set.
    field: 'Acknowledge_datetime', 'Accept_datetime', or 'Normalize_datetime'
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = create_db_connection()
    cursor = conn.cursor()

    # Step 1: Check if alarm exists
    check_query = f"SELECT {field} FROM alarm_history WHERE ID = %s"
    cursor.execute(check_query, (alarm_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return "not_found"

    if result[0] is not None:
        cursor.close()
        conn.close()
        return "already_done"

    # Step 2: Update the datetime field
    update_query = f"""
        UPDATE alarm_history
        SET {field} = %s
        WHERE ID = %s
    """
    cursor.execute(update_query, (now, alarm_id))
    conn.commit()
    updated = cursor.rowcount

    cursor.close()
    conn.close()

    return "success" if updated > 0 else "update_failed"

def get_alarm_message_by_id(alarm_id):
    """
    Fetch the alarm message from the alarm_history table using the alarm ID.
    Returns the message if found, or None if not found.
    """
    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT Message FROM alarm_history WHERE ID = %s"
        cursor.execute(query, (alarm_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # The message
        else:
            return None

    except Exception as e:
        print(f"Error fetching alarm message: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


# ---------- Run It ----------
if __name__ == "__main__":
    setup_database_and_tables()
