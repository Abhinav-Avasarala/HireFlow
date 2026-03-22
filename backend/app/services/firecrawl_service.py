from __future__ import annotations

from dataclasses import dataclass
import re

import httpx

from app.config import settings


class FirecrawlError(RuntimeError):
    """Raised when Firecrawl fails to return scrape content."""


BAD_SCRAPE_PATTERNS = (
    "our careers site has moved",
    "this site has moved",
    "page has moved",
    "access denied",
    "enable javascript",
    "just a moment",
    "verify you are human",
    "cloudflare",
)

NOISE_KEYWORDS = {
    "http",
    "https",
    "html",
    "www",
    "careers",
    "career",
    "job",
    "jobs",
    "apply",
    "application",
}


@dataclass
class FirecrawlScrapeResult:
    markdown: str
    title: str
    description: str
    keywords: list[str]
    source_url: str


class FirecrawlService:
    async def scrape_job_posting(self, url: str) -> FirecrawlScrapeResult:
        if not settings.firecrawl_api_key:
            raise FirecrawlError("FIRECRAWL_API_KEY is not configured.")

        endpoint = f"{settings.firecrawl_base_url.rstrip('/')}/v2/scrape"
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
        }

        headers = {
            "Authorization": f"Bearer {settings.firecrawl_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=settings.firecrawl_timeout_seconds) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

        if response.status_code >= 400:
            raise FirecrawlError(
                f"Firecrawl scrape failed with status {response.status_code}: {response.text}"
            )

        body = response.json()
        data = body.get("data", body)
        metadata = data.get("metadata", {})
        markdown = data.get("markdown", "")

        if not markdown.strip():
            raise FirecrawlError("Firecrawl returned an empty markdown payload.")

        keywords_value = metadata.get("keywords", "")
        keywords = [
            item.strip()
            for item in keywords_value.split(",")
            if isinstance(keywords_value, str) and item.strip()
        ]
        keywords = clean_keywords(keywords)
        validate_scrape_quality(markdown, metadata.get("title", ""), metadata.get("description", ""))

        return FirecrawlScrapeResult(
            markdown=markdown,
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            keywords=keywords,
            source_url=metadata.get("sourceURL", url),
        )


def clean_keywords(keywords: list[str]) -> list[str]:
    cleaned: list[str] = []
    for keyword in keywords:
        normalized = keyword.strip().lower()
        if not normalized:
            continue
        if normalized in NOISE_KEYWORDS:
            continue
        if normalized.startswith("http") or "/" in normalized or ".com" in normalized:
            continue
        cleaned.append(keyword.strip())
    return cleaned


def validate_scrape_quality(markdown: str, title: str, description: str) -> None:
    combined = " ".join([title, description, markdown[:1200]]).lower()
    if any(pattern in combined for pattern in BAD_SCRAPE_PATTERNS):
        raise FirecrawlError(
            "The job URL resolved to a redirect, moved page, or blocked page instead of a usable job posting. "
            "Try a different direct job URL or paste the job description text."
        )
    if not re.search(r"\b(requirements|responsibilities|qualifications|experience|skills)\b", combined):
        raise FirecrawlError(
            "Firecrawl did not return content that looks like a job posting. Try a different direct job URL or paste the job description text."
        )
