#!/usr/bin/env python3
"""Inject a fixed lower-right corner nav (Tree / Home / Up) into live site pages.

Idempotent: replaces an existing #ancestry-corner-nav block.
Targets clean **/index.html pages only (skips SingleFile dumps, form.html, fix.html).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKER_START = "<!-- ancestry-corner-nav -->"
MARKER_END = "<!-- /ancestry-corner-nav -->"

# Lawsuit parent chain (relative from the detail page directory).
LAWSUIT_UP = {
    "sutcliffe/big-house-appeal": "../the-big-house-lawsuit/",
    "sutcliffe/the-big-house-lawsuit": "../nelson-v-dodge/",
    "sutcliffe/nelson-v-dodge": "../karl-carl-leonard-nilsson-nelson/",
}

BIO_SUBPAGE_SUFFIXES = ("-birth", "-maine")

ICON_TREE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 14 3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 8h-.2A1 1 0 0 1 8 6.3L12 2l4 4.3a1 1 0 0 1-.8 1.7H15l3 4.3a1 1 0 0 1-.7 1.7H17Z"/><path d="M12 22v-8"/></svg>"""

ICON_HOME = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>"""

ICON_UP = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 9-6-6-6 6"/><path d="M12 3v14"/><path d="M5 21h14"/></svg>"""

NAV_CSS = """#ancestry-corner-nav{position:fixed;z-index:999;right:20px;bottom:20px;display:flex;flex-direction:column;align-items:flex-end;gap:8px;pointer-events:none}
#ancestry-corner-nav a{pointer-events:auto;display:flex;align-items:center;justify-content:center;width:50px;height:50px;border-radius:4px;background:var(--color_brand,#6a7a7a);color:#fff;text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.22);opacity:.92;transition:opacity .2s,filter .2s,transform .15s}
#ancestry-corner-nav a:hover,#ancestry-corner-nav a:focus-visible{opacity:1;filter:brightness(1.08)}
#ancestry-corner-nav a:focus-visible{outline:2px solid #f8f5f2;outline-offset:2px}
body:has(.back-to-top) #ancestry-corner-nav{bottom:80px}
@media (min-width:568px){#ancestry-corner-nav{right:30px;bottom:30px}body:has(.back-to-top) #ancestry-corner-nav{bottom:90px}}
@media (min-width:1025px){#ancestry-corner-nav{right:40px;bottom:40px}body:has(.back-to-top) #ancestry-corner-nav{bottom:100px}}
@media print{#ancestry-corner-nav{display:none!important}}"""

BLOCK_RE = re.compile(
    r"\n*" + re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\n*",
    re.DOTALL,
)


def prefix_to_root(rel: Path) -> str:
    depth = len(rel.parts) - 1  # exclude filename
    return "" if depth == 0 else "../" * depth


def page_dir_key(rel: Path) -> str:
    """sutcliffe/fred-sutcliffe/index.html -> sutcliffe/fred-sutcliffe"""
    if rel.name.lower() != "index.html":
        return rel.as_posix().rsplit(".", 1)[0]
    if len(rel.parts) == 1:
        return ""
    return rel.parent.as_posix()


def up_href(rel: Path) -> str | None:
    key = page_dir_key(rel)
    parts = rel.parts

    if len(parts) == 1:
        return None  # root letter
    if parts[0] == "tree":
        return None

    # Family hubs: sutcliffe/index.html, riley/index.html, bock/index.html
    if len(parts) == 2 and parts[0] in {"sutcliffe", "riley", "bock"}:
        return "../tree/"

    slug = parts[1] if len(parts) >= 3 else ""

    if key in LAWSUIT_UP:
        return LAWSUIT_UP[key]

    if slug.startswith("chapter-") or slug.startswith("cchapter-"):
        return "../letter-menu/"

    if slug == "letter-menu":
        return "../carl-theodor-hansen/"

    for suffix in BIO_SUBPAGE_SUFFIXES:
        if slug.endswith(suffix):
            parent = slug[: -len(suffix)]
            if parent:
                return f"../{parent}/"

    return None  # main person bios and anything without a clear parent


def buttons_for(rel: Path) -> list[tuple[str, str, str]]:
    """Return (label, href, icon) in visual order Tree, Home, Up."""
    prefix = prefix_to_root(rel)
    parts = rel.parts
    under_tree = parts[0] == "tree"
    is_root = len(parts) == 1

    buttons: list[tuple[str, str, str]] = []
    if not under_tree:
        tree_href = "/tree/" if not prefix else f"{prefix}tree/"
        buttons.append(("Tree", tree_href, ICON_TREE))
    # No Home on root letter or on the tree page (Ernest: remove Home from tree).
    if not is_root and not under_tree:
        home = prefix if prefix else "./"
        buttons.append(("Home", home, ICON_HOME))
    up = up_href(rel)
    if up:
        buttons.append(("Up", up, ICON_UP))
    return buttons


