import glob, io, json, os, sys

OUT = r"E:\logo\class10\website\js\allquestions.js"
DATA = r"E:\logo\class10\website\js\data"

combined = {}
for f in sorted(glob.glob(os.path.join(DATA, '*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        subj = json.load(fh)
    combined[os.path.basename(f)[:-5]] = subj

total = sum(len(s["questions"]) for s in combined.values())
payload = json.dumps(combined, ensure_ascii=False, separators=(",", ":"))
js = ("// Auto-generated embedded question bank (" + str(total) + " questions).\n"
      "// Loaded first on every page so the site works from file:// without fetch.\n"
      "window.ALL_QUESTIONS = " + payload + ";\n")

with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write(js)

print("wrote", OUT, "-", total, "questions,", len(combined), "subjects")