import unittest
from unittest.mock import patch, MagicMock
from app.models import Page, Link, initialize
from app.crawl import extract_hrefs, crawl_page, create_links, add_page_info_to_page


link1 = "http://www.example.com/foo"
link2 = "http://www.example.com/bar"
link_html = '''
<a href="{}">Foo</a>
<a href="{}">Bar</a>
'''.format(link1, link2)


class T(unittest.TestCase):
    def setUp(self):
        initialize(':memory:')

    # MOVE THESE TWO TO A LINKS FUNCTION CONSUMED BY CRAWL
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

    def test_crawl_existing_page(self):
        content = 'foobar'
        page = Page.create(url=link1, content=content, status_code=200)

        crawled_page, crawled = crawl_page(link1)

        self.assertFalse(crawled)
        self.assertEqual(page.id, crawled_page.id)

    @patch('app.crawl.requests.head')
    @patch('app.crawl.requests.get')
    def test_add_page_info_to_page(self, requests_get, requests_head):
        url = "http://www.example.com/foo"
        text = '<div>hi world</div>'
        content_type = 'text/html'
        headers = {
            'content-type': '{}; charset=utf-8'.format(content_type),
        }
        requests_head.return_value = MagicMock(status_code=200, headers=headers)
        requests_get.return_value = MagicMock(status_code=200, text=text)

        page = Page.create(url=url, content='', status_code=0)
        add_page_info_to_page(page)

        self.assertEqual(page.content, text)
        self.assertEqual(page.content_type, content_type)

        self.assertEqual(requests_head.call_count, 1)
        self.assertEqual(requests_get.call_count, 1)

    @patch('app.crawl.requests.head')
    @patch('app.crawl.requests.get')
    def test_permanent_redirect(self, requests_get, requests_head):
        url = "http://www.example.com/foo"
        redirect_url = "http://www.example.com/bar"
        headers = { 'location': redirect_url }
        requests_head.return_value = MagicMock(status_code=301, headers=headers)

        page = Page.create(url=url, content='', status_code=0)
        add_page_info_to_page(page)

        to_page = Page.select().where(Page.url == redirect_url).first()
        self.assertTrue(to_page)

        url_redirect_link = Link.select().where(
            Link.from_page == page,
            Link.to_page == to_page)
        self.assertTrue(url_redirect_link.exists())

        self.assertEqual(requests_head.call_count, 1)
        self.assertFalse(requests_get.called)

        self.assertEqual(page.content, redirect_url)
