"""PDF memo export — renders an AnalysisResult as a clean one-pager with fpdf2."""

from fpdf import FPDF

ACCENT = (91, 45, 144)
MUTED = (91, 98, 116)
LINE = (227, 230, 239)
RISK_COLORS = {
    "Low": (15, 123, 77),
    "Medium": (160, 90, 0),
    "High": (179, 38, 30),
    "Unclear": (74, 85, 104),
}

# Core PDF fonts are latin-1; map the common typographic characters first.
_CHAR_MAP = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "--", "…": "...", " ": " ",
    "•": "-", "₹": "Rs ",
})


def _s(text: str) -> str:
    return str(text).translate(_CHAR_MAP).encode("latin-1", "replace").decode("latin-1")


class _MemoPDF(FPDF):
    def header(self):
        self.set_fill_color(*ACCENT)
        self.rect(0, 0, self.w, 16, "F")
        self.set_y(4)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, "Compliance Copilot - Analysis Memo", align="L")
        self.set_font("Helvetica", "", 8)
        self.cell(0, 8, "Policy-grounded - AI-assisted - Human review required", align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_y(22)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*LINE)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Synthetic demo data only - not a final compliance decision - page {self.page_no()}",
                  align="C")

    def section(self, title: str):
        self.ln(3)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, _s(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*LINE)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(1.5)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(26, 29, 41)

    def para(self, text: str, muted: bool = False):
        if muted:
            self.set_text_color(*MUTED)
        self.multi_cell(0, 5, _s(text))
        self.set_text_color(26, 29, 41)

    def bullet(self, text: str, marker: str = "-"):
        self.set_x(self.l_margin + 2)
        self.multi_cell(0, 5, _s(f"{marker} {text}"))


def build_pdf(result: dict, meta: dict) -> bytes:
    pdf = _MemoPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Meta + risk banner
    risk = result.get("risk_level", "Unclear")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*RISK_COLORS.get(risk, MUTED))
    esc_txt = "ESCALATION REQUIRED" if result.get("escalation_required") else "No escalation needed"
    pdf.cell(0, 7, _s(f"Risk level: {risk.upper()}    |    {esc_txt}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, _s(f"Policy type: {meta.get('policy_type', 'n/a')}    |    Model: {meta.get('model', 'n/a')}"),
             new_x="LMARGIN", new_y="NEXT")

    pdf.section("Direct answer")
    pdf.para(result["direct_answer"])

    pdf.section("Policy basis (cited evidence)")
    for c in result.get("policy_basis", []):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.bullet(f"Chunk {c['chunk_id']}: \"{c['excerpt']}\"")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_x(pdf.l_margin + 6)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 5, _s(c["point"]))
        pdf.set_text_color(26, 29, 41)
        pdf.ln(0.5)

    pdf.section("Missing information checklist")
    for m in result.get("missing_information", []) or ["None identified"]:
        pdf.bullet(m, marker="[ ]")

    if result.get("escalation_required"):
        pdf.section("Escalation")
        pdf.para(result.get("escalation_reason", ""))

    if result.get("assumptions"):
        pdf.section("Assumptions")
        for a in result["assumptions"]:
            pdf.bullet(a)

    pdf.section("Internal note (CRM / ticket draft)")
    pdf.para(result.get("internal_note", ""))

    pdf.section("Customer-safe response")
    pdf.para(result.get("customer_safe_response", ""))

    pdf.section("Disclaimer")
    pdf.para(result.get("disclaimer", ""), muted=True)

    return bytes(pdf.output())
