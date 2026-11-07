import csv
from datetime import date, datetime

FILE_NAME = "expenses.csv"


def load_expenses():
    expenses = []
    try:
        with open(FILE_NAME, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["amount"] = float(row["amount"])
                expenses.append(row)
    except FileNotFoundError:
        pass
    return expenses


def save_expenses(expenses):
    with open(FILE_NAME, "w", newline="") as f:
        fields = ["date", "category", "amount", "description"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(expenses)


def get_amount():
    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            return amount
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_date():
    while True:
        text = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if text == "":
            return str(date.today())
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("Invalid date format. Example: 2026-11-07")


def add_expense():
    expense_date = get_date()
    category = input("Enter category (food, travel, bills...): ").strip().lower()
    if category == "":
        category = "other"
    amount = get_amount()
    description = input("Enter description: ").strip()

    expenses = load_expenses()
    expenses.append({
        "date": expense_date,
        "category": category,
        "amount": amount,
        "description": description,
    })
    save_expenses(expenses)
    print("\nExpense added successfully!")


def print_table(expenses):
    print(f"\n{'No.':<5}{'Date':<13}{'Category':<12}{'Amount':>10}  Description")
    print("-" * 55)
    for i, e in enumerate(expenses, start=1):
        print(f"{i:<5}{e['date']:<13}{e['category']:<12}{e['amount']:>10.2f}  {e['description']}")


def view_expenses():
    expenses = load_expenses()
    if not expenses:
        print("\nNo expenses recorded yet.")
        return
    print_table(expenses)


def total_spent():
    expenses = load_expenses()
    total = sum(e["amount"] for e in expenses)
    print(f"\nTotal spent: {total:.2f}")


def category_summary():
    expenses = load_expenses()
    if not expenses:
        print("\nNo expenses recorded yet.")
        return

    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]

    print("\nSpending by category:")
    for category, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:<12}{amount:>10.2f}")


def search_expenses():
    term = input("Enter category to search: ").strip().lower()
    if term == "":
        print("Search cannot be empty.")
        return

    matches = [e for e in load_expenses() if e["category"] == term]
    if matches:
        print_table(matches)
        print(f"\nTotal for '{term}': {sum(e['amount'] for e in matches):.2f}")
    else:
        print(f"\nNo expenses found for category '{term}'.")


def delete_expense():
    expenses = load_expenses()
    if not expenses:
        print("\nNo expenses to delete.")
        return

    print_table(expenses)
    try:
        number = int(input("\nEnter the number of the expense to delete: "))
    except ValueError:
        print("Invalid input.")
        return

    if 1 <= number <= len(expenses):
        removed = expenses.pop(number - 1)
        save_expenses(expenses)
        print(f"\nDeleted: {removed['category']} - {removed['amount']:.2f}")
    else:
        print("Number out of range.")


def show_menu():
    print("\n===== Expense Tracker =====")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Total Spent")
    print("4. Spending by Category")
    print("5. Search by Category")
    print("6. Delete Expense")
    print("7. Exit")
    return input("Enter choice (1-7): ").strip()


def main():
    print("Welcome to Expense Tracker!")

    while True:
        choice = show_menu()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            total_spent()
        elif choice == "4":
            category_summary()
        elif choice == "5":
            search_expenses()
        elif choice == "6":
            delete_expense()
        elif choice == "7":
            print("Thank you for using Expense Tracker!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
