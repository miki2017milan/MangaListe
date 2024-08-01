import os

def input_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  Du musst eine Zahl eingeben!")

def get_int_input_in_range(maxmin):
    while True:
        choice = input_int("> ")

        if not choice in range(maxmin[0], maxmin[1] + 1):
            print(f"  Du musst eine Zahl eingeben zwischen {maxmin[0]}-{maxmin[1]}")
            continue
        return choice

clear = lambda: os.system("cls & color 7")