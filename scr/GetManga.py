import html
import sqlite3 as sq
import requests as r
import re
import jellyfish as jf

from bs4 import BeautifulSoup
from openpyxl.styles import *
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

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

def printC(name, message, color=None):
    # Adding spaces so that the string is 9 chars long to make it look better
    for i in range(43 - len(message)):
        message += ' '

    if not color == None:
        print(f"     > {color}{message}{bcolors.ENDC}: '{name}'")
    else:
        print(f"     > {message}: '{name}'")

def get_int_input_in_range(maxmin):
    while True:
        try:
            choice = int(input("> "))
            if not choice in range(maxmin[0], maxmin[1] + 1):
                print(f"{bcolors.FAIL}  Du musst eine Zahl eingeben zwischen {maxmin[0]}-{maxmin[1]}{bcolors.ENDC}")
                continue
            break
        except ValueError:
            print(f"{bcolors.FAIL}  Du musst eine Zahl eingeben!{bcolors.ENDC}")

    return choice

def choose_from_selection(selection):
    for i, s in enumerate(selection):
        print(f"[{i + 1}] {s[1]}")

    print("\nWähle aus welchen Manga du hinzufügen möchtest.")

    choise = get_int_input_in_range((1, len(selection)))

    return selection[choise - 1]

def get_manga(name):
    print(f"Loading '{name}'...")

    # Finding the manga page from name
    search_name = name.replace(" ", "+")

    search_link = "https://www.mangaguide.de/index.php?include=24&suche=" + search_name
    search_page = r.get(search_link)

    # Checking for multiple results
    search_results = BeautifulSoup(search_page.content, "html.parser").find(id="inhalt").find_all("a")

    if len(search_results) == 0:
        return None

    if len(search_results) == 1:
        result = (search_results[0]['href'], search_results[0].text)
        print(f"{bcolors.OKGREEN}\nFound '{search_results[0].text}'!{bcolors.ENDC}")
    else:
        for i in range(len(search_results) - 1, -1, -1):
            if "edition" in search_results[i]['href'] or "manga_id=1214" in search_results[i]['href']:
                search_results.pop(i)
                continue
            search_results[i] = (search_results[i]['href'], search_results[i].text)

        if len(search_results) == 1:
            print(f"{bcolors.OKGREEN}\nFound '{search_results[0][1]}'!{bcolors.ENDC}")
            result = search_results[0]
        else:
            print(f"{bcolors.OKGREEN}\nFound multiple results!{bcolors.ENDC}")
            result = choose_from_selection(search_results)
            print(f"{bcolors.OKGREEN}\nLoading '{result[1]}'!{bcolors.ENDC}")

    manga_link = "https://www.mangaguide.de/" + result[0]
    manga_page = r.get(manga_link)
    manga_data = BeautifulSoup(manga_page.content, "html.parser").find(id="inhalt")

    """Title"""
    # Getting basic Information [Title, Author, Max_Count]
    tr_tags = manga_data.find("table").find_all("tr")

    # The title is always the first tr tag
    manga_title = tr_tags[0].find("td").text
    printC(result[1], "Successfully loaded the Manga title!", bcolors.OKGREEN)

    """Author"""
    # Searching for the a tag with the 'mangaka_id' in the 'href' to get the author
    author = None
    a_tags = manga_data.find_all("a")
    for a in a_tags:
        if a.has_attr('href'):
            if "mangaka_id=" in a['href']:
                author = a.text
                printC(author, "Successfully loaded the Manga author!", bcolors.OKGREEN)
                break
    
    # Checking if the author has been found
    if author == None:
        printC("-", "Failed to load the Manga author!", bcolors.FAIL)
        author = "Error"

    """Max Count"""
    try:
        # Getting the text where the maximal count of a Manga is stored
        max_count_text = manga_page.text.split("nglich erschien")[1]
        # Getting from the text the number
        max_count = int(re.findall(r'\d+', max_count_text)[0])
        printC(max_count, "Successfully loaded the Manga max count!", bcolors.OKGREEN)
    except Exception as e:
        printC("-", "Failed to load the Manga max count!", bcolors.FAIL)
        max_count = -1

    """Genre"""
    # Searching for the a tag with the 'kategorie=' in the 'href' to get the genre
    genre = None
    for a in a_tags:
        if a.has_attr('href'):
            if "kategorie=" in a['href']:
                genre = a['href'].split("kategorie=")[1]
                printC(genre, "Successfully loaded the Manga genre!", bcolors.OKGREEN)
                break

    # Checking if the genre has been found
    if genre == None:
        printC("-", "Failed to load the Manga genre!", bcolors.FAIL)
        genre = "Error"

    """German Count"""
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

        printC(german_count, "Successfully loaded the Manga german count!", bcolors.OKGREEN)
    except Exception as e:
        printC("-", "Failed to load the Manga max count!", bcolors.FAIL)
        german_count = -1

    """Cost"""
    # Going throgh all of the volumes of the Manga to get a cost if the fist few dont have one given
    cost = -1
    for i in manga_data.find_all("td", {"class": "bandtext"}):
        try:
            cost_text = i.text.split("Kaufpreis: ")[1]
            cost_nums = re.findall(r'\d+', cost_text)
            cost = int(cost_nums[0]) + (int(cost_nums[1]) / 100)
            printC(cost, "Successfully loaded the Manga cost!", bcolors.OKGREEN)
            break
        except Exception as e:
            cost = -1
    
    # If it dosnt find any price in all the volumes
    if cost == -1:
        printC("-", "Failed to load the Manga cost!", bcolors.FAIL)
    
    """Cover"""
    # Getting the cover-link beging with the 2nd char to not get the '.' at the beginning
    try:
        cover_link = manga_data.find("td", {"class": "cover"}).find("a")["href"][1:]
        cover = "https://www.mangaguide.de" + cover_link
        printC(cover, "Successfully loaded the Manga cover!", bcolors.OKGREEN)
    except:
        try:
            cover_link = manga_data.find("td", {"class": "cover"}).find("img")["src"][1:]
            cover = "https://www.mangaguide.de" + cover_link
            printC(cover, "Successfully loaded the Manga cover!", bcolors.OKGREEN)
        except:
            try:
                cover_link = manga_data.find("td", {"class": "japcover"}).find("a")["href"][1:]
                cover = "https://www.mangaguide.de" + cover_link
                printC(cover, "Successfully loaded the Manga cover!", bcolors.OKGREEN)
            except:
                printC("-", "Failed to load the Manga cover!", bcolors.FAIL)
                cover = None

    return {"name": manga_title, "author": author, "max_count": max_count, "german_count": german_count, "genre": genre, "cost": cost, "cover": cover}

if __name__ == "__main__":
    print(get_manga("naruto"))