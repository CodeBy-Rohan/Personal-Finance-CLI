# Small Personal Finance 

import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


# Constants are values that the program reuses and should not change while it runs.
DATA_FILE = Path(__file__).with_name("finance_data.json")
ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def new_data():
    """Make the empty lists and dictionaries used by the program."""
    return {"transactions": [], "budgets": {}}


def parse_amount(value):
    """Convert saved text to a positive amount with no more than two decimals."""
    if not isinstance(value, str):
        raise ValueError("An amount in the save file must be text.")

    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("An amount in the save file is not a number.") from error

    if not amount.is_finite() or amount <= ZERO:
        raise ValueError("Saved amounts must be positive, finite numbers.")

    try:
        rounded_amount = amount.quantize(CENT)
    except InvalidOperation as error:
        raise ValueError("A saved amount is too large.") from error

    if amount != rounded_amount:
        raise ValueError("Saved amounts can have at most two decimal places.")
    return rounded_amount


def is_valid_month(month):
    """Return True only for a real month written as YYYY-MM."""
    try:
        return datetime.strptime(month, "%Y-%m").strftime("%Y-%m") == month
    except ValueError:
        return False


def load_data():
    """Read and check the JSON save file; return None if it cannot be trusted."""
    if not DATA_FILE.exists():
        return new_data()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as save_file:
            saved_data = json.load(save_file)

        if not isinstance(saved_data, dict):
            raise ValueError("The top-level JSON value must be an object.")
        transactions = saved_data.get("transactions")
        budgets = saved_data.get("budgets")
        if not isinstance(transactions, list) or not isinstance(budgets, dict):
            raise ValueError("The save file must contain transactions and budgets.")

        # Check each record before the rest of the program uses its fields.
        for transaction in transactions:
            if not isinstance(transaction, dict):
                raise ValueError("A transaction must be an object.")
            if transaction.get("type") not in ("income", "expense"):
                raise ValueError("A transaction has an unknown type.")
            if not isinstance(transaction.get("category"), str) or not transaction["category"].strip():
                raise ValueError("A transaction needs a category.")
            if not isinstance(transaction.get("note"), str):
                raise ValueError("A transaction note must be text.")
            transaction_date = transaction.get("date")
            if not isinstance(transaction_date, str):
                raise ValueError("A transaction date must be text.")
            if date.fromisoformat(transaction_date).isoformat() != transaction_date:
                raise ValueError("A transaction date must use YYYY-MM-DD format.")
            transaction["amount"] = parse_amount(transaction.get("amount"))

        for month, month_budgets in budgets.items():
            if not isinstance(month, str) or not is_valid_month(month):
                raise ValueError("A budget has an invalid month.")
            if not isinstance(month_budgets, dict):
                raise ValueError("Each month's budgets must be an object.")
            for category, amount in month_budgets.items():
                if not isinstance(category, str) or not category.strip():
                    raise ValueError("A budget needs a category.")
                month_budgets[category] = parse_amount(amount)

        return {"transactions": transactions, "budgets": budgets}
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("Could not load saved data: {}".format(error))
        print("The save file was left unchanged. Fix it before running the program again.")
        return None


def save_data(data):
    """Write JSON to a temporary file first, then replace the previous save."""
    save_data_as_text = {
        "transactions": [
            dict(transaction, amount=str(transaction["amount"]))
            for transaction in data["transactions"]
        ],
        "budgets": {
            month: {category: str(amount) for category, amount in month_budgets.items()}
            for month, month_budgets in data["budgets"].items()
        },
    }

    temporary_file = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
    with temporary_file.open("w", encoding="utf-8") as save_file:
        json.dump(save_data_as_text, save_file, indent=2)
        save_file.write("\n")
    temporary_file.replace(DATA_FILE)


def save_and_report(data):
    """Save changes and tell the user clearly if the save fails."""
    try:
        save_data(data)
    except OSError as error:
        print("Your change is in memory, but it could not be saved: {}".format(error))
    else:
        print("Saved to {}.".format(DATA_FILE.name))


def ask_amount(prompt):
    """Keep asking until the user enters a valid positive money amount."""
    while True:
        answer = input(prompt).strip()
        try:
            amount = Decimal(answer)
            if not amount.is_finite() or amount <= ZERO:
                raise InvalidOperation
            rounded_amount = amount.quantize(CENT)
            if amount != rounded_amount:
                print("Enter an amount with at most two decimal places.")
                continue
            return rounded_amount
        except InvalidOperation:
            print("Enter a positive number, such as 12 or 12.50.")


def ask_month():
    """Ask for a month in YYYY-MM format and make sure it exists."""
    while True:
        month = input("Month (YYYY-MM): ").strip()
        if is_valid_month(month):
            return month
        print("Enter a real month like 2026-03.")


