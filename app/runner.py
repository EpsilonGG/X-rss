from typing import Optional

from config.loader import load_accounts
from config.loader import load_config

from exporters import RSSExporter
from fetchers import NitterFetcher
from infrastructure.http import HTTPClient
from infrastructure.http import RawResponse
from parsers import HTMLTweetParser


def run() -> None:
    config = load_config()
    accounts = load_accounts()

    client = HTTPClient(
        timeout=config.http.timeout,
    )

    parser = HTMLTweetParser()
    exporter = RSSExporter()

    try:
        for account in accounts:
            response = fetch_account(
                username=account.username,
                endpoints=config.provider.endpoints,
                client=client,
            )

            if response is None:
                print("=" * 60)
                print(account.username)
                print("Failed      : all endpoints failed")
                continue

            tweets = parser.parse(response)
            output_path = config.rss.output_path / f"{account.username}.xml"

            exporter.export(
                tweets,
                output_path=output_path,
                title=f"@{account.username} on X",
                link=response.url,
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


def fetch_account(
    *,
    username: str,
    endpoints: list[str],
    client: HTTPClient,
) -> Optional[RawResponse]:
    for endpoint in endpoints:
        fetcher = NitterFetcher(
            endpoint=endpoint,
            client=client,
        )

        try:
            return fetcher.fetch(username)
        except Exception as exc:
            print("=" * 60)
            print(username)
            print(f"Endpoint    : {endpoint}")
            print(f"Error       : {exc}")

    return None
