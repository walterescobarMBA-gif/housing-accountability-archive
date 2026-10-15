"""Publish HAA-2026-001 v1.0.2 from the archived v1.0.1 PDF.
Source edition is never overwritten. Changes are five focused copy corrections
and removal of stale XMP metadata; the 42-page findings are unchanged.
"""
from pathlib import Path
import os
import fitz
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "HAA_2026_001_Annual_Compliance_Review_v1.0.1_DATE_CORRECTION.pdf"
OUTPUT = ROOT / "HAA_2026_001_Annual_Compliance_Review_v1.0.2.pdf"
LOG = ROOT / "HAA_Correction_Log_v1.0.2.pdf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
BLACK = (0.121, 0.16, 0.215)

def line(page, old, new, size, family):
    found = page.search_for(old)
    if len(found) != 1:
        raise RuntimeError("Expected one occurrence, found %d on page %d: %s" % (len(found), page.number+1, old))
    r = found[0]
    page.add_redact_annot(fitz.Rect(r.x0-.3, r.y0-.1, r.x1+.4, r.y1+.1), fill=(1,1,1))
    page.apply_redactions(images=0, graphics=0, text=0)
    font = SERIF if family == "serif" else SANS
    fontname = "HAASerif" if family == "serif" else "HAASans"
    page.insert_font(fontname=fontname, fontfile=font)
    page.insert_text((r.x0, r.y0 + (0.891 if family == "serif" else 0.905)*size),
                     new, fontsize=size, fontname=fontname, color=BLACK)

def paragraph(page, start, replacement, top, bottom):
    matches = [b for b in page.get_text("dict")["blocks"]
               if "lines" in b and any(start in s["text"] for l in b["lines"] for s in l["spans"])]
    if len(matches) != 1: raise RuntimeError("Cannot locate paragraph on page %d" % (page.number+1))
    page.add_redact_annot((55.9, top-.2, 562, bottom+.2), fill=(1,1,1))
    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname="HAASerif", fontfile=SERIF)
    remainder = page.insert_textbox((56.25, top-.2, 562, bottom+4),
                                    replacement, fontsize=10.5,
                                    lineheight=1.247, fontname="HAASerif", color=BLACK)
    if remainder < 0: raise RuntimeError("Replacement text overflows page %d" % (page.number+1))

def make_report():
    pdf = fitz.open(str(SOURCE))
    if pdf.page_count != 42: raise RuntimeError("Unexpected page count")
    paragraph(pdf[2], "The final PDF is organized",
        "This report is organized so a reader unfamiliar with HOPWA can understand the program first, then follow the case, then evaluate the findings. Detailed source notes and the authority crosswalk appear in the appendices.",
        100.1945, 124.868)
    paragraph(pdf[9], "The LAHD manual states that project sponsors",
        "The LAHD manual states that sponsors must maintain written termination procedures and terminate assistance only in the most severe cases. The federal minimum process requires written reasons, review by someone who neither made nor approved the termination decision and is not subordinate to anyone who did, and prompt written notice of the final decision.",
        355.4945, 406.268)
    line(pdf[11], "No document in HAA's collection does not mean the document never existed.",
         "The absence of a document in HAA's collection does not mean it never existed.", 10, "serif")
    line(pdf[13], "Primary record: LAHD, “Update on Transitional Housing Case,” Aug. 4-11, 2025 (E-14 source thread).",
         "Primary record: LAHD, “Update on Transitional Housing Case,” Aug. 4-11, 2025 (CASE-04).", 7.5, "sans")
    line(pdf[35], "provider materials; County accepts/routs to APLA.",
         "provider materials; County accepts/routes to APLA.", 8, "sans")
    pdf.del_xml_metadata()
    pdf.set_metadata({
        "title": "HAA-2026-001 — Annual Compliance Review: Public Housing Program Administration",
        "author": "Housing Accountability Archive",
        "subject": "Documentary review of HOPWA program administration in Los Angeles using Participant Zero as a case study",
        "keywords": "HAA-2026-001, HOPWA, records verification, version 1.0.2",
        "creator": "Housing Accountability Archive",
        "producer": "Housing Accountability Archive — corrective public edition",
        "creationDate": "D:20261014204400-07'00'",
        "modDate": "D:20261014204400-07'00'"
    })
    pdf.save(str(OUTPUT), garbage=4, deflate=True, clean=False)
    pdf.close()
    before = fitz.open(str(SOURCE))
    after = fitz.open(str(OUTPUT))
    touched = {2,9,11,13,35}
    if len(after) != 42: raise RuntimeError("Result changed page count")
    for i in range(42):
        if i not in touched and before[i].get_text() != after[i].get_text():
            raise RuntimeError("Unexpected text change on page %d" % (i+1))
    corpus = " ".join(" ".join(x.get_text().split()) for x in after)
    for token in ("This report is organized", "neither made nor approved",
                  "The absence of a document", "(CASE-04)", "accepts/routes to APLA."):
        if token not in corpus: raise RuntimeError("Correction not verified: " + token)
    if OUTPUT.stat().st_size > 5*1024*1024: raise RuntimeError("PDF exceeds Voqal attachment limit")

