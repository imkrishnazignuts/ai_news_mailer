import html

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from fastapi import APIRouter
from news_news import items
from new_article_retrival import get_new_articles
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from database import Session_local
import os
import json

load_dotenv()

router = APIRouter(
    prefix="/send-mail",
    tags=["summarize news mail"]
)

load_dotenv()


llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
    """
You are an elite AI and software industry analyst preparing a premium daily engineering briefing email for developers, AI engineers, CTOs, architects, engineering managers, researchers, and technical professionals.

Your task is to analyze the provided technology news and return ONLY valid JSON for a professional HTML email newsletter.

======================== NEWS INPUT ========================

{news}

============================================================

STRICT FILTERING RULES:
eturn ONLY news that has DIRECT PRACTICAL VALUE for developers/coders.

STRICT INCLUDE ONLY IF THE NEWS IS ABOUT:
- New AI model release developers can use
- New LLM API, SDK, framework, tool, or platform
- Coding agent / AI IDE / developer tooling update
- RAG, agents, vector DB, embeddings, inference, fine-tuning
- Open-source AI library/model release
- Cloud/GPU/inference infrastructure useful for builders
- Security issue affecting AI apps, APIs, packages, or dev tools
- Breaking API/pricing/model/deprecation change developers must know
- Major benchmark/research that changes model choice or architecture

STRICT REJECT:
- Politics or government AI policy
- Stock market / funding / company valuation
- Executive orders
- Cabinet/minister/portfolio announcements
- Generic enterprise AI adoption
- Marketing articles
- Opinion pieces
- Non-technical business news
- AI used by restaurants, banks, retail, hospitals, etc. unless it releases developer-facing tech
- Certifications/courses unless they introduce an actual developer tool/API/framework
- News that only says “company uses AI”
- Anything not useful to a developer building software this week

 ONLY INCLUDE NEWS THAT IS:
   - Highly relevant to developers
   - Technically impactful
   - Important for future engineering trends
   - Significant infrastructure/platform changes
   - Important model/API releases
   - Major security incidents
   - Important cloud/GPU/AI ecosystem updates
   - Major open-source releases
   - Important AI agent/RAG/LLM developments
   - Important developer tooling/platform updates

 IGNORE:
   - Minor feature updates
   - Small announcements
   - Marketing articles
   - Opinion pieces
   - Generic AI discussions
   - Tiny product updates
   - Duplicate news
   - Weak or low-impact stories
   - News without technical significance

 REMOVE DUPLICATES:
   - If multiple articles discuss the same topic, merge them into ONE clean summary.

 VERY IMPORTANT FILTERING RULE:
   - ONLY include genuinely important and high-impact news.
   - Quality is FAR more important than quantity.
   - If only 1 story is important, return only 1.
   - If only 2 stories are important, return only 2.
   - Never force unnecessary news into the digest.
   - Maximum allowed stories is 5.
   - Returning fewer stories is completely acceptable.
   - DO NOT include mediocre or filler content just to increase count.

6. WRITING STYLE:
   - Professional
   - Concise
   - Executive engineering briefing style
   - Easy to scan quickly in email
   - No hype
   - No clickbait
   - No exaggerated claims

7. SUMMARY RULES:
   - Each summary should be 2-4 concise sentences.
   - Focus on technical impact.
   - Explain WHY engineers should care.
   - Keep summaries information dense.
   - Avoid repeating title words.

9. OUTPUT RULES:
   - Return ONLY valid JSON.
   - No markdown.
   - No explanations.
   - No code blocks.
   - No extra text before or after JSON.
   - JSON must be parseable with json.loads()

RETURN THIS EXACT JSON STRUCTURE:

{{
  "newsletter_title": "Todays Latest AI news",
  "newsletter_subtitle": "Today's Highlights",
  "date": "according to day",
  "total_stories": accroding data ,
  "highlights": [
    {{
      "category": "AI",
      "title": "title",
      "summary": "Professional 2-4 sentence summary explaining technical impact and why developers should care.",
      "source": "as per source",
      "importance": "high"
    }}
  ],
  "key_takeaway": "One concise paragraph summarizing the biggest industry trend from today's news."
}}

FINAL RULE:
If a news item is not important enough for busy engineers to spend time reading, DO NOT include it.
"""
)

chain = prompt | llm | JsonOutputParser()

MAX_ARTICLES_FOR_LLM = 25
MAX_SUMMARY_CHARS = 700
MAX_NEWS_INPUT_CHARS = 18000

PREFERRED_SOURCES = {"OpenAI", "LangChain", "Hugging Face", "arXiv AI", "arXiv ML", "arXiv NLP"}
DEVELOPER_KEYWORDS = {
    "agent",
    "ai",
    "api",
    "arxiv",
    "benchmark",
    "cloud",
    "code",
    "coding",
    "developer",
    "embedding",
    "fine-tuning",
    "framework",
    "gpu",
    "inference",
    "langchain",
    "llm",
    "model",
    "open source",
    "openai",
    "rag",
    "sdk",
    "security",
    "tool",
    "vector",
}

