# -*- coding: utf-8 -*-
"""Generate Answer Key text and PDF files for all subjects."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from pdfgen import build

BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.abspath(os.path.join(BASE, '..'))

def addpath(p):
    sys.path.insert(0, p)

def sortkey(k):
    s = str(k)
    return int(s) if s.isdigit() else s

results = []

# Hindi
addpath(os.path.join(HOME, 'Hindi'))
import hindi_data
results.append(('Hindi', 'Hindi', hindi_data.ANSWER_KEY, 'KVGD'))

# English
addpath(os.path.join(HOME, 'English'))
import english_data
# English uses A/B/C/D
results.append(('English', 'English', english_data.ANSWER_KEY, 'ABCD'))

# Mathematics
addpath(os.path.join(HOME, 'Mathematics'))
import maths_data
results.append(('Mathematics', 'Mathematics', maths_data.ANSWER_KEY, 'KVGD'))

# Science
addpath(os.path.join(HOME, 'Science'))
import science_data
results.append(('Science', 'Science', science_data.ANSWER_KEY, 'KVGD'))

# History
addpath(os.path.join(HOME, 'Social_Science', '1_Itihaas_History'))
import history_data
results.append(('History', 'History_Itihaas', history_data.ANSWER_KEY, 'KVGD'))

# Geography
addpath(os.path.join(HOME, 'Social_Science', '2_Bhugol_Geography'))
import geography_data
results.append(('Geography', 'Geography_Bhugol', geography_data.ANSWER_KEY, 'KVGD'))

# Civics
addpath(os.path.join(HOME, 'Social_Science', '3_Rajneeti_Civics'))
import civics_data
results.append(('Civics', 'Civics_Rajneeti', civics_data.ANSWER_KEY, 'KVGD'))

# Economics
addpath(os.path.join(HOME, 'Social_Science', '4_Arthshastra_Economics'))
import economics_data
results.append(('Economics', 'Economics_Arthshastra', economics_data.ANSWER_KEY, 'KVGD'))

for name, idname, akey, fmt in results:
    # text file
    txtpath = os.path.join(HOME, 'Answer_Keys', f'{idname}_Answer_Key.txt')
    with open(txtpath, 'w', encoding='utf-8') as f:
        f.write(f"JAC BOARD CLASS 10 - {name.upper()} ANSWER KEY\n")
        f.write("=" * 60 + "\n\n")
        f.write("बहुविकल्पीय प्रश्नों (MCQ) के उत्तर:\n\n")
        for k, v in sorted(akey.items(), key=lambda x: sortkey(x[0])):
            f.write(f"Q{k}: {v}\n")
        f.write("\nसभी वस्तुनिष्ठ/बहुविकल्पीय प्रश्नों के उत्तर उपरोक्त कुंजी में दिए गए हैं।\n")
        f.write("(व्यक्तिपरक प्रश्नों के उत्तर मुख्य प्रश्न-पत्र PDF में ही उत्तर के साथ दिए गए हैं।)\n")
    # pdf
    pdfpath = os.path.join(HOME, 'Answer_Keys', f'{idname}_Answer_Key.pdf')
    # build as lines
    items = []
    for k in sorted(akey.keys(), key=sortkey):
        items.append(('Q', f"Q{k} : {akey[k]}"))
    sections = [
        (f"{name.upper()} ANSWER KEY - MCQ (बहुविकल्पीय उत्तर)", items)
    ]
    build(pdfpath, f"{name.upper()} ANSWER KEY", "JAC Board Class 10 - MCQ Objective Answer Key", sections)
    print(f"{idname} answer key done")

print("\nAll answer keys generated!")
