import html
import sqlite3 as sq
import requests as r
import re
import jellyfish as jf

from utils import *
from bs4 import BeautifulSoup
from openpyxl.styles import *
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

def printC(name, message, color=None):
    # Adding padding at the end of the message
    for i in range(60 - len(message)):
        message += ' '

    if not color == None:
        print(f"     > {color}{message}{bcolors.ENDC}: '{name}'")
    else:
        print(f"     > {message}: '{name}'")

def choose_from_selection(selection):
    for i, s in enumerate(selection):
        print(f"[{i + 1}] {s[1]}")

    print("\nWähle aus welchen Manga du hinzufügen möchtest.")

    choise = get_int_input_in_range((1, len(selection)))

    return selection[choise - 1]

def get_manga(name):
    print(f"Lädt '{name}'...")

    # Finding the manga page from name
    search_name = name.replace(" ", "+")

    search_link = "https://www.mangaguide.de/index.php?include=24&suche=" + search_name
    search_page = r.get(search_link)

    # Checking for multiple results
    search_results = BeautifulSoup(search_page.content, "html.parser").find(id="inhalt").find_all("a")

    # No search result was found
    if len(search_results) == 0:
        return None

    # Only one search result is found
    if len(search_results) == 1:
        result = (search_results[0]['href'], search_results[0].text)
        print_color(f"\nDer Manga '{search_results[0].text}' wurde gefunden!", bcolors.OKGREEN)
    # Multitiple search results have been found
    else:
        for i in range(len(search_results) - 1, -1, -1):
            # Remove manga wich are just editions of other manga
            # Remove manga '1214' because it's a duplicate
            if "edition" in search_results[i]['href'] or "manga_id=1214" in search_results[i]['href']:
                search_results.pop(i)
                continue
            # Saving results as an tuple of the link to the manga and the name of it
            search_results[i] = (search_results[i]['href'], search_results[i].text)

        # If now only one search result is left just skip picking on of the results
        if len(search_results) == 1:
            print_color(f"\nDer Manga '{search_results[0][1]}' wurde gefunden!", bcolors.OKGREEN)
            result = search_results[0]
        else:
            print_color(f"\nEs wurden mehrere Suchergebnisse gefunden!",  bcolors.OKGREEN)
            result = choose_from_selection(search_results)

    print_color(f"\nLädt '{result[1]}'!", bcolors.OKGREEN)

    manga_link = "https://www.mangaguide.de/" + result[0]
    manga_page = r.get(manga_link)
    manga_data = BeautifulSoup(manga_page.content, "html.parser").find(id="inhalt")

    # Getting basic Information [Title, Author, Max_Count]
    #title
    tr_tags = manga_data.find("table").find_all("tr")

    # The title is always the first tr tag
    manga_title = tr_tags[0].find("td").text
    printC(result[1], "Es wurde erfolgreich der Manga Title geladen!", bcolors.OKGREEN)

    # Author
    # Searching for the a tag with the 'mangaka_id' in the 'href' to get the author
    author = None
    a_tags = manga_data.find_all("a")
    for a in a_tags:
        if a.has_attr('href'):
            if "mangaka_id=" in a['href']:
                author = a.text
                printC(author, "Es wurde erfolgreich der Manga Author geladen!", bcolors.OKGREEN)
                break
    
    # Checking if the author has been found
    if author == None:
        printC("-", "Das Laden des Manga Authors ist fehlgeschlagen!", bcolors.FAIL)
        author = "Error"

    # Max count
    try:
        # Getting the text where the maximal count of a Manga is stored
        max_count_text = manga_page.text.split("nglich erschien")[1]
        # Getting from the text the number
        max_count = int(re.findall(r'\d+', max_count_text)[0])
        printC(max_count, "Es wurde erfolgreich die maximale Manga Anzahl geladen!", bcolors.OKGREEN)
    except:
        printC("-", "Das Laden der maximalen Manga Anzahl ist fehlgeschlagen!", bcolors.FAIL)
        max_count = -1

    # Genre
    # Searching for the a tag with the 'kategorie=' in the 'href' to get the genre
    genre = None
    for a in a_tags:
        if a.has_attr('href'):
            if "kategorie=" in a['href']:
                genre = a['href'].split("kategorie=")[1]
                printC(genre, "Es wurde erfolgreich das Manga Genre geladen!", bcolors.OKGREEN)
                break

    # Checking if the genre has been found
    if genre == None:
        printC("-", "Das Laden des Manga Genre ist fehlgeschlagen!", bcolors.FAIL)
        genre = "Error"

    # German count
    try:
        # Getting the text where the german count is stored
        german_count_text = manga_page.text.split("auf Deutsch erschienen.")[0][-20:]
        # Getting from the text the numbers
        temp = re.findall(r'\d+', german_count_text)
        # Checking if there is actually a number or just 'ein'
        if len(temp) == 0:
            german_count = 1
        else:
            german_count = int(temp[0])

        printC(german_count, "Es wurde erfolgreich die Anzahl der deutschen Manga geladen!", bcolors.OKGREEN)
    except:
        printC("-", "Das Laden der Anzahl der deutschen Manga ist fehlgeschlagen!", bcolors.FAIL)
        german_count = -1

    # Cost
    # Going throgh all of the volumes of the Manga to get a cost if the fist few dont have one given
    cost = -1
    for i in manga_data.find_all("td", {"class": "bandtext"}):
        try:
            cost_text = i.text.split("Kaufpreis: ")[1]
            cost_nums = re.findall(r'\d+', cost_text)
            cost = int(cost_nums[0]) + (int(cost_nums[1]) / 100)
            printC(cost, "Es wurden erfolgreich die Manga kosten geladen!", bcolors.OKGREEN)
            break
        except:
            cost = -1
    
    # If it dosnt find any price in all the volumes
    if cost == -1:
        printC("-", "Das Laden der Manga kosten ist fehlgeschlagen!", bcolors.FAIL)
    
    # Cover
    # Getting the cover-link beging with the 2nd char to not get the '.' at the beginning
    try:
        cover_link = manga_data.find("td", {"class": "cover"}).find("a")["href"][1:]
        cover = "https://www.mangaguide.de" + cover_link
        printC(cover, "Es wurde erfolgreich das Manga Cover geladen!", bcolors.OKGREEN)
    except:
        try:
            cover_link = manga_data.find("td", {"class": "cover"}).find("img")["src"][1:]
            cover = "https://www.mangaguide.de" + cover_link
            printC(cover, "Es wurde erfolgreich das Manga Cover geladen!", bcolors.OKGREEN)
        except:
            try:
                cover_link = manga_data.find("td", {"class": "japcover"}).find("a")["href"][1:]
                cover = "https://www.mangaguide.de" + cover_link
                printC(cover, "Es wurde erfolgreich das Manga Cover geladen!", bcolors.OKGREEN)
            except:
                printC("-", "Das Laden des Manga Covers ist fehlgeschlagen!", bcolors.FAIL)
                cover = None

    return {"name": manga_title, "author": author, "max_count": max_count, "german_count": german_count, "genre": genre, "cost": cost, "cover": cover}

if __name__ == "__main__":
    print(get_manga("bj alex"))