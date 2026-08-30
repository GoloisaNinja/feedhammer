import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

import feedparser
from datetime import datetime
from time import mktime
from django.core.management.base import BaseCommand
from django.utils import timezone
from py_feeder.models import Feed, Article


class Command(BaseCommand):
    help = "Fetches latest articles from all saved RSS feeds securely."

    def handle(self, *args, **options):
        # Disguise request to avoid getting blocked by strict CDNs
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        feeds = Feed.objects.all()
        if not feeds:
            self.stdout.write(self.style.WARNING("No feeds found in the database."))
            return

        for feed in feeds:
            self.stdout.write(f"Connecting to feed: {feed.title}...")
            parsed_feed = feedparser.parse(feed.url, agent=USER_AGENT)

            # Check if feed parser failed entirely
            if parsed_feed.bozo:
                self.stdout.write(self.style.ERROR(f"Parsing error on '{feed.title}': {parsed_feed.bozo_exception}"))
                continue

            if not parsed_feed.entries:
                self.stdout.write(self.style.WARNING(f"Zero entries found for '{feed.title}'. Check URL structure."))
                continue

            saved_count = 0
            for entry in parsed_feed.entries:
                # Use unique fallback fields if standard .link is missing
                link = getattr(entry, 'link', None) or getattr(entry, 'id', None)
                if not link:
                    continue

                if Article.objects.filter(link=link).exists():
                    continue

                # Ensure datetime objects are timezone aware
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    naive_dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                    dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
                else:
                    dt = timezone.now()

                desc = getattr(entry, 'summary', '') or getattr(entry, 'description', '')

                Article.objects.create(
                    feed=feed,
                    title=getattr(entry, 'title', 'Untitled Post'),
                    description=desc,
                    link=link,
                    pub_date=dt
                )
                saved_count += 1

            self.stdout.write(self.style.SUCCESS(f"Finished '{feed.title}': Processed {saved_count} new entries."))
