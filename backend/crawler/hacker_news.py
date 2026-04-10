import httpx
from datetime import date
from sqlalchemy.exc import IntegrityError

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

CATEGORY_KEYWORDS = {
    "AI": [
        "ai", "artificial intelligence", "machine learning", "llm", "gpt",
        "neural", "deep learning", "chatgpt", "claude", "gemini", "openai",
        "anthropic", "generative", "transformer", "diffusion", "copilot",
    ],
    "WebDev": [
        "javascript", "react", "vue", "angular", "css", "html", "frontend",
        "backend", "node.js", "nodejs", "typescript", "next.js", "svelte",
        "webpack", "vite", "browser", "web dev", "webassembly", "wasm",
    ],
    "SpringBoot": [
        "spring boot", "spring framework", "java ", "jvm", "kotlin",
        "microservice", "hibernate", "maven", "gradle", "quarkus", "micronaut",
    ],
    "AWS": [
        "aws", "amazon web services", "ec2", "s3 ", "lambda", "cloudformation",
        "eks", "ecs", "dynamodb", "cloudfront", "sagemaker", "bedrock",
    ],
    "Azure": [
        "azure", "microsoft azure", "cosmos db", "azure functions", "aks",
        "azure devops", "microsoft cloud", "azure openai",
    ],
    "DevOps": [
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "github actions",
        "terraform", "ansible", "devops", "helm", "pipeline", "gitops",
        "observability", "prometheus", "grafana", "argocd",
    ],
}


def categorize(title: str, summary: str = "") -> str:
    text = (title + " " + (summary or "")).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "General"


def crawl_hacker_news(db) -> int:
    from models import Article

    count = 0
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(HN_TOP_STORIES_URL)
            story_ids = resp.json()[:60]

            for story_id in story_ids:
                try:
                    item_resp = client.get(HN_ITEM_URL.format(story_id))
                    item = item_resp.json()

                    if not item or item.get("type") != "story" or not item.get("url"):
                        continue

                    title = item.get("title", "").strip()
                    url = item.get("url", "").strip()
                    score = item.get("score", 0)
                    comments = item.get("descendants", 0)

                    article = Article(
                        title=title,
                        url=url,
                        summary=f"Score: {score} points · {comments} comments on Hacker News",
                        source="Hacker News",
                        category=categorize(title),
                        published_date=date.today(),
                        score=score,
                    )
                    db.add(article)
                    db.commit()
                    count += 1
                except IntegrityError:
                    db.rollback()
                except Exception:
                    db.rollback()
    except Exception as e:
        print(f"[HN] Crawl error: {e}")

    return count
