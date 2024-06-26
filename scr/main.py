import openpyxl as px
import requests as r
import shutil as sh
import os

from utils import *
from manga_information import *

from LoadToExcel import *
from tkinter import filedialog

PREFIX = "scr\\"

# Checks if given path is valid
def path_is_valid(path):
    if not os.path.isfile(path):
        print_color(f"Die Liste vom angegebenen path exestiert nicht! [{path}]", bcolors.FAIL)
        return False

    # Checking if it is an excel file
    if not path.endswith(".xlsx"):
        print_color(f"Die Liste vom angegebenen path ist keine Excel-Datei! [{path}]", bcolors.FAIL)
        return False

    return True

# Adding a manga to a list
def adding_manga(path):
    if path == "":
        print("Du hast noch keine Liste ausgewählt!", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        return

    manga_name = input("Gib den Manga namen ein ('0' um zurückzukehren): ")

    if manga_name == "0":
        clear()
        return

    manga_data = get_manga(manga_name)

    # Manga coundn't be found
    if not manga_data:
        print_color(f"\nDie Suche brachte keine Ergebnisse. (Suche auf 'https://www.mangaguide.de/', wie man den Manga schreibt!)", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        clear()
        return

    # Getting how many manga the user has
    manga_count = input_int("\nWie viele hast du davon? ('0' um zurückzukehren): ")

    if manga_count == 0:
        clear()
        return

    # Adding the manga to the excel list
    add_to_excel_file(path, manga_data, manga_count)
    input("Drücke 'Enter' um zurückzukehren...")

def update_list(path):
    # Opening the list
    print(f"\nLädt '{bcolors.OKBLUE}{path}{bcolors.ENDC}'...")
    try:
        wb = px.load_workbook(path)
        print_color("Datai wurde erfolgreich geladen!\n", bcolors.OKGREEN)
    except FileNotFoundError:
        print_color("Datei wurde nicht gefunden!\n", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        return False

    sheet = wb.active

    # Getting all the names and hyperlinks from the list
    manga = [] # (name, link)
    for i, row in enumerate(sheet['B']):
        if i < 4:
            continue

        if row.value:
            manga.append((row.value, row.hyperlink.target))
            continue
        break

    # Loading the new count of german manga and the max realeased amount
    new_manga_data = []

    for m in manga:
        manga_page = r.get(m[1])
        manga_data = BeautifulSoup(manga_page.content, "html.parser").find(id="inhalt")

        print(f"Lädt '{m[0]}'...")
        new_manga_data.append((get_manga_german_count(manga_page), get_manga_max_count(manga_page), get_finished(manga_data)))

    # Loading the new data into the excel file
    for i, n in enumerate(new_manga_data):
        # German max / Count max
        counts_cell = "F" + str(i + 5)

        sheet[counts_cell].font = count_font_lauft if not n[2] else count_font
        sheet[counts_cell].alignment = aline
        sheet[counts_cell].fill = fill
        sheet[counts_cell].border = border
        sheet[counts_cell].number_format = "@"

        if n[0] == n[1]:
            sheet[counts_cell] = n[1]
        else:
            sheet[counts_cell] = str(n[0]) + "/" + str(n[1])

    wb.save(path)
    print_color("\nDie Liste wurde erfolgreich aktualisiert!\n", bcolors.OKGREEN)
    input("Drücke 'Enter' um zurückzukehren...")

def create_list():
    name = input("\nWie soll die Liste heißen? ('0' um zurückzukehren): ")

    if not name:
        print_color(f"Gib einen validen Namen ein!\n", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        clear()
        return

    if name == "0":
        clear()
        return
    
    # Opening the file explorer for selecting a directory for the new list
    temp_path = filedialog.askdirectory()

    if temp_path:
        # Copying and renameing the blank list to the selected directory
        target = temp_path + "/" + name + ".xlsx"
        sh.copy2(PREFIX + "Blank.xlsx", target)

    return target

# Beginnig of the program
clear()

# Loading path from file
if os.path.exists(PREFIX + "path.txt"):
    with open(PREFIX + "path.txt", "r") as file:
        path = file.readline()

    if not path_is_valid(path):
        path = ""
else:
    with open(PREFIX + "path.txt", "w"): pass

    path = ""

while True:
    # Welcome Screen
    print("\nWillkommen bei der Manga Bibliothek!")

    print(f"\n[1] Manga zur Liste hinzufügen.")

    if path == "":
        print(f"\n[2] Path zur Liste ändern.\n    Akutueller Path: {bcolors.FAIL}Noch keinen path angegeben.{bcolors.ENDC}")
    else:
        print(f"\n[2] Path zur Liste ändern.\n    Akutueller Path: {bcolors.OKGREEN}[{path}]{bcolors.ENDC}")

    print(f"\n[3] Neue Liste erstellen.")
    print(f"\n[4] Liste öffnen.")
    print(f"\n[5] Liste aktualisieren.")
    print(f"\n[6] Liste aus Vorlage erstellen.")
    print(f"\n[7] Programm beenden.")

    # Choosing action
    choice = get_int_input_in_range((1, 7))

    clear()

    # Adding Manga
    if choice == 1:
        print("Manga zu einer Liste hinzufügen.\n")
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
            with open(PREFIX + "path.txt", "w+") as file:
                file.write(path)

    # Creating a new list
    if choice == 3:
        clear()
        print("Neue Liste erstellen.")

        temp_path = create_list()

        if temp_path:
            path = temp_path
            # Saving the new file path in the path.txt
            with open(PREFIX + "path.txt", "w+") as file:
                file.write(path)

    # Opeining the list
    if choice == 4:
        clear()
        print("Liste wird geöffnet...")

        os.system(path)

    # Update list
    if choice == 5:
        update_list(path)

    if choice == 6:
        print("Neue Liste aus einer Vorlage erstellen.")
        print("\nWähle eine Vorlage als '.txt' Datei in diesem Format aus:\n-----------------------------------------------")
        print_color("Name des Manga\nAnzahl der Manga die du von diesem Manga besitzt", bcolors.OKCYAN)
        print("-----------------------------------------------")
        print("Als Beispiel:\n-----------------------------------------------")
        print_color("Naruto\n15\nTokyo Ghul\n5\nOne Punche Man\n31", bcolors.OKCYAN)
        print("-----------------------------------------------")
        input("Drücke 'Enter' um zurückzukehren...")

        preset_path = filedialog.askopenfilename(filetypes=[("Textdatei", ".txt")])

        if not preset_path:
            clear()
            continue

        if not os.path.exists(preset_path):
            print_color(f"Vorlage wurde nicht gefunden! [{preset_path}]\n", bcolors.FAIL)
            input("Drücke 'Enter' um zurückzukehren...")
            clear()
            continue

        if not preset_path.endswith(".txt"):
            print_color(f"Vorlage muss mit .txt enden! [{preset_path}]\n", bcolors.FAIL)
            input("Drücke 'Enter' um zurückzukehren...")
            clear()
            continue

        path = create_list()

        # Saving the new file path in the path.txt
        with open(PREFIX + "path.txt", "w+") as file:
            file.write(path)

        # Read manga from list
        manga = []
        with open(preset_path, "r") as file:
            manga = file.readlines()

        # Remove new line char
        for i in range(len(manga)):
            manga[i] = manga[i].replace("\n", "")

        for m in range(0, len(manga), 2):
            add_to_excel_file(path, get_manga(manga[m]), int(manga[m + 1]))

        print_color(f"Die Manga wurden erfolgreich zur Liste '{path}' hinzugefügt!\n", bcolors.OKGREEN)
        input("Drücke 'Enter' um zurückzukehren...")
        
    # Closeing the program
    if choice == 7:
        exit()


    clear()
