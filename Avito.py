import datetime
import urllib.parse
from collections import namedtuple

import bs4
import requests

InnerBlock = namedtuple('Block', 'title, price, currency, date, url')


class Block(InnerBlock):
    def __str__(self):
        return f'{self.title}\t{self.price}\t{self.currency}\t{self.date}\t{self.url}'


class AvitoParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5 37.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.82 Safari/537.36',
            'Accept-Language': 'ru',
        }

    def get_page(self, page: int = None):
        params = {
            'radius': 0,
            'user': 1,
        }
        if page and page > 1:
            params['p'] = page

            url = "https://www.avito.ru/vladivostok/avtomobili/honda/"
            r = self.session.get(url, params=params)
            return r.text

    @staticmethod
    def parse_date(item: str):
        params = item.strip().split(' ')
        # print(params)
        if len(params) == 2:
            day, time = params
            if day == 'Сегодня':
                date = datetime.date.today()
            elif day == 'Вчера':
                date = datetime.date.today() - datetime.timedelta(days=1)
            else:
                print('Не смогли разобрать день:', item)
                return
            time = datetime.datetime.strptime(time, '"%H:%M').time()
            return datetime.datetime.combine(date=date, time=time)
        elif len(params) == 3:
            day, month_hry, time = params
            day = int(day)
            months_map = {
                'января': 1,
                'февраля': 2,
                'марта': 3,
                'апреля': 4,
                'мая': 5,
                'июня': 6,
                'июля': 7,
                'августа': 8,
                'сентября': 9,
                'октября': 10,
                'ноября': 11,
                'декабря': 12,
            }
            month = months_map.get(month_hry)
            if not month:
                print('Не получилось узнать месяц:', item)
                return
            today = datetime.datetime.today()
            time = datetime.datetime.strptime(time, '%H:%M')
            return datetime.datetime(day=day, month=month, year=today.year, hour=time.hour, minute=time.minute)
        else:
            print('Не получилось разобрать формат:', item)
            return

    def parse_block(self, item):
        global url
        url_block = item.select_one('a.iva-item-sliderLink-2hFV_')
        href = url_block.get('href')
        if href:
            url = "https://www.avito.ru/ + href"
        # Блок с названием
        title_block = item.select_one('h3.title.item-description-title span')
        title = title_block.string.strip()

        # Блок с названием и валютой
        price_block = item.select_one('span.price')
        price_block = price_block.get_text('\n')
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) == 2:
            price, currency = price_block
        else:
            price, currency = None, None
            print('Что-то пошло не так с ценой', price_block)

        # Блок с датой размещения объявления
        date = None
        date_block = item.select_one('div.item-date div.js-item-date.c-2')
        absolute_date = date_block.get('data-absolute-date')
        if absolute_date:
            date = self.parse_date(item=absolute_date)

        return Block(
            url=url,
            title=title,
            price=price,
            currency=currency,
            date=date,
        )

    def get_pagination_limit(self):
        text = self.get_page()
        soup = bs4.BeautifulSoup(text,'lxml')

        container = soup.select('a.pagination-page')
        last_button = container[-1]
        href = last_button.get('href')
        if not href:
            return

        r = urllib.parse.urlparse(href)

        #print(last_button)



    def get_blocks(self):
        text = self.get_page(page=2)
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('iva-item-content-m2FiN')
        for item in container:
            print(item)
            return
            block = self.parse_block(item=item)
            print(block)


def main():
    p = AvitoParser()
    p.get_pagination_limit()
    p.get_blocks()
