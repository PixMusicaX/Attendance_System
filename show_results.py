from pymongo import MongoClient
from tabulate import tabulate
from datetime import datetime
import os
from dotenv import load_dotenv

# MongoDB connection string
load_dotenv()
MONGO_CONNECTION_STRING = os.environ['mongo_string']

def connect_to_mongodb():
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client["attendance_system"]
        attendance_collection = db["attendance"]
        # Test the connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB")
        return attendance_collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def display_attendance(collection):
    if collection is None:
        return

    try:
        # Retrieve all attendance records
        records = list(collection.find())

        if not records:
            print("No attendance records found.")
            return

        # Prepare data for tabulate
        headers = ["Name", "Timestamp"]
        table_data = [[record["name"], record.get("timestamp", "N/A")] for record in records]

        # Display the table
        print("\nAttendance Records:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Display summary
        print(f"\nTotal Records: {len(records)}")

    except Exception as e:
        print(f"Error retrieving attendance records: {e}")

def main():
    collection = connect_to_mongodb()
    if collection is not None:
        display_attendance(collection)

if __name__ == "__main__":
    main()