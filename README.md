# Dilshan — JAC Class 10 Study Hub

एक पूरा ऑफ़लाइन-रेडी स्टडी हब Class 10 (Jharkhand Academic Council — JAC Board) के लिए —
भौतिक/रसायन/जीव विज्ञान, गणित, हिंदी, अंग्रेज़ी और सामाजिक विज्ञान (इतिहास, भूगोल, राजनीति, अर्थशास्त्र)।

## 🌐 Live site
**https://dilshanking7.github.io/dilshan/**

हर बार `main` ब्रांच पर push होते ही GitHub Pages पर साइट अपने आप update हो जाती है।

## 📚 Features
- **Quiz & MCQ** — chapter-wise questions, मॉक टेस्ट, results save
- **प्रयोगशाला (Virtual Lab)** — physics/chemistry/biology experiments
- **रसायन Mixing Lab** — drag & drop करके 138 पदार्थ मिलाओ, अभिक्रिया/समीकरण/निष्कर्ष देखो
- **Diagram Lab** — 26 आरेख, click करके हर अंग का कार्य जानो
- **आवर्त सारणी** — सभी तत्व, गलनांक/क्वथनांक slider
- **Notes, Formulas, Practicals, Stories, PDFs**, previous-5-years frequency analysis

## 📂 Structure
- `class10/website/` — असली वेबसाइट (पूरी तरह static, कोई server नहीं चाहिए)
- `class10/Scripts/` — data/PDF build scripts (Python + Node)
- `class10/Answer_Keys/`, `class10/Science/`, `class10/Mathematics/` आदि — question banks

## 🚀 Local use
सिर्फ `class10/website/index.html` को ब्राउज़र में खोलो — बिना internet भी सब कुछ चलता है।

## 🛠 Dev workflow (नया feature जोड़ने पर)
```bash
git add .
git commit -m "add: kya feature add kiya"
git push
```
Push होते ही live site अपने आप deploy हो जाती है।

## ⚙️ Note
GitHub Pages deploy GitHub Actions workflow (`.github/workflows/pages.yml`) से होता है —
Settings → Pages → Source: **GitHub Actions**।