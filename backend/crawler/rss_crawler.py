import re
import feedparser
from datetime import date
from sqlalchemy.exc import IntegrityError
from .hacker_news import categorize

RSS_FEEDS = [
    # AI / ML
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "source": "TechCrunch AI", "default_category": "AI"},
    # General Tech
    {"url": "https://techcrunch.com/feed/", "source": "TechCrunch", "default_category": "General"},
    {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "source": "Ars Technica", "default_category": "General"},
    {"url": "https://www.theverge.com/rss/index.xml", "source": "The Verge", "default_category": "General"},
    # Java / Spring Boot
    {"url": "https://spring.io/blog.atom", "source": "Spring Blog", "default_category": "SpringBoot"},
    {"url": "https://www.infoq.com/java/rss/", "source": "InfoQ Java", "default_category": "SpringBoot"},
    # AWS
    {"url": "https://aws.amazon.com/blogs/aws/feed/", "source": "AWS Blog", "default_category": "AWS"},
    {"url": "https://aws.amazon.com/blogs/devops/feed/", "source": "AWS DevOps", "default_category": "DevOps"},
    # Azure
    {"url": "https://azure.microsoft.com/en-us/blog/feed/", "source": "Azure Blog", "default_category": "Azure"},
    # DevOps
    {"url": "https://kubernetes.io/feed.xml", "source": "Kubernetes Blog", "default_category": "DevOps"},
    {"url": "https://www.docker.com/blog/feed/", "source": "Docker Blog", "default_category": "DevOps"},
    {"url": "https://github.blog/feed/", "source": "GitHub Blog", "default_category": "DevOps"},
    {"url": "https://www.infoq.com/devops/rss/", "source": "InfoQ DevOps", "default_category": "DevOps"},
]

_HTML_TAG = re.compile(r"<[^>]+>")


def _parse_date(entry) -> date:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return date(t.tm_year, t.tm_mon, t.tm_mday)
    return date.today()


def _clean(text: str, max_len: int = 500) -> str:
    return _HTML_TAG.sub("", text).strip()[:max_len]


def crawl_rss_feeds(db) -> int:
    from models import Article

    count = 0
    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:20]:
                title = (entry.get("title") or "").strip()
                url = (entry.get("link") or "").strip()
                if not title or not url:
                    continue

                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = _clean(raw_summary)
                pub_date = _parse_date(entry)
                category = categorize(title, summary) or feed_info["default_category"]

                try:
                    db.add(Article(
                        title=title,
                        url=url,
                        summary=summary,
                        source=feed_info["source"],
                        category=category,
                        published_date=pub_date,
                        score=0,
                    ))
                    db.commit()
                    count += 1
                except IntegrityError:
                    db.rollback()
        except Exception as e:
            print(f"[RSS] {feed_info['source']} error: {e}")

    return count
