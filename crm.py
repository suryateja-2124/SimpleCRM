# Simple CRM System with All Enhancements

import sqlite3
from datetime import datetime, date
from tabulate import tabulate
import csv
import getpass

# -------- LOGIN SYSTEM --------
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    print("\n====== Login to Simple CRM ======")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    if username == USERNAME and password == PASSWORD:
        print("\n✅ Login successful!\n")
    else:
        print("\n❌ Invalid credentials. Exiting.")
        exit()

# -------- DATABASE SETUP --------
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    status TEXT,
    created_at TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    date TEXT,
    note TEXT,
    followup_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
''')

conn.commit()

# -------- CORE FUNCTIONS --------

def add_customer():
    name = input("Enter name: ")
    email = input("Enter email: ")
    phone = input("Enter phone: ")
    address = input("Enter address: ")
    status = input("Enter status (Lead, Prospect, Converted, Inactive): ")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO customers (name, email, phone, address, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, email, phone, address, status, created_at))
    conn.commit()
    print("✅ Customer added successfully!\n")

def view_customers():
    cursor.execute("SELECT id, name, email, phone, address, status, created_at FROM customers")
    rows = cursor.fetchall()
    print("\n--- All Customers ---")
    print(tabulate(rows, headers=["ID", "Name", "Email", "Phone", "Address", "Status", "Created At"], tablefmt="grid"))
    print()

def search_customer():
    keyword = input("Enter name, phone, email or status to search: ")
    cursor.execute("""
        SELECT id, name, email, phone, address, status, created_at 
        FROM customers
        WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR status LIKE ?
    """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    rows = cursor.fetchall()
    print("\n--- Search Results ---")
    print(tabulate(rows, headers=["ID", "Name", "Email", "Phone", "Address", "Status", "Created At"], tablefmt="grid"))
    print()

def update_customer():
    customer_id = input("Enter customer ID to update: ")
    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    data = cursor.fetchone()
    if data:
        name = input(f"New name ({data[1]}): ") or data[1]
        email = input(f"New email ({data[2]}): ") or data[2]
        phone = input(f"New phone ({data[3]}): ") or data[3]
        address = input(f"New address ({data[4]}): ") or data[4]
        status = input(f"New status ({data[5]}): ") or data[5]

        cursor.execute('''UPDATE customers SET name=?, email=?, phone=?, address=?, status=? WHERE id=?''',
                       (name, email, phone, address, status, customer_id))
        conn.commit()
        print("✅ Customer updated successfully!\n")
    else:
        print("❌ Customer not found.\n")

def delete_customer():
    customer_id = input("Enter customer ID to delete: ")
    cursor.execute("SELECT name FROM customers WHERE id=?", (customer_id,))
    data = cursor.fetchone()
    if data:
        confirm = input(f"Are you sure you want to delete {data[0]} (ID {customer_id})? (Y/N): ").strip().lower()
        if confirm == 'y':
            cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            cursor.execute("DELETE FROM interactions WHERE customer_id=?", (customer_id,))
            conn.commit()
            print("🗑️ Customer and their interactions deleted.\n")
        else:
            print("❎ Delete cancelled.\n")
    else:
        print("❌ Customer not found.\n")

def add_interaction():
    customer_id = input("Enter customer ID: ")
    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    if cursor.fetchone():
        note = input("Enter interaction note: ")
        followup_date = input("Enter next follow-up date (YYYY-MM-DD) [optional]: ")
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO interactions (customer_id, date, note, followup_date) VALUES (?, ?, ?, ?)",
                       (customer_id, date_now, note, followup_date or None))
        conn.commit()
        print("📌 Interaction added.\n")
    else:
        print("❌ Customer not found.\n")

def view_interactions():
    customer_id = input("Enter customer ID to view interactions: ")
    cursor.execute("SELECT id, date, note, followup_date FROM interactions WHERE customer_id=?", (customer_id,))
    rows = cursor.fetchall()
    print("\n--- Interaction History ---")
    print(tabulate(rows, headers=["ID", "Date", "Note", "Follow-up Date"], tablefmt="grid"))
    print()

def export_to_csv():
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    with open("customers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Email", "Phone", "Address", "Status", "Created At"])
        writer.writerows(rows)
    print("📁 Exported customers to customers.csv\n")

def show_reminders():
    today = date.today().isoformat()
    cursor.execute("""
        SELECT customers.name, interactions.followup_date
        FROM interactions 
        JOIN customers ON customers.id = interactions.customer_id
        WHERE followup_date = ?
    """, (today,))
    reminders = cursor.fetchall()
    for r in reminders:
        print(f"🔔 Follow-up due today for: {r[0]} (Date: {r[1]})")
    print()

def dashboard():
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM customers ORDER BY created_at DESC LIMIT 1")
    last_customer = cursor.fetchone()
    print("\n📊 CRM Dashboard:")
    print(f"- Total Customers: {total_customers}")
    print(f"- Total Interactions: {total_interactions}")
    print(f"- Newest Customer: {last_customer[0] if last_customer else 'N/A'}\n")

# -------- MAIN MENU --------

def main():
    login()
    show_reminders()
    dashboard()
    while True:
        print("====== Simple CRM System ======")
        print("1. Add Customer")
        print("2. View All Customers")
        print("3. Search Customer")
        print("4. Update Customer Info")
        print("5. Delete Customer")
        print("6. Add Interaction Note")
        print("7. View Interaction History")
        print("8. Export Customers to CSV")
        print("9. Exit")
        print("================================")
        choice = input("Enter your choice (1-9): ")

        if choice == '1':
            add_customer()
        elif choice == '2':
            view_customers()
        elif choice == '3':
            search_customer()
        elif choice == '4':
            update_customer()
        elif choice == '5':
            delete_customer()
        elif choice == '6':
            add_interaction()
        elif choice == '7':
            view_interactions()
        elif choice == '8':
            export_to_csv()
        elif choice == '9':
            print("👋 Exiting CRM. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
