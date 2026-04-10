from .hacker_news import crawl_hacker_news
from .rss_crawler import crawl_rss_feeds
from .dev_to import crawl_dev_to


def run_all_crawlers(db) -> int:
    count = 0
    print("Crawling Hacker News...")
    count += crawl_hacker_news(db)
    print("Crawling RSS feeds...")
    count += crawl_rss_feeds(db)
    print("Crawling Dev.to...")
    count += crawl_dev_to(db)
    print(f"Total new articles: {count}")
    return count
