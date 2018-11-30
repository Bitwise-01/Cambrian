# Date: 11/06/2018
# Author: Pure-L0G1C
# Description: Download images from Pixabay


import re 
from queue import Queue 
from platform import system
from time import time, sleep
from subprocess import Popen
from argparse import ArgumentParser
from threading import Thread, RLock
from bs4 import BeautifulSoup as bs 
from requests import get as urlopen
from os.path import splitext, exists
from urllib.request import urlretrieve as download


class Pixabay(object):


    def __init__(self, item, path):
        self.lock = RLock()
        self.imgs = Queue()
        self.is_alive = True      
        self.page_number = 0
        self.max_pages = None 
        self.threads_active = 0
        self.start_time = time()
        self.imgs_downloaded = 0
        self.download_path = path
        self.cls = 'cls' if system() == 'Windows' else 'clear'
        self.url = 'https://pixabay.com/en/photos/{}/?&pagi={}'.format(item, '{}')
    
    
    def set_max_pages(self):
        html = urlopen(self.url).text
        form = bs(html, 'html.parser').find('form', {'class': 'add_search_params pure-form hide-xs hide-sm hide-md'})
        listnum = re.findall(r'\d+', form.text)
        self.max_pages = int(listnum[0])    
        

    def get_images(self, url):
        for img in bs(urlopen(url).text, 'html.parser').find_all('img'):
            src = img.get('data-lazy-srcset')
            if src:
                img_src = src.split(',')[0].split()[0]
                self.imgs.put(img_src)
                

    def collect_images(self):
        while self.is_alive:
            if self.page_number < self.max_pages:
                self.page_number += 1
                self.get_images(self.url.format(self.page_number))
            
    
    def download_img(self, url):
        self.imgs_downloaded += 1
        exten = splitext(url)[1][:4]
        path = '{}/img{}{}'.format(self.download_path, self.imgs_downloaded, exten)
        try:
            download(url, path)
        except:pass 
        finally:
            self.threads_active -= 1


    def download_images(self):
        while self.is_alive:
            if self.imgs.qsize():
                with self.lock:
                    self.threads_active += 1
                    src = self.imgs.get()
                    Thread(target=self.download_img, args=[src], daemon=True).start()


    def status(self):
        Popen(self.cls, shell=True).wait()
        print('Page Number: {}\nImages Downloaded: {}\n'.format(self.page_number, self.imgs_downloaded))


    def start(self):
        self.set_max_pages()
        Thread(target=self.download_images, daemon=True).start()
        Thread(target=self.collect_images, daemon=True).start()
        sleep(3)

        last_num = 0
        while self.is_alive:
            if last_num != self.imgs_downloaded:
                last_num = self.imgs_downloaded
                if self.is_alive:self.status()
            if all([self.page_number >= self.max_pages, not self.threads_active, not self.imgs.qsize()]):
                self.stop()              
        

    def stop(self):
        self.is_alive = False
        t = round(time() - self.start_time, 3)
        mins = round(t/60, 3)
        print('Time-Elapsed: {}(sec)\n\t\t{}(min)'.format(t, mins))


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument('-t', '--topic', help='What to search for. Example: domestic cat', nargs='+', required=True)
    args.add_argument('-p', '--path', help='Download folder.', nargs='+', required=True)
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