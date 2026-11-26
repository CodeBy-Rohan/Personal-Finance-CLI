# Personal Finance CLI

A command-line tracker for income, expenses, and monthly budgets, written in Python. Data is stored in a local JSON file, so there is nothing to install or set up.

## Features

- Add income and expenses with a category, date, and optional note
- Set a monthly budget for each category
- Get a warning when an expense pushes a category over its budget
- View a monthly summary: income, expenses, balance, and budget status
- List all saved transactions
- Input validation on every prompt, so bad entries are rejected and asked again
- Safe saving and loading that protects your data from corruption

## Requirements

- Python 3.8 or newer
- No external libraries (standard library only)

## How to run

```
git clone https://github.com/YOUR-USERNAME/finance-cli.git
cd finance-cli
python finance.py
```

On some systems, use `python3` instead of `python`.

The save file `finance_data.json` is created in the same folder as the script the first time you add data.

## Menu

| Option | What it does |
| --- | --- |
| 1 | Add income |
| 2 | Add expense |
| 3 | Set monthly budget |
| 4 | Show monthly summary |
| 5 | List transactions |
| 6 | Exit |

## Sample session

```
Personal Finance
1. Add income
2. Add expense
3. Set monthly budget
4. Show monthly summary
5. List transactions
6. Exit
Choose 1-6: 3
Month (YYYY-MM): 2026-11
Category: Food
Budget amount: 5000
Saved to finance_data.json.

Choose 1-6: 2
Amount: 5200
Category: Food
Date (YYYY-MM-DD, blank for today):
Note (optional): Groceries
Saved to finance_data.json.
Warning: Food spending is 200.00 over its 5,000.00 budget.
```

> Replace this with real output from your own run before publishing.

## Design decisions

- **`Decimal` instead of `float`.** Floats give errors like `0.1 + 0.2 = 0.30000000000000004`, which is not acceptable for money. All amounts use `Decimal` and are limited to two decimal places.
- **Amounts stored as strings in JSON.** JSON cannot store `Decimal` values, so amounts are saved as text and converted back when the file is loaded.
- **Atomic saves.** Data is written to a temporary file first, then it replaces the real save file. A crash in the middle of a write cannot corrupt existing data.
- **Validation on load.** The program checks every transaction and budget in the file. If anything is invalid, it prints the problem and exits without touching the file, so nothing is overwritten.
- **Case-insensitive categories.** Matching uses `casefold()`, so "Food" and "food" count as the same category when checking budgets.
- **Balanced recursive sum.** Totals are calculated by splitting the list in half and adding each half. This keeps recursion shallow, so long lists do not hit Python's recursion limit.

## Project structure

```
finance-cli/
  finance.py          main program
  finance_data.json   created on first save (not committed)
  README.md
  .gitignore
```

## What I learned

- Why floating point numbers are risky for money, and how `Decimal` fixes it
- How to validate untrusted input, both from the user and from a file
- How to save data safely with a temp file and replace
- How to structure a program into small functions with one job each
