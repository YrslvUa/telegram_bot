import os
import re
import requests
from bs4 import BeautifulSoup as Bs


def link_name_parser():
    url = 'https://www.aspca.org/pet-care/animal-poison-control/dogs-plant-list'

    response = requests.get(url)
    html = Bs(response.content, 'html.parser')
    links = html.find_all("a", href=re.compile("^/pet-care/animal-poison-control/toxic-and-non-toxic-plants/"))
    name_link_dict = {link.get_text().strip(): link.get("href") for link in links}
    contents_parser(name_link_dict=name_link_dict)


def contents_parser(name_link_dict):
    for name, link in name_link_dict.items():
        url = f"https://www.aspca.org{link}"
        response = requests.get(url)
        html = Bs(response.content, 'html.parser')

        names = html.find_all(class_="label-inline-format-label")
        contents = html.find_all(class_="values")

        names_list = [element.get_text(separator=' ').rstrip(':') for element in names]
        contents_list = [element.get_text(separator=' ') for element in contents]

        contents_dict = {name: content for name, content in zip(names_list, contents_list)}
        contents_dict['name'] = name

        img_tag = html.find("img")
        image_link = img_tag['data-echo']
        if image_link:
            download_image(img_url=image_link, plant_name=name)


def download_image(img_url, plant_name):
    response = requests.get(img_url)

    images_directory = "images"
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    with open(os.path.join(images_directory, f"{plant_name}.jpg"), "wb") as img_file:
        img_file.write(response.content)


if __name__ == "__main__":
    link_name_parser()
