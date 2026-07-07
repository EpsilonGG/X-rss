from __future__ import annotations

from datetime import datetime
from datetime import timezone
from email.utils import parsedate_to_datetime
from html import unescape
from re import sub
from urllib.parse import urlparse
from xml.etree import ElementTree

from domain.models.author import Author
from domain.models.media import Media
from domain.models.tweet import Tweet
from infrastructure.http import RawResponse
from parsers.base import BaseParser


class RSSTweetParser(BaseParser):
    def parse(self, response: RawResponse) -> list[Tweet]:
        try:
            root = ElementTree.fromstring(response.text)
        except ElementTree.ParseError:
            return []

        username = self._username_from_url(response.url)
        tweets: list[Tweet] = []
        seen_ids: set[str] = set()

        for item in root.findall("./channel/item"):
            link = self._text(item, "link")
            title = self._text(item, "title")
            description = self._text(item, "description")

            if not link or "/status/" not in link:
                continue

            tweet_id = link.rstrip("/").split("/")[-1]
            if not tweet_id or tweet_id in seen_ids:
                continue

            content = self._clean_html(description) or title
            author = self._parse_author(title, username)

            tweets.append(
                Tweet(
                    tweet_id=tweet_id,
                    url=link,
                    content=content,
                    published=self._parse_published(self._text(item, "pubDate")),
                    author=author,
                    media=self._parse_media(item),
                )
            )
            seen_ids.add(tweet_id)

        return tweets

    def _text(self, item: ElementTree.Element, tag: str) -> str:
        node = item.find(tag)
        return (node.text or "").strip() if node is not None else ""

    def _clean_html(self, value: str) -> str:
        text = sub(r"<br\s*/?>", "\n", value)
        text = sub(r"<[^>]+>", "", text)
        return unescape(text).strip()

    def _parse_author(self, title: str, fallback_username: str) -> Author:
        if ":" in title:
            name = title.split(":", 1)[0].strip().lstrip("@")
        else:
            name = fallback_username

        return Author(
            name=name,
            username=name or fallback_username,
        )

    def _parse_media(self, item: ElementTree.Element) -> list[Media]:
        media: list[Media] = []

        for enclosure in item.findall("enclosure"):
            url = enclosure.attrib.get("url")
            content_type = enclosure.attrib.get("type", "")
            if url:
                media.append(
                    Media(
                        url=url,
                        type="video" if content_type.startswith("video/") else "image",
                    )
                )

        return media

    def _parse_published(self, value: str) -> datetime:
        if not value:
            return datetime.now(timezone.utc)

        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _username_from_url(self, url: str) -> str:
        parts = [part for part in urlparse(url).path.split("/") if part]
        return parts[0] if parts else ""
