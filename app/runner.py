from typing import Optional

from config.loader import load_accounts
from config.loader import load_config
from domain.models.tweet import Tweet
from exporters import RSSExporter
from fetchers import NitterFetcher
from infrastructure.http import HTTPClient
from infrastructure.http import RawResponse
from parsers import HTMLTweetParser
from parsers import RSSTweetParser
from app.endpoint_pool import EndpointPool
from processors import RSSProcessor

def run() -> None:
    config = load_config()
    accounts = load_accounts()
    client = HTTPClient(
        timeout=config.http.timeout,
    )
    endpoint_pool = EndpointPool(config.provider.endpoints)
    fetchers = {
        endpoint: NitterFetcher(
            endpoint=endpoint,
            client=client,
        )
        for endpoint in config.provider.endpoints
    }
    
    html_parser = HTMLTweetParser()
    rss_parser = RSSTweetParser()
    exporter = RSSExporter()
    processor = RSSProcessor(
        output_dir=config.rss.processed_output_path,
    )
    
    try:
        for account in accounts:
            output_path = config.rss.output_path / f"{account.username}.xml"
            response, tweets = fetch_and_parse_account(
                username=account.username,
                endpoint_pool=endpoint_pool,
                fetchers=fetchers,
                html_parser=html_parser,
                rss_parser=rss_parser,
            )

            if response is None:
                print("=" * 60)
                print(account.username)
                print("Failed      : all endpoints failed or returned no tweets")
                if output_path.exists():
                    output_path.unlink()
                    print(f"Removed     : {output_path}")
                continue

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
        processor.process_directory(
            config.rss.output_path,
        )
    
        client.close()


def fetch_and_parse_account(
    *,
    username: str,
    endpoint_pool: EndpointPool,
    fetchers: dict[str, NitterFetcher],
    html_parser: HTMLTweetParser,
    rss_parser: RSSTweetParser,
) -> tuple[Optional[RawResponse], list[Tweet]]:
    for endpoint in endpoint_pool.endpoints():
        fetcher = fetchers[endpoint]

        result = try_fetch_and_parse(
            username=username,
            endpoint=endpoint,
            source="rss",
            fetch=lambda: fetcher.fetch_rss(username),
            parse=rss_parser.parse,
        )
        if result is not None:
            endpoint_pool.mark_success(endpoint)
            return result

        result = try_fetch_and_parse(
            username=username,
            endpoint=endpoint,
            source="html",
            fetch=lambda: fetcher.fetch(username),
            parse=html_parser.parse,
        )
        if result is not None:
            endpoint_pool.mark_success(endpoint)
            return result

    endpoint_pool.mark_failure(endpoint)
    return None, []


def try_fetch_and_parse(
    *,
    username: str,
    endpoint: str,
    source: str,
    fetch,
    parse,
) -> Optional[tuple[RawResponse, list[Tweet]]]:
        try:
            response = fetch()
            tweets = parse(response)

            print("=" * 60)
            print(username)
            print(f"Endpoint    : {endpoint}")
            print(f"Source      : {source}")
            print(f"Status      : {response.status_code}")
            print(f"Bytes       : {len(response.text.encode())}")
            print(f"Tweets      : {len(tweets)}")

            if tweets:
                return response, tweets

            print("Skip        : no tweets parsed")
        except Exception as exc:
            print("=" * 60)
            print(username)
            print(f"Endpoint    : {endpoint}")
            print(f"Source      : {source}")
            print(f"Error       : {exc}")

        return None
