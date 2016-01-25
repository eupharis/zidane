import requests
import unittest
from unittest.mock import MagicMock
from app.models import Page, initialize
from app.crawl import extract_hrefs, crawl_page, create_links


link1 = "http://www.example.com/foo"
link2 = "http://www.example.com/bar"
link_html = '''
<a href="{}">Foo</a>
<a href="{}">Bar</a>
'''.format(link1, link2)


class T(unittest.TestCase):
    def setUp(self):
        initialize(':memory:')

    def test_extract_hrefs(self):
        links = extract_hrefs(link_html)
        self.assertListEqual(links, [link1, link2])

    def test_create_links(self):
        # no pages should exist
        self.assertEqual(Page.select().count(), 0)

        # create links
        links = create_links(link1, [link2])
        self.assertTrue(len(links), 1)
        link = links[0]
        self.assertEqual(link.from_page.url, link1)
        self.assertEqual(link.to_page.url, link2)

        # 2 pages should exist
        self.assertEqual(Page.select().count(), 2)

    def test_crawl_page(self):
        get_mock = MagicMock(name='method')
        get_mock.return_value = MagicMock(status_code=200, text='<div>hi world</div>')
        requests.get = get_mock

        content = 'foobar'
        page = Page.create(url=link1, content=content, status_code=200)

        crawled_page, crawled = crawl_page(link1)

        self.assertFalse(crawled)
        self.assertEqual(page.id, crawled_page.id)
