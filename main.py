import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from tkcalendar import DateEntry, Calendar
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'user': 'root',       # <-- Replace
            'password': 'qui234',   # <-- Replace
            'database': 'bills'
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to connect: {e}")
            return None

class PaymentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Payment Tracker")
        self.db = Database()
        self.record_id_var = tk.StringVar()
        self.setup_widgets()
        self.load_records()
        self.display_payments()

    def setup_widgets(self):
        # Input Fields
        tk.Label(self.root, text="Payment Name:").grid(row=0, column=0, sticky='e')
        self.entry_name = tk.Entry(self.root)
        self.entry_name.grid(row=0, column=1)

        tk.Label(self.root, text="Amount ($):").grid(row=1, column=0, sticky='e')
        self.entry_amount = tk.Entry(self.root)
        self.entry_amount.grid(row=1, column=1)

        tk.Label(self.root, text="Due Date:").grid(row=2, column=0, sticky='e')
        self.cal_due = DateEntry(self.root, width=18)
        self.cal_due.grid(row=2, column=1)

        tk.Button(self.root, text="Add Payment", command=self.insert_payment).grid(row=3, column=0, pady=5)
        tk.Button(self.root, text="Update Payment", command=self.update_record).grid(row=3, column=1, pady=5)

        tk.Button(self.root, text="Show All Payments", command=self.display_payments).grid(row=4, column=0, columnspan=2, pady=5)
        self.text_output = tk.Text(self.root, width=45, height=6)
        self.text_output.grid(row=5, column=0, columnspan=2)

        # Payday
        tk.Label(self.root, text="Payday (Friday):").grid(row=6, column=0, sticky='e')
        self.cal_payday = DateEntry(self.root, width=18)
        self.cal_payday.grid(row=6, column=1)

        tk.Button(self.root, text="Calculate Weekly Budget", command=self.calculate_weekly_need).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Open Calendar", command=self.show_calendar_with_bills).grid(row=8, column=0, columnspan=2, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Name', 'Amount', 'Due'), show='headings')
        for col in ('ID', 'Name', 'Amount', 'Due'):
            self.tree.heading(col, text=col)
        self.tree.grid(row=9, column=0, columnspan=2, pady=5)

        tk.Button(self.root, text="Delete Selected", command=self.delete_selected).grid(row=10, column=0, pady=5)
        tk.Button(self.root, text="Load for Edit", command=self.load_selected_for_edit).grid(row=10, column=1, pady=5)

    def run_query(self, query, values=(), fetch=False):
        conn = self.db.connect()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute(query, values)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = []
        cursor.close()
        conn.close()
        return result

    def insert_payment(self):
        name = self.entry_name.get()
        amount = self.entry_amount.get()
        due_date = self.cal_due.get_date()
        if not name or not amount:
            messagebox.showwarning("Missing Info", "Please enter all fields.")
            return
        try:
            amount = float(amount)
            self.run_query("INSERT INTO payments (name, amount, due_date) VALUES (%s, %s, %s)",
                           (name, amount, due_date))
            messagebox.showinfo("Success", "Payment added successfully.")
            self.entry_name.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.display_payments()
            self.load_records()
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")

    def update_record(self):
        rid = self.record_id_var.get()
        if not rid:
            messagebox.showwarning("No Record", "Load a record before updating.")
            return
        name = self.entry_name.get()
        amount = self.entry_amount.get()
        due_date = self.cal_due.get_date()
        try:
            amount = float(amount)
            self.run_query("UPDATE payments SET name = %s, amount = %s, due_date = %s WHERE id = %s",
                           (name, amount, due_date, rid))
            messagebox.showinfo("Updated", "Payment updated successfully.")
            self.display_payments()
            self.load_records()
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return
        rid = self.tree.item(selected[0])['values'][0]
        self.run_query("DELETE FROM payments WHERE id = %s", (rid,))
        messagebox.showinfo("Deleted", "Payment deleted successfully.")
        self.display_payments()
        self.load_records()

    def load_selected_for_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a record to load.")
            return
        values = self.tree.item(selected[0])['values']
        self.record_id_var.set(values[0])
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, values[2])
        self.cal_due.set_date(values[3])

    def display_payments(self):
        self.text_output.delete('1.0', tk.END)
        rows = self.run_query("SELECT name, amount, due_date FROM payments ORDER BY due_date", fetch=True)
        if not rows:
            self.text_output.insert(tk.END, "No payments found.\n")
        for row in rows:
            self.text_output.insert(tk.END, f"{row[2]} - {row[0]}: ${row[1]:.2f}\n")

    def load_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.run_query("SELECT id, name, amount, due_date FROM payments ORDER BY due_date", fetch=True)
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    def calculate_weekly_need(self):
        payday = self.cal_payday.get_date()
        start = payday
        end = payday + timedelta(days=6)
        rows = self.run_query("SELECT name, amount, due_date FROM payments WHERE due_date BETWEEN %s AND %s ORDER BY due_date",
                              (start, end), fetch=True)
        total = sum(row[1] for row in rows)
        summary = f"Pay Period: {start} to {end}\nTotal Needed: ${total:.2f}\n\n"
        for name, amount, due in rows:
            summary += f" - {due}: {name} for ${amount:.2f}\n"
        messagebox.showinfo("Weekly Budget", summary)

    def show_calendar_with_bills(self):
        win = Toplevel(self.root)
        win.title("Bill Calendar")
        cal = Calendar(win, selectmode='day')
        cal.pack(pady=10)
        rows = self.run_query("SELECT name, amount, due_date FROM payments", fetch=True)
        for name, amount, due in rows:
            cal.calevent_create(due, f"{name}: ${amount:.2f}", "bill")

        def on_date_select(e):
            selected = cal.get_date()
            events = cal.get_calevents(date=selected)
            output = ""
            for event_id in events:
                output += cal.calevent_cget(event_id, "text") + "\n"
            if output:
                messagebox.showinfo("Bills on " + selected, output)
            else:
                messagebox.showinfo("No Bills", f"No bills due on {selected}")

        cal.bind("<<CalendarSelected>>", on_date_select)

if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentTrackerApp(root)
    root.mainloop()