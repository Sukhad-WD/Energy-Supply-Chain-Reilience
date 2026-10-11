import feedparser
import re
from datetime import datetime, timezone
from typing import List, Dict


RSS_FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}


ENERGY_KEYWORDS = [
    "oil",
    "crude",
    "gas",
    "energy",
    "iran",
    "iraq",
    "saudi",
    "russia",
    "ukraine",
    "hormuz",
    "red sea",
    "yemen",
    "houthi",
    "shipping",
    "tanker",
    "refinery",
    "pipeline",
    "sanction",
    "supply",
    "opec",
    "suez",
    "bab el-mandeb",
]


def clean_html(text: str) -> str:
    """Remove basic HTML tags from RSS summaries."""

    if not text:
        return ""

    return re.sub(r"<[^>]+>", "", text).strip()


def parse_published_time(entry) -> str:
    """
    Extract publication time from an RSS entry.
    Returns ISO-8601 UTC string.
    """

    parsed_time = entry.get("published_parsed")

    if parsed_time:
        dt = datetime(
            *parsed_time[:6],
            tzinfo=timezone.utc
        )

        return dt.isoformat()

    # If RSS feed doesn't provide a date,
    # use current UTC time.
    return datetime.now(timezone.utc).isoformat()


def fetch_news(limit: int = 30) -> List[Dict]:
    """
    Fetch recent geopolitical and energy-related news.
    """

    articles = []

    for source, feed_url in RSS_FEEDS.items():

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:

                title = entry.get("title", "").strip()

                summary = clean_html(
                    entry.get("summary", "")
                )

                link = entry.get("link", "")

                text = f"{title} {summary}".lower()

                if not any(
                    keyword in text
                    for keyword in ENERGY_KEYWORDS
                ):
                    continue

                articles.append(
                    {
                        "source": source,
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "published_at":
                            parse_published_time(entry),
                    }
                )

                if len(articles) >= limit:
                    return articles

        except Exception as error:
            print(
                f"Error fetching {source}: {error}"
            )

    return articles