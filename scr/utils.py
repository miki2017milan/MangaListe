import os

# Color codes
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def input_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print_color("  Du musst eine Zahl eingeben!", bcolors.FAIL)

def get_int_input_in_range(maxmin):
    while True:
        choice = input_int("> ")

        if not choice in range(maxmin[0], maxmin[1] + 1):
            print_color(f"  Du musst eine Zahl eingeben zwischen {maxmin[0]}-{maxmin[1]}", bcolors.FAIL)
            continue
        return choice

print_color = lambda msg, color: print(f"{color}{msg}{bcolors.ENDC}")
clear = lambda: os.system("cls & color 7")