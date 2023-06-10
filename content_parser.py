import os
import re
import requests
from bs4 import BeautifulSoup as Bs


class Parser:

    def __init__(self):
        self.animals_name = None

    def get_html(self, url):
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                html = Bs(response.content, 'html.parser')
                return html
            else:
                print(f"Error: Unable to fetch URL ({response.status_code})")
        else:
            print('Error: URL not provided')

    def link_name_parser(self):
        animals = {
            'cats': 'cats-plant-list',
            'dogs': 'dogs-plant-list',
            'horses': 'horse-plant-list',
        }
        for animals_name, link in animals.items():
            url = f'https://www.aspca.org/pet-care/animal-poison-control/{link}'
            html = self.get_html(url)
            if html:
                links = html.find_all("a", href=re.compile("^/pet-care/animal-poison-control/toxic-and-non-toxic-plants/"))
                name_link_dict = {link.get_text().strip(): link.get("href") for link in links}
                self.animals_name = animals_name
                self.contents_parser(name_link_dict=name_link_dict)

    def contents_parser(self, name_link_dict):
        for name, link in name_link_dict.items():
            url = f"https://www.aspca.org{link}"
            html = self.get_html(url)
            if html:
                names = html.find_all(class_="label-inline-format-label")
                contents = html.find_all(class_="values")
                img_tag = html.find("img")

                names_list = [element.get_text(separator=' ').rstrip(':') for element in names]
                contents_list = [element.get_text(separator=' ') for element in contents]

                contents_dict = {name: content for name, content in zip(names_list, contents_list)}
                contents_dict['name'] = name

                image_link = img_tag['data-echo'] if img_tag else None
                if image_link:
                    Downloader(img_url=image_link, plant_name=name, directory_name=self.animals_name)
                else:
                    print(f'{name}')


class Downloader:
    def __init__(self, img_url, plant_name, directory_name):
        self.directory_name = directory_name
        self.img_url = img_url
        self.plant_name = plant_name
        if img_url:
            self.download_image()

    def download_image(self):
        response = requests.get(self.img_url)

        images_directory = f"{self.directory_name}"
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        with open(os.path.join(images_directory, f"{self.plant_name}.jpg"), "wb") as img_file:
            img_file.write(response.content)


if __name__ == "__main__":
    parser = Parser()
    parser.link_name_parser()
