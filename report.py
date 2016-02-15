import os
from app.models import initialize, Page, Link


def sizeof_fmt(num, suffix='B'):
    """ print formatted file size
    http://stackoverflow.com/a/1094933
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == "__main__":
    initialize('corpus.db')
    page_count = Page.select().count()
    crawled_count = Page.select().where(
        (Page.status_code == 200) &
        ((Page.content_type == 'text/html') |
        (Page.content_type == 'text/plain')))\
        .count()
    redirect_count = Page.select().where(Page.status_code == 301).count()
    to_crawl_count = Page.select().where(Page.status_code == 0).count()
    other_count = page_count - crawled_count - redirect_count - to_crawl_count

    link_count = Link.select().count()

    corpus_size = os.stat('corpus.db').st_size
    corpus_size = sizeof_fmt(corpus_size)

    print('crawled pages: {}'.format(crawled_count))
    print('redirect pages: {}'.format(redirect_count))
    print('pages to crawl: {}'.format(to_crawl_count))
    print('other pages: {}'.format(other_count))  # could include temporary redirects, server errors, etc.
    print('links: {}'.format(link_count))
    print('db size: {}'.format(corpus_size))
    print
