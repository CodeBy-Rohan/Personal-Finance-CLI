# Small Personal Finance 

def main():
    data = load_data()
    if data is None:
        return 

    while True:
        print("\n Personal Finance CLI")
        print("1. Add income")
        print("2. Add expense")
        print("3. Set monthly budget")
        print("4. Show monthly summary")
        print("5. List transactions")
        print("6. Exit")
        choice = input("Choose 1-6: ").strip()
