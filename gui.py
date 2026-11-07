import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import csv

FILE_NAME = "expenses.csv"


def load_expenses():
    expenses = []
    try:
        with open(FILE_NAME, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["amount"] = float(row["amount"])
                expenses.append(row)
    except FileNotFoundError:
        pass
    except (ValueError, KeyError) as error:
        messagebox.showerror("File error", f"Could not read expenses.csv:\n{error}")
    return expenses


def save_expenses(expenses):
    with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
        fields = ["date", "category", "amount", "description"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(expenses)


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("850x600")
        self.root.minsize(720, 500)

        self.expenses = load_expenses()
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Expense Tracker", font=("Arial", 22, "bold")).pack(anchor="w")
        ttk.Label(main, text="Record and review your spending", foreground="gray").pack(anchor="w", pady=(0, 14))

        form = ttk.LabelFrame(main, text="Add an expense", padding=12)
        form.pack(fill="x")

        self.date_var = tk.StringVar(value=str(date.today()))
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()

        fields = [
            ("Date (YYYY-MM-DD)", self.date_var, 18),
            ("Category", self.category_var, 18),
            ("Amount", self.amount_var, 14),
            ("Description", self.description_var, 30),
        ]
        for column, (label, variable, width) in enumerate(fields):
            cell = ttk.Frame(form)
            cell.grid(row=0, column=column, padx=5, sticky="ew")
            ttk.Label(cell, text=label).pack(anchor="w")
            ttk.Entry(cell, textvariable=variable, width=width).pack(fill="x", pady=(4, 0))
            form.columnconfigure(column, weight=1)

        ttk.Button(form, text="Add Expense", command=self.add_expense).grid(
            row=1, column=0, columnspan=4, sticky="e", padx=5, pady=(12, 0)
        )

        summary = ttk.Frame(main)
        summary.pack(fill="x", pady=12)
        self.total_label = ttk.Label(summary, text="Total spent: 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left")
        ttk.Button(summary, text="Category Summary", command=self.category_summary).pack(side="right", padx=(6, 0))
        ttk.Button(summary, text="Delete Selected", command=self.delete_selected).pack(side="right")

        search_bar = ttk.Frame(main)
        search_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(search_bar, text="Search category:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_bar, textvariable=self.search_var, width=24)
        search_entry.pack(side="left", padx=6)
        search_entry.bind("<Return>", lambda event: self.search_expenses())
        ttk.Button(search_bar, text="Search", command=self.search_expenses).pack(side="left")
        ttk.Button(search_bar, text="Show All", command=self.show_all).pack(side="left", padx=6)

        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "category", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("description", text="Description")
        self.tree.column("date", width=115, anchor="center")
        self.tree.column("category", width=130)
        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("description", width=350)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(main, text="Data is saved locally in expenses.csv", foreground="gray").pack(anchor="w", pady=(8, 0))

    def refresh_table(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = self.expenses if records is None else records
        for index, expense in enumerate(records):
            self.tree.insert(
                "", "end", iid=str(index),
                values=(expense["date"], expense["category"],
                        f'{expense["amount"]:.2f}', expense["description"])
            )

        total = sum(item["amount"] for item in self.expenses)
        self.total_label.config(text=f"Total spent: {total:.2f}")

    def add_expense(self):
        expense_date = self.date_var.get().strip()
        category = self.category_var.get().strip().lower() or "other"
        description = self.description_var.get().strip()

        try:
            datetime.strptime(expense_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Enter the date in YYYY-MM-DD format.")
            return

        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a number greater than 0.")
            return

        self.expenses.append({
            "date": expense_date,
            "category": category,
            "amount": amount,
            "description": description,
        })
        try:
            save_expenses(self.expenses)
        except OSError as error:
            self.expenses.pop()
            messagebox.showerror("Save error", str(error))
            return

        self.amount_var.set("")
        self.category_var.set("")
        self.description_var.set("")
        self.date_var.set(str(date.today()))
        self.refresh_table()
        messagebox.showinfo("Success", "Expense added successfully!")

    def search_expenses(self):
        term = self.search_var.get().strip().lower()
        if not term:
            messagebox.showwarning("Search", "Enter a category to search.")
            return
        matches = [
            (index, item) for index, item in enumerate(self.expenses)
            if item["category"] == term
        ]
        self.refresh_table([item for _, item in matches])
        if not matches:
            messagebox.showinfo("Search", f"No expenses found for '{term}'.")

    def show_all(self):
        self.search_var.set("")
        self.refresh_table()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Select an expense first.")
            return

        # Search results can be a filtered subset, so identify the selected row by its values.
        values = self.tree.item(selected[0], "values")
        match_index = next(
            (i for i, item in enumerate(self.expenses)
             if item["date"] == values[0]
             and item["category"] == values[1]
             and f'{item["amount"]:.2f}' == values[2]
             and item["description"] == values[3]),
            None
        )
        if match_index is None:
            messagebox.showerror("Delete", "Could not identify that expense. Refresh and try again.")
            return

        if messagebox.askyesno("Confirm delete", "Delete the selected expense?"):
            self.expenses.pop(match_index)
            save_expenses(self.expenses)
            self.refresh_table()

    def category_summary(self):
        if not self.expenses:
            messagebox.showinfo("Category Summary", "No expenses recorded yet.")
            return

        totals = {}
        for item in self.expenses:
            category = item["category"]
            totals[category] = totals.get(category, 0) + item["amount"]

        lines = [
            f"{category:<15} {amount:.2f}"
            for category, amount in sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
        ]
        messagebox.showinfo("Spending by Category", "\n".join(lines))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
