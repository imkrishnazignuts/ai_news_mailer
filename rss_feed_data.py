import feedparser
from datetime import datetime,timezone
from bs4 import BeautifulSoup

RSS_FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "LangChain": "https://blog.langchain.dev/rss.xml/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "arXiv AI": "https://rss.arxiv.org/rss/cs.AI",
    "arXiv ML": "https://rss.arxiv.org/rss/cs.LG",
    "arXiv NLP": "https://rss.arxiv.org/rss/cs.CL",
    "Google News AI": "https://news.google.com/rss/search?q=artificial+intelligence",
}

def clean_html(html_text:str):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(" ", strip=True)

def fetch_news() -> list[dict]:
    articles = []

    for source_name,url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for news in feed.entries:
            article = {
                "title": news.get("title", ""),
                "url": news.get("link", ""),
                "source": source_name,
                "published": news.get("published", ""),
                "summary": clean_html(news.get("summary", "")),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

            articles.append(article)
    return articles


