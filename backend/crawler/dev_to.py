import httpx
from datetime import date
from sqlalchemy.exc import IntegrityError
from .hacker_news import categorize

DEV_TO_API = "https://dev.to/api/articles"
TAGS = ["ai", "webdev", "java", "aws", "azure", "devops", "springboot", "kubernetes", "docker", "machinelearning"]


def crawl_dev_to(db) -> int:
    from models import Article

    count = 0
    try:
        with httpx.Client(timeout=15) as client:
            for tag in TAGS:
                try:
                    resp = client.get(DEV_TO_API, params={"tag": tag, "per_page": 8, "top": 1})
                    if resp.status_code != 200:
                        continue

                    for item in resp.json():
                        title = (item.get("title") or "").strip()
                        url = (item.get("url") or "").strip()
                        summary = (item.get("description") or "").strip()[:500]

                        if not title or not url:
                            continue

                        try:
                            pub_date = date.fromisoformat(item["published_at"][:10])
                        except Exception:
                            pub_date = date.today()

                        try:
                            db.add(Article(
                                title=title,
                                url=url,
                                summary=summary,
                                source="Dev.to",
                                category=categorize(title, summary),
                                published_date=pub_date,
                                score=item.get("public_reactions_count", 0),
                            ))
                            db.commit()
                            count += 1
                        except IntegrityError:
                            db.rollback()
                except Exception as e:
                    print(f"[Dev.to] tag={tag} error: {e}")
    except Exception as e:
        print(f"[Dev.to] crawl error: {e}")

    return count
