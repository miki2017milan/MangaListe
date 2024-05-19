import traceback
import requests as r
import re

from typing import Tuple
from utils import *
from bs4 import BeautifulSoup, ResultSet
from openpyxl.styles import *

class Manga:
    def __init__(self, name: str, author: str, max_count: int, german_count: int, genre: str, cost: float, cover: str, finished: bool, link: str):
        self.name = name
        self.author = author
        self.max_count = max_count
        self.german_count = german_count
        self.genre = genre
        self.cost = cost
        self.cover = cover
        self.finished = finished
        self.link = link

    def __repr__(self) -> str:
        return f"Manga: {self.name}"

    def show(self) -> str:
        print(f"""----------------------------------------------------------------
Name: {self.name}
Author: {self.author}
Max_count: {self.max_count}
German_count: {self.german_count}
Genre: {self.genre}
Cost: {self.cost}
Cover: {self.cover}
Finished: {self.finished}
Link: {self.link}
----------------------------------------------------------------""")

class Getting_manga_info:
    def get_manga_from_search_name(self, search_name: str) -> Tuple[Manga]:
        manga_links = self.getting_manga_urls_from_search_name(search_name)

        if manga_links is None:
            return None
        
        mangas = []
        for i, m in enumerate(manga_links):
            manga_page = r.get(m)
            manga_data = BeautifulSoup(manga_page.content, "html.parser").find(id="inhalt")
            a_tags = manga_data.find_all("a")

            manga = Manga(self.get_manga_title(manga_data),
                          self.get_manga_author(a_tags),
                          self.get_manga_max_count(manga_page),
                          self.get_manga_german_count(manga_page),
                          self.get_manga_genre(a_tags),
                          self.get_manga_cost(manga_data),
                          self.get_manga_cover(manga_data),
                          self.get_finished(manga_data),
                          m)
            mangas.append(manga)
            
            print(i + 1, "/", len(manga_links))

        return mangas

    def getting_manga_urls_from_search_name(self, search_name: str) -> Tuple[str]:
        # Finding the manga page from name
        url_name = search_name.replace(" ", "+") # formatting the search_name to have '+' instead of spaces for the url

        search_link = "https://www.mangaguide.de/index.php?include=24&suche=" + url_name
        try:
            search_page = r.get(search_link)
        except r.exceptions.MissingSchema:
            return None

        # Getting the serach results
        search_results = BeautifulSoup(search_page.content, "html.parser").find(id="inhalt").find_all("a")

        # No search results were found
        if len(search_results) == 0:
            return None

        # Remove manga wich are just editions of other manga
        # Remove manga '1214' because it's a duplicate
        for i in range(len(search_results) - 1, -1, -1):
            if "edition" in search_results[i]['href'] or "manga_id=1214" in search_results[i]['href']:
                search_results.pop(i)
                continue
            # Saving only the url
            search_results[i] = "https://www.mangaguide.de/" + search_results[i]['href']

        return search_results

    def get_manga_title(self, manga_data: BeautifulSoup) -> str:
        return manga_data.find("table").find_all("tr")[0].find("td").text

    def get_manga_author(self, a_tags: ResultSet) -> str:
        # Searching for the a tag with the 'mangaka_id' in the 'href' to get the author
        for a in a_tags:
            if a.has_attr('href'):
                if "mangaka_id=" in a['href']:
                    return a.text
        
        return None
    
    def get_manga_genre(self, a_tags: ResultSet) -> str:
        # Searching for the a tag with the 'kategorie=' in the 'href' to get the genre
        for a in a_tags:
            if a.has_attr('href'):
                if "kategorie=" in a['href']:
                    return a['href'].split("kategorie=")[1]
        
        return None

    def get_manga_max_count(self, manga_page: r.Response) -> int:
        try:
            # Getting the text where the maximal count of a Manga is stored
            max_count_text = manga_page.text.split("nglich erschien")[1]

            # Getting the number from the text
            return int(re.findall(r'\d+', max_count_text)[0])
        except Exception:
            traceback.print_exc()
            return None

    def get_manga_german_count(self, manga_page: r.Response) -> int:
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

            return german_count
        except Exception:
            traceback.print_exc()
            return None

    def get_manga_cost(self, manga_data: BeautifulSoup) -> float:
        # Going throgh all of the volumes of the Manga to get a cost if the fist few dont have one
        for i in manga_data.find_all("td", {"class": "bandtext"}):
            try:
                cost_text = i.text.split("Kaufpreis: ")[1]
                cost_nums = re.findall(r'\d+', cost_text)
                cost = int(cost_nums[0]) + (int(cost_nums[1]) / 100)

                return cost
            except:
                continue
        
        return None

    def get_manga_cover(self, manga_data: BeautifulSoup) -> str:
        # Getting the cover-link beging with the 2nd char to not get the '.' at the beginning
        try:
            cover_link = manga_data.find("td", {"class": "cover"}).find("a")["href"][1:]
            cover = "https://www.mangaguide.de" + cover_link
        except:
            try:
                cover_link = manga_data.find("td", {"class": "cover"}).find("img")["src"][1:]
                cover = "https://www.mangaguide.de" + cover_link
            except:
                try:
                    cover_link = manga_data.find("td", {"class": "japcover"}).find("a")["href"][1:]
                    cover = "https://www.mangaguide.de" + cover_link
                except Exception:
                    traceback.print_exc()
                    cover = None

        return cover

    def get_finished(self, manga_data : BeautifulSoup) -> bool:
        try:
            finished = False if manga_data.find("span")['class'][0] == "laeuft" else True
            return finished
        except Exception:
            traceback.print_exc()
            return None

if __name__ == "__main__":
    test = Getting_manga_info()
    tests = test.get_manga_from_search_name("giv")
    for t in tests:
        t.show()