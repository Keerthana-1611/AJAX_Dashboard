import subprocess
import os
from db_handler import create_server_connection,DB_CONFIG
from datetime import datetime

MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"  # or wherever it's installed
MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"  # or wherever it's installed

def backup_database(backup_dir='backups'):

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"{DB_CONFIG['database']}_backup_{timestamp}.sql")
    
    command = [
        MYSQLDUMP_PATH,
        '-u', DB_CONFIG['user'],
        f"-p{DB_CONFIG['password']}",
        '-h', DB_CONFIG['host'],
        DB_CONFIG['database']
    ]

    with open(backup_file, 'w') as f:
        subprocess.run(command, stdout=f, stderr=subprocess.PIPE, shell=False)

    print(f"✅ Backup completed: {backup_file}")
    return backup_file


def restore_database(backup_file):
    try:
        # Step 1: Ensure database exists
        conn = create_server_connection()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        conn.close()
        print(f"✅ Database `{DB_CONFIG['database']}` ensured.")

        # Step 2: Build mysql restore command
        command = [
            MYSQL_PATH,
            '-u', DB_CONFIG['user'],
            f"-p{DB_CONFIG['password']}",
            '-h', DB_CONFIG['host'],
            '-D', DB_CONFIG['database']  # ✅ Use the database explicitly
        ]

        # Step 3: Execute the SQL file
        with open(backup_file, 'r') as f:
            result = subprocess.run(command, stdin=f, capture_output=True, text=True, shell=False)

        # Step 4: Print results
        if result.returncode != 0:
            print("❌ Restore failed!")
            print("stderr:", result.stderr)
        else:
            print(f"✅ Restore completed from: {backup_file}")
            if result.stdout.strip():
                print("stdout:", result.stdout)

    except Exception as e:
        print(f"❌ Exception during restore: {e}")


'''
Example Usage"
Backuping the entire schema with the database call the function below.

backup_database()

restoring Backup call the below function with the sql file path as the parameter

restore_database(r'D:\Production Projects\Ajax-Backend\backups\Ajax_backup_20250628_163004.sql')
'''
