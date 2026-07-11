from __future__ import annotations

import re
from pathlib import Path
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET


class RSSProcessor:

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_directory(self, input_dir: Path) -> None:
        for file in sorted(input_dir.glob("*.xml")):
            self.process(file)

    def process(self, xml_path: Path) -> None:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        channel = root.find("channel")
        if channel is None:
            return

        username = self._get_username(channel)

        items = []

        seen = set()

        for item in channel.findall("item"):

            self._normalize_title(item)

            self._normalize_link(item, username)

            guid = item.findtext("guid", "")

            if guid in seen:
                continue

            seen.add(guid)

            items.append(item)

        items.sort(
            key=self._pubdate,
            reverse=True,
        )

        for item in channel.findall("item"):
            channel.remove(item)

        for item in items:
            channel.append(item)

        ET.indent(tree, space="    ")

        output = self.output_dir / xml_path.name

        tree.write(
            output,
            encoding="utf-8",
            xml_declaration=True,
        )

    def _get_username(self, channel) -> str:

        title = channel.findtext("title", "")

        m = re.match(r"@(.+?) on X", title)

        return m.group(1) if m else ""

    def _normalize_link(self, item, username):

        guid = item.find("guid")

        if guid is None:
            return

        m = re.search(r"/status/(\d+)", guid.text or "")

        if not m:
            return

        url = f"https://x.com/{username}/status/{m.group(1)}"

        guid.text = url

        link = item.find("link")

        if link is not None:
            link.text = url

    def _normalize_title(self, item):

        title = item.find("title")

        if title is None or not title.text:
            return

        text = title.text.strip()

        # 完全重复
        mid = len(text) // 2

        if len(text) % 2 == 0:

            left = text[:mid].strip()

            right = text[mid:].strip()

            if left == right:
                title.text = left
                return

        # 按行重复
        lines = [i.strip() for i in text.splitlines() if i.strip()]

        if len(lines) >= 2:

            half = len(lines) // 2

            if (
                len(lines) % 2 == 0
                and lines[:half] == lines[half:]
            ):
                title.text = "\n".join(lines[:half])

    def _pubdate(self, item):

        try:
            return parsedate_to_datetime(
                item.findtext("pubDate", "")
            )
        except Exception:
            return parsedate_to_datetime(
                "Thu, 01 Jan 1970 00:00:00 +0000"
            )
