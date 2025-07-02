import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

fake = Faker()

# Sample alarm types
ALARM_TYPES = [
    'Overload',
    'Low Voltage',
    'Sensor Failure',
    'Overheat',
    'Emergency Stop',
    'Communication Failure',
    'Motor Jammed',
    'Door Open',
    'Power Surge',
    'Low Oil Pressure',
    'Error', 
    'Warning', 
    'Failure', 
    'Power Loss'
]

USERS = ['Admin', 'OEM']
ACK_PROBABILITY = 0.8  # 80% chance of acknowledgment
ACCEPT_PROBABILITY = 0.6
NORMALISE_PROBABILITY = 0.5

# Connect to MySQL
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="User1",
            password="User1.",
            database="ajax"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        exit()

# Generate Client Details
def generate_clients(cursor, n=10):
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO client_details (Client_Name, Site, Address)
                VALUES (%s, %s, %s)
            """, (fake.company(), fake.city(), fake.address()))
        except mysql.connector.Error as err:
            print(f"Error inserting client data: {err}")

# Generate Vehicles
def generate_vehicles(cursor):
    cursor.execute("SELECT Client_ID FROM client_details")
    client_ids = [row[0] for row in cursor.fetchall()]
    for client_id in client_ids:
        for _ in range(random.randint(1, 3)):
            try:
                cursor.execute("""
                    INSERT INTO vehicle_details (Client_ID, Vehicle_Type, Vehicle_Quantity, Vehicle_Number)
                    VALUES (%s, %s, %s, %s)
                """, (client_id, random.choice(['Truck', 'Mini-Truck']), random.randint(1, 10), fake.license_plate()))
            except mysql.connector.Error as err:
                print(f"Error inserting vehicle data: {err}")

# Generate Mix Designs
def generate_mix_designs(cursor, n=5):
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO mix_design (MixdesignName, Grade, MixingTime, `20MM`, `10MM`, R_Sand, C_Sand, MT, CMT1, CMT2, WTR1, ADM1, ADM2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                fake.word(), random.choice(['M20', 'M25', 'M30']), round(random.uniform(5, 10), 2),
                *[round(random.uniform(0.5, 5), 2) for _ in range(10)]
            ))
        except mysql.connector.Error as err:
            print(f"Error inserting mix design data: {err}")


# Generate Sales Orders and Batches
def generate_sales_orders_batches(cursor, n_sales_orders=10):
    cursor.execute("SELECT Client_ID FROM client_details")
    client_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT Vehicle_ID, Vehicle_Number FROM vehicle_details")
    vehicle_details = {row[0]: row[1] for row in cursor.fetchall()}
    vehicle_ids = list(vehicle_details.keys()) # Get just the IDs

    cursor.execute("SELECT MixdesignName FROM mix_design")
    mix_design_names = [row[0] for row in cursor.fetchall()]

    for _ in range(n_sales_orders):
        mix_name = random.choice(mix_design_names) if mix_design_names else fake.word() # Use existing or generate
        client_id = random.choice(client_ids)
        truck_id = random.choice(vehicle_ids)
        truck_number = vehicle_details[truck_id]
        date_time = fake.date_time_this_year()
        ordered_qty = round(random.uniform(5, 20), 2)
        load_qty = round(ordered_qty - random.uniform(0, 2), 2)
        produced_qty = round(load_qty - random.uniform(0, 1), 2)
        mixing_time = round(random.uniform(5, 10), 2)

        try:
            cursor.execute("""
                INSERT INTO sales_order (Mix_Name, Client_ID, `Date/Time`, Truck_ID, Ordered_Qty, Load_Qty, Produced_Qty, MixingTime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (mix_name, client_id, date_time, truck_id, ordered_qty, load_qty, produced_qty, mixing_time))
            sales_order_id = cursor.lastrowid

            for series_id in range(1, random.randint(2, 4)):
                for batch_num in range(1, random.randint(2, 5)):
                    batch_datetime = date_time + timedelta(minutes=batch_num*10)
                    cursor.execute("""
                        INSERT INTO batches (SalesOrderID, Batch_Series_ID, Batch_Number, `Date/Time`, `20MM`, `10MM`, R_Sand, C_Sand, MT, CMT1, CMT2, WTR1, ADM1, ADM2, Quantity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        sales_order_id, series_id, batch_num, batch_datetime,
                        *[round(random.uniform(0.5, 5), 2) for _ in range(10)], round(random.uniform(1, 5), 2)
                    ))
                    batch_id = cursor.lastrowid

                    transport_datetime = date_time + timedelta(minutes=batch_num*15)
                    cursor.execute("""
                        INSERT INTO transport_log (SalesOrderID, Batch_ID, Batch_Series_ID, Truck_ID, Truck_Number, Driver_Name, Transport_DateTime, Delivered_Qty)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        sales_order_id, batch_id, series_id, truck_id,
                        truck_number, fake.name(), transport_datetime,
                        round(random.uniform(0.5, 5), 2)
                    ))
        except mysql.connector.Error as err:
            print(f"Error inserting sales order/batch/transport log data: {err}")


