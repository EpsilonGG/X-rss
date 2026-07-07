from __future__ import annotations

from datetime import datetime
from datetime import timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

from domain.models.tweet import Tweet
from exporters.base import BaseExporter


class RSSExporter(BaseExporter):
    def export(
        self,
        tweets: list[Tweet],
        *,
        output_path: Path,
        title: str,
        link: str,
        description: str,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            self.generate(
                tweets,
                title=title,
                link=link,
                description=description,
            ),
            encoding="utf8",
        )

    def generate(
        self,
        tweets: list[Tweet],
        *,
        title: str,
        link: str,
        description: str,
    ) -> str:
        rss = Element("rss", {"version": "2.0"})
        channel = SubElement(rss, "channel")

        self._text(channel, "title", title)
        self._text(channel, "link", link)
        self._text(channel, "description", description)
        self._text(channel, "lastBuildDate", self._rfc2822(datetime.now(timezone.utc)))

        for tweet in tweets:
            item = SubElement(channel, "item")
            self._text(item, "title", self._title(tweet))
            self._text(item, "link", tweet.url)
            self._text(item, "guid", tweet.url)
            self._text(item, "pubDate", self._rfc2822(tweet.published))
            self._text(item, "description", self._description(tweet))

        return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
            rss,
            encoding="unicode",
            short_empty_elements=False,
        )

    def _text(self, parent: Element, tag: str, value: str) -> None:
        SubElement(parent, tag).text = value

    def _title(self, tweet: Tweet) -> str:
        content = " ".join(tweet.content.split())
        if len(content) > 80:
            content = f"{content[:77]}..."
        username = tweet.author.username or tweet.author.name
        return f"@{username}: {content}" if content else f"@{username}"

    def _description(self, tweet: Tweet) -> str:
        parts = [f"<p>{escape(tweet.content).replace(chr(10), '<br/>')}</p>"]

        for media in tweet.media:
            escaped_url = escape(media.url, quote=True)
            parts.append(f'<p><a href="{escaped_url}">{escaped_url}</a></p>')

        return "\n".join(parts)

    def _rfc2822(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return format_datetime(value)
