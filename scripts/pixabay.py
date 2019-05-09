# Date: 11/06/2018
# Author: Pure-L0G1C
# Description: Download images from Pixabay

import re
import requests
from queue import Queue
from platform import system
from time import time, sleep
from subprocess import Popen
from argparse import ArgumentParser
from threading import Thread, RLock
from bs4 import BeautifulSoup as bs
from requests import get as urlopen
from os.path import splitext, exists


class Pixabay(object):

    def __init__(self, item, path):
        self.lock = RLock()
        self.imgs = Queue()
        self.is_alive = True
        self.page_number = 0
        self.wait_threads = 0
        self.max_pages = None
        self.threads_active = 0
        self.start_time = time()
        self.imgs_downloaded = 0
        self.chunk_size = 0xffff
        self.download_path = path
        self.max_downloads = None
        self.cls = 'cls' if system() == 'Windows' else 'clear'
        self.url = 'https://pixabay.com/en/photos/{}/?&pagi={}'.format(
            item, '{}'
        )

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }

    def set_max_pages(self):
        html = urlopen(self.url).text
        form = bs(html, 'html.parser').find(
            'form', {'class': 'add_search_params pure-form hide-xs hide-sm hide-md'})
        listnum = re.findall(r'\d+', form.text)
        self.max_pages = int(listnum[0])

    def set_max_downloads(self):
        html = urlopen(self.url).text

        container_div = bs(html, 'html.parser').find(
            'div', {'class': 'media_list'}
        )

        str_num = container_div.find_all(
            'div')[-1].string.split()[0].replace(',', '')
        self.max_downloads = int(str_num)

    def download(self, url, save_as):
        resp = requests.get(url, headers=self.headers, stream=True)

        with open(save_as, 'wb') as f:

            for data in resp.iter_content(self.chunk_size):
                if data:
                    f.write(data)

    def get_images(self, url, tries=5):
        imgs = None

        try:
            imgs = bs(urlopen(url).text, 'html.parser').find_all('img')
        except:
            if tries:
                self.get_images(url, tries-1)

        if not imgs:
            return

        for img in imgs:
            _src = img.get('srcset')
            src = img.get('data-lazy-srcset')

            if _src:
                _src = _src.split()[0]

            src = src if src else _src

            if src:
                img_src = src.split(',')[0].split()[0]
                self.imgs.put(img_src)

        if not self.wait_threads:
            self.wait_threads += 1

    def collect_images(self):
        while self.is_alive:
            if self.page_number < self.max_pages:
                self.page_number += 1
                self.get_images(self.url.format(self.page_number))
            else:
                sleep(1)

    def download_img(self, url):
        path = '{}/{}'.format(
            self.download_path, url.split('/')[-1]
        )

        try:
            self.download(url, path)
            self.imgs_downloaded += 1
        except:
            with self.lock:
                self.imgs.put(url)
        finally:
            self.threads_active -= 1

    def download_images(self):
        while self.is_alive:
            if self.imgs.qsize():
                with self.lock:

                    src = self.imgs.get()

                    if not src:
                        break

                    try:
                        Thread(
                            target=self.download_img,
                            args=[src],
                            daemon=True
                        ).start()

                        self.threads_active += 1
                    except:
                        self.imgs.put(src)

    def status(self):
        Popen(self.cls, shell=True).wait()
        print('Page Number: {}\nImages Downloaded: {}\nImages Left: {}\nComplete: {}%'.format(
            self.page_number,
            self.imgs_downloaded,
            self.max_downloads - self.imgs_downloaded,
            round((self.imgs_downloaded/self.max_downloads) * 100, 2)
        ))

    def start(self):
        self.set_max_pages()
        self.set_max_downloads()

        Thread(target=self.download_images, daemon=True).start()
        Thread(target=self.collect_images, daemon=True).start()

        last_num = 0
        while self.is_alive:
            if last_num != self.imgs_downloaded:
                last_num = self.imgs_downloaded
                if self.is_alive:
                    self.status()
                    sleep(0.3)
            if all([self.page_number >= self.max_pages, not self.threads_active, not self.imgs.qsize(), self.wait_threads]):
                self.stop()

    def stop(self):
        self.is_alive = False
        t = round(time() - self.start_time, 3)
        mins = round(t/60, 3)
        print('Time-Elapsed: {}(sec)\n\t\t{}(min)'.format(t, mins))


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument(
        '-t', '--topic', help='What to search for. Example: domestic cat', nargs='+', required=True)
    args.add_argument('-p', '--path', help='Download folder.',
                      nargs='+', required=True)
    args = args.parse_args()

    topic, download_path = ' '.join(args.topic), ''.join(args.path)

    if exists(download_path):
        pixabay = Pixabay(topic, download_path)
        try:
            pixabay.start()
        except KeyboardInterrupt:
            pixabay.stop()
    else:
        print('Error: Unable to locate the path: {}'.format(download_path))
