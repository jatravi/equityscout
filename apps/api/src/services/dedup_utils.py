from __future__ import annotations

import hashlib
import posixpath
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


# Tracking/query params to drop during canonicalization
_DROP_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "igshid",
    "ref",
    "ref_src",
    "source",
}


def canonicalize_url(url: str) -> str:
    """
    Canonical URL normalization for dedup:
    - lower-case scheme + host
    - remove default ports (:80 for http, :443 for https)
    - normalize path (collapse //, resolve dot segments)
    - trim trailing slash except root
    - sort query params
    - remove known tracking params (utm_*, gclid, fbclid, etc.)
    - drop fragment
    """
    parts = urlsplit(url.strip())

    scheme = (parts.scheme or "https").lower()

    # netloc normalization
    hostname = (parts.hostname or "").lower()
    port = parts.port

    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    if port and not default_port:
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    # path normalization
    raw_path = parts.path or "/"
    norm_path = posixpath.normpath(raw_path)

    # normpath removes trailing slash semantics; keep root as "/"
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path
    if norm_path != "/" and norm_path.endswith("/"):
        norm_path = norm_path.rstrip("/")

    # query normalization (drop tracking params, sort stable)
    q = parse_qsl(parts.query, keep_blank_values=True)
    filtered = []
    for k, v in q:
        lk = k.lower()
        if lk in _DROP_QUERY_KEYS or lk.startswith("utm_"):
            continue
        filtered.append((k, v))

    # Sort by key,value for stable canonical form
    filtered.sort(key=lambda x: (x[0], x[1]))
    query = urlencode(filtered, doseq=True)

    # drop fragment always
    return urlunsplit((scheme, netloc, norm_path, query, ""))


def sha256_bytes(content: bytes) -> str:
    """Return hex SHA-256 digest for byte content."""
    return hashlib.sha256(content).hexdigest()