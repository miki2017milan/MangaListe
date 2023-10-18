import openpyxl as px
import shutil as sh
import os
import requests as r

from utils import *
from GetManga import *

from LoadToExcel import *
from tkinter import filedialog

prefix = ""

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

    # Checking if it is an excel file
    if not path[-5:] == ".xlsx":
        if not path == "":
            print_color(f"Die Liste vom angegebenen path ist keine Excel-Datei! [{path}]", bcolors.FAIL)
        return False
    
    return True

# Adding a manga to a list
def adding_manga(path):
    print("Manga zu einer Liste hinzufügen.\n")

    if path == "":
        print(f"Du hast noch keine Liste ausgewählt!", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        return

    manga_name = input("Gib den Manga namen ein ('0' um zurückzukehren): ")

    if manga_name == "0":
        clear()
        return

    manga_data = get_manga(manga_name)

    # Manga coundn't be found
    if manga_data is None:
        print_color(f"\nDie Suche brachte keine Ergebnisse. (Suche auf 'https://www.mangaguide.de/', wie man den Manga schreibt!)", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        clear()
        return

    manga_count = input_int("\nWie viele hast du davon? ('0' um zurückzukehren): ")

    if manga_count == 0:
        clear()
        return

    add_to_excel_file(path, manga_data, manga_count)

def update_list(path):
    print(f"\nLädt '{bcolors.OKBLUE}{path}{bcolors.ENDC}'...")
    try:
        wb = px.load_workbook(path)
        print_color("Datai wurde erfolgreich geladen!\n", bcolors.OKGREEN)
    except FileNotFoundError:
        print_color("Datei wurde nicht gefunden!\n", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        return False

    sheet = wb.active

    manga = []
    for i, row in enumerate(sheet['B']):
        if i < 4:
            continue

        if row.value is None:
            break
        else:
            manga.append((row.value, row.hyperlink.target))

    new_manga_data = []

    for m in manga:
        manga_page = r.get(m[1])
        print(f"Lädt '{m[0]}'...")
        new_manga_data.append((get_manga_german_count(manga_page), get_manga_max_count(manga_page)))

    # TODO make it a for loop
    index = 0
    while True:
        counts_cell = "F" + str(index + 5)
        if sheet[counts_cell].value is None:
            break

        sheet[counts_cell].font = count_font
        sheet[counts_cell].alignment = aline
        sheet[counts_cell].fill = fill
        sheet[counts_cell].border = border
        if new_manga_data[index][1] == new_manga_data[index][0]:
            sheet[counts_cell] = new_manga_data[index][1]
        else:
            sheet[counts_cell] = str(new_manga_data[index][0]) + "/" + str(new_manga_data[index][1])

        index += 1

    wb.save(path)
    input("Drücke 'Enter' um zurückzukehren...")

# Loading path from file
try:
    with open(prefix + "path.txt", "r") as file:
        path = file.readline()

    if not path_is_valid(path):
        path = ""
# Sets path to "" if it dosn't exist
except FileNotFoundError:
    with open(prefix + "path.txt", "w") as file:
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
    print(f"\n[5] Liste aktualisieren.")
    print(f"\n[6] Programm beenden.")

    # Choosing action
    choice = get_int_input_in_range((1, 6))

    clear()

    # Adding Manga
    if choice == 1:
        adding_manga(path)
    
    # Changing the path to the list
    if choice == 2:
        print("Path zur Liste ändern.")

        # Opening file explorer to select a list
        temp_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

        # If a file has been selected
        if not temp_path == "":
            path = temp_path

            # Saving the new file path in the path.txt
            with open(prefix + "path.txt", "w+") as file:
                file.write(path)

    # Creating a new list
    if choice == 3:
        clear()
        print("Neue liste erstellen.")
        print("\nWie soll die Liste heißen? (Keine Sonderzeichen!): ")
        name = input("  > ")
        if not name == "":
            # Opening the file explorer for selecting a directory for the new list
            temp_path = filedialog.askdirectory()
            if not temp_path == "":
                # Copying and renameing the blank list to the selected directory
                sh.copy2("Blank.xlsx", temp_path + "\\" + name + ".xlsx")

    # Opeining the list
    if choice == 4:
        clear()
        print("Liste wird geöffnet...")

        os.system(path)

    # Update list
    if choice == 5:
        update_list(path)
        
    # Closeing the program
    if choice == 6:
        exit()


    clear()
