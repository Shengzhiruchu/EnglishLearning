"""Render the blog using Python's standard library. Only docs/ is published."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs"


def escape(value):
    return html.escape(str(value), quote=True)


def render(name, **values):
    return Template((ROOT / "templates" / name).read_text(encoding="utf-8")).substitute(values)


def load_posts(config):
    posts = []
    slugs = set()
    for path in (ROOT / "content" / "posts").glob("*.json"):
        post = json.loads(path.read_text(encoding="utf-8"))
        for field in ("slug", "title", "date", "summary", "reading_minutes", "draft"):
            if field not in post:
                raise ValueError(f"{path.name}: missing {field}")
        slug = post["slug"]
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug != path.stem:
            raise ValueError(f"{path.name}: slug must match filename and use lowercase words separated by hyphens")
        if slug in slugs:
            raise ValueError(f"Duplicate slug: {slug}")
        slugs.add(slug)
        date.fromisoformat(post["date"])
        if type(post["draft"]) is not bool or type(post.get("example", False)) is not bool:
            raise ValueError(f"{path.name}: draft and example must be booleans")
        if type(post["reading_minutes"]) is not int or post["reading_minutes"] < 1:
            raise ValueError(f"{path.name}: reading_minutes must be a positive integer")
        for field in ("title", "summary"):
            if not isinstance(post[field], str) or not post[field].strip():
                raise ValueError(f"{path.name}: {field} must be nonempty text")
        post["content"] = path.with_suffix(".html").read_text(encoding="utf-8")
        if not post["draft"]:
            posts.append(post)
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def card(post):
    sample = '<span class="sample-badge">示例</span>' if post.get("example") else ""
    searchable = escape(post["title"] + " " + post["summary"])
    return f'''<article class="article-card" data-search="{searchable}">
<div class="card-art art-reading" aria-hidden="true"><span class="art-word">Read<span>.</span></span><span class="art-caption">BETWEEN THE LINES</span></div>
<div class="card-body"><div class="card-meta"><span class="card-label">学习札记{sample}</span><time datetime="{post['date']}">{post['date'].replace('-', '.')}</time></div>
<h3><a href="posts/{post['slug']}/">{escape(post['title'])}</a></h3><p>{escape(post['summary'])}</p><div class="card-footer"><span>{post['reading_minutes']} 分钟阅读</span><span aria-hidden="true">↗</span></div></div></article>'''


def layout(config, body, prefix, title, description, home=False):
    return render("layout.html", body=body, prefix=prefix, title=escape(config["title"]), english_title=escape(config["english_title"]), page_title=escape(title), description=escape(description), home_current='aria-current="page"' if home else "")


def word_card():
    words = json.loads((ROOT / "content" / "words.json").read_text(encoding="utf-8"))["cards"]
    if not words:
        raise ValueError("At least one word card is required")
    fields = ("word", "phonetic", "meaning", "line_one", "line_two", "highlight", "caption", "theme")
    for word in words:
        for field in fields:
            if not isinstance(word.get(field), str) or not word[field].strip():
                raise ValueError(f"Word card missing {field}")
        if word["theme"] not in ("sage", "gold", "blue", "rose", "olive", "lavender"):
            raise ValueError("Unknown word card theme")
    payload = json.dumps(words, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return render("word-card.html", **{field: escape(words[0][field]) for field in fields}, word_count=f"{len(words):02}", word_data=payload)


def build():
    config = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    posts = load_posts(config)
    words = word_card()
    # Never recursively remove a path other than this repository's generated docs directory.
    if OUTPUT.is_symlink() or OUTPUT.resolve() != ROOT / "docs" or OUTPUT.resolve().parent != ROOT:
        raise ValueError("Unsafe output directory")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    shutil.copytree(ROOT / "assets", OUTPUT / "assets")
    (OUTPUT / ".nojekyll").touch()
    notice = "标注“示例”的札记用于展示内容与排版，后续可替换为正式文章。" if any(p.get("example") for p in posts) else ""
    body = render("home.html", description=escape(config["description"]), post_count=len(posts), word_card=words, cards="\n".join(card(p) for p in posts), sample_notice=notice)
    (OUTPUT / "index.html").write_text(layout(config, body, ".", config["title"] + " · " + config["english_title"], config["description"], True), encoding="utf-8", newline="\n")
    for post in posts:
        destination = OUTPUT / "posts" / post["slug"]
        destination.mkdir(parents=True)
        body = render("article.html", prefix="../..", date_display=post["date"].replace("-", "."), sample_label="· 示例札记" if post.get("example") else "", post_title=escape(post["title"]), summary=escape(post["summary"]), reading_minutes=post["reading_minutes"], content=post["content"])
        (destination / "index.html").write_text(layout(config, body, "../..", post["title"] + " · " + config["title"], post["summary"]), encoding="utf-8", newline="\n")
    print(f"Built {len(posts)} posts into {OUTPUT}")


if __name__ == "__main__":
    build()
