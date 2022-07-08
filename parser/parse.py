import requests
from bs4 import BeautifulSoup
import csv
import os

URL = 'https://ekaterinburg.n1.ru/snyat/posutochno/kvartiry/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36 OPR/88.0.4412.53', 'accept': '*/*'}
HOST = 'https://ekaterinburg.n1.ru/'
FILE = 'flats.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', class_='paginator-pages__link')
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('article', class_='living-search-item__card _show')

    flats = []
    for item in items:
        material = item.find('div',
                             class_='living-list-card__material living-list-card-material living-list-card__inner-block')
        if material:
            material = material.get_text()
        else:
            material = 'Материал не указан'
        flats.append({
            'title': item.find('span', class_='link-text').get_text(strip=True),
            'link': HOST + item.find('a', class_='link').get('href'),
            'price': item.find('div', class_='living-list-card-price__item _object').get('title').replace(' руб/сутки', ''),
            'size': item.find('div', class_='living-list-card__area living-list-card-area living-list-card__inner-block').get_text(),
            'floor': item.find('span', class_='living-list-card-floor__item').get_text().replace('этаж', ''),
            'material': material,
        })
    # print(flats)
    return flats


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Ссылка', 'Цена', 'Площадь', 'Этаж', 'Материал'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price'], item['size'], item['floor'], item['material']])

def parse():
    # URL = input('Введите URL:').strip()
    html = get_html(URL)
    if html.status_code == 200:
        flats = []
        pages_count = get_pages_count(html.text)
        print(f'Количество страниц {pages_count}')
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            flats.extend(get_content(html.text))
        save_file(flats, FILE)
        print(flats)
        print(f'Всего предлложений: {len(flats)}')
        os.startfile(FILE)
    else:
        print(f'Ошибка: {html}')


parse()