def ask_transaction_date():
    """Ask for a transaction date, using today's date when left blank."""
    while True:
        answer = input("Date (YYYY-MM-DD, blank for today): ").strip()
        if not answer:
            return date.today().isoformat()
        try:
            return date.fromisoformat(answer).isoformat()
        except ValueError:
            print("Enter a real date like 2026-03-15.")


def ask_category():
    """Return a non-empty category name."""
    while True:
        category = input("Category: ").strip()
        if category:
            return category
        print("A category cannot be empty.")


def create_transaction(kind, amount, **details):
    """Build a transaction dictionary from its type, amount, and named details."""
    return {"type": kind, "amount": amount, **details}


def recursive_sum(amounts):
    """Add a list by splitting it in half, demonstrating a safe basic recursion."""
    if not amounts:
        return ZERO
    if len(amounts) == 1:
        return amounts[0]
    middle = len(amounts) // 2
    return recursive_sum(amounts[:middle]) + recursive_sum(amounts[middle:])


def sum_amounts(*amounts):
    """Accept any number of amounts (*args) and add them."""
    return recursive_sum(list(amounts))


def add_transaction(data, kind):
    """Ask questions, create an income or expense, save it, and check its budget."""
    amount = ask_amount("Amount: ")
    category = ask_category()
    transaction = create_transaction(
        kind,
        amount,
        category=category,
        date=ask_transaction_date(),
        note=input("Note (optional): ").strip(),
    )
    data["transactions"].append(transaction)
    save_and_report(data)

    if kind == "expense":
        warn_if_over_budget(data, transaction)


def set_budget(data):
    """Create or replace the budget for one category and month."""
    month = ask_month()
    category = ask_category()
    amount = ask_amount("Budget amount: ")
    data["budgets"].setdefault(month, {})[category] = amount
    save_and_report(data)


def warn_if_over_budget(data, transaction):
    """Compare this month's spending with the matching category budget."""
    month = transaction["date"][:7]
    month_budgets = data["budgets"].get(month, {})
    budget = next(
        (
            amount
            for category, amount in month_budgets.items()
            if category.casefold() == transaction["category"].casefold()
        ),
        None,
    )
    if budget is None:
        return

    spent = sum_amounts(
        *(
            item["amount"]
            for item in data["transactions"]
            if item["type"] == "expense"
            and item["date"][:7] == month
            and item["category"].casefold() == transaction["category"].casefold()
        )
    )
    if spent > budget:
        print("Warning: {} spending is {} over its {} budget.".format(
            transaction["category"], format_amount(spent - budget), format_amount(budget)
        ))


def format_amount(amount):
    """Show an amount with commas and exactly two decimal places."""
    return "{:,.2f}".format(amount)


def show_monthly_summary(data):
    """Print income, expenses, balance, and budget progress for one month."""
    month = ask_month()
    month_transactions = [
        item for item in data["transactions"] if item["date"][:7] == month
    ]
    income = sum_amounts(
        *(item["amount"] for item in month_transactions if item["type"] == "income")
    )
    expenses = sum_amounts(
        *(item["amount"] for item in month_transactions if item["type"] == "expense")
    )

    print("\nSummary for {}".format(month))
    print("Income:   {}".format(format_amount(income)))
    print("Expenses: {}".format(format_amount(expenses)))
    print("Balance:  {}".format(format_amount(income - expenses)))

    month_budgets = data["budgets"].get(month, {})
    if month_budgets:
        print("\nBudgets:")
        for category, budget in month_budgets.items():
            spent = sum_amounts(
                *(
                    item["amount"]
                    for item in month_transactions
                    if item["type"] == "expense"
                    and item["category"].casefold() == category.casefold()
                )
            )
            status = "OVER by {}".format(format_amount(spent - budget)) if spent > budget else "within budget"
            print("- {}: {} spent / {} budget ({})".format(
                category, format_amount(spent), format_amount(budget), status
            ))
    if not month_transactions:
        print("\nNo transactions recorded for this month.")


def list_transactions(data):
    """Print every saved transaction in the order it was entered."""
    if not data["transactions"]:
        print("No transactions yet.")
        return

    for item in data["transactions"]:
        print("{} | {:7} | {:12} | {}".format(
            item["date"],
            item["type"].title(),
            format_amount(item["amount"]),
            item["category"],
        ))
        if item["note"]:
            print("  Note: {}".format(item["note"]))


def main():
    """Run the menu until the user chooses to exit."""
    data = load_data()
    if data is None:
        return

    while True:
        print("\nPersonal Finance")
        print("1. Add income")
        print("2. Add expense")
        print("3. Set monthly budget")
        print("4. Show monthly summary")
        print("5. List transactions")
        print("6. Exit")
        choice = input("Choose 1-6: ").strip()

        if choice == "1":
            add_transaction(data, "income")
        elif choice == "2":
            add_transaction(data, "expense")
        elif choice == "3":
            set_budget(data)
        elif choice == "4":
            show_monthly_summary(data)
        elif choice == "5":
            list_transactions(data)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Choose a menu number from 1 to 6.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
