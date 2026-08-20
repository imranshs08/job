from fpdf import FPDF
import re, textwrap

md_path = r"c:\Job Tracker\06-Interview-Prep\interview-prep.md"
pdf_path = r"c:\Job Tracker\06-Interview-Prep\interview-prep.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

def strip_md(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = text.replace('☐ Low ☐ Med ☐ High', '[ ] Low  [ ] Med  [ ] High')
    # Remove all emoji/non-latin chars
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.strip()

class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, "DevOps Interview Preparation Guide", align="L")
        self.ln(3)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Cover Page
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(15, 52, 96)
pdf.ln(25)
pdf.cell(0, 12, "DevOps Interview Preparation", align="C", ln=True)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Phase 5  |  December 2026  |  80+ Questions", align="C", ln=True)
pdf.cell(0, 6, "Generated: August 2026", align="C", ln=True)
pdf.ln(8)
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "Linux | Git | Docker | Kubernetes | CI/CD | Terraform | Cloud | Scenarios", align="C", ln=True)
pdf.add_page()

table_header = []
fill = False

i = 0
while i < len(lines):
    raw = lines[i].rstrip("\r\n")
    text = strip_md(raw)
    i += 1

    # Horizontal rule
    if re.match(r'^-{3,}$', raw.strip()):
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        table_header = []
        fill = False
        continue

    # H1
    if raw.startswith("# "):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(15, 52, 96)
        pdf.multi_cell(0, 8, text)
        pdf.set_draw_color(15, 52, 96)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        continue

    # H2
    if raw.startswith("## "):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 52, 96)
        pdf.multi_cell(0, 7, text)
        pdf.set_draw_color(15, 52, 96)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        continue

    # H3
    if raw.startswith("### "):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(26, 26, 46)
        pdf.multi_cell(0, 6, text)
        pdf.ln(1)
        continue

    # H4
    if raw.startswith("#### "):
        pdf.ln(2)
        pdf.set_font("Helvetica", "BI", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5, text)
        pdf.ln(1)
        continue

    # Blockquote
    if raw.startswith("> "):
        pdf.set_fill_color(240, 244, 255)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(60, 60, 80)
        content = strip_md(raw[2:]).strip()
        pdf.multi_cell(0, 5, content, fill=True)
        pdf.ln(2)
        continue

    # Table row
    if raw.startswith("|"):
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if all(re.match(r'^[-: ]+$', c) for c in cells if c):
            fill = False
            continue
        if not table_header:
            table_header = cells
            col_count = len(cells)
            col_w = 190 / col_count
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(15, 52, 96)
            pdf.set_text_color(255, 255, 255)
            for c in cells:
                pdf.cell(col_w, 6, strip_md(c)[:35], border=1, fill=True)
            pdf.ln()
        else:
            col_count = len(cells)
            col_w = 190 / col_count
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(30, 30, 30)
            bg = (244, 247, 251) if fill else (255, 255, 255)
            pdf.set_fill_color(*bg)
            x0, y0 = pdf.get_x(), pdf.get_y()
            # Calculate row height
            row_h = 6
            for c in cells:
                cw = col_w
                lines_needed = max(1, len(textwrap.wrap(strip_md(c), int(cw * 0.4))))
                row_h = max(row_h, lines_needed * 5)
            for j, c in enumerate(cells):
                pdf.set_xy(x0 + j * col_w, y0)
                pdf.multi_cell(col_w, row_h / max(1, len(textwrap.wrap(strip_md(c), int(col_w * 0.4))) or 1), strip_md(c), border=1, fill=True, max_line_height=5)
                # reset to same y row
            pdf.set_xy(x0, y0 + row_h)
            fill = not fill
        continue
    else:
        table_header = []
        fill = False

    # Bullet
    if re.match(r'^(\s*)[-*]\s', raw):
        indent = len(raw) - len(raw.lstrip())
        content = strip_md(re.sub(r'^(\s*)[-*]\s+', '', raw))
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(10 + indent)
        pdf.cell(5, 5, chr(149))
        pdf.multi_cell(175 - indent, 5, content)
        continue

    # Numbered list
    m = re.match(r'^\s*\d+\.\s+(.*)', raw)
    if m:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 5, strip_md(m.group(1)))
        continue

    # Empty line
    if not text:
        pdf.ln(2)
        continue

    # Regular paragraph
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 5, text)
    pdf.ln(1)

pdf.output(pdf_path)
print(f"PDF generated: {pdf_path}")
