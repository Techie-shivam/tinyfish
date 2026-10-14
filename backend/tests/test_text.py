from app.services.text import missing_lines, readability, same_site


def test_missing_lines_finds_js_only_text():
    rendered = "Welcome to our shop today\nPrice: $49 per month for the pro plan"
    fetched = "Welcome to our shop today"
    assert missing_lines(rendered, fetched) == ["Price: $49 per month for the pro plan"]
    assert readability(rendered, fetched) == 0.5


def test_same_site_handles_www_and_subdomains():
    assert same_site("https://www.a.com/x", "https://a.com/y")
    assert not same_site("https://a.com", "https://b.com")
