"""
Check database tables for İrrigo Project
"""
import pymysql
import sys
from tabulate import tabulate

# Database connection parameters - using the ones from your .env file
HOST = 'mysql-39fcea5a-c3mc3f-85cc.f.aivencloud.com'
PORT = 26927
USER = 'avnadmin'
PASSWORD = 'AVNS_z46AZhlgazLrqlk0f83'
DATABASE = 'irrigodb'

print(f"Connecting to database {DATABASE} on {HOST}...")

try:
    # Connect to the database
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        database=DATABASE
    )
    print("Connected successfully!")
    
    with connection.cursor() as cursor:
        # Check tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
        else:
            print(f"Found {len(tables)} tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
                
                # Get table structure
                cursor.execute(f"DESCRIBE `{table[0]}`")
                columns = cursor.fetchall()
                
                # Format columns for display
                headers = ["Field", "Type", "Null", "Key", "Default", "Extra"]
                data = [[col[0], col[1], col[2], col[3], col[4], col[5]] for col in columns]
                
                try:
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                except ImportError:
                    # If tabulate is not installed
                    print("Table structure:")
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}, {'NULL' if col[2]=='YES' else 'NOT NULL'}, {col[3]}, Default: {col[4]}, {col[5]}")
                print()
    
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
