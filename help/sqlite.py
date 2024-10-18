# pip install prettytable
import sqlite3
import argparse
from prettytable import PrettyTable
from prettytable import from_db_cursor

def execute_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Create a PrettyTable directly from the cursor
        table = from_db_cursor(cursor)
        
        # Get the number of rows
        row_count = len(table._rows)
        
        # Close the connection
        conn.close()
        
        return table, row_count
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None, 0

def display_results(table, row_count):
    if table:
        print(table)
        print(f"\nTotal rows: {row_count}")
    else:
        print("No results found or an error occurred.")

def main():
    parser = argparse.ArgumentParser(description="Execute SQLite queries and display results in a pretty table.")
    parser.add_argument("db_path", help="Path to the SQLite database file")
    parser.add_argument("query", help="SQL query to execute")
    args = parser.parse_args()

    table, row_count = execute_query(args.db_path, args.query)
    display_results(table, row_count)

if __name__ == "__main__":
    main()