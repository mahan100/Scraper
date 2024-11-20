import requests
import json
import pandas
import argparse
import numpy as np
import concurrent.futures
from time import sleep


class Scrape:
    def __init__(self, search, items):
        self.items = items
        self.proxy_available = []
        self.url = f'https://api.digikala.com/v1/search/?q={search}&page='
        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'api.digikala.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
        }

    def send_request(self, page):
        try:
            sleep(2)
            response = requests.get(self.url + f'{page}', headers=self.header)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f'Page {page} received successfully.')
            return response.json()
        except requests.RequestException as e:
            print(f'Failed to fetch page {page}: {e}')
            return {"data": {"products": []}}  # Return empty data on failure

    def get_data(self):
        end_page = int(np.ceil(self.items / 20))
        end_item = self.items - (end_page - 1) * 20
        page = 1
        data = self.send_request(page)
        data_final = []
        index = 20

        while data['data']['products']:
            max_len = len(data['data']['products'])
            if page == end_page:
                index = end_item if end_item < max_len else max_len

            for i in range(0, int(index)):
                try:
                    product = data['data']['products'][i]
                    title = product['title_fa']
                    product_url = 'https://www.digikala.com/' + product['url']['uri']
                    category = product['data_layer']['category']
                    image_url = product['images']['main']['url'][0]
                    rating = product['rating']['rate']
                    price = product['default_variant']['price']['selling_price']
                    data_final.append({
                        'title': title,
                        'product_url': product_url,
                        'category': category,
                        'image_url': image_url,
                        'rating': rating,
                        'price': price
                    })
                except KeyError as e:
                    print(f"KeyError for product {i} on page {page}: {e}")

            page += 1
            if page > end_page:
                print(f'Total rows = {len(data_final)}')
                break
            else:
                data = self.send_request(page)

        df = pandas.DataFrame(data_final, columns=['title', 'product_url', 'category', 'image_url', 'rating', 'price'])
        return df

    def save_json(self):
        result = self.send_request(1)  # Save the first page data as a sample
        with open('data.json', 'w', encoding='utf8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)
        print('Data stored in JSON file successfully.')

    def save_csv(self):
        df = self.get_data()
        df.to_csv('file_csv.csv', sep=',', encoding='utf-8', index=False)
        print('Data stored in CSV file successfully.')

    @classmethod
    def start(cls, search, items):
        return cls(search, items)

    def proxy(self):
        proxy_list = []
        proxy_list_path = 'proxy_list.txt'  # Replace with the correct path
        try:
            with open(proxy_list_path, encoding='utf-8') as p:
                for row in p:
                    proxy_list.append(row.strip())
        except FileNotFoundError:
            print(f"Proxy list file not found: {proxy_list_path}")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as c:
            c.map(self.proxy_check_request, proxy_list)
            c.shutdown(wait=True)
            self.proxy_selection()

    def proxy_selection(self):
        print(f'Available proxies: {self.proxy_available}')

    def proxy_check_request(self, proxy):
        try:
            check = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=3)
            if check.ok:
                print(f'Proxy {proxy} is available.')
                self.proxy_available.append(proxy)
        except requests.RequestException as e:
            print(f'Proxy {proxy} failed: {e}')

    @staticmethod
    def arg_parse():
        parser = argparse.ArgumentParser(
            description='''Digikala Data Extraction: Search Field'''
        )
        parser.add_argument('-s', '--search', required=True, help='Enter the name of the product (e.g., "mobile")')
        parser.add_argument('-i', '--items', required=True, type=int, help='Enter the number of products (e.g., 22)')
        args = parser.parse_args()

        search = args.search
        items = args.items
        print(f'Your product name is "{search}" for {items} items.')
        scraper = Scrape.start(search=search, items=items)
        scraper.save_csv()


if __name__ == '__main__':
    Scrape.arg_parse()
