# -*- coding: utf-8 -*-
"""Master PDF builder for all JAC Class 10 subjects."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from pdfgen import build

BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(BASE)

def addpath(p):
    sys.path.insert(0, p)

# Hindi
addpath(os.path.join(HOME, 'Hindi'))
import hindi_data
build(os.path.join(HOME, 'Hindi', 'Hindi_JAC_Board_Question_Bank.pdf'),
      hindi_data.TITLE, hindi_data.SUBTITLE, hindi_data.SECTIONS)
print("Hindi OK")

# English
addpath(os.path.join(HOME, 'English'))
import english_data
build(os.path.join(HOME, 'English', 'English_JAC_Board_Question_Bank.pdf'),
      english_data.TITLE, english_data.SUBTITLE, english_data.SECTIONS)
print("English OK")

# Mathematics
addpath(os.path.join(HOME, 'Mathematics'))
import maths_data
build(os.path.join(HOME, 'Mathematics', 'Mathematics_JAC_Board_Question_Bank.pdf'),
      maths_data.TITLE, maths_data.SUBTITLE, maths_data.SECTIONS)
print("Mathematics OK")

# Science
addpath(os.path.join(HOME, 'Science'))
import science_data
build(os.path.join(HOME, 'Science', 'Science_JAC_Board_Question_Bank.pdf'),
      science_data.TITLE, science_data.SUBTITLE, science_data.SECTIONS)
print("Science OK")

# History
addpath(os.path.join(HOME, 'Social_Science', '1_Itihaas_History'))
import history_data
build(os.path.join(HOME, 'Social_Science', '1_Itihaas_History', 'History_Itihaas_Question_Bank.pdf'),
      history_data.TITLE, history_data.SUBTITLE, history_data.SECTIONS)
print("History OK")

# Geography
addpath(os.path.join(HOME, 'Social_Science', '2_Bhugol_Geography'))
import geography_data
build(os.path.join(HOME, 'Social_Science', '2_Bhugol_Geography', 'Geography_Bhugol_Question_Bank.pdf'),
      geography_data.TITLE, geography_data.SUBTITLE, geography_data.SECTIONS)
print("Geography OK")

# Civics
addpath(os.path.join(HOME, 'Social_Science', '3_Rajneeti_Civics'))
import civics_data
build(os.path.join(HOME, 'Social_Science', '3_Rajneeti_Civics', 'Civics_Rajneeti_Question_Bank.pdf'),
      civics_data.TITLE, civics_data.SUBTITLE, civics_data.SECTIONS)
print("Civics OK")

# Economics
addpath(os.path.join(HOME, 'Social_Science', '4_Arthshastra_Economics'))
import economics_data
build(os.path.join(HOME, 'Social_Science', '4_Arthshastra_Economics', 'Economics_Arthshastra_Question_Bank.pdf'),
      economics_data.TITLE, economics_data.SUBTITLE, economics_data.SECTIONS)
print("Economics OK")

print("\nAll PDFs generated successfully!")
