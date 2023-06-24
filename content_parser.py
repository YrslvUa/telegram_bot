import functools
import os
import re
import asyncio
from time import time

import aiofiles
import httpx
from bs4 import BeautifulSoup as Bs


class Parser:

    def __init__(self):
        self.animals_name = None

    async def get_html(self, url):
        if url:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    html = Bs(response.content, 'html.parser')
                    return html
                else:
                    print(f"Error: Unable to fetch URL ({response.status_code})\nURL: {url}")
        else:
            print('Error: URL not provided')

    async def link_name_parser(self):
        animals = {
            'cats': 'cats-plant-list',
            'dogs': 'dogs-plant-list',
            'horses': 'horse-plant-list',
        }
        for animals_name, link in animals.items():
            url = f'https://www.aspca.org/pet-care/animal-poison-control/{link}'
            html = await self.get_html(url)
            if html:
                links = html.find_all("a",
                                      href=re.compile("^/pet-care/animal-poison-control/toxic-and-non-toxic-plants/"))
                name_link_dict = {link.get_text().strip(): link.get("href") for link in links}
                self.animals_name = animals_name
                await self.contents_parser(name_link_dict=name_link_dict)

    async def contents_parser(self, name_link_dict):
        semaphore = asyncio.Semaphore(5)
        async with httpx.AsyncClient() as client:
            tasks = []
            for name, link in name_link_dict.items():
                url = f"https://www.aspca.org{link}"
                tasks.append(self.parse_plant(client, url, name, semaphore))
            await asyncio.gather(*tasks)

    async def parse_plant(self, client, url, name, semaphore):
        async with semaphore:
            html = await self.get_html(url)
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
                    await self.download_image(client, image_link, name)

    async def download_image(self, client, img_url, plant_name):
        async with client.stream('GET', img_url) as response:
            images_directory = f"{self.animals_name}"
            if not os.path.exists(images_directory):
                os.makedirs(images_directory)

            valid_plant_name = plant_name.replace('"', '').replace('/', '_')

            file_path = os.path.join(images_directory, f"{valid_plant_name}.jpg")
            async with aiofiles.open(file_path, "wb") as file:
                async for chunk in response.aiter_bytes():
                    await file.write(chunk)


def get_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        result = await func(*args, **kwargs)
        end_time = time()
        execution_time = end_time - start_time
        print(f"Функція {func.__name__} виконана за {execution_time} секунд")
        return result
    return wrapper


@get_time
async def main():
    parser = Parser()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    await parser.link_name_parser()


if __name__ == "__main__":
    asyncio.run(main())
