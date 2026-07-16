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


PERU_REGIONS = ["worldwide", "anywhere", "peru", "latam", "latin america",
                "south america", "americas"]


def test_location_eligible_for_peru():
    ok = lambda loc: discover.location_eligible(loc, PERU_REGIONS)
    # clearly eligible
    assert ok("Worldwide")
    assert ok("Anywhere")
    assert ok("LATAM")
    assert ok("Latin America only")
    assert ok("Argentina, Brazil, Peru")
    assert ok("Americas")
    # vague -> keep, let the ranker decide
    assert ok("")
    assert ok("Remote")
    assert ok("see post")
    assert ok("Distributed team")   # names no known geography
    # clearly ineligible
    assert not ok("USA Only")
    assert not ok("United States")
    assert not ok("US-only, must be based in the US")
    assert not ok("Canada")
    assert not ok("Europe")
    assert not ok("UK or Ireland")
    assert not ok("North America")
    assert not ok("EMEA")


def test_location_eligible_no_regions_means_everything():
    assert discover.location_eligible("USA Only", [])


def test_mojibake_repair():
    assert discover._fix_mojibake("SÃ£o Paulo") == "São Paulo"
    assert discover._fix_mojibake("plain text") == "plain text"


def test_strip_html_unescapes_first():
    # Greenhouse-style entity-escaped markup must not survive as literal tags
    escaped = "&lt;div class=&quot;content&quot;&gt;Great job&lt;/div&gt;"
    out = discover._strip_html(escaped)
    assert "<" not in out and out == "Great job"
