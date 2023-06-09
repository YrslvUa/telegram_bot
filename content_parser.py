import re
import requests
from bs4 import BeautifulSoup as Bs


def link_name_parser():
    url = 'https://www.aspca.org/pet-care/animal-poison-control/dogs-plant-list'

    response = requests.get(url)
    html = Bs(response.content, 'html.parser')
    links = html.find_all("a", href=re.compile("^/pet-care/animal-poison-control/toxic-and-non-toxic-plants/"))
    for link in links:
        href = link.get("href")
        text = link.get_text().strip()
        content_parser(url=href)
        # print("Link:", href)
        # print("Name:", text)
        # print()

def content_parser(url):
    pass


if __name__ == "__main__":
    link_name_parser()
