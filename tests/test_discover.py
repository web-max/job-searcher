"""Discovery helper tests (offline)."""
from agent import discover


def test_strip_html():
    assert discover._strip_html("<p>Hello&nbsp;<b>world</b></p>") == "Hello world"


def test_job_id_stable():
    a = discover._job("src", "Co", "Role", "https://x.com/1")
    b = discover._job("src", "Co", "Role", "https://x.com/1")
    c = discover._job("src", "Co", "Role", "https://x.com/2")
    assert a["id"] == b["id"] != c["id"]
    assert len(a["id"]) == 12


def test_matches_terms():
    assert discover._matches_terms("Senior Customer Success Manager", ["customer success"])
    assert not discover._matches_terms("Backend Engineer", ["customer success"])
    assert discover._matches_terms("anything", [])  # empty terms = match all


def test_description_truncated():
    j = discover._job("s", "c", "t", "u", description="x" * 10000)
    assert len(j["description"]) <= 6000
