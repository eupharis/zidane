import os
import time
import datetime
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from .models import Page, Link, database


START_URL = 'https://news.ycombinator.com'
FOUR_GIGABYTES = 4294967296
CRAWLABLE_CONTENT_TYPES = set(['text/html', 'text/plain'])


def blow_up_when_db_too_big(db_name):
    if db_name == ':memory:':
        # in memory db used for tests, assume it's good
        return
    elif os.stat(db_name).st_size > FOUR_GIGABYTES:
        raise NotImplementedError('DB getting too big for this machine! Abort!')


def add_page_info_to_page(page):
    try:
        resp = requests.head(page.url, timeout=5, allow_redirects=False)
    except RequestException as e:
        page.status_code = 490
        page.content = str(e)
    else:
        page.status_code = resp.status_code

    if page.status_code == 301:
        # permanent redirect
        redirect_url = resp.headers.get('location', '')
        page.content = redirect_url

        defaults = {'content': '', 'status_code': 0}
        to_page, _ = Page.get_or_create(
            url=redirect_url,
            defaults=defaults)

        Link.get_or_create(
            from_page=page,
            to_page=to_page)

    if page.status_code != 200:
        # this is a redirect or something
        print('Received status code {} for {}, skipping'.format(page.status_code, page.content))
        return

    content_type = resp.headers.get('content-type')
    if content_type:
        content_type = content_type.split(';')[0]  # get rid of charset
        page.content_type = content_type.strip()

    if content_type not in CRAWLABLE_CONTENT_TYPES:
        return

    content_length = resp.headers.get('content-length')
    if content_length and int(content_length) > 10485760:
        # skip pages > 10 MiB in length
        return

    try:
        resp = requests.get(page.url, timeout=5, allow_redirects=False)
        page.content = resp.text
    except RequestException as e:
        page.status_code = 490
        page.content = str(e)


def crawl_page(url):
    blow_up_when_db_too_big(database.database)

    page = Page.select().where(Page.url == url).first()
    if page and page.status_code != 0:
        crawled = False
        # print('Already crawled {}, skipping'.format(page.url))
        return page, crawled

    crawled = True
    if not page:
        page = Page.create(url=url, content='', status_code=0)

    # set date to right before crawling
    page.first_visited = datetime.datetime.utcnow()
    page.last_visited = datetime.datetime.utcnow()

    print('Crawling {}'.format(url))
    add_page_info_to_page(page)
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
    defaults = {'content': '', 'status_code': 0}
    from_page, _ = Page.get_or_create(url=from_url, defaults=defaults)

    for to_url in to_urls:
        to_page, _ = Page.get_or_create(url=to_url, defaults=defaults)
        print("creating link from {} to {}".format(from_url, to_url))
        link, _ = Link.get_or_create(from_page=from_page, to_page=to_page)
        links.append(link)

    return links


def go():
    defaults = {'status_code': 0, 'content': ''}
    Page.get_or_create(url=START_URL, defaults=defaults)

    while True:
        time.sleep(0.1)
        for page in Page.select().where(Page.status_code == 0):
            page, crawled = crawl_page(page.url)

            hrefs = extract_hrefs(page.content)
            create_links(page.url, hrefs)
            if crawled:
                time.sleep(0.1)
