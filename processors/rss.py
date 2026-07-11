from __future__ import annotations

import re
from pathlib import Path
from email.utils import parsedate_to_datetime
from xml.dom import minidom
from xml.etree import ElementTree as ET


class RSSProcessor:

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_directory(
        self,
        input_dir: Path,
    ) -> None:

        for xml_file in sorted(input_dir.glob("*.xml")):
            self.process(xml_file)

    def process(
        self,
        xml_path: Path,
    ) -> None:

        tree = ET.parse(xml_path)
        root = tree.getroot()

        channel = root.find("channel")

        if channel is None:
            return

        username = self._username(channel)

        items = channel.findall("item")

        seen = set()
        processed = []

        for item in items:

            self._normalize_title(item)

            self._normalize_links(
                item,
                username,
            )

            guid = item.findtext("guid", "")

            if guid in seen:
                continue

            seen.add(guid)

            processed.append(item)

        processed.sort(
            key=self._pubdate,
            reverse=True,
        )

        for item in channel.findall("item"):
            channel.remove(item)

        for item in processed:
            channel.append(item)

        xml = ET.tostring(
            root,
            encoding="utf-8",
        )

        pretty = minidom.parseString(xml).toprettyxml(
            indent="    ",
            encoding="utf-8",
        )

        output = self.output_dir / xml_path.name

        output.write_bytes(pretty)

    def _username(
        self,
        channel,
    ) -> str:

        title = channel.findtext(
            "title",
            "",
        )

        m = re.match(
            r"@(.+?) on X",
            title,
        )

        if m:
            return m.group(1)

        return ""

    def _normalize_links(
        self,
        item,
        username,
    ) -> None:

        guid = item.find("guid")
        link = item.find("link")

        if guid is None:
            return

        status = self._status_id(
            guid.text or "",
        )

        if not status:
            return

        x = f"https://x.com/{username}/status/{status}"

        guid.text = x

        if link is not None:
            link.text = x

    def _status_id(
        self,
        url: str,
    ) -> str:

        m = re.search(
            r"/status/(\d+)",
            url,
        )

        if m:
            return m.group(1)

        return ""

    def _normalize_title(
        self,
        item,
    ) -> None:

        title = item.find("title")

        if title is None:
            return

        text = (title.text or "").strip()

        lines = [i.strip() for i in text.splitlines() if i.strip()]

        if len(lines) == 2 and lines[0] == lines[1]:
            title.text = lines[0]
            return

        words = text.split()

        if len(words) % 2 == 0:

            half = len(words) // 2

            if words[:half] == words[half:]:

                title.text = " ".join(words[:half])

    def _pubdate(
        self,
        item,
    ):

        try:

            return parsedate_to_datetime(
                item.findtext(
                    "pubDate",
                    "",
                )
            )

        except Exception:

            return parsedate_to_datetime(
                "Thu, 01 Jan 1970 00:00:00 +0000"
            )
