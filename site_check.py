#!/usr/bin/env python3
"""Dependency-free quality and publication-safety checks for the static site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from datetime import date
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://housingaccountabilityarchive.org"
TAGLINE = "Documenting Housing. Advancing Accountability."
PROJECT_DESCRIPTION = "An independent, participant-founded public-interest documentation and records-verification project."
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SENSITIVE_EXTENSIONS = {".7z", ".csv", ".doc", ".docx", ".eml", ".heic", ".jpeg", ".jpg", ".msg", ".pdf", ".png", ".pst", ".tif", ".tiff", ".xls", ".xlsx", ".zip"}
ALLOWED_BINARY = {Path("assets/og-preview.png")}
SCOPE_NOTE = (
    "These educational models describe common administrative principles and draw primarily "
    "from HUD HOPWA authorities and guidance. Program-specific requirements vary, and cited "
    "HOPWA authorities should not be treated as governing other housing programs unless "
    "independently applicable."
)
LEARNING_AUTHORITY_PAGES = {
    "about-haa.html",
    "accountability-benefits.html",
    "documentation-matters.html",
    "housing-administration.html",
    "participant-pathway.html",
    "supportive-services.html",
}
GUIDEBOOK_URL = "https://files.hudexchange.info/resources/documents/HOPWARentalAssistanceGuidebook.pdf"


class Document(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.attrs: list[tuple[str, dict[str, str]]] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.headings: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.errors.append(f"duplicate attribute on <{tag}>")
        data = {name: value or "" for name, value in attrs}
        self.attrs.append((tag, data))
        if tag == "title":
            self.in_title = True
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}>")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"mismatched </{tag}> after <{self.stack[-1]}>")
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def fail(errors: list[str], path: Path | str, message: str) -> None:
    errors.append(f"{path}: {message}")


def main() -> int:
    errors: list[str] = []
    html_files = sorted(ROOT.glob("*.html"))
    expected_nav: list[str] | None = None
    public_pages = {path.name for path in html_files if path.name != "404.html"}
    parsed: dict[str, Document] = {}
    public_titles: dict[str, str] = {}
    public_descriptions: dict[str, str] = {}

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        doc = Document(path)
        doc.feed(text)
        doc.close()
        parsed[path.name] = doc
        if not text.lstrip().lower().startswith("<!doctype html>"):
            fail(errors, path.name, "missing HTML5 doctype")
        if not re.search(r'<html\s+lang="en"', text, re.I):
            fail(errors, path.name, "missing document language")
        if '<meta charset="utf-8">' not in text.lower():
            fail(errors, path.name, "missing UTF-8 charset")
        if 'name="viewport"' not in text:
            fail(errors, path.name, "missing responsive viewport metadata")
        if '<a class="skip-link" href="#main">' not in text or '<main id="main" tabindex="-1">' not in text:
            fail(errors, path.name, "skip link or focusable main target is missing")
        if 'document.documentElement.classList.add("js")' not in text:
            fail(errors, path.name, "progressive-enhancement marker is missing")
        if doc.stack:
            fail(errors, path.name, f"unclosed elements: {', '.join(doc.stack[-5:])}")
        for message in doc.errors:
            fail(errors, path.name, message)
        if doc.headings.count(1) != 1:
            fail(errors, path.name, f"expected one H1, found {doc.headings.count(1)}")
        for previous, current in zip(doc.headings, doc.headings[1:]):
            if current > previous + 1:
                fail(errors, path.name, f"heading level jumps from H{previous} to H{current}")

        metas = [attrs for tag, attrs in doc.attrs if tag == "meta"]
        links = [attrs for tag, attrs in doc.attrs if tag == "link"]
        title = "".join(doc.title_parts).strip()
        meta_names = {meta.get("name"): meta.get("content") for meta in metas if meta.get("name")}
        meta_properties = {meta.get("property"): meta.get("content") for meta in metas if meta.get("property")}
        description = meta_names.get("description", "").strip()
        if not title:
            fail(errors, path.name, "missing title")
        canonical = next((link.get("href") for link in links if link.get("rel") == "canonical"), None)
        if path.name == "404.html":
            robots = {token.strip().lower() for token in meta_names.get("robots", "").split(",")}
            if robots != {"noindex", "nofollow"}:
                fail(errors, path.name, "404 page must use noindex, nofollow")
            if canonical is not None:
                fail(errors, path.name, "404 page must not declare a canonical URL")
        else:
            expected_canonical = f"{DOMAIN}/" if path.name == "index.html" else f"{DOMAIN}/{path.name}"
            public_titles[path.name] = title
            public_descriptions[path.name] = description
            if not description:
                fail(errors, path.name, "missing required description")
            if "| HAA" in title:
                fail(errors, path.name, "title uses an abbreviated brand name")
            if canonical != expected_canonical:
                fail(errors, path.name, f"canonical must remain {expected_canonical}")
            required_social = {
                "og:title": bool(meta_properties.get("og:title")),
                "og:description": bool(meta_properties.get("og:description")),
                "og:type": bool(meta_properties.get("og:type")),
                "og:url": meta_properties.get("og:url") == expected_canonical,
                "og:image": meta_properties.get("og:image") == f"{DOMAIN}/assets/og-preview.png",
                "twitter:card": meta_names.get("twitter:card") == "summary_large_image",
                "twitter:title": meta_names.get("twitter:title") == meta_properties.get("og:title"),
                "twitter:description": meta_names.get("twitter:description") == meta_properties.get("og:description"),
                "twitter:image": meta_names.get("twitter:image") == f"{DOMAIN}/assets/og-preview.png",
            }
            for label, present in required_social.items():
                if not present:
                    fail(errors, path.name, f"missing or inconsistent required {label}")
            for property_name in ("og:title", "og:description", "og:type", "og:url", "og:image"):
                if sum(meta.get("property") == property_name for meta in metas) != 1:
                    fail(errors, path.name, f"expected exactly one {property_name} declaration")
            for name in ("description", "twitter:card", "twitter:title", "twitter:description", "twitter:image"):
                if sum(meta.get("name") == name for meta in metas) != 1:
                    fail(errors, path.name, f"expected exactly one {name} declaration")

        if path.name in LEARNING_AUTHORITY_PAGES:
            if text.count(SCOPE_NOTE) != 1:
                fail(errors, path.name, "required HAA-OR educational-authority scope note is missing or duplicated")
            if GUIDEBOOK_URL in text and not re.search(
                rf'<a href="{re.escape(GUIDEBOOK_URL)}">[^<]*\(PDF\)</a>', text
            ):
                fail(errors, path.name, "public guidebook link must be labeled as a PDF")

        nav_match = re.search(r'<nav class="site-nav"[^>]*>(.*?)</nav>', text, re.S)
        if not nav_match:
            fail(errors, path.name, "missing primary navigation")
        else:
            nav = re.findall(r'href="([^"]+)"', nav_match.group(1))
            if expected_nav is None:
                expected_nav = nav
            elif nav != expected_nav:
                fail(errors, path.name, "primary navigation links or order differ")
            if 'href="https://administrativedisplacement.org/"' not in nav_match.group(1):
                fail(errors, path.name, "primary navigation does not link to Administrative Displacement")
        if f"<span>{TAGLINE}</span>" not in text:
            fail(errors, path.name, "header tagline is inconsistent")
        if PROJECT_DESCRIPTION not in text:
            fail(errors, path.name, "standard project description is missing")
        if 'aria-controls="primary-navigation"' not in text:
            fail(errors, path.name, "mobile menu button lacks aria-controls")
        for tag, attrs in doc.attrs:
            if tag == "img" and not attrs.get("alt"):
                fail(errors, path.name, "image lacks alt text")
            if tag == "button" and "filter-button" in attrs.get("class", "") and attrs.get("aria-pressed") not in {"true", "false"}:
                fail(errors, path.name, "filter button lacks aria-pressed state")
            if tag in {"iframe", "embed", "object", "form"}:
                fail(errors, path.name, f"disallowed public element: <{tag}>")
            if tag == "script" and attrs.get("src", "").startswith(("http://", "https://")):
                fail(errors, path.name, "third-party JavaScript is not allowed")
        if 'href="updates.html"' not in text:
            fail(errors, path.name, "footer does not link to updates.html")
        if "<h3>Related Projects</h3>" not in text:
            fail(errors, path.name, "footer is missing the Related Projects section")
        if 'href="https://housingaccountabilityarchive.org/"' not in text or 'href="https://administrativedisplacement.org/"' not in text:
            fail(errors, path.name, "footer is missing a required related-project link")

        for tag, attrs in doc.attrs:
            for attr in ("href", "src"):
                value = attrs.get(attr)
                if not value or value.startswith(("#", "mailto:", "http://", "https://")):
                    continue
                target = ROOT / urlparse(value).path
                if not target.exists():
                    fail(errors, path.name, f"broken internal {attr}: {value}")

    for label, values in (("title", public_titles), ("description", public_descriptions)):
        duplicates: dict[str, list[str]] = {}
        for page, value in values.items():
            duplicates.setdefault(value, []).append(page)
        for value, pages in duplicates.items():
            if not value or len(pages) == 1:
                continue
            fail(errors, "metadata", f"duplicate {label} on {', '.join(sorted(pages))}: {value}")

    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_pages: set[str] = set()
    lastmods: list[str] = []
    for url in sitemap.findall("s:url", namespace):
        loc = url.findtext("s:loc", namespaces=namespace)
        lastmod = url.findtext("s:lastmod", namespaces=namespace)
        if not loc or not loc.startswith(DOMAIN):
            fail(errors, "sitemap.xml", f"invalid location: {loc}")
            continue
        sitemap_pages.add("index.html" if loc == f"{DOMAIN}/" else loc.rsplit("/", 1)[-1])
        if not lastmod or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod):
            fail(errors, "sitemap.xml", f"missing or invalid lastmod for {loc}")
        else:
            lastmods.append(lastmod)
    if sitemap_pages != public_pages:
        fail(errors, "sitemap.xml", f"coverage mismatch: missing={sorted(public_pages-sitemap_pages)}, extra={sorted(sitemap_pages-public_pages)}")

    home_doc = parsed["index.html"]
    archive_items = [attrs for tag, attrs in home_doc.attrs if tag == "a" and "data-archive-item" in attrs]
    indexed = {
        urlparse(item.get("href", "")).path.rsplit("/", 1)[-1]
        for item in archive_items
        if item.get("href", "").endswith(".html") and not item.get("href", "").startswith(("http://", "https://"))
    }
    if indexed != public_pages:
        fail(errors, "index.html", f"archive coverage mismatch: missing={sorted(public_pages-indexed)}, extra={sorted(indexed-public_pages)}")
    archive_hrefs = {item.get("href", "") for item in archive_items}
    required_external_pathways = {
        "https://administrativedisplacement.org/",
        "https://administrativedisplacement.org/concept-note/",
    }
    missing_external = required_external_pathways - archive_hrefs
    if missing_external:
        fail(errors, "index.html", f"archive is missing external pathways: {sorted(missing_external)}")
    if "404.html" in archive_hrefs:
        fail(errors, "index.html", "404 page must not appear in the public archive index")

    home_text = (ROOT / "index.html").read_text(encoding="utf-8")
    count_match = re.search(r'data-archive-count>(\d+)</strong>', home_text)
    if not count_match:
        fail(errors, "index.html", "server-rendered archive count is missing")
    elif int(count_match.group(1)) != len(archive_items) or int(count_match.group(1)) == 0:
        fail(errors, "index.html", f"server-rendered archive count must equal {len(archive_items)}")
    if any("hidden" in item for item in archive_items):
        fail(errors, "index.html", "archive pathways must be visible in the initial server-rendered state")
    archive_status = next(
        (attrs for tag, attrs in home_doc.attrs if tag == "p" and "data-archive-status" in attrs),
        {},
    )
    if (
        archive_status.get("role") != "status"
        or archive_status.get("aria-live") != "polite"
        or archive_status.get("aria-atomic") != "true"
    ):
        fail(errors, "index.html", "archive status must be an atomic polite live region")
    if not re.search(r'<noscript>.*All \d+ pathways are listed below\..*</noscript>', home_text, re.S):
        fail(errors, "index.html", "archive explorer needs an honest no-JavaScript fallback")
    if not re.search(r'data-archive-empty hidden', home_text):
        fail(errors, "index.html", "archive empty state must be hidden before criteria are applied")

    script = (ROOT / "script.js").read_text(encoding="utf-8")
    for key in ("ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "Home", "End", "Escape"):
        if f'"{key}"' not in script:
            fail(errors, "script.js", f"archive keyboard behavior is missing {key}")
    if 'if (activeFilter === "all") search.value = "";' not in script:
        fail(errors, "script.js", "All filter must clear search and restore every pathway")

    if lastmods:
        latest = date.fromisoformat(max(lastmods))
        expected_footer_date = f"Site updated {latest.strftime('%B')} {latest.day}, {latest.year}"
        for path in html_files:
            if expected_footer_date not in path.read_text(encoding="utf-8"):
                fail(errors, path.name, f"footer date is stale; expected {expected_footer_date}")

    required_home_text = [
        "HAA-OR-2026-001",
        "Submitted to Los Angeles City Controller",
        '<time datetime="2026-08-05">August 5, 2026</time>',
        '<span class="badge warning oversight-card-status">Pending Intake Review</span>',
        '<p class="eyebrow">Related initiative</p>',
        "AdministrativeDisplacement.org",
        "publication and documentation platform",
    ]
    for required in required_home_text:
        if required not in home_text:
            fail(errors, "index.html", f"missing required homepage update: {required}")

    schema_blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', home_text, re.S)
    if not schema_blocks:
        fail(errors, "index.html", "missing Organization relationship metadata")
    else:
        try:
            graph = json.loads(schema_blocks[0]).get("@graph", [])
            if not any(item.get("@type") == "Organization" and item.get("name") == "Housing Accountability Archive" for item in graph):
                fail(errors, "index.html", "structured metadata is missing the HAA Organization")
            if not any("https://administrativedisplacement.org/" in item.get("sameAs", []) for item in graph):
                fail(errors, "index.html", "structured metadata is missing the Administrative Displacement sameAs URL")
        except (json.JSONDecodeError, AttributeError) as exc:
            fail(errors, "index.html", f"invalid relationship JSON-LD: {exc}")

    oversight_path = ROOT / "oversight-action-haa-or-2026-001.html"
    oversight_text = oversight_path.read_text(encoding="utf-8")
    required_oversight_text = [
        "Administrative Oversight Referral HAA-OR-2026-001",
        "Targeted review request concerning publicly funded housing-program administration, contractor oversight, documentation controls, and housing stability.",
        "Submitted — Pending Intake Review",
        "August 5, 2026",
        "Office of the Los Angeles City Controller",
        "Fraud, Waste and Abuse Unit",
        "FWA0003652",
        "On August 5, 2026, the Housing Accountability Archive submitted Administrative Oversight Referral HAA-OR-2026-001 to the Office of the Los Angeles City Controller for evaluation under the Controller’s audit authority.",
        "The referral requests an independent review of whether City-administered housing funds, contracted responsibilities, participant-status systems, supportive-service documentation, transition planning, billing records, delegated authority, property-payment records, monitoring activity, corrective action, and records-custody controls can be reconciled through contemporaneous administrative records.",
        "The submission does not ask the Controller to adjudicate private liability or presume fraud. It requests verification of whether public funds, contractor responsibilities, documented services, and oversight controls operated consistently and were supported by records expected to exist.",
        "One property, one provider chain, and the period June 2023 through July 2026.",
        "Participant status, eligibility, extension, and exit records",
        "Supportive-service and housing-navigation documentation",
        "Participant-specific and bed-level billing records",
        "Delegated removal authority and approval controls",
        "Property-payment and occupancy records",
        "Monitoring, corrective action, and follow-up",
        "Contractor and subcontractor responsibility",
        "Records custody, retention, transfer, and audit trails",
        "August 5, 2026</time> — Referral submitted through the Controller’s official Fraud, Waste and Abuse portal",
        "August 5, 2026</time> — Case number FWA0003652 assigned",
        "Current</span> — Pending intake processing and review",
        "Supplemental exhibits</span> — Not included in the initial portal upload because of file-size limitations; submission method pending",
        "The underlying referral and supporting exhibits are not published because they contain personally identifying information, confidential participant records, and health-related information. Public updates will describe procedural developments without disclosing protected information.",
        "The underlying referral is withheld from public publication to protect confidential participant information and health-related records.",
        "The Controller’s online Fraud, Waste and Abuse portal accepted the submission and assigned case number FWA0003652.",
    ]
    for required in required_oversight_text:
        if required not in oversight_text:
            fail(errors, oversight_path.name, f"missing required public text: {required}")

    protected_program_pattern = re.compile(r"\b(?:HIV|AIDS|HOPWA)\b|Housing Opportunities for Persons With AIDS", re.I)
    improper_status_pattern = re.compile(
        r"accept(?:ed|ance)\s+(?:of\s+)?(?:the\s+)?allegations|"
        r"(?:initiated?|opened?)\s+(?:an?\s+)?audit|"
        r"(?:initiated?|opened?)\s+(?:an?\s+)?investigation|"
        r"referr(?:ed|al)\s+to\s+Audit Services",
        re.I,
    )
    if protected_program_pattern.search(oversight_text):
        fail(errors, oversight_path.name, "protected-program or health-status terminology is exposed")
    if improper_status_pattern.search(oversight_text):
        fail(errors, oversight_path.name, "portal intake is characterized as a substantive Controller action")
    if re.search(r"\b(?:associatedMedia|contentUrl|portal\s+(?:access\s+)?key)\b", oversight_text, re.I):
        fail(errors, oversight_path.name, "attachment metadata or portal-key language is exposed")
    if re.search(r"(?:href|src)=[\"'][^\"']+\.(?:pdf|docx?|xlsx?|zip)(?:[?#][^\"']*)?[\"']|\sdownload(?:=|\s|>)", oversight_text, re.I):
        fail(errors, oversight_path.name, "confidential-document link or download control is present")
    private_contact_pattern = re.compile(
        r"href=[\"'](?:mailto|tel):|"
        r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
        r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}|"
        r"\b\d{1,5}\s+[A-Z0-9.'-]+(?:\s+[A-Z0-9.'-]+){0,4}\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way)\b",
        re.I,
    )
    if private_contact_pattern.search(oversight_text):
        fail(errors, oversight_path.name, "private contact channel is exposed")

    oversight_schema_blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', oversight_text, re.S)
    if not oversight_schema_blocks:
        fail(errors, oversight_path.name, "missing WebPage structured metadata")
    else:
        try:
            oversight_schema = json.loads(oversight_schema_blocks[0])
            if oversight_schema.get("@type") != "WebPage" or oversight_schema.get("identifier") != "HAA-OR-2026-001":
                fail(errors, oversight_path.name, "structured metadata must describe only the public status webpage")
        except (json.JSONDecodeError, AttributeError) as exc:
            fail(errors, oversight_path.name, f"invalid status-page JSON-LD: {exc}")

    local_path_pattern = re.compile(r"(?:file://|/Users/|/home/|[A-Za-z]:\\\\)")
    private_data_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|(?:api[_-]?key|password|secret)\s*[:=]", re.I)
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in SENSITIVE_EXTENSIONS and relative not in ALLOWED_BINARY:
            fail(errors, relative, "sensitive or private-data file extension is not allowed")
        if path.suffix.lower() in {".html", ".css", ".js", ".md", ".txt", ".xml", ".yml", ".yaml", ".svg"}:
            text = path.read_text(encoding="utf-8")
            if local_path_pattern.search(text):
                fail(errors, relative, "accidental local filesystem path detected")
            if private_data_pattern.search(text):
                fail(errors, relative, "obvious secret or private-data pattern detected")

    if errors:
        print("Site quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Site quality checks passed for {len(html_files)} HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
