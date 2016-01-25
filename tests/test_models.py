import datetime
import unittest
from peewee import IntegrityError
from app.models import Page, initialize


class T(unittest.TestCase):
    def setUp(self):
        initialize(':memory:')

    def test_page(self):
        now = datetime.datetime.utcnow()
        page = Page.create(url='http://www.example.com/foo', content='hi world')
        self.assertTrue(page.first_visited > now)

    def test_page_twice(self):
        # make sure database is cleared out between tests
        url = 'http://www.example.com/foo'
        Page.create(url=url, content='hi world')
        self.assertEqual(Page.select().count(), 1)

        self.assertRaises(IntegrityError, Page.create, url=url, content='hi world')
