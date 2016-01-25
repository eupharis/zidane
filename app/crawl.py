import os
import time
import datetime
import requests
from bs4 import BeautifulSoup
from .models import Page, Link


START_URL = 'http://www.cavesofnarshe.com/'


def crawl_page(url):
    if os.stat('corpus.db').st_size > 2147483648:
        raise NotImplementedError('DB getting too big for this machine! Abort!')

    page = Page.select().where(Page.url == url).first()
    if page and page.content != 'PLACEHOLDER':
        crawled = False
        print('Already crawled {}, skipping')
        print
    else:
        crawled = True
        print('Crawling {}'.format(url))
        resp = requests.get(url)
        assert resp.status_code == 200
        if not page:
            page = Page.create(url=url, content=resp.text)

        # update last updated
        page.content = resp.text
        page.first_visited = datetime.datetime.utcnow()
        page.last_visited = datetime.datetime.utcnow()
        page.save()

        print('Crawling finished!')
        print

    return page, crawled


def extract_hrefs(content):
    link_hrefs = []
    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('http'):
            link_hrefs.append(href)

    return link_hrefs


def create_links(from_url, to_urls):
    links = []
    defaults = {'content': 'PLACEHOLDER'}
    from_page, _ = Page.get_or_create(url=from_url, defaults=defaults)

    for to_url in to_urls:
        to_page, _ = Page.get_or_create(url=to_url, defaults=defaults)
        print("creating link from {} to {}".format(from_url, to_url))
        link, _ = Link.get_or_create(from_page=from_page, to_page=to_page)
        links.append(link)

    return links


def go():
    page, _ = crawl_page(START_URL)

    hrefs = extract_hrefs(page.content)
    create_links(START_URL, hrefs)

    while True:
        print('---------')
        print('new loop!')
        print('---------')
        print
        time.sleep(1)
        for page in Page.select().where(Page.content == 'PLACEHOLDER'):
            page, crawled = crawl_page(page.url)

            hrefs = extract_hrefs(page.content)
            create_links(page.url, hrefs)

            if crawled:
                time.sleep(1)
