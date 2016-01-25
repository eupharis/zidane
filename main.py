from app.models import initialize
from app.crawl import go


if __name__ == "__main__":
    initialize('corpus.db')
    go()
