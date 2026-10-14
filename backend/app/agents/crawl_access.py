"""Crawl-Access: robots.txt, sitemap.xml, llms.txt and whether AI crawlers may fetch the page."""
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

from app.schemas.state import AuditState, CrawlState
from app.services import http

AI_BOTS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Bytespider"]


def run(state: AuditState) -> None:
    root = urljoin(state.url, "/")
    r_status, robots = http.get(urljoin(root, "robots.txt"))
    s_status, _ = http.get(urljoin(root, "sitemap.xml"))
    l_status, _ = http.get(urljoin(root, "llms.txt"))
    crawl = CrawlState(robots_found=r_status == 200, sitemap_found=s_status == 200, llms_found=l_status == 200)
    parser = RobotFileParser()
    parser.parse(robots.splitlines() if crawl.robots_found else [])
    crawl.bots = {bot: parser.can_fetch(bot, state.url) for bot in AI_BOTS}
    blocked = [b for b, ok in crawl.bots.items() if not ok]
    if blocked:
        crawl.notes.append(f"robots.txt blocks: {', '.join(blocked)}")
    if not crawl.llms_found:
        crawl.notes.append("No /llms.txt found")
    if not crawl.sitemap_found:
        crawl.notes.append("No /sitemap.xml found")
    state.crawl = crawl
