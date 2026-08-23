from apps.api.src.services.dedup_utils import canonicalize_url, sha256_bytes


def test_canonicalize_url_tracking_and_case():
    u = "HTTPS://Example.COM:443/a//b/../c/?utm_source=x&b=2&a=1#frag"
    c = canonicalize_url(u)
    assert c == "https://example.com/a/c?a=1&b=2"


def test_sha256_bytes():
    assert sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"