def _clip_text(value, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."

def _article_score(article: dict) -> int:
    source = article.get("source", "")
    text = f"{article.get('title', '')} {article.get('summary', '')} {source}".lower()
    score = 3 if source in PREFERRED_SOURCES else 0
    return score + sum(1 for keyword in DEVELOPER_KEYWORDS if keyword in text)

def prepare_news_for_llm(articles: list[dict]) -> str:
    ranked_articles = sorted(articles, key=_article_score, reverse=True)
    compact_articles = []

    for article in ranked_articles[:MAX_ARTICLES_FOR_LLM]:
        compact_articles.append({
            "title": _clip_text(article.get("title"), 220),
            "source": article.get("source"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "summary": _clip_text(article.get("summary"), MAX_SUMMARY_CHARS),
        })

    news_json = json.dumps(compact_articles, default=str, ensure_ascii=False)
    if len(news_json) <= MAX_NEWS_INPUT_CHARS:
        return news_json

    trimmed_articles = []
    total_chars = 2
    for article in compact_articles:
        article_json = json.dumps(article, default=str, ensure_ascii=False)
        if total_chars + len(article_json) + 1 > MAX_NEWS_INPUT_CHARS:
            break
        trimmed_articles.append(article)
        total_chars += len(article_json) + 1

    return json.dumps(trimmed_articles, default=str, ensure_ascii=False)

def build_newsletter_html(data: dict) -> str:
    highlights_html = ""

    for item in data.get("highlights", []):
        category = html.escape(item.get("category", "TECH"))
        title = html.escape(item.get("title", ""))
        summary = html.escape(item.get("summary", ""))
        source = html.escape(item.get("source", ""))
        importance = html.escape(item.get("importance", "high"))

        highlights_html += f"""
        <tr>
            <td style="padding:22px 0;border-bottom:1px solid #e5e7eb;">
                <div style="font-size:11px;font-weight:700;color:#f97316;text-transform:uppercase;letter-spacing:.5px;">
                    {category} · {importance}
                </div>

                <h2 style="font-family:Georgia,serif;font-size:22px;line-height:1.25;margin:8px 0 8px;color:#111827;">
                    {title}
                </h2>

                <p style="font-size:15px;line-height:1.7;color:#374151;margin:0;">
                    {summary}
                </p>

                <p style="font-size:13px;color:#6b7280;margin:12px 0 0;">
                    Source: {source}
                </p>
            </td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;">
        <tr>
            <td align="center" style="padding:28px 12px;">
                <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:34px;">

                    <tr>
                        <td style="border-bottom:1px solid #d1d5db;padding-bottom:18px;">
                            <p style="font-size:13px;color:#6b7280;margin:0;">
                                AI News Daily Digest
                            </p>

                            <h1 style="font-family:Georgia,serif;font-size:38px;line-height:1.1;margin:8px 0;color:#111827;">
                                {html.escape(data.get("newsletter_title", "Medium Daily Digest"))}
                            </h1>

                            <p style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#6b7280;margin:0;">
                                {html.escape(data.get("newsletter_subtitle", "Today's Highlights"))}
                            </p>
                        </td>
                    </tr>

                    {highlights_html}

                    <tr>
                        <td style="padding-top:24px;">
                            <h3 style="font-size:17px;color:#111827;margin:0 0 8px;">
                                Key Takeaway of the Day
                            </h3>

                            <p style="font-size:15px;line-height:1.7;color:#374151;margin:0;">
                                {html.escape(data.get("key_takeaway", ""))}
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

def send_newsletter_email(to_emails:list[str],subject:str,html_content:str):
   msg = MIMEMultipart("alternative")
   msg["from"]=os.getenv("SMTP_EMAIL")
   msg["to"]=", ".join(to_emails)
   msg["subject"]=subject
   msg.attach(MIMEText(html_content,"html"))

   with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
       server.login(
           os.getenv("SMTP_EMAIL"),
           os.getenv("SMTP_PASSWORD")
       )
       server.sendmail(
            os.getenv("SMTP_EMAIL"),
            to_emails,
            msg.as_string()
        )

@router.get("")
def send_mail():
    db:Session=Session_local()
    try:
      news = get_new_articles(db)
      data = chain.invoke({"news":news})

      html_content = build_newsletter_html(data)
      send_newsletter_email(["krishnaz@zignuts.com","anshg@zignuts.com","devp@zignuts.com","abhinava@zignuts.com"],"Latest Ai News",html_content=html_content)
      return {
          "message":"email sended succesfully"
      }
    finally:
        db.close()

# @router.get("")
# def send_mail():
#     print("CRON HIT /send-mail")
#     db:Session=Session_local()
#     try:
#       news = get_new_articles(db)
#       news_input = prepare_news_for_llm(news)
#       print(f"LLM news input: {len(news)} articles fetched, {len(news_input)} chars sent")
#       data = chain.invoke({"news": news_input})

#       html_content = build_newsletter_html(data)
#       send_newsletter_email(["krishnaz@zignuts.com"],"Latest Ai News",html_content=html_content)
#       return {
#           "message":"email sended succesfully"
#       }
#     finally:
#         db.close()
