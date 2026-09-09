# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Scripts'))
from pdfgen import build

# Hindi
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import hindi_data as HD

sections = []
for head, items in HD.SECTIONS:
    sections.append((head, items))

build(
    os.path.join(os.path.dirname(__file__), 'Hindi_JAC_Board_Question_Bank.pdf'),
    HD.TITLE,
    HD.SUBTITLE,
    sections
)
print("Hindi PDF generated")
