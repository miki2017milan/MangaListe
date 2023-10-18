import openpyxl as px
import io
import urllib3

from utils import *
from openpyxl.drawing.image import Image
from openpyxl.styles import *

# Styles
fill = PatternFill("solid", fgColor="D9E1F2")
thin = Side(border_style="thin", color="000000")
border = Border(right=thin, left=thin, top=thin, bottom=thin)
aline = Alignment(horizontal="center", vertical="center")

name_font = Font(name="Calibri", size=14, bold=True)
name_aline = Alignment(horizontal="left", vertical="center")

genre_font = Font(name="Calibri", size=16, bold=True)

count_font = Font(name="Calibri", size=20, bold=True)

def add_to_excel_file(path, data, manga_have_count):
    # Loading the excel file and catching errors
    print(f"\nLädt '{bcolors.OKBLUE}{path}{bcolors.ENDC}'...")
    try:
        print(path)
        wb = px.load_workbook(path)
        print_color("Datai wurde erfolgreich geladen!\n", bcolors.OKGREEN)
    except FileNotFoundError:
        print_color("Datei wurde nicht gefunden!\n", bcolors.FAIL)
        input("Drücke 'Enter' um zurückzukehren...")
        return False

    sheet = wb.active

    # Starting from the next empty row beginning at row 4
    for i, row in enumerate(sheet['B']):
        if i < 4:
            continue

        print(row.value)
        if row.value is None:
            cur = str(i + 1)
            break

        if i == len(sheet['B']) - 1:
            cur = str(len(sheet['B']) + 1)

    # Loading the cover into the 'A' columne
    if data["cover"] is not None:
        http = urllib3.PoolManager()
        req = http.request('GET', data["cover"])
        image_file = io.BytesIO(req.data)
        img = Image(image_file)

        img.anchor = "A" + cur
        img.width = 96
        img.height = 134
        sheet.add_image(img, "A" + cur)

    sheet.row_dimensions[int(cur)].height = 100

    # Loading the name into the 'B' columne
    name_cell = "B" + cur

    sheet[name_cell].font = name_font
    sheet[name_cell].alignment = name_aline
    sheet[name_cell].fill = fill
    sheet[name_cell].border = border
    sheet[name_cell] = data["name"]
    sheet[name_cell].hyperlink = data["link"]

    # Loading the author into the 'C' columne
    author_cell = "C" + cur

    sheet[author_cell].font = name_font
    sheet[author_cell].alignment = aline
    sheet[author_cell].fill = fill
    sheet[author_cell].border = border
    sheet[author_cell] = data["author"]

    # Loading the genre into the 'D' columne
    genre_cell = "D" + cur

    sheet[genre_cell].font = genre_font
    sheet[genre_cell].alignment = aline
    sheet[genre_cell].fill = fill
    sheet[genre_cell].border = border
    sheet[genre_cell] = data["genre"]

    # Loading the have count into the 'E' columne
    count_cell = "E" + cur

    sheet[count_cell].font = count_font
    sheet[count_cell].alignment = aline
    sheet[count_cell].fill = fill
    sheet[count_cell].border = border
    sheet[count_cell] = manga_have_count

    # Loading the german- and max count into the 'F' columne
    counts_cell = "F" + cur

    sheet[counts_cell].font = count_font
    sheet[counts_cell].alignment = aline
    sheet[counts_cell].fill = fill
    sheet[counts_cell].border = border
    if data["max_count"] == data["german_count"]:
        sheet[counts_cell] = data["max_count"]
    else:
        sheet[counts_cell] = str(data["german_count"]) + "/" + str(data["max_count"])

    # Loading the cost into the 'H' columne
    cost_cell = "G" + cur

    sheet[cost_cell].font = count_font
    sheet[cost_cell].alignment = aline
    sheet[cost_cell].fill = fill
    sheet[cost_cell].border = border
    sheet[cost_cell] = data["cost"]
    sheet[cost_cell].number_format = "0.00€"

    wb.save(path)

    print_color(f"Der Manga '{data['name']}' wurde erfolgreich zur Liste hinzugefügt!\n", bcolors.OKGREEN)
    input("Drücke 'Enter' um zurückzukehren...")

    return True