# Insert Operator Parameters, Product Settings, Product Container Settings
def insert_generic_settings(cursor, n=5):
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO operator_parameters (Defination, Moisture, Tolerance, Flight_Weight, Recalculate)
                VALUES (%s, %s, %s, %s, %s)
            """, (fake.word(), random.uniform(0.1, 5.0), random.uniform(0.1, 0.5), random.uniform(1.0, 10.0), random.randint(0, 1)))

            cursor.execute("""
                INSERT INTO product_settings (Scales, Dead_Weight, Fill_time, Discharge_time, Loading_Sequence, Jog_Close_Time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fake.word(), *[round(random.uniform(0.5, 10.0), 2) for _ in range(5)]))

            cursor.execute("""
                INSERT INTO product_container_settings (Product_Code, Defination, Large_Jog_Weight, Large_Jog_Time, Small_Jog_Time, Weighting_Mode)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fake.word(), fake.word(), *[round(random.uniform(0.5, 5.0), 2) for _ in range(4)]))
        except mysql.connector.Error as err:
            print(f"Error inserting generic settings data: {err}")

# Generate Users
def generate_users(cursor, n=5):
    for _ in range(n):
        try:
            cursor.execute("""
                INSERT INTO users (Username, Password)
                VALUES (%s, %s)
            """, (fake.user_name(), fake.password()))
        except mysql.connector.Error as err:
            print(f"Error inserting user data: {err}")


def generate_random_alarms(cursor, n=50):
    try:
        insert_query = """
            INSERT INTO alarm_history (
                User, Alarm_Type, Message,
                Event_datetime, Acknowledge_datetime,
                Accept_datetime, Normalise_datetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for _ in range(n):
            alarm_type = random.choice(ALARM_TYPES)
            user = random.choice(USERS)
            message = f"{alarm_type} detected at {fake.word()} zone"
            event_time = fake.date_time_between(start_date='-5d', end_date='now')

            # Simulate follow-up timestamps based on probabilities
            acknowledge_time = (
                event_time + timedelta(minutes=random.randint(1, 10))
                if random.random() < ACK_PROBABILITY else None
            )
            accept_time = (
                acknowledge_time + timedelta(minutes=random.randint(1, 10))
                if acknowledge_time and random.random() < ACCEPT_PROBABILITY else None
            )
            normalise_time = (
                accept_time + timedelta(minutes=random.randint(5, 15))
                if accept_time and random.random() < NORMALISE_PROBABILITY else None
            )

            cursor.execute(insert_query, (
                user, alarm_type, message,
                event_time, acknowledge_time,
                accept_time, normalise_time
            ))

        conn.commit()
        print(f"{n} random alarm history records inserted successfully.")

    except Exception as e:
        print("Error:", e)

# Run the generator
# generate_random_alarms(100)  # Generates 100 random records

# Main Entry
if __name__ == "__main__":
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                print("Generating client data...")
                # generate_clients(cursor, n=10)
                print("Generating vehicle data...")
                # generate_vehicles(cursor)
                print("Generating mix design data...")
                # generate_mix_designs(cursor, n=5)
                print("Generating sales orders and batches data...")
                # generate_sales_orders_batches(cursor, n_sales_orders=10)
                # print("Inserting generic settings data...")
                # insert_generic_settings(cursor, n=5)
                print("Generating user data...")
                # generate_users(cursor, n=5)
                generate_random_alarms(cursor,n=100)
            conn.commit()
        print("Dummy data generated successfully.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")