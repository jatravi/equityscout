from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import httpx


DEFAULT_USER_AGENT = "equityscout-bot/0.1 (+https://example.com/contact)"


@dataclass
class FetchResult:
    url: str
    final_url: Optional[str]
    status_code: Optional[int]
    headers: dict[str, str]
    content_bytes: Optional[bytes]
    fetched_at: datetime
    error: Optional[str]
    attempts: int


def _parse_retry_after(retry_after_value: str | None) -> Optional[float]:
    """
    Retry-After can be:
    - delta-seconds: "120"
    - HTTP date: "Wed, 21 Oct 2015 07:28:00 GMT"
    Returns seconds to wait.
    """
    if not retry_after_value:
        return None

    v = retry_after_value.strip()
    if not v:
        return None

    # delta-seconds
    if v.isdigit():
        return max(0.0, float(v))

    # HTTP date
    try:
        dt = parsedate_to_datetime(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delta)
    except Exception:
        return None


def _compute_backoff_seconds(
    attempt_index: int,  # 1-based
    base_delay: float = 0.5,
    max_delay: float = 15.0,
    jitter_ratio: float = 0.2,
) -> float:
    """
    Exponential backoff: base * 2^(attempt-1), capped at max_delay
    Add +/- jitter_ratio randomness.
    """
    exp = min(max_delay, base_delay * (2 ** (attempt_index - 1)))
    jitter = exp * jitter_ratio
    return max(0.0, exp + random.uniform(-jitter, jitter))


def fetch_url(
    url: str,
    *,
    connect_timeout: float = 5.0,
    read_timeout: float = 20.0,
    max_attempts: int = 4,
    base_backoff: float = 0.5,
    max_backoff: float = 15.0,
    user_agent: str = DEFAULT_USER_AGENT,
    follow_redirects: bool = True,
) -> FetchResult:
    """
    Fetch a URL with retry/backoff/rate-limit handling.

    Retry on:
    - HTTP 429
    - HTTP 5xx
    - network timeout / transport errors
    """
    timeout = httpx.Timeout(connect=connect_timeout, read=read_timeout, write=read_timeout, pool=connect_timeout)
    headers = {"User-Agent": user_agent, "Accept": "*/*"}

    last_error: Optional[str] = None
    last_status: Optional[int] = None
    last_headers: dict[str, str] = {}
    last_final_url: Optional[str] = None

    with httpx.Client(timeout=timeout, follow_redirects=follow_redirects, headers=headers) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.get(url)
                last_status = resp.status_code
                last_headers = dict(resp.headers)
                last_final_url = str(resp.url)

                # Success
                if 200 <= resp.status_code < 300:
                    return FetchResult(
                        url=url,
                        final_url=last_final_url,
                        status_code=resp.status_code,
                        headers=last_headers,
                        content_bytes=resp.content,
                        fetched_at=datetime.now(timezone.utc),
                        error=None,
                        attempts=attempt,
                    )

                # Retryable HTTP statuses
                retryable = (resp.status_code == 429) or (500 <= resp.status_code <= 599)
                if retryable and attempt < max_attempts:
                    retry_after = _parse_retry_after(resp.headers.get("Retry-After"))
                    sleep_s = retry_after if retry_after is not None else _compute_backoff_seconds(
                        attempt, base_delay=base_backoff, max_delay=max_backoff
                    )
                    time.sleep(sleep_s)
                    continue

                # Non-retryable or retries exhausted
                return FetchResult(
                    url=url,
                    final_url=last_final_url,
                    status_code=resp.status_code,
                    headers=last_headers,
                    content_bytes=resp.content if resp.content else None,
                    fetched_at=datetime.now(timezone.utc),
                    error=f"HTTP {resp.status_code}",
                    attempts=attempt,
                )

            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError, httpx.RemoteProtocolError, httpx.TransportError) as ex:
                last_error = f"{type(ex).__name__}: {ex}"
                if attempt < max_attempts:
                    time.sleep(_compute_backoff_seconds(attempt, base_delay=base_backoff, max_delay=max_backoff))
                    continue

                return FetchResult(
                    url=url,
                    final_url=last_final_url,
                    status_code=last_status,
                    headers=last_headers,
                    content_bytes=None,
                    fetched_at=datetime.now(timezone.utc),
                    error=last_error,
                    attempts=attempt,
                )

            except Exception as ex:
                # unexpected exception: don't spin forever
                last_error = f"{type(ex).__name__}: {ex}"
                return FetchResult(
                    url=url,
                    final_url=last_final_url,
                    status_code=last_status,
                    headers=last_headers,
                    content_bytes=None,
                    fetched_at=datetime.now(timezone.utc),
                    error=last_error,
                    attempts=attempt,
                )

    # Defensive fallback (should not hit)
    return FetchResult(
        url=url,
        final_url=last_final_url,
        status_code=last_status,
        headers=last_headers,
        content_bytes=None,
        fetched_at=datetime.now(timezone.utc),
        error=last_error or "Unknown fetch failure",
        attempts=max_attempts,
    )