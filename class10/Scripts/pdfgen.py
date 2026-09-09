# -*- coding: utf-8 -*-
"""
PDF Generator for JAC Board Class 10 Question Banks - Supports Hindi (Devanagari) + English.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Mangal', os.path.join(FONT_DIR, 'mangal.ttf')))
pdfmetrics.registerFont(TTFont('Mangal-Bold', os.path.join(FONT_DIR, 'mangalb.ttf')))
# Try Arial for English; fallback to Mangal if not found
try:
    pdfmetrics.registerFont(TTFont('Helvetica', os.path.join(FONT_DIR, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Helvetica-Bold', os.path.join(FONT_DIR, 'arialbd.ttf')))
except Exception:
    pdfmetrics.registerFont(TTFont('Helvetica', os.path.join(FONT_DIR, 'mangal.ttf')))
    pdfmetrics.registerFont(TTFont('Helvetica-Bold', os.path.join(FONT_DIR, 'mangalb.ttf')))

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
LINE_H = 0.82 * cm

PURPLE = HexColor('#9C27B0')
GREEN = HexColor('#2E7D32')
DARK = HexColor('#000000')
GRAY = HexColor('#666666')

def _wrap(c, text, font, size, maxw):
    words = text.split(' ')
    cur = ''
    lines = []
    for w in words:
        t = (cur + ' ' + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

class PDFGen:
    def __init__(self, path, title, subtitle):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.title = title
        self.subtitle = subtitle
        self.pageno = 0
        self.y = PAGE_H - 2.2 * cm
        self.x = MARGIN
        self.w = PAGE_W - 2 * MARGIN

    def _draw_frame(self):
        # header
        self.c.setFont('Mangal-Bold', 9)
        self.c.setFillColor(PURPLE)
        self.c.drawString(self.x, PAGE_H - 1.4 * cm, "JAC Board Class 10 - Question Bank")
        self.c.drawRightString(self.x + self.w, PAGE_H - 1.4 * cm, "Previous 5 Years (2020-2024)")
        # footer
        self.c.setFont('Mangal', 8)
        self.c.setFillColor(GRAY)
        self.c.drawString(self.x, 1.0 * cm, "NCERT - Hindi Medium | Answer Key Included")
        self.c.drawRightString(self.x + self.w, 1.0 * cm, f"Page {self.pageno}")

    def new_page(self):
        self.c.showPage()
        self.pageno += 1
        self.y = PAGE_H - 2.2 * cm
        self._draw_frame()

    def need(self, h):
        if self.y - h < 2.0 * cm:
            self.new_page()

    def title_page(self):
        self.c.setFont('Mangal-Bold', 22)
        self.c.setFillColor(PURPLE)
        self.c.drawCentredString(PAGE_W/2, PAGE_H*0.75, "JAC BOARD CLASS 10")
        self.c.setFont('Mangal-Bold', 18)
        self.c.drawCentredString(PAGE_W/2, PAGE_H*0.68, self.title)
        self.c.setFont('Mangal', 13)
        self.c.setFillColor(DARK)
        self.c.drawCentredString(PAGE_W/2, PAGE_H*0.60, self.subtitle)
        self.c.setFont('Mangal', 11)
        self.c.setFillColor(GRAY)
        self.c.drawCentredString(PAGE_W/2, PAGE_H*0.52, "Previous 5 Years (2020-2024) Question Papers")
        self.c.drawCentredString(PAGE_W/2, PAGE_H*0.48, "Analysis + Frequency + Answer Key")
        self.new_page()

    def heading(self, text):
        self.need(1.5 * LINE_H)
        self.y -= 0.8 * LINE_H
        self.c.setFont('Mangal-Bold', 14)
        self.c.setFillColor(PURPLE)
        self.c.drawString(self.x, self.y, text)
        tw = self.c.stringWidth(text, 'Mangal-Bold', 14)
        self.c.setStrokeColor(PURPLE)
        self.c.setLineWidth(1.2)
        self.c.line(self.x, self.y - 0.15*cm, self.x + tw, self.y - 0.15*cm)
        self.y -= 0.65 * LINE_H

    def sub(self, text):
        self.need(1.2 * LINE_H)
        self.y -= 0.6 * LINE_H
        self.c.setFont('Mangal-Bold', 12.5)
        self.c.setFillColor(GREEN)
        self.c.drawString(self.x, self.y, text)
        self.y -= 0.6 * LINE_H

    def para(self, text, size=11.5, bold=False, color=DARK, indent=0):
        font = 'Mangal-Bold' if bold else 'Mangal'
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        for line in _wrap(self.c, text, font, size, self.w - indent):
            self.need(0.62 * LINE_H)
            self.c.drawString(self.x + indent, self.y, line)
            self.y -= 0.62 * LINE_H
        self.y -= 0.28 * LINE_H

    def q(self, text):
        self.need(1.0 * LINE_H)
        self.para(text, size=12.5, bold=True, color=DARK)

    def a(self, text):
        self.need(1.0 * LINE_H)
        self.para(text, size=11.5, bold=False, color=GREEN, indent=0.4 * cm)

    def save(self):
        self.c.save()

def build(path, title, subtitle, sections):
    g = PDFGen(path, title, subtitle)
    g.title_page()
    g._draw_frame()
    for head, items in sections:
        g.heading(head)
        for it in items:
            if isinstance(it, tuple):
                tag, txt = it[0], it[1]
                if tag == 'S':
                    g.sub(txt)
                elif tag == 'Q':
                    g.q(txt)
                elif tag == 'A':
                    g.a(txt)
                elif tag == 'MCQ':
                    g.q(txt)
                elif tag == 'FK':  # frequency key line
                    g.q(txt)
            else:
                g.para(str(it))
    g.save()
    return path
