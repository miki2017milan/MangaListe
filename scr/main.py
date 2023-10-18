import shutil as sh

from utils import *

from LoadToExcel import add_to_excel_file
from GetManga import get_manga, get_int_input_in_range
from tkinter import filedialog
from os import system

# Checks if given path is valid
def path_is_valid(path):
    try:
        file = open(path, "r")
        file.close()
    # Checking if file exists
    except FileNotFoundError:
        if not path == "":
            print_color(f"Die Liste vom angegebenen path exestiert nicht! [{path}]", bcolors.FAIL)
        return False
    # except PermissionError:
    #     print(f"{bcolors.FAIL}Du musst die Excel-Datei geschlossen haben um das Programm zu benutzen!{bcolors.ENDC}")
    #     input("Drücke 'Enter' um das Programm zu beenden.")
    #     exit()

    # Checking if it is an excel file
    if not path[-5:] == ".xlsx":
        if not path == "":
            print_color(f"Die Liste vom angegebenen path ist keine Excel-Datei! [{path}]", bcolors.FAIL)
        return False
    
    return True

# Adding a manga to a list
def adding(path):
    print("Manga zu einer Liste hinzufügen.\n")

    if path == "":
        print(f"{bcolors.FAIL}Du hast noch keine Liste ausgewählt!{bcolors.ENDC}")
        input("Drücke 'Enter' um zurückzukehren...")
        return

    manga_name = input("Gib den Manga namen ein: ('0' um zurückzukehren)")

    if manga_name == "0":
        clear()
        return

    manga_data = get_manga(manga_name)

    if manga_data is None:
        print_color(f"\nDie Suche brachte keine Ergebnisse. (Suche auf 'https://www.mangaguide.de/', wie man den Manga schreibt!)", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        clear()
        return

    manga_count = input_int("\nWie viele hast du davon?: ")

    add_to_excel_file(path, manga_data, manga_count)

# Loading path from file
try:
    with open("path.txt", "r") as file:
        path = file.readline()

    if not path_is_valid(path):
        path = ""
# Sets path to "" if it dosn't exist
except FileNotFoundError:
    with open("path.txt", "w") as file:
        path = ""

clear()
while True:
    # Welcome Screen
    print("Willkommen bei der Manga Bibliothek!")

    print(f"\n[1] Manga zur Liste hinzufügen.")

    if path == "":
        print(f"\n[2] Path zur Liste ändern.\n    Akutueller Path: {bcolors.FAIL}Noch keinen path angegeben.{bcolors.ENDC}")
    else:
        print(f"\n[2] Path zur Liste ändern.\n    Akutueller Path: {bcolors.OKGREEN}[{path}]{bcolors.ENDC}")

    print(f"\n[3] Neue Liste erstellen.")
    print(f"\n[4] Liste öffnen.")
    print(f"\n[5] Programm beenden.")

    # Choosing action
    choice = get_int_input_in_range((1, 5))

    clear()
    # Adding Manga
    if choice == 1:
        

    if choice == 2:
        print("Path zur Liste ändern.")
        temp_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not temp_path == "":
            path = temp_path

            with open("path.txt", "w+") as file:
                file.write(path)

    # Closeing the Program
    if choice == 3:
        cls()
        print("Neue liste erstellen.")
        print("\nWie soll die Liste heißen? (Keine Sonderzeichen!)")
        name = input("  > ")
        if not name == "":
            temp_path = filedialog.askdirectory()
            if not temp_path == "":
                sh.copy2("Blank.xlsx", temp_path + "\\" + name + ".xlsx")

    if choice == 4:
        cls()
        print("Liste wird geöffnet...")

        system(path)
        
    if choice == 5:
        exit()

    cls()