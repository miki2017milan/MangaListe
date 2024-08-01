import traceback
import requests as r
import re

from utils import *
from bs4 import BeautifulSoup, ResultSet
from openpyxl.styles import *

from dataclasses import dataclass
from pprint import pprint

@dataclass
class Manga:
    name: str
    author: str
    max_count: int
    german_count: int
    genre: str
    cost: float
    cover: str
    finished: bool
    link: str

class GetMangaInfo:
    @staticmethod
    def get_manga_from_search_name(search_name: str) -> list[Manga] | None:
        manga_links = GetMangaInfo.get_manga_urls(search_name)

        if not manga_links:
            return
        
        mangas = []
        for i, link in enumerate(manga_links):
            manga_page_content = r.get(link).content
            manga_data = BeautifulSoup(manga_page_content, "html.parser").find(id="inhalt") # manga data is the whole content from the container <div> with the id "inhalt"
            a_tags = manga_data.find_all("a")

            manga = Manga(GetMangaInfo.get_manga_title(manga_data),
                          GetMangaInfo.get_manga_author(a_tags),
                          GetMangaInfo.get_manga_max_count(str(manga_page_content)),
                          GetMangaInfo.get_manga_german_count(str(manga_page_content)),
                          GetMangaInfo.get_manga_genre(a_tags),
                          GetMangaInfo.get_manga_cost(manga_data),
                          GetMangaInfo.get_manga_cover(manga_data),
                          GetMangaInfo.get_finished(manga_data),
                          link)
            mangas.append(manga)

        return mangas

    @staticmethod
    def get_manga_urls(search_name: str) -> tuple[str] | None:
        # Finding the manga page from name
        url_name = search_name.replace(" ", "+") # formatting the search_name to have '+' instead of spaces for the url

        search_link = "https://www.mangaguide.de/index.php?include=24&suche=" + url_name
        try:
            search_page = r.get(search_link)
        except r.exceptions.MissingSchema:
            return

        # Getting the serach results
        search_results = BeautifulSoup(search_page.content, "html.parser").find(id="inhalt").find_all("a")

        # Remove manga wich are just editions of other manga
        # Remove manga '1214' because it's a duplicate
        filterd_search_results = []
        for s in search_results:
            if "edition" in s['href'] or "manga_id=1214" in s['href']:
                continue
            # Saving only the url
            filterd_search_results.append("https://www.mangaguide.de/" + s['href'])

        # No search results were found
        if len(filterd_search_results) == 0:
            return

        return filterd_search_results

    @staticmethod
    def get_manga_title(manga_data: BeautifulSoup) -> str | None:
        return manga_data.find("table").find_all("tr")[0].find("td").text

    @staticmethod
    def get_manga_author(a_tags: ResultSet) -> str | None:
        # Searching for the a tag with the 'mangaka_id' in the 'href' to get the author
        for a in a_tags:
            if a.has_attr('href'):
                if "mangaka_id=" in a['href']:
                    return a.text
    
    @staticmethod
    def get_manga_genre(a_tags: ResultSet) -> str | None:
        # Searching for the a tag with the 'kategorie=' in the 'href' to get the genre
        for a in a_tags:
            if a.has_attr('href'):
                if "kategorie=" in a['href']:
                    return a['href'].split("kategorie=")[1]

    @staticmethod
    def get_manga_max_count(manga_page: r.Response) -> int | None:
        try:
            # Getting the text where the maximal count of a Manga is stored
            max_count_text = manga_page.split("nglich erschien")[1][:20]

            # Getting the number from the text
            return int(re.findall(r'\d+', max_count_text)[0])
        except :
            traceback.print_exc()

    @staticmethod
    def get_manga_german_count(manga_page: r.Response) -> int | None:
        try:
            # Getting the text where the german count is stored
            german_count_text = manga_page.split("auf Deutsch erschienen.")[0][-20:]
            # Getting from the text the numbers
            temp = re.findall(r'\d+', german_count_text)

            # Checking if there is actually a number or just 'ein'
            german_count = 1 if len(temp) == 0 else int(temp[0])

            return german_count
        except:
            traceback.print_exc()

    @staticmethod
    def get_manga_cost(manga_data: BeautifulSoup) -> float | None:
        # Going throgh all of the volumes of the Manga to get a cost if the fist few dont have one
        for i in manga_data.find_all("td", {"class": "bandtext"}):
            try:
                cost_text = i.text.split("Kaufpreis: ")[1]
                cost_nums = re.findall(r'\d+', cost_text)
                cost = int(cost_nums[0]) + (int(cost_nums[1]) / 100)

                return cost
            except:
                continue # Not best practice but it just tries to find the cost if its in the rigth format. All other errors are irrelevant

    @staticmethod
    def get_manga_cover(manga_data: BeautifulSoup) -> str | None:
        # Getting the cover-link beginning with the 2nd char to not get the '.' at the beginning
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
                except:
                    traceback.print_exc()
                    return

        return cover

    @staticmethod
    def get_finished(manga_data : BeautifulSoup) -> bool | None:
        try:
            return False if manga_data.find("span")['class'][0] == "laeuft" else True
        except:
            traceback.print_exc()

if __name__ == "__main__":
    test = GetMangaInfo()
    tests = test.get_manga_from_search_name("given")
    
    pprint(tests)