# -*- coding: utf-8 -*-
"""Build Frequency Analysis PDF."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from pdfgen import build
import frequency_data

out = os.path.join(os.path.dirname(__file__), '..', 'Frequency_Analysis_Previous_5_Years.pdf')
build(out, "FREQUENCY ANALYSIS - प्रश्न आवृत्ति विश्लेषण",
      "JAC Board Class 10 - कौन सा प्रश्न कितनी बार आया (2020-2024)",
      frequency_data.frequency_sections())
print("Frequency PDF generated:", out)
