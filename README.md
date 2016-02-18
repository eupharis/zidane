# Zidane: Simple Web Crawler

A single threaded python web crawler built on top of:

* [requests](http://docs.python-requests.org/en/master/)
* [sqlite](https://www.sqlite.org/about.html)
* [peewee](http://docs.peewee-orm.com/en/latest/)

To install:

```bash
mkvirtualenv zidane --python=python3.5
pip install -r requirements.txt

# to run the crawler
python main.py

# to get reports about what has been crawled
python report.py
```
