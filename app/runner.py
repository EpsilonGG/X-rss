from config.loader import load_accounts
from config.loader import load_config

from exporters import RSSExporter
from fetchers import NitterFetcher
from infrastructure.http import HTTPClient
from parsers import HTMLTweetParser


def run() -> None:
    config = load_config()
    accounts = load_accounts()

    client = HTTPClient(
        timeout=config.http.timeout,
    )

    fetcher = NitterFetcher(
        endpoint=config.provider.endpoints[0],
        client=client,
    )
    parser = HTMLTweetParser()
    exporter = RSSExporter()

    try:
        for account in accounts:
            response = fetcher.fetch(account.username)
            tweets = parser.parse(response)
            output_path = config.rss.output_path / f"{account.username}.xml"
            feed_link = f"{fetcher.endpoint}/{account.username}"

            exporter.export(
                tweets,
                output_path=output_path,
                title=f"@{account.username} on X",
                link=feed_link,
                description=f"RSS feed for @{account.username}",
            )

            print("=" * 60)
            print(account.username)
            print(f"Status      : {response.status_code}")
            print(f"ContentType : {response.content_type}")
            print(f"Bytes       : {len(response.text.encode())}")
            print(f"URL         : {response.url}")
            print(f"Tweets      : {len(tweets)}")
            print(f"RSS         : {output_path}")

            if tweets:
                latest = tweets[0]
                print()
                print(latest.author.name)
                print(latest.published)
                print(latest.url)
                print()
                print(latest.content[:200])

    finally:
        client.close()