def make_log():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="HAAHeader", parent=styles["Title"], textColor=colors.HexColor("#15263e"), fontName="Helvetica-Bold", fontSize=19, leading=24, spaceAfter=8))
    styles.add(ParagraphStyle(name="HAASection", parent=styles["Heading2"], textColor=colors.HexColor("#0c6b6d"), fontSize=11, spaceBefore=15, spaceAfter=7))
    styles.add(ParagraphStyle(name="HAABody", parent=styles["BodyText"], fontSize=9.5, leading=14, spaceAfter=9))
    doc = SimpleDocTemplate(str(LOG), pagesize=(612,792), rightMargin=52, leftMargin=52, topMargin=50, bottomMargin=50,
                            title="HAA-2026-001 Version and Correction Log — v1.0.2",
                            author="Housing Accountability Archive")
    story = [
        Paragraph("Housing Accountability Archive", styles["HAAHeader"]),
        Paragraph("HAA-2026-001 | Version and Correction Log", styles["Heading2"]),
        Paragraph("Current edition: Version 1.0.2 | October 14, 2026", styles["HAABody"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0c6b6d"), spaceAfter=12),
        Paragraph("Version 1.0 — Original issued edition", styles["HAASection"]),
        Paragraph("Original publication and distribution record. The Annual Compliance Review was published September 26, 2026.", styles["HAABody"]),
        Paragraph("Version 1.0.1 — September 25, 2026", styles["HAASection"]),
        Paragraph("Corrected the date of Participant Zero's written HSS records request from June 30 to July 1, 2026. The July 1 event was moved from the review-period chronology to Appendix E, Subsequent Events After June 30, 2026. No findings, verification determinations, recommendations, or substantive conclusions changed.", styles["HAABody"]),
        Paragraph("Version 1.0.2 — October 14, 2026", styles["HAASection"]),
        Paragraph("<b>Page 10:</b> Corrected the description of the HOPWA termination-review safeguard to specify that a reviewer must not have made or approved the termination decision and must not be subordinate to the person who did (24 CFR 574.310(e)(2)(ii)(B)).", styles["HAABody"]),
        Paragraph("<b>Page 14:</b> Replaced an inconsistent internal source designation with the public Appendix D code CASE-04.", styles["HAABody"]),
        Paragraph("<b>Page 36:</b> Corrected 'routs' to 'routes' in the consolidated chronology.", styles["HAABody"]),
        Paragraph("<b>Pages 3 and 12:</b> Made non-substantive editorial clarifications for readability.", styles["HAABody"]),
        Paragraph("<b>PDF metadata:</b> Removed stale 2013 XMP dates and refreshed the descriptive PDF metadata.", styles["HAABody"]),
        Paragraph("<b>Effect:</b> No findings, verification determinations, recommendations, or substantive case conclusions changed. The 42-page document remains the public-interest documentary review, not a governmental audit or legal determination.", styles["HAABody"]),
        Spacer(1, 12),
        Paragraph("<b>Publication control:</b> Versions 1.0 and 1.0.1 remain part of the historical record. Version 1.0.2 supersedes both for current citation and download. Corrections are recorded rather than silently overwritten.", styles["HAABody"]),
    ]
    doc.build(story)

if __name__ == "__main__":
    if not Path(SERIF).exists() or not Path(SANS).exists(): raise RuntimeError("Liberation fonts not available")
    make_report()
    make_log()
    print("Built:", OUTPUT.name, OUTPUT.stat().st_size, "bytes;", LOG.name, LOG.stat().st_size, "bytes")
