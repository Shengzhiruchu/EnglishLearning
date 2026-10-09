"""Check generated local links, missing images, fragments, and duplicate IDs."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.errors = []
        self.lang = False
        self.title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = bool(attrs.get("lang"))
        if tag == "title":
            self.title = True
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == "img" and "alt" not in attrs:
            self.errors.append("Image missing alt text")


def check():
    pages = {}
    errors = []
    for path in SITE.rglob("*.html"):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        pages[path.resolve()] = page
        errors.extend(f"{path.relative_to(SITE)}: {error}" for error in page.errors)
        if not page.lang or not page.title:
            errors.append(f"{path.relative_to(SITE)}: missing language or title")
    if not pages or not (SITE / "index.html").exists():
        errors.append("Missing site homepage")
    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                errors.append(f"{path.relative_to(SITE)}: root-relative link breaks project Pages URLs: {link}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(SITE.resolve()):
                errors.append(f"{path.relative_to(SITE)}: link leaves site: {link}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{path.relative_to(SITE)}: broken link: {link}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{path.relative_to(SITE)}: broken fragment: {link}")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Validated {len(pages)} HTML pages: local links, fragments, images, titles and IDs")


if __name__ == "__main__":
    check()