def render_block(rel: Path) -> str:
    items = buttons_for(rel)
    links = []
    for label, href, icon in items:
        links.append(
            f'  <a href="{href}" title="{label}" aria-label="{label}">{icon}</a>'
        )
    inner = "\n".join(links) if links else ""
    return (
        f"{MARKER_START}\n"
        f'<nav id="ancestry-corner-nav" aria-label="Site shortcuts">\n'
        f"<style>{NAV_CSS}</style>\n"
        f"{inner}\n"
        f"</nav>\n"
        f"{MARKER_END}"
    )


def should_process(rel: Path) -> tuple[bool, str]:
    posix = rel.as_posix()
    if posix == "form.html" or rel.name == "form.html":
        return False, "form.html"
    if posix.startswith("sutcliffe/letters/"):
        return False, "SingleFile letter dump"
    if rel.name.startswith("carl_") and rel.suffix == ".html":
        return False, "SingleFile dump"
    if rel.name == "fix.html":
        return False, "fix.html"
    if rel.name != "index.html":
        return False, "not index.html"
    return True, ""


def strip_existing(html: str) -> str:
    html = BLOCK_RE.sub("", html)
    # Also strip a bare leftover wrapper if a prior run used only the id.
    html = re.sub(
        r'\s*<nav id="ancestry-corner-nav"[^>]*>.*?</nav>\s*',
        "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def inject(html: str, block: str) -> str:
    html = strip_existing(html)
    if re.search(r"</body>", html, flags=re.I):
        return re.sub(r"</body>", "\n" + block + "\n</body>", html, count=1, flags=re.I)
    if re.search(r"</html>", html, flags=re.I):
        return re.sub(r"</html>", "\n" + block + "\n</html>", html, count=1, flags=re.I)
    return html.rstrip() + "\n" + block + "\n"


def parse_hrefs(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = re.search(
        r'<nav id="ancestry-corner-nav"[^>]*>(.*?)</nav>',
        html,
        flags=re.DOTALL,
    )
    if not m:
        return out
    for href, label in re.findall(
        r'<a href="([^"]*)" title="([^"]*)"', m.group(1)
    ):
        out[label] = href
    return out


VERIFY_PAGES = [
    "index.html",
    "tree/index.html",
    "sutcliffe/fred-sutcliffe/index.html",
    "sutcliffe/fred-sutcliffe-birth/index.html",
    "sutcliffe/karl-carl-leonard-nilsson-nelson/index.html",
    "sutcliffe/nelson-v-dodge/index.html",
    "sutcliffe/letter-menu/index.html",
    "sutcliffe/chapter-1-mexican-border/index.html",
    "riley/index.html",
]


def main() -> int:
    updated: list[str] = []
    skipped: list[tuple[str, str]] = []
    errors: list[str] = []

    html_files = sorted(ROOT.rglob("*.html"))
    for path in html_files:
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        ok, reason = should_process(rel)
        if not ok:
            skipped.append((rel.as_posix(), reason))
            continue
        original = path.read_text(encoding="utf-8")
        items = buttons_for(rel)
        if not items:
            # e.g. tree page: no Tree/Home/Up — strip any prior nav
            stripped = strip_existing(original)
            if stripped != original:
                path.write_text(stripped, encoding="utf-8", newline="\n")
                updated.append(rel.as_posix())
            continue
        block = render_block(rel)
        new = inject(original, block)
        if new == original:
            continue
        path.write_text(new, encoding="utf-8", newline="\n")
        updated.append(rel.as_posix())

    print(f"Updated {len(updated)} pages")
    print("\n=== Verify hrefs ===")
    for rels in VERIFY_PAGES:
        p = ROOT / rels
        if not p.exists():
            print(f"MISSING {rels}")
            continue
        html = p.read_text(encoding="utf-8")
        hrefs = parse_hrefs(html)
        present = "ancestry-corner-nav" in html
        print(f"{rels}")
        print(f"  prefix={prefix_to_root(Path(rels))!r} nav={present} hrefs={hrefs}")
        expected = {label: href for label, href, _ in buttons_for(Path(rels))}
        if hrefs != expected:
            print(f"  MISMATCH expected={expected}")
            errors.append(f"href mismatch: {rels}")

    print("\n=== Skipped ===")
    by_reason: dict[str, list[str]] = {}
    for posix, reason in skipped:
        by_reason.setdefault(reason, []).append(posix)
    for reason, files in sorted(by_reason.items()):
        print(f"  {reason} ({len(files)}):")
        for f in files:
            print(f"    {f}")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(" ", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
