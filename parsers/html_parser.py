from __future__ import annotations

from datetime import datetime
from datetime import timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from domain.models.author import Author
from domain.models.media import Media
from domain.models.tweet import Tweet
from infrastructure.http import RawResponse
from parsers.base import BaseParser


class HTMLTweetParser(BaseParser):
    def parse(self, response: RawResponse) -> list[Tweet]:
        tree = HTMLParser(response.text)
        tweets: list[Tweet] = []
        seen_ids: set[str] = set()

        for item in tree.css("div.timeline-item"):
            link = item.css_first("a.tweet-link")
            content = item.css_first("div.tweet-content")
            date = item.css_first("span.tweet-date a")

            if not (link and content):
                continue

            href = link.attributes.get("href", "")
            if "/status/" not in href:
                continue

            tweet_id = href.rstrip("/").split("/")[-1]
            if not tweet_id or tweet_id in seen_ids:
                continue

            tweets.append(
                Tweet(
                    tweet_id=tweet_id,
                    url=urljoin(response.url, href),
                    content=content.text(separator="\n", strip=True),
                    published=self._parse_published(date.attributes if date else {}),
                    author=self._parse_author(item),
                    media=self._parse_media(item, response.url),
                )
            )
            seen_ids.add(tweet_id)

        return tweets

    def _parse_author(self, item) -> Author:
        fullname = item.css_first("a.fullname")
        username = item.css_first("a.username")

        return Author(
            name=fullname.text(strip=True) if fullname else "",
            username=username.text(strip=True).lstrip("@") if username else "",
        )

    def _parse_media(self, item, base_url: str) -> list[Media]:
        media: list[Media] = []

        for node in item.css("div.attachments img, div.gallery-row img, video source"):
            src = node.attributes.get("src") or node.attributes.get("data-url")
            if src:
                media.append(Media(url=urljoin(base_url, src)))

        return media

    def _parse_published(self, attrs: dict[str, str]) -> datetime:
        raw = attrs.get("title") or attrs.get("datetime") or ""
        if not raw:
            return datetime.now(timezone.utc)

        normalized = raw.replace(" · ", " ")
        for fmt in ("%b %d, %Y %I:%M %p %Z", "%B %d, %Y %I:%M %p %Z"):
            try:
                return datetime.strptime(normalized, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        try:
            value = parsedate_to_datetime(normalized)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
