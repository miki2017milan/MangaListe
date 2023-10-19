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

def getting_manga_page(name):
    # Finding the manga page from name
    search_name = name.replace(" ", "+")

    search_link = "https://www.mangaguide.de/index.php?include=24&suche=" + search_name
    try:
        search_page = r.get(search_link)
    except r.exceptions.MissingSchema:
        return None

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
    return "https://www.mangaguide.de/" + result[0]

def get_manga_title(manga_data):
    manga_title = manga_data.find("table").find_all("tr")[0].find("td").text
    printC(manga_title, "Es wurde erfolgreich der Manga Title geladen!", bcolors.OKGREEN)

    return manga_title

def get_manga_author(a_tags):
    # Searching for the a tag with the 'mangaka_id' in the 'href' to get the author
    for a in a_tags:
        if a.has_attr('href'):
            if "mangaka_id=" in a['href']:
                author = a.text
                printC(author, "Es wurde erfolgreich der Manga Author geladen!", bcolors.OKGREEN)
                return author
    
    printC("-", "Das Laden des Manga Authors ist fehlgeschlagen!", bcolors.FAIL)
    return "Error"

def get_manga_max_count(manga_page):
    try:
        # Getting the text where the maximal count of a Manga is stored
        max_count_text = manga_page.text.split("nglich erschien")[1]
        # Getting from the text the number
        max_count = int(re.findall(r'\d+', max_count_text)[0])
        printC(max_count, "Es wurde erfolgreich die maximale Manga Anzahl geladen!", bcolors.OKGREEN)

        return max_count
    except:
        printC("-", "Das Laden der maximalen Manga Anzahl ist fehlgeschlagen!", bcolors.FAIL)
        return -1

def get_manga_genre(a_tags):
    # Searching for the a tag with the 'kategorie=' in the 'href' to get the genre
    for a in a_tags:
        if a.has_attr('href'):
            if "kategorie=" in a['href']:
                genre = a['href'].split("kategorie=")[1]
                printC(genre, "Es wurde erfolgreich das Manga Genre geladen!", bcolors.OKGREEN)
                return genre
    
    printC("-", "Das Laden des Manga Genre ist fehlgeschlagen!", bcolors.FAIL)
    return "Error"

def get_manga_german_count(manga_page):
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
        return german_count
    except:
        printC("-", "Das Laden der Anzahl der deutschen Manga ist fehlgeschlagen!", bcolors.FAIL)
        return -1

def get_manga_cost(manga_data):
    # Going throgh all of the volumes of the Manga to get a cost if the fist few dont have one given
    cost = -1
    for i in manga_data.find_all("td", {"class": "bandtext"}):
        try:
            cost_text = i.text.split("Kaufpreis: ")[1]
            cost_nums = re.findall(r'\d+', cost_text)
            cost = int(cost_nums[0]) + (int(cost_nums[1]) / 100)

            printC(cost, "Es wurden erfolgreich die Manga kosten geladen!", bcolors.OKGREEN)
            return cost
        except:
            return -1
    
    printC("-", "Das Laden der Manga kosten ist fehlgeschlagen!", bcolors.FAIL)
    return -1

def get_manga_cover(manga_data):
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

    return cover

def get_finished(manga_data):
    try:
        finished = False if manga_data.find("span")['class'][0] == "laeuft" else True
        printC(finished, "Es wurden erfolgreich die Manga Abgeschlossenkheit geladen!", bcolors.OKGREEN)
        return finished
    except:
        printC("-", "Das Laden der Manga Abgeschlossenkheit ist fehlgeschlagen!", bcolors.FAIL)

def get_manga(name):
    print(f"Lädt '{name}'...")

    manga_link = getting_manga_page(name)

    if manga_link is None:
        return None

    manga_page = r.get(manga_link)
    manga_data = BeautifulSoup(manga_page.content, "html.parser").find(id="inhalt")
    a_tags = manga_data.find_all("a")

    return {"name": get_manga_title(manga_data), 
            "author": get_manga_author(a_tags), 
            "max_count": get_manga_max_count(manga_page), 
            "german_count": get_manga_german_count(manga_page), 
            "genre": get_manga_genre(a_tags), 
            "cost": get_manga_cost(manga_data), 
            "cover": get_manga_cover(manga_data), 
            "finished": get_finished(manga_data),
            "link": manga_link}

if __name__ == "__main__":
    get_manga("bj alex")
    get_manga("given")
    get_manga("to your et")