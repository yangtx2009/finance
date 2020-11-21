import feedparser
import pprint

rss_urls = ["http://feeds.reuters.com/reuters/topNews",
            # "http://topics.bloomberg.com/belarus",
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",
            "http://rss.cnn.com/rss/edition_world.rss",
            "http://feeds.washingtonpost.com/rss/world",
            "https://www.cnbc.com/id/100727362/device/rss/rss.html",
            "https://www.rt.com/rss/news/",
            "https://www.spiegel.de/international/index.rss"]

if __name__ == '__main__':
    feed = feedparser.parse(rss_urls[4])
    # pprint.pprint(feed)
    print(len(feed))
    print(feed.entries[0].keys())
    print(feed.entries[0].title)
    print(feed.entries[0].published)
