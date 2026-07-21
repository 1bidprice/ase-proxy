from __future__ import annotations

from typing import Iterable

from .models import Asset, NewsItem


def _match_tickers(text: str, assets: Iterable[Asset]) -> list[str]:
    text_l = text.casefold()
    matched = []
    for asset in assets:
        token_candidates = {
            asset.ticker.casefold(),
            asset.name.casefold(),
            asset.name.split()[0].casefold(),
            *(alias.casefold() for alias in asset.aliases),
        }
        if any(token and token in text_l for token in token_candidates):
            matched.append(asset.ticker)
    return sorted(set(matched))


def fetch_rss_news(sources: list[dict], assets: list[Asset], max_items_per_source: int = 40) -> list[NewsItem]:
    import feedparser

    items: list[NewsItem] = []
    seen_links: set[str] = set()

    for source in sources:
        if source.get("type") != "rss":
            continue

        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:max_items_per_source]:
            title = getattr(entry, "title", "") or ""
            link = getattr(entry, "link", "") or ""
            summary = getattr(entry, "summary", "") or ""
            published = getattr(entry, "published", None)

            if link and link in seen_links:
                continue

            matched = _match_tickers(f"{title} {summary} {link}", assets)
            if matched:
                items.append(
                    NewsItem(
                        source=source["name"],
                        title=title,
                        link=link,
                        published=published,
                        matched_tickers=matched,
                    )
                )
                if link:
                    seen_links.add(link)

    return items
