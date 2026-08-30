# py_feeder/services.py
import os
import certifi
import feedparser
from datetime import datetime
from time import mktime
from django.utils import timezone
from py_feeder.models import Feed, Article

os.environ['SSL_CERT_FILE'] = certifi.where()

def sync_all_feeds():
    """Fetches and saves new articles for all feeds. Returns total saved count."""
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    feeds = Feed.objects.all()
    total_saved = 0

    for feed in feeds:
        parsed_feed = feedparser.parse(feed.url, agent=USER_AGENT)

        if parsed_feed.bozo or not parsed_feed.entries:
            continue

        for entry in parsed_feed.entries:
            link = getattr(entry, 'link', None) or getattr(entry, 'id', None)
            if not link or Article.objects.filter(link=link).exists():
                continue

            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                naive_dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            else:
                dt = timezone.now()

            Article.objects.create(
                feed=feed,
                title=getattr(entry, 'title', 'Untitled Post'),
                description=getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                link=link,
                pub_date=dt
            )
            total_saved += 1

    return total_